#
# This file is part of PySkiplist. PySkiplist is Copyright (c) 2012-2015 by
# the PySkiplist authors.
#
# PySkiplist is free software available under the MIT license. See the file
# named LICENSE distributed with this file for the exact licensing terms.

from __future__ import absolute_import, print_function

import os
import sys

from argparse import ArgumentParser
from unittest import TestLoader, TextTestRunner, TestSuite


parser = ArgumentParser()
parser.add_argument('-v', '--verbose', help='be more verbose', action='count', default=1)
parser.add_argument('-f', '--failfast', help='stop on first failure', action='store_true')
parser.add_argument('-b', '--buffer', help='buffer stdout and stderr', action='store_true')
parser.add_argument('suite', nargs='+', help='name of test suite to run', metavar='suite',
                    choices=('all', 'unit', 'performance', 'memory', 'documentation'))
args = parser.parse_args()

if 'all' in args.suite:
    args.suite = ['unit', 'performance', 'memory', 'documentation']

os.environ['VERBOSE'] = str(args.verbose)

# Change directory to tests/ irrespective of where we're called from.
topdir = os.path.split(os.path.abspath(__file__))[0]
testdir = os.path.join(topdir, 'tests')
os.chdir(testdir)

# If running under tox, replace the entry for the current directory on sys.path
# with the test directory. This prevents the tox runs from running in the
# potentially unclean environment from the checkout our source tree.
# Otherwise, if not running under tox, we want the option to run from the
# current directory, so we add the test directory instead.
if os.environ.get('TOX') == 'yes':
    sys.path[0] = testdir
else:
    sys.path.insert(0, testdir)

from support import TestCase, MemoryTest, PerformanceTest

suite = TestSuite()

for name in args.suite:
    TestCase.setup_loader()
    if name == 'unit':
        pattern = 'test_*.py'
    elif name == 'performance':
        pattern = 'perf_*.py'
        PerformanceTest.setup_loader()
        PerformanceTest.start_new_results()
    elif name == 'memory':
        pattern = 'mem_*.py'
        MemoryTest.setup_loader()
        MemoryTest.start_new_results()
    elif name == 'documentation':
        pattern = 'documentation.py'
    loader = TestLoader()
    tests = loader.discover('.', pattern)
    suite.addTest(tests)

runner = TextTestRunner(verbosity=args.verbose, buffer=args.buffer, failfast=args.failfast)
result = runner.run(suite)
if result.errors or result.failures:
    sys.exit(1)
