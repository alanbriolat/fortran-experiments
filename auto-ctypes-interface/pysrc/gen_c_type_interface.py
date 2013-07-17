"""
Fortran derived type interface generator.

Usage:
    gen_interface bind_c <module_name> [<input>...]
    gen_interface (py_ctypes | py_numpy) [<input>...]
"""

import sys
import collections
from itertools import chain


def split(s, *args, **kwargs):
    """Do ``s.split(...)``, but trim whitespace from all results."""
    return [x.strip() for x in s.split(*args, **kwargs)]


def produce_lines(stream):
    """Produce canonical Fortran source lines from *stream*.

    Filter *stream*, which is an iterable of source lines, by removing Fortran
    comments, extraneous whitespace and blank lines, and joining lines that are
    split by continuation characters.
    """
    output = ''
    for line in stream:
        # Remove comment, strip whitespace
        line = split(line, '!', 1)[0]
        # Skip empty lines
        if line == '':
            continue
        # Accumulate another line if continuation character is present
        if line.endswith('&'):
            output += line.rstrip('& ')
            continue
        # Yield a line
        yield output + line
        output = ''


def indent(s, pad='  ', count=1):
    return pad * count + s


class Module(collections.namedtuple('Module', ['name', 'types'])):
    def import_f_types(self):
        return ['use {0.module}, only: {0.name}'.format(t) for t in self.types]

    def bind_c_types_and_decls(self, defs):
        return list(chain.from_iterable(t.bind_c_type(defs) + t.bind_c_decls() for t in self.types))

    def bind_c_converters(self):
        return list(chain.from_iterable(t.bind_c_converters() for t in self.types))


class Type(collections.namedtuple('Type', ['name', 'module', 'members'])):
    @property
    def c_name(self):
        return "{}_{}_c".format(self.module, self.name)

    @property
    def f_to_c(self):
        return "{}_{}_f_to_c".format(self.module, self.name)

    @property
    def c_to_f(self):
        return "{}_{}_c_to_f".format(self.module, self.name)

    def bind_c_type(self, defs):
        return [
            'type, bind(c) :: ' + self.c_name,
            ] + [indent(v.bind_c(defs)) for v in self.members] + [
            'end type ' + self.c_name,
        ]

    def bind_c_decls(self):
        return [
            'public :: ' + self.c_name,
            'public :: ' + self.f_to_c,
            'public :: ' + self.c_to_f,
        ]

    def bind_c_converters(self):
        return [
            'pure subroutine {}(f, c)'.format(self.f_to_c),
            indent('type({}), intent(in) :: f'.format(self.name)),
            indent('type({}), intent(out) :: c'.format(self.c_name)),
            ] + [indent(v.bind_c_convert_f_to_c(defs), count=2) for v in self.members] + [
            'end subroutine {}'.format(self.f_to_c),
            'pure subroutine {}(c, f)'.format(self.c_to_f),
            indent('type({}), intent(in) :: c'.format(self.c_name)),
            indent('type({}), intent(out) :: f'.format(self.name)),
            ] + [indent(v.bind_c_convert_c_to_f(defs), count=2) for v in self.members] + [
            'end subroutine {}'.format(self.c_to_f),
        ]


class Variable(collections.namedtuple('Variable', ['name', 'typespec'])):
    def bind_c(self, defs):
        return '{} :: {}'.format(self.typespec.bind_c(defs), self.name)

    def bind_c_convert_f_to_c(self, defs):
        if self.typespec.type == 'type':
            type = defs.type_index[self.typespec.type_args[0]]
            return 'call {1}(f%{0}, c%{0})'.format(self.name, type.f_to_c)
        else:
            return 'c%{0} = f%{0}'.format(self.name)

    def bind_c_convert_c_to_f(self, defs):
        if self.typespec.type == 'type':
            type = defs.type_index[self.typespec.type_args[0]]
            return 'call {1}(c%{0}, f%{0})'.format(self.name, type.c_to_f)
        else:
            return 'f%{0} = c%{0}'.format(self.name)


class Typespec(collections.namedtuple('Typespec', ['type', 'type_args', 'dimension', 'other'])):
    def bind_c(self, defs):
        parts = []

        if self.type == 'real':
            parts.append('real(c_double)')
        elif self.type == 'integer':
            parts.append('integer(c_int)')
        elif self.type == 'character':
            parts.append('character({})'.format(','.join(['kind=c_char'] + self.type_args)))
        elif self.type == 'logical':
            parts.append('logical(c_bool)')
        elif self.type == 'type':
            assert len(self.type_args) == 1
            parts.append('type({})'.format(defs.type_index[self.type_args[0]].c_name))
        else:
            raise ValueError('Unhandled type: {}({})'.format(self.type, ','.join(self.type_args)))

        if self.dimension is not None:
            parts.append('dimension({})'.format(','.join(self.dimension)))

        for spec in self.other:
            raise ValueError('Unhandled type specifier: ' + spec)

        return ', '.join(parts)


class Definitions(object):
    def __init__(self, modules):
        self.modules = modules
        self.module_index = dict((m.name, m) for m in self.modules)
        self.type_index = dict(chain.from_iterable(((t.name, t) for t in m.types) for m in self.modules))

    def bind_c_module(self, name):
        return [
            'module {}'.format(name),
            indent('use iso_c_binding'),
            ] + map(indent, chain.from_iterable(m.import_f_types() for m in self.modules)) + [
            indent('implicit none'),
            indent('private'),
            ] + map(indent, chain.from_iterable(m.bind_c_types_and_decls(defs) for m in self.modules)) + [
            'contains',
            ] + map(indent, chain.from_iterable(m.bind_c_converters() for m in self.modules)) + [
            'end module {}'.format(name),
        ]


def scan_module(line, reader):
    name = split(line)[1]
    types = []
    while True:
        line = next(reader)
        if line.startswith('end module'):
            return Module(name, types)
        if line.startswith('type '):
            types.append(scan_type(name, line, reader))


def scan_type(module, line, reader):
    if '::' in line:
        name = split(line, '::')[1]
    else:
        name = split(line)[1]
    members = []
    while True:
        line = next(reader)
        if line.startswith('end type'):
            return Type(name, module, members)
        else:
            members += scan_variables(line)


def scan_variables(line):
    typespec, names = split(line, '::')

    typespec = split(typespec, ',')
    typename = None
    typeargs = None
    dimension = None
    others = []
    for spec in typespec:
        outer, inner = split_specifier(spec)
        if outer in ('real', 'integer', 'character', 'logical', 'type'):
            typename = outer
            typeargs = inner
            continue
        elif outer == 'dimension':
            dimension = inner
        else:
            other.append(spec)
    typespec = Typespec(typename, typeargs, dimension, others)

    names = split(names, ',')

    return [Variable(name, typespec) for name in names]


def split_specifier(spec):
    outer, _, inner = spec.partition('(')
    return (outer.lower(), [] if inner == '' else split(inner[:-1], ','))


if __name__ == '__main__':
    from docopt import docopt

    args = docopt(__doc__)

    if args['<input>']:
        stream = chain.from_iterable(open(f, 'r') for f in args['<input>'])
    else:
        stream = sys.stdin

    reader = produce_lines(stream)
    modules = []
    for line in reader:
        if line.startswith('module '):
            modules.append(scan_module(line, reader))

    defs = Definitions(modules)

    if args['bind_c']:
        print('\n'.join(defs.bind_c_module(args['<module_name>'])))
    elif args['py_ctypes']:
        pass
    elif args['py_numpy']:
        pass
