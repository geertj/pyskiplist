#
# This file is part of PySkiplist. PySkiplist is Copyright (c) 2012-2015 by
# the PySkiplist authors.
#
# PySkiplist is free software available under the MIT license. See the file
# named LICENSE distributed with this file for the exact licensing terms.

from __future__ import absolute_import, print_function

import sys

__all__ = ['Node', 'dllist']


if __debug__:

    def dump(dll, file=sys.stdout):
        print('== Dumping dllist {!r}'.format(dll), file=file)
        print('Size: {}'.format(dll._size), file=file)
        print('First: {!r}'.format(dll.first if dll.first else None), file=file)
        print('Last: {!r}'.format(dll.last if dll.last else None), file=file)
        print('Nodes:', file=file)
        count = 0
        node = dll.first
        while node is not None:
            print('- {!r} [{}]'.format(node, count), file=file)
            node = node._next
            count += 1
        print('Total nodes: {}'.format(count), file=file)

    def check(dll):
        if dll.first is None:
            assert dll.last is None
            assert dll._size == 0
            return
        node = dll.first
        assert node._prev is None
        nnode = node._next
        count = 1
        while nnode is not None:
            assert nnode._prev is node
            node, nnode = nnode, nnode._next
            count += 1
        assert node is dll.last
        assert count == dll._size

    def getsize(obj):
        """Return the size of a Node or dllist."""
        size = sys.getsizeof(obj)
        for key in obj.__slots__:
            size += sys.getsizeof(getattr(obj, key))
        return size


class Node(object):
    """Base node class for :class:`dllist`.

    You can create a custom node with extra attributes by inheriting from this
    class. When you do this you need to set the ``'__slots__'`` attribute to
    include your custom attributes, and include ``'_prev'`` and ``'_next'`` also.
    """

    __slots__ = ('_prev', '_next', 'value')

    def __repr__(self):
        return '<Node(prev={:#x}, next={:#x}, value={!r})>' \
                    .format(id(self._prev), id(self._next), self.value)

    def __init__(self, value=None):
        self._prev = None
        self._next = None
        self.value = value


class dllist(object):
    """A doubly linked list."""

    __slots__ = ('_first', '_last', '_size')

    def __init__(self):
        self._first = None
        self._last = None
        self._size = 0

    @property
    def first(self):
        """The first node in the list."""
        return self._first

    @property
    def last(self):
        """The last node in the list."""
        return self._last

    def __len__(self):
        """Return the number of nodes in this list."""
        return self._size

    def remove(self, node):
        """Remove a node from the list.

        The *node* argument must be a node that was previously inserted in the
        list
        """
        if node is None or node._prev == -1:
            return
        if node._next is None:
            self._last = node._prev  # last node
        else:
            node._next._prev = node._prev
        if node._prev is None:
            self._first = node._next  # first node
        else:
            node._prev._next = node._next
        node._prev = node._next = -1
        self._size -= 1

    def insert(self, node, before=None):
        """Insert a new node in the list.

        The *node* argument must be a :class:`Node` instance.

        If *before* is not provided (the default), the node is appended at the
        end of the list. If *before* is provided, it must be a :class:`Node`
        instance that is already part of this list, and the node is inserted
        before this node.

        To insert at the start of the list, set *before* to :attr:`first`.
        """
        if self._first is None:
            self._first = self._last = node  # first node in list
            self._size += 1
            return node
        if before is None:
            self._last._next = node  # insert as last node
            node._prev = self._last
            self._last = node
        else:
            node._next = before
            node._prev = before._prev
            if node._prev:
                node._prev._next = node
            else:
                self._first = node  # inserting as first node
            node._next._prev = node
        self._size += 1

    def __iter__(self):
        """Return an iterator/generator that yields all nodes.

        Note: it is safe to remove the current node while iterating but you
        should not remove the next one.
        """
        node = self._first
        while node is not None:
            next_node = node._next
            yield node
            node = next_node
