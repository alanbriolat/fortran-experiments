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
        internal = self.attr.__get__(obj, objtype)
        external = internal.rstrip(' ')
        print '[get] converted', repr(internal), 'to', repr(external)
        return external

    def __set__(self, obj, val):
        """Add space padding on the right for the internal value."""
        external = val
        internal = val + ' ' * (self.attr.size - len(val))
        print '[set] converted', repr(external), 'to', repr(internal)
        self.attr.__set__(obj, internal)


class ConfigType(ctypes.Structure):
    _fields_ = [('a', ctypes.c_int),
                ('b', ctypes.c_char * 8),
                ('c', ctypes.c_int)]

ConfigType.b = FortranString(ConfigType.b)


check_config = configstrings.__configstrings_MOD_check_config
check_config.restype = None
check_config.argtypes = [ctypes.POINTER(ConfigType)]

conf = ConfigType(12, 'hello', 52)
print(repr(conf.b))
check_config(conf)
