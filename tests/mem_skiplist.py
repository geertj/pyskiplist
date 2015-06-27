#
# This file is part of PySkiplist. PySkiplist is Copyright (c) 2012-2015 by
# the PySkiplist authors.
#
# PySkiplist is free software available under the MIT license. See the file
# named LICENSE distributed with this file for the exact licensing terms.

from __future__ import absolute_import, print_function

import sys
import unittest

from support import MemoryTest
from pyskiplist import SkipList
from pyskiplist.skiplist import getsize


class MemSkipList(MemoryTest):
    """Memory usage tests for SkipList."""

    def mem_size(self):
        sl = SkipList()
        self.add_result(getsize(sl))

    def mem_node_size(self):
        for logN in range(3, 6):
            items = 10**logN
            sl = SkipList()
            for i in range(items):
                sl.insert(i, i)
            size = getsize(sl)
            self.add_result(size/items, suffix=items)

    def mem_node_overhead(self):
        for logN in range(3, 6):
            items = 10**logN
            sl = SkipList()
            for i in range(items):
                sl.insert(i, i)
            overhead = getsize(sl) - items * 2 * sys.getsizeof(i)
            self.add_result(overhead/items, suffix=items)


if __name__ == '__main__':
    MemSkipList.setup_loader()
    unittest.main()
