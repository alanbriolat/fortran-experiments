#!/usr/bin/env python2
import ctypes
import sys

import numpy as np

configstrings = ctypes.cdll.LoadLibrary(sys.argv[1])


class FortranString(object):
    """Wrap a C character array descriptor to use Fortran string conventions.

    C strings are null-terminated, whereas Fortran strings are space-padded.
    This descriptor can be used to wrap around a :class:`ctypes.Structure`
    character array attribute to use space-padded values internally.
    """
    def __init__(self, attr):
        self.attr = attr

    def __get__(self, obj, objtype):
        """Strip space padding from the right of the internal value."""
        return self.attr.__get__(obj, objtype).rstrip(' ')

    def __set__(self, obj, val):
        """Add space padding on the right for the internal value."""
        self.attr.__set__(obj, '{{: <{}s}}'.format(self.attr.size).format(val))


def use_fortran_strings(cls):
    """Treat all character arrays as Fortran strings.

    A class decorator that applies the :class:`FortranString` descriptor to all
    character arrays in a :class:`ctypes.Structure`.
    """
    for name, type in cls._fields_:
        if type.__name__.startswith('c_char_Array_'):
            setattr(cls, name, FortranString(getattr(cls, name)))
            print name, '-> FortranString'
    return cls


@use_fortran_strings
class ConfigType(ctypes.Structure):
    _fields_ = [('a', ctypes.c_int),
                ('b', ctypes.c_char * 8),
                ('c', ctypes.c_int)]


check_config = configstrings.__configstrings_MOD_check_config
check_config.restype = None
check_config.argtypes = [ctypes.POINTER(ConfigType)]

conf = ConfigType(12, 'hello', 52)
print(repr(conf.b))
check_config(conf)
