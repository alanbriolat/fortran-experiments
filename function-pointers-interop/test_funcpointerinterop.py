#!/usr/bin/env python2
import ctypes
import sys


STRFUNC = ctypes.CFUNCTYPE(None, ctypes.c_int)


class funcs_t(ctypes.Structure):
    _fields_ = [('debug', STRFUNC),
                ('error', STRFUNC)]


def debug(*args):
    print(args)


def error(*args):
    raise Exception(args)


funcpointerinterop = ctypes.cdll.LoadLibrary(sys.argv[1])

do_debug = funcpointerinterop.__funcpointerinterop_MOD_do_debug
do_debug.restype = None
do_debug.argtypes = [ctypes.POINTER(funcs_t)]
do_error = funcpointerinterop.__funcpointerinterop_MOD_do_error
do_error.restype = None
do_error.argtypes = [ctypes.POINTER(funcs_t)]


conf = funcs_t(STRFUNC(debug), STRFUNC(error))
do_debug(conf)
do_error(conf)
