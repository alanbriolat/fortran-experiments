#!/usr/bin/env python

SUBPROJECTS = ['function-pointers']


def options(opt):
    opt.load('compiler_c')
    opt.load('compiler_fc')

    for p in SUBPROJECTS:
        opt.recurse(p)

def configure(conf):
    conf.load('compiler_c')
    conf.load('compiler_fc')
    conf.check_fortran()

    conf.env.FCFLAGS = [
        '-Wall', '-Wextra', '-Wimplicit-interface', '-fimplicit-none',
        '-fmax-errors=1',
    ]

    env = conf.env

    conf.setenv('debug')
    conf.env.FCFLAGS += ['-g', '-fcheck=all', '-fbacktrace']

    # TODO: figure out how variants/setenv works...
    #conf.setenv('release', env)
    #conf.env.FCFLAGS += ['-O3', '-march=native', '-ffast-math', '-funroll-loops']

    for p in SUBPROJECTS:
        conf.recurse(p)


def build(bld):
    for p in SUBPROJECTS:
        bld.recurse(p)
