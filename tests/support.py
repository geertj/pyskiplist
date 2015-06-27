#
# This file is part of PySkiplist. PySkiplist is Copyright (c) 2012-2015 by
# the PySkiplist authors.
#
# PySkiplist is free software available under the MIT license. See the file
# named LICENSE distributed with this file for the exact licensing terms.

from __future__ import absolute_import, print_function

import os
import sys
import unittest
import tempfile
import shutil
import re


__all__ = ['TestCase', 'PerformanceTest', 'MemoryTest']


class TestCase(unittest.TestCase):
    """Base class for test suites."""

    test_prefix = 'test'

    @classmethod
    def setup_loader(cls):
        unittest.TestLoader.testMethodPrefix = cls.test_prefix

    @classmethod
    def setUpClass(cls):
        cls.testdir = os.path.abspath(os.path.split(__file__)[0])
        cls.topdir = os.path.split(cls.testdir)[0]

    def setUp(self):
        self._tmpindex = 0
        self.__tmpdir = None

    def tearDown(self):
        if self.__tmpdir is None:
            return
        # Some paranoia checks to make me feel better before calling
        # shutil.rmtree()..
        assert '/..' not in self.__tmpdir and '\\..' not in self.__tmpdir
        assert os.stat(self.__tmpdir).st_ino == self.__tmpinode
        try:
            shutil.rmtree(self.__tmpdir)
        except OSError:
            # On Windows a WindowsError is raised when files are
            # still open (WindowsError inherits from OSError).
            pass
        self.__tmpdir = None
        self.__tmpinode = None

    @property
    def tempdir(self):
        if self.__tmpdir is None:
            self.__tmpdir = os.path.realpath(tempfile.mkdtemp('pyskiplist-test'))
            self.__tmpinode = os.stat(self.__tmpdir).st_ino
        return self.__tmpdir

    def tempname(self, name=None):
        if name is None:
            name = 'tmpfile-{0}'.format(self._tmpindex)
            self._tmpindex += 1
        return os.path.join(self.tempdir, name)

    @property
    def verbose(self):
        try:
            return int(os.environ['VERBOSE'])
        except (KeyError, ValueError):
            return 0

    def assertRaises(self, exc, func, *args, **kwargs):
        # Like unittest.assertRaises, but returns the exception.
        try:
            func(*args, **kwargs)
        except exc as e:
            exc = e
        except Exception as e:
            self.fail('Wrong exception raised: {0!s}'.format(e))
        else:
            self.fail('Exception not raised: {0!s}'.format(exc))
        return exc


re_lu = re.compile('[A-Z]+[a-z0-9]+')

def split_cap_words(s):
    """Split the CamelCase string *s* into words."""
    return re_lu.findall(s)


class PerformanceTest(TestCase):
    """Base class for performance tests."""

    results_name = 'performance.txt'
    test_prefix = 'perf'

    def add_result(self, result, suffix=None, params={}, name=None):
        """Add a performance test result."""
        if name is None:
            frame = sys._getframe(1)
            clsname = frame.f_locals.get('self', '').__class__.__name__
            methname = frame.f_code.co_name
            names = split_cap_words(clsname)
            name = '{0}_{1}'.format(''.join(names[1:]), methname[len(self.test_prefix)+1:]).lower()
        if suffix is not None:
            name = '{}_{!s}'.format(name, suffix)
        if params is not None:
            params = ','.join(['{0}={1}'.format(k, params[k]) for k in params])
        with open(self.results_name, 'a') as fout:
            fout.write('{0:<32s} {1:<16.2f} {2:s}\n'.format(name, result, params))

    @classmethod
    def start_new_results(cls):
        try:
            os.unlink(cls.results_name)
        except OSError:
            pass


class MemoryTest(PerformanceTest):
    """Special case of a performance test that writes to memory.txt."""

    results_name = 'memory.txt'
    test_prefix = 'mem'
