#
# This file is part of PySkiplist. PySkiplist is Copyright (c) 2012-2015 by
# the PySkiplist authors.
#
# PySkiplist is free software available under the MIT license. See the file
# named LICENSE distributed with this file for the exact licensing terms.

from __future__ import absolute_import, print_function

from invoke import run, task


@task
def clean():
    run('find . -name __pycache__ | xargs rm -rf || :', echo=True)
    run('rm -rf build dist', echo=True)


@task(clean)
def develop():
    run('python setup.py develop', echo=True)
