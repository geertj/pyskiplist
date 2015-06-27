#
# This file is part of PySkiplist. PySkiplist is Copyright (c) 2012-2015 by
# the PySkiplist authors.
#
# PySkiplist is free software available under the MIT license. See the file
# named LICENSE distributed with this file for the exact licensing terms.

from __future__ import absolute_import, print_function

import random
import unittest
import six

from support import TestCase
from pyskiplist import SkipList
from pyskiplist.skiplist import check, dump, getsize


class TestSkipList(TestCase):
    """Unit test suite for SkipList."""

    size = 100

    def _create_skiplist(self, size, keysize, valuesize):
        sl = SkipList()
        pairs = []
        values = {}
        for i in range(size):
            pair = (random.randint(0, keysize), random.randint(0, valuesize))
            sl.insert(*pair)
            pairs.append(pair)
            if pair[0] not in values:
                values[pair[0]] = []
            values[pair[0]].append(pair[1])
        pairs = sorted(pairs, key=lambda x: x[0])
        return sl, pairs, values

    # GENERAL API ...

    def test_level(self):
        sl = SkipList()
        self.assertEqual(sl.level, 1)
        check(sl)

    def test_insert(self):
        size = self.size
        sl = SkipList()
        pairs = []
        for i in range(size):
            pair = (random.randint(0, 2*size), random.randint(0, 10*size))
            sl.insert(*pair)
            pairs = sorted(pairs + [pair], key=lambda x: x[0])
            check(sl); self.assertEqual(list(sl), pairs)
        self.assertGreater(sl.level, 1)

    def test_replace(self):
        size = self.size
        sl = SkipList()
        values = {}
        for i in range(size):
            pair = (random.randint(0, 2*size), random.randint(0, 10*size))
            sl.replace(*pair)
            values[pair[0]] = pair[1]
            pairs = sorted(values.items(), key=lambda x: x[0])
            check(sl); self.assertEqual(list(sl), pairs)
        self.assertGreater(sl.level, 1)

    def test_clear(self):
        size = self.size
        sl = SkipList()
        for i in range(size):
            sl.insert(random.randint(0, 2*size), random.randint(0, 10*size))
        self.assertGreater(sl.level, 1)
        self.assertEqual(len(sl), size)
        sl.clear()
        check(sl); self.assertEqual(list(sl), [])
        self.assertEqual(sl.level, 1)

    def test_len(self):
        size = self.size
        sl = SkipList()
        pairs = []
        for i in range(size):
            pair = (random.randint(0, 2*size), random.randint(0, 10*size))
            sl.insert(*pair)
            pairs = sorted(pairs + [pair], key=lambda x: x[0])
            self.assertEqual(len(sl), i+1)
            check(sl); self.assertEqual(list(sl), pairs)

    def test_bool(self):
        sl = SkipList()
        self.assertFalse(sl)
        self.assertFalse(bool(sl))
        check(sl)
        sl.insert('foo', 'bar')
        self.assertTrue(sl)
        self.assertTrue(bool(sl))
        check(sl)

    def test_repr(self):
        sl = SkipList()
        sl.insert(1, 2)
        sl.insert(3, 4)
        self.assertEqual(repr(sl), 'SkipList(((1, 2), (3, 4)))')
        check(sl)

    def test_iter(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, 2*size, 10*size)
        self.assertEqual(list(sl), pairs)
        check(sl)

    def test_items(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, size, 10*size)
        # test .items(), .keys() and .values()
        for ix, func in ((slice(0, 2), sl.items), (0, sl.keys), (1, sl.values)):
            def ref(start, stop):
                return [pair[ix] for pair in pairs
                            if (start is None or pair[0] >= start)
                                    and (stop is None or pair[0] < stop)]
            self.assertEqual(list(func()), ref(None, None))
            self.assertEqual(list(func(start=10)), ref(10, None))
            self.assertEqual(list(func(start=10.1)), ref(10.1, None))
            self.assertEqual(list(func(start=11)), ref(11, None))
            self.assertEqual(list(func(stop=90)), ref(None, 90))
            self.assertEqual(list(func(stop=90.1)), ref(None, 90.1))
            self.assertEqual(list(func(stop=91)), ref(None, 91))
            self.assertEqual(list(func(start=10, stop=90)), ref(10, 90))
            self.assertEqual(list(func(start=10.1, stop=90)), ref(10.1, 90))
            self.assertEqual(list(func(start=10, stop=90.1)), ref(10, 90.1))
            self.assertEqual(list(func(start=10.1, stop=90.1)), ref(10.1, 90.1))
            check(sl); self.assertEqual(list(sl), pairs)

    def test_popitem(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, 2*size, 10*size)
        while pairs:
            self.assertEqual(sl.popitem(), pairs[0])
            del pairs[0]
            check(sl); self.assertEqual(list(sl), pairs)
        self.assertRaises(KeyError, sl.popitem)
        check(sl); self.assertEqual(list(sl), pairs)

    # KEY BASED API ...

    def test_search(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, 2*size, 10*size)
        for key in values:
            self.assertEqual(sl.search(key), values[key][0])
            check(sl); self.assertEqual(list(sl), pairs)
            self.assertIsNone(sl.search(random.randint(2*size, 10*size)))
            check(sl); self.assertEqual(list(sl), pairs)
            self.assertEqual(sl.search(random.randint(2*size, 10*size), -1), -1)
            check(sl); self.assertEqual(list(sl), pairs)

    def test_remove(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, 2*size, 10*size)
        for key in values:
            for value in values[key]:
                sl.remove(key)
                pairs.remove((key, value))
                check(sl); self.assertEqual(list(sl), pairs)
            self.assertRaises(KeyError, sl.remove, key)
            check(sl); self.assertEqual(list(sl), pairs)

    def test_pop(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, 2*size, 10*size)
        for key in values:
            for value in values[key]:
                self.assertEqual(sl.pop(key), value)
                pairs.remove((key, value))
                check(sl); self.assertEqual(list(sl), pairs)
            self.assertRaises(KeyError, sl.pop, key)
            check(sl); self.assertEqual(list(sl), pairs)
            self.assertIsNone(sl.pop(key, None))
            check(sl); self.assertEqual(list(sl), pairs)
            self.assertEqual(sl.pop(key, -1), -1)
            check(sl); self.assertEqual(list(sl), pairs)

    def test_contains(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, 2*size, 10*size)
        for key in values:
            self.assertIn(key, sl)
            check(sl); self.assertEqual(list(sl), pairs)
            self.assertNotIn(random.randint(2*size, 10*size), sl)
            check(sl); self.assertEqual(list(sl), pairs)

    def test_index(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, 2*size, 10*size)
        for key in values:
            self.assertEqual(sl.index(key), pairs.index((key, values[key][0])))
            check(sl); self.assertEqual(list(sl), pairs)
            self.assertRaises(KeyError, sl.index, random.randint(2*size, 10*size))
            check(sl); self.assertEqual(list(sl), pairs)

    def test_count(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, 2*size, 10*size)
        for key in values:
            self.assertEqual(sl.count(key), len(values[key]))
            check(sl); self.assertEqual(list(sl), pairs)
            self.assertEqual(sl.count(random.randint(2*size, 10*size)), 0)
            check(sl); self.assertEqual(list(sl), pairs)

    # BY POSITION API ...

    def test_getitem(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, 2*size, 10*size)
        for i in range(size):
            self.assertEqual(sl[i], pairs[i])
            check(sl); self.assertEqual(list(sl), pairs)
            self.assertEqual(sl[-i-1], pairs[-i-1])
            check(sl); self.assertEqual(list(sl), pairs)
        self.assertRaises(IndexError, sl.__getitem__, size)
        check(sl); self.assertEqual(list(sl), pairs)
        self.assertRaises(IndexError, sl.__getitem__, -size-1)
        check(sl); self.assertEqual(list(sl), pairs)
        self.assertRaises(TypeError, sl.__getitem__, 'foo')
        check(sl); self.assertEqual(list(sl), pairs)

    def test_getitem_slice(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, 2*size, 10*size)
        for ix in (slice(None, None), slice(None, 10), slice(10, None),
                   slice(10, 90), slice(10, -10), slice(-10, None),
                   slice(-10, -1), slice(None, -10), slice(None, -1)):
            self.assertEqual(list(sl[ix]), pairs[ix])
            check(sl); self.assertEqual(list(sl), pairs)

    def test_delitem(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, 2*size, 10*size)
        while pairs:
            ix = random.randrange(-len(pairs), len(pairs))
            del sl[ix]
            del pairs[ix]
            check(sl); self.assertEqual(list(sl), pairs)
            self.assertRaises(IndexError, sl.__delitem__, len(pairs))
            check(sl); self.assertEqual(list(sl), pairs)
            self.assertRaises(IndexError, sl.__delitem__, -len(pairs)-1)
            check(sl); self.assertEqual(list(sl), pairs)
        self.assertRaises(TypeError, sl.__delitem__, 'foo')
        check(sl); self.assertEqual(list(sl), pairs)

    def test_setitem(self):
        size = self.size
        sl, pairs, values = self._create_skiplist(size, 2*size, 10*size)
        for ix, pair in enumerate(pairs):
            sl[ix] = 2*pair[1]
            pairs[ix] = (pair[0], 2*pair[1])
            check(sl); self.assertEqual(list(sl), pairs)
        self.assertRaises(IndexError, sl.__setitem__, size, None)
        check(sl); self.assertEqual(list(sl), pairs)
        self.assertRaises(IndexError, sl.__setitem__, -size-1, None)
        check(sl); self.assertEqual(list(sl), pairs)
        self.assertRaises(TypeError, sl.__setitem__, 'foo', None)
        check(sl); self.assertEqual(list(sl), pairs)


class TestSkipListDebug(TestCase):
    """Coverage for debugging tools."""

    def test_size(self):
        sl = SkipList()
        sl.insert('foo', 'bar')
        size = getsize(sl)
        self.assertIsInstance(size, int)
        self.assertGreater(size, 0)
        self.assertLess(size, 5000)

    def test_node_size(self):
        sl = SkipList()
        for i in range(1000):
            sl.insert(i, None)
        size = getsize(sl)
        self.assertIsInstance(size, int)
        self.assertGreater(size, 0)
        self.assertLess(size/1000, 250)

    def test_dump(self):
        sl = SkipList()
        sl.insert('foo', 'bar')
        sl.insert('baz', 'qux')
        out = six.StringIO()
        dump(sl, out)
        s = out.getvalue()
        self.assertIsInstance(s, str)
        self.assertGreater(len(s), 20)


if __name__ == '__main__':
    unittest.main()
