#
# This file is part of PySkiplist. PySkiplist is Copyright (c) 2012-2015 by
# the PySkiplist authors.
#
# PySkiplist is free software available under the MIT license. See the file
# named LICENSE distributed with this file for the exact licensing terms.

from __future__ import absolute_import, print_function, division

import time
import random
import unittest

from pyskiplist import SkipList
from support import PerformanceTest


class PerfSkipList(PerformanceTest):
    """Performance tests for our skiplist."""

    def _create_skiplist(self, n):
        # Create a skiplist with *n* elements.
        sl = SkipList()
        maxkey = 100*n
        for i in range(n):
            sl.insert(random.randint(0, maxkey), i)
        return sl

    def _create_workload(self, sl, n):
        # Create a workload with *n* items.
        pairs = []
        maxkey = 100*len(sl)
        for i in range(n):
            pair = (random.randint(0, maxkey), i)
            pairs.append(pair)
        return pairs

    def perf_search_throughput(self):
        for logN in range(3, 6):
            items = 10**logN
            sl = self._create_skiplist(items)
            pairs = list(sl)
            random.shuffle(pairs)
            load = pairs[0:int(0.2*len(sl))]
            count = 0
            t0 = t1 = time.time()
            while count < len(load) and t1 - t0 < 1:
                sl.search(load[count][0])
                count += 1
                if count % 100 == 0:
                    t1 = time.time()
            throughput = count / (t1 - t0)
            self.add_result(throughput, suffix=items)

    def perf_insert_throughput(self):
        for logN in range(3, 6):
            items = 10**logN
            sl = self._create_skiplist(items)
            load = self._create_workload(sl, int(0.2*len(sl)))
            count = 0
            t0 = t1 = time.time()
            while count < len(load) and t1 - t0 < 1:
                sl.insert(*load[count])
                count += 1
                if count % 100 == 0:
                    t1 = time.time()
            throughput = count / (t1 - t0)
            self.add_result(throughput, suffix=items)

    def perf_remove_throughput(self):
        for logN in range(3, 6):
            items = 10**logN
            sl = self._create_skiplist(items)
            pairs = list(sl)
            random.shuffle(pairs)
            load = pairs[0:int(0.2*len(sl))]
            count = 0
            t0 = t1 = time.time()
            while count < len(load) and t1 - t0 < 1:
                sl.remove(load[count][0])
                count += 1
                if count % 100 == 0:
                    t1 = time.time()
            throughput = count / (t1 - t0)
            self.add_result(throughput, suffix=items)

    def perf_index_throughput(self):
        for logN in range(3, 6):
            items = 10**logN
            sl = self._create_skiplist(items)
            load = random.sample(range(items), int(0.2*len(sl)))
            count = 0
            t0 = t1 = time.time()
            while count < len(load) and t1 - t0 < 1:
                sl[load[count]]
                count += 1
                if count % 100 == 0:
                    t1 = time.time()
            throughput = count / (t1 - t0)
            self.add_result(throughput, suffix=items)


if __name__ == '__main__':
    PerfSkipList.setup_loader()
    unittest.main()
