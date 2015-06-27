#
# This file is part of PySkiplist. PySkiplist is Copyright (c) 2012-2015 by
# the PySkiplist authors.
#
# PySkiplist is free software available under the MIT license. See the file
# named LICENSE distributed with this file for the exact licensing terms.

from __future__ import absolute_import, print_function

import os
import doctest
import unittest
import sphinx

from support import TestCase


class TestDocumentation(TestCase):

    def test_readme(self):
        doctest.testfile(os.path.join(self.topdir, 'README.rst'),
                         module_relative=False, verbose=self.verbose > 2)

    def test_build_docs(self):
        docdir = os.path.join(self.topdir, 'docs')
        os.chdir(docdir)
        htmldir = self.tempdir
        args = ['sphinx', '-b', 'html', '-nW', '.', htmldir]
        if self.verbose < 3:
            args += ['-Q']
        try:
            sphinx.main(args)
        except SystemExit as e:
            ret = e.code
        self.assertEqual(ret, 0)


if __name__ == '__main__':
    os.environ['VERBOSE'] = '3'
    unittest.main()
