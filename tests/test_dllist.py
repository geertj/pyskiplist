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

from pyskiplist import dllist, Node
from pyskiplist.dllist import check, dump, getsize
from support import TestCase


class TestDllist(TestCase):

    def test_basic(self):
        dll = dllist()
        check(dll)
        self.assertIsNone(dll.first)
        self.assertIsNone(dll.last)
        self.assertEqual(len(dll), 0)
        # insert first element
        n1 = Node('foo')
        dll.insert(n1)
        self.assertIs(dll.first, n1)
        self.assertIs(dll.last, n1)
        self.assertEqual(len(dll), 1)
        check(dll)
        # insert second at end
        n2 = Node('bar')
        dll.insert(n2)
        self.assertIs(dll.first, n1)
        self.assertIs(dll.last, n2)
        self.assertEqual(len(dll), 2)
        check(dll)
        # insert in middle
        n3 = Node('baz')
        dll.insert(n3, before=n2)
        self.assertIs(dll.first, n1)
        self.assertIs(dll.last, n2)
        self.assertEqual(len(dll), 3)
        check(dll)
        # remove middle
        dll.remove(n3)
        self.assertIs(dll.first, n1)
        self.assertIs(dll.last, n2)
        self.assertEqual(len(dll), 2)
        check(dll)
        # remove first
        dll.remove(n1)
        self.assertIs(dll.first, n2)
        self.assertIs(dll.last, n2)
        self.assertEqual(len(dll), 1)
        check(dll)
        # remove remaining element
        dll.remove(n2)
        self.assertIsNone(dll.first)
        self.assertIsNone(dll.last)
        self.assertEqual(len(dll), 0)
        check(dll)

    def test_remove_removed(self):
        # It is OK to remove an already removed node.
        dll = dllist()
        node = Node('foo')
        dll.insert(node)
        self.assertIn(node, list(dll))
        dll.remove(node)
        self.assertNotIn(node, list(dll))
        dll.remove(node)
        check(dll)

    def test_iter(self):
        dll = dllist()
        for i in range(10):
            dll.insert(Node(10+i))
            check(dll)
        value = 10
        for node in dll:
            self.assertIsInstance(node, Node)
            self.assertEqual(node.value, value)
            value += 1
        check(dll)

    def test_many_nodes(self):
        nodes = []
        dll = dllist()
        count = 10000
        for i in range(count):
            before = random.choice(nodes) if nodes else None
            node = Node(i)
            dll.insert(node, before)
            nodes.append(node)
            self.assertEqual(len(dll), i+1)
            if i % 100 == 0:
                check(dll)
        check(dll)
        for i in range(count):
            r = random.randint(0, len(nodes)-1)
            node = nodes[r]; del nodes[r]
            dll.remove(node)
            self.assertEqual(len(dll), count-i-1)
            if i % 100 == 0:
                check(dll)
        check(dll)

    def test_size(self):
        dll = dllist()
        size = getsize(dll)
        self.assertIsInstance(size, int)
        self.assertGreater(size, 0)
        self.assertLess(size, 200)

    def test_node_size(self):
        node = Node('foo')
        size = getsize(node)
        self.assertIsInstance(size, int)
        self.assertGreater(size, 0)
        self.assertLess(size, 200)


class TestDllistDebug(TestCase):
    """Coverage for debugging tools."""

    def test_dump(self):
        dll = dllist()
        dll.insert(Node('foo'))
        dll.insert(Node('bar'))
        out = six.StringIO()
        dump(dll, out)
        s = out.getvalue()
        self.assertIsInstance(s, str)
        self.assertGreater(len(s), 20)


if __name__ == '__main__':
    unittest.main()
