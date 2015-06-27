#
# This file is part of Bluepass. Bluepass is Copyright (c) 2012-2014
# Geert Jansen.
#
# Bluepass is free software available under the GNU General Public License,
# version 3. See the file LICENSE distributed with this file for the exact
# licensing terms.

from __future__ import absolute_import, print_function

import os
import sys
import math
import random

__all__ = ['SkipList']


# The following functions are debugging functions. They are available only when
# Python is not started with -O.

if __debug__:

    def fmtnode(node):
        """Format a single skiplist node."""
        level = max(1, len(node) - 3)
        skip = '(none)' if level == 1 else node[-1]
        return '<Node(level={}, key={}, value={}, skip={})>' \
                    .format(level, node[0], node[1], skip)

    def dump(sl, file=sys.stdout):
        """Dump a skiplist to standard output."""
        print('== Dumping skiplist {0!r}'.format(sl), file=file)
        print('Level: {}/{}'.format(sl.level, sl.maxlevel), file=file)
        print('Size: {}'.format(len(sl)), file=file)
        node = sl._head
        print('{0} (head)'.format(fmtnode(node)), file=file)
        node = node[2]
        avglvl = avglen = avgsiz = 0
        while node is not sl._tail:
            print('{0}'.format(fmtnode(node)), file=file)
            node = node[2]
            avglvl += max(1, len(node) - 3)
            avglen += len(node)
            avgsiz += nodesize(node)
        print('{0} (tail)'.format(fmtnode(node)), file=file)
        print('Avg level: {:.2f}'.format(avglvl/len(sl)), file=file)
        print('Avg node len: {:.2f}'.format(avglen/len(sl)), file=file)
        print('Avg node memory: {:.2f}'.format(avgsiz/len(sl)), file=file)
        print(file=file)

    def check(sl):
        """Check the internal structure of a skiplist."""
        level = sl.maxlevel
        assert level > 0
        while sl._head[1+level] is sl._tail and level > 1:
            level -= 1
        assert level == sl.level
        assert sl._head[0] is sl._head[1] is None
        assert sl._head[-1] == 0
        pos = 0
        node = sl._head
        inbound = {id(sl._head): 0, id(sl._tail): len(sl)}
        while node is not sl._tail:
            assert isinstance(node, list)
            level = min(sl.level, max(1, len(node)-3))
            assert 1 <= level <= sl.maxlevel
            for i in range(1, level):
                fnode = node[2+i]
                flevel = min(sl.level, max(1, len(fnode)-3))
                if i == flevel-1:
                    inbound[id(fnode)] = pos
            if level > 1:
                assert id(node) in inbound
                assert pos == inbound[id(node)] + node[-1]
            for i in range(level):
                fnode = node[2+i]
                assert isinstance(fnode, list)
                level = max(1, len(node) - 3)
                assert level >= i+1
            node = node[2]
            pos += 1
        assert sl._tail[0] is None
        assert sl._tail[1] is None
        for i in range(sl.maxlevel):
            assert sl._tail[2+i] is None
        assert len(sl) == inbound[id(sl._tail)] + node[-1]

    def nodesize(node):
        """Return the size of a skiplist node."""
        size = sys.getsizeof(node)
        size += sys.getsizeof(node[0])
        size += sys.getsizeof(node[1])
        # All elements in [3:-1] are references so don't count
        if len(node) > 3:
            size += sys.getsizeof(node[-1])
        return size

    def getsize(sl):
        """Return total size of a skiplist."""
        size = sys.getsizeof(sl)
        size += sys.getsizeof(sl._level)
        node = sl._head
        while node is not sl._tail:
            size += nodesize(node)
            node = node[2]
        size += nodesize(node)
        size += sys.getsizeof(sl._path)  # contains references or None
        size += sys.getsizeof(sl._distance)
        for el in sl._distance:
            size += sys.getsizeof(el)
        return size


