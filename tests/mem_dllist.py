#
# This file is part of PySkiplist. PySkiplist is Copyright (c) 2012-2015 by
# the PySkiplist authors.
#
# PySkiplist is free software available under the MIT license. See the file
# named LICENSE distributed with this file for the exact licensing terms.

from __future__ import absolute_import, print_function

import unittest

from pyskiplist import dllist, Node
from pyskiplist.dllist import getsize
from support import MemoryTest


class TestDllist(MemoryTest):

    def mem_node(self):
        self.add_result(getsize(Node()))

    def mem_dllist(self):
        self.add_result(getsize(dllist()))


if __name__ == '__main__':
    TestDllist.setup_loader()
    unittest.main()
