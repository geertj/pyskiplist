#
# This file is part of PySkiplist. PySkiplist is Copyright (c) 2012-2015 by
# the PySkiplist authors.
#
# PySkiplist is free software available under the MIT license. See the file
# named LICENSE distributed with this file for the exact licensing terms.

from __future__ import absolute_import, print_function

import time
import unittest

from pyskiplist import dllist, Node
from support import PerformanceTest


class PerfDllist(PerformanceTest):

    def perf_insert_throughput(self):
        t0 = t1 = time.time()
        count = 0
        batch = 1000
        dll = dllist()
        value = 'foo'
        while t1 - t0 < 1:
            for i in range(batch):
                dll.insert(Node(value))
            count += batch
            t1 = time.time()
        speed = count / (t1 - t0)
        self.add_result(speed)


if __name__ == '__main__':
    unittest.defaultTestLoader.testMethodPrefix = 'perf'
    unittest.main()