class SkipList(object):
    """An indexable skip list.

    A SkipList provides an ordered sequence of key-value pairs. The list is
    always sorted on key and supports O(1) forward iteration. It has O(log N)
    time complexity for key lookup, pair insertion and pair removal anywhere in
    the list. The list also supports O(log N) element access by position.

    The keys of all pairs you add to the skiplist must be be comparable against
    each other, and define the ``<`` and ``<=`` operators.
    """

    UNSET = object()

    p = int((1<<31) / math.e)
    maxlevel = 20

    # Kudos to http://pythonsweetness.tumblr.com/post/45227295342 for some
    # useful tricks, including using a list for the nodes to save memory.

    # Use the built-in Mersenne Twister random number generator. It is more
    # appropriate than SystemRandom because we don't need cryptographically
    # secure random numbers, and we don't want to do a system call to read
    # /dev/urandom for each random number we need (every insertion needs a new
    # random number).

    _rnd = random.Random()
    _rnd.seed(os.urandom(16))

    __slots__ = ('_level', '_head', '_tail', '_path', '_distance')

    def __init__(self):
        self._level = 1
        self._head = self._new_node(self.maxlevel, None, None)
        self._tail = self._new_node(self.maxlevel, None, None)
        for i in range(self.maxlevel):
            self._head[2+i] = self._tail
        self._path = [None] * self.maxlevel
        self._distance = [None] * self.maxlevel

    def _new_node(self, level, key, value):
        # Node layout: [key, value, next*LEVEL, skip?]
        # The "skip" element indicates how many nodes are skipped by the
        # highest level incoming link.
        if level == 1:
            return [key, value, None]
        else:
            return [key, value] + [None]*level + [0]

    def _random_level(self):
        # Exponential distribution as per Pugh's paper.
        l = 1
        maxlevel = min(self.maxlevel, self.level+1)
        while l < maxlevel and self._rnd.getrandbits(31) < self.p:
            l += 1
        return l

    def _create_node(self, key, value):
        # Create a new node, updating the list level if required.
        level = self._random_level()
        if level > self.level:
            self._tail[-1] = len(self)
            self._level = level
            self._path[level-1] = self._head
            self._distance[level-1] = 0
        return self._new_node(level, key, value)

    def _find_lt(self, key):
        # Find path to last node < key
        node = self._head
        distance = 0
        for i in reversed(range(self.level)):
            nnode = node[2+i]
            while nnode is not self._tail and nnode[0] < key:
                nnode, node = nnode[2+i], nnode
                distance += 1 if i == 0 else node[-1]
            self._path[i] = node
            self._distance[i] = distance

    def _find_lte(self, key):
        # Find path to last node <= key
        node = self._head
        distance = 0
        for i in reversed(range(self.level)):
            nnode = node[2+i]
            while nnode is not self._tail and nnode[0] <= key:
                nnode, node = nnode[2+i], nnode
                distance += 1 if i == 0 else node[-1]
            self._path[i] = node
            self._distance[i] = distance

    def _find_pos(self, pos):
        # Create path to node at pos.
        node = self._head
        distance = 0
        for i in reversed(range(self.level)):
            nnode = node[2+i]
            ndistance = distance + (1 if i == 0 else nnode[-1])
            while nnode is not self._tail and ndistance <= pos:
                nnode, node, distance = nnode[2+i], nnode, ndistance
                ndistance += 1 if i == 0 else nnode[-1]
            self._path[i] = node
            self._distance[i] = distance

    def _insert(self, node):
        # Insert a node in the list. The _path and _distance must be set.
        path, distance = self._path, self._distance
        # Update pointers
        level = max(1, len(node) - 3)
        for i in range(level):
            node[2+i] = path[i][2+i]
            path[i][2+i] = node
        if level > 1:
            node[-1] = 1 + distance[0] - distance[level-1]
        # Update skip counts
        node = node[2]
        i = 2; j = min(len(node) - 3, self.level)
        while i <= self.level:
            while j < i:
                node = node[i]
                j = min(len(node) - 3, self.level)
            node[-1] -= distance[0] - distance[j-1] if j <= level else -1
            i = j+1

    def _remove(self, node):
        # Remove a node. The _path and _distance must be set.
        path, distance = self._path, self._distance
        level = max(1, len(node) - 3)
        for i in range(level):
            path[i][2+i] = node[2+i]
        # Update skip counts
        value = node[1]
        node = node[2]
        i = 2; j = min(len(node) - 3, self.level)
        while i <= self.level:
            while j < i:
                node = node[i]
                j = min(len(node) - 3, self.level)
            node[-1] += distance[0] - distance[j-1] if j <= level else -1
            i = j+1
        # Reduce level if last node on current level was removed
        while self.level > 1 and self._head[1+self.level] is self._tail:
            self._level -= 1
            self._tail[-1] += self._tail[-1] - len(self)
        return value

    # PUBLIC API ...

    @property
    def level(self):
        """The current level of the skip list."""
        return self._level

    def insert(self, key, value):
        """Insert a key-value pair in the list.

        The pair is inserted at the correct location so that the list remains
        sorted on *key*. If a pair with the same key is already in the list,
        then the pair is appended after all other pairs with that key.
        """
        self._find_lte(key)
        node = self._create_node(key, value)
        self._insert(node)

    def replace(self, key, value):
        """Replace the value of the first key-value pair with key *key*.

        If the key was not found, the pair is inserted.
        """
        self._find_lt(key)
        node = self._path[0][2]
        if node is self._tail or key < node[0]:
            node = self._create_node(key, value)
            self._insert(node)
        else:
            node[1] = value

    def clear(self):
        """Remove all key-value pairs."""
        for i in range(self.maxlevel):
            self._head[2+i] = self._tail
            self._tail[-1] = 0
        self._level = 1

    def __len__(self):
        """Return the number of pairs in the list."""
        dist = 0
        idx = self.level + 1
        node = self._head[idx]
        while node is not self._tail:
            dist += node[-1] if idx > 2 else 1
            node = node[idx]
        dist += node[-1]
        return dist

    __bool__ = __nonzero__ = lambda self: len(self) > 0

    def __repr__(self):
        return type(self).__name__ + '((' + repr(list(self.items()))[1:-1] + '))'

    def items(self, start=None, stop=None):
        """Return an iterator yielding pairs.

        If *start* is specified, iteration starts at the first pair with a key
        that is larger than or equal to *start*. If not specified, iteration
        starts at the first pair in the list.

        If *stop* is specified, iteration stops at the last pair that is
        smaller than *stop*. If not specified, iteration end with the last pair
        in the list.
        """
        if start is None:
            node = self._head[2]
        else:
            self._find_lt(start)
            node = self._path[0][2]
        while node is not self._tail and (stop is None or node[0] < stop):
            yield (node[0], node[1])
            node = node[2]

    __iter__ = items

    def keys(self, start=None, stop=None):
        """Like :meth:`items` but returns only the keys."""
        return (item[0] for item in self.items(start, stop))

    def values(self, start=None, stop=None):
        """Like :meth:`items` but returns only the values."""
        return (item[1] for item in self.items(start, stop))

    def popitem(self):
        """Removes the first key-value pair and return it.

        This method raises a ``KeyError`` if the list is empty.
        """
        node = self._head[2]
        if node is self._tail:
            raise KeyError('list is empty')
        self._find_lt(node[0])
        self._remove(node)
        return (node[0], node[1])

    # BY KEY API ...

    def search(self, key, default=None):
        """Find the first key-value pair with key *key* and return its value.

        If the key was not found, return *default*. If no default was provided,
        return ``None``. This method never raises a ``KeyError``.
        """
        self._find_lt(key)
        node = self._path[0][2]
        if node is self._tail or key < node[0]:
            return default
        return node[1]

    def remove(self, key):
        """Remove the first key-value pair with key *key*.

        If the key was not found, a ``KeyError`` is raised.
        """
        self._find_lt(key)
        node = self._path[0][2]
        if node is self._tail or key < node[0]:
            raise KeyError('{!r} is not in list'.format(key))
        self._remove(node)

    def pop(self, key, default=UNSET):
        """Remove the first key-value pair with key *key*.

        If a pair was removed, return its value. Otherwise if *default* was
        provided, return *default*. Otherwise a ``KeyError`` is raised.
        """
        self._find_lt(key)
        node = self._path[0][2]
        if node is self._tail or key < node[0]:
            if default is self.UNSET:
                raise KeyError('key {!r} not in list')
            return default
        self._remove(node)
        return node[1]

    def __contains__(self, key):
        """Return whether *key* is contained in the list."""
        self._find_lt(key)
        node = self._path[0][2]
        return node is not self._tail and not key < node[0]

    def index(self, key, default=UNSET):
        """Find the first key-value pair with key *key* and return its position.

        If the key is not found, return *default*. If default was not provided,
        raise a ``KeyError``
        """
        self._find_lt(key)
        node = self._path[0][2]
        if node is self._tail or key < node[0]:
            if default is self.UNSET:
                raise KeyError('key {!r} not in list'.format(key))
            return default
        return self._distance[0]

    def count(self, key):
        """Return the number of pairs with key *key*."""
        count = 0
        pos = self.index(key, -1)
        if pos == -1:
            return count
        count += 1
        for i in range(pos+1, len(self)):
            if self[i][0] != key:
                break
            count += 1
        return count

    # BY POSITION API ...

    def __getitem__(self, pos):
        """Return a pair by its position.

        If *pos* is a slice, then return a generator that yields pairs as
        specified by the slice.
        """
        size = len(self)
        if isinstance(pos, int):
            if pos < 0:
                pos += size
            if not 0 <= pos < size:
                raise IndexError('list index out of range')
            self._find_pos(pos)
            node = self._path[0][2]
            return (node[0], node[1])
        elif isinstance(pos, slice):
            start, stop = pos.start, pos.stop
            if start is None:
                start = 0
            elif start < 0:
                start += size
            if stop is None:
                stop = size
            elif stop < 0:
                stop += size
            self._find_pos(start)
            def genpairs():
                pos = start; node = self._path[0][2]
                while node is not self._tail and pos < stop:
                    yield (node[0], node[1])
                    node = node[2]; pos += 1
            return genpairs()
        else:
            raise TypeError('expecting int or slice, got {0.__name__!r}'.format(type(pos)))

    def __delitem__(self, pos):
        """Delete a pair by its position."""
        if not isinstance(pos, int):
            raise TypeError('expecting int, got {0.__name__!r}'.format(type(pos)))
        size = len(self)
        if pos < 0:
            pos += size
        if not 0 <= pos < size:
            raise IndexError('list index out of range')
        self._find_pos(pos)
        node = self._path[0][2]
        self._remove(node)

    def __setitem__(self, pos, value):
        """Set a value by its position."""
        if not isinstance(pos, int):
            raise TypeError('expecting int, got {0.__name__!r}'.format(type(pos)))
        size = len(self)
        if pos < 0:
            pos += size
        if not 0 <= pos < size:
            raise IndexError('list index out of range')
        self._find_pos(pos)
        node = self._path[0][2]
        node[1] = value
