import sys
import collections


def split(s, *args, **kwargs):
    """Do ``s.split(...)``, but trim whitespace from all results."""
    return [x.strip() for x in s.split(*args, **kwargs)]


def produce_lines(stream):
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


Module = collections.namedtuple('Module', ['name', 'types'])
Type = collections.namedtuple('Type', ['name', 'members'])
Variable = collections.namedtuple('Variable', ['name', 'typespec'])
Typespec = collections.namedtuple('Typespec', ['type', 'dimension', 'other'])


def scan_module(line, reader):
    name = split(line)[1]
    types = []
    while True:
        line = next(reader)
        if line.startswith('end module'):
            return Module(name, types)
        if line.startswith('type '):
            types.append(scan_type(line, reader))


def scan_type(line, reader):
    if '::' in line:
        name = split(line, '::')[1]
    else:
        name = split(line)[1]
    members = []
    while True:
        line = next(reader)
        if line.startswith('end type'):
            return Type(name, members)
        else:
            members += scan_variables(line)


def scan_variables(line):
    variables = []
    typespec, names = split(line, '::')

    typespec = split(typespec, ',')
    typename = None
    dimension = None
    others = []
    for spec in typespec:
        outer, inner = split_specifier(spec)
        if outer in ('real', 'integer', 'character', 'logical', 'type'):
            typename = spec
            continue
        elif outer == 'dimension':
            dimension = inner
        else:
            other.append(spec)
    typespec = Typespec(typename, dimension, others)

    names = split(names, ',')

    return [Variable(name, typespec) for name in names]


def split_specifier(spec):
    outer, _, inner = spec.partition('(')
    return (outer.lower(), [] if inner == '' else split(inner[:-1], ','))


if __name__ == '__main__':
    reader = produce_lines(sys.stdin)
    modules = []
    for line in reader:
        if line.startswith('module '):
            modules.append(scan_module(line, reader))
    print(modules)
