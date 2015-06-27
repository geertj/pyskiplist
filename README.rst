Welcome to PySkipList
=====================

PySkipList is a fast, pure Python implementation of an indexable skiplist. It
implements a ``SkipList`` data structure that provides an always sorted,
list-like data structure for (key, value) pairs. It efficiently supports the
following operations:

* Insert a pair in the list, maintaining sorted order.
* Find the value of a given key.
* Remove a given pair based on a key.
* Iterate over all pairs in sorted order.
* Find the position of a given key.
* Access a pair at a certain position.
* Delete a pair at a certain position.
  
Since PySkipList is a pure Python implementation, it should work well on
alternative Python implementations such as PyPy and Jython.


Example
=======

The following provides a few examples on how to use the ``SkipList`` API::

  >>> from pyskiplist import SkipList
  >>> sl = SkipList()
  >>> sl.insert('foo', 'bar')
  >>> sl.insert('baz', 'qux')
  >>> sl
  SkipList((('baz', 'qux'), ('foo', 'bar')))
  >>> sl.search('foo')
  'bar'
  >>> sl[0]
  ('baz', 'qux')
  >>> sl.remove('foo')  # remove by key
  >>> del sl[0]  # remove by position


Asymptotic Complexity
=====================

Below are the Big-O complexities of the various operations implemented by
pyskiplist:

==================  ==========
Operation           Complexity
==================  ==========
insertion           O(log N)
search by key       O(log N)
removal by key      O(log N) 
forward iteration   O(1)
find by position    O(log N)
access by position  O(log N)
delete by position  O(log N)
==================  ==========


Performance
===========

Below are the results of some performance tests. These are for Python 3.4.2 on
my Linux laptop:

===================  ===================
Test                 Operations / second
===================  ===================
Insert @ 1k nodes    45,056
Insert @ 10k nodes   42,137
Insert @ 100k nodes  28,086
Remove @ 1k nodes    54,316
Remove @ 10k nodes   46,240
Remove @ 100k nodes  35,114
Search @ 1k nodes    137,248
Search @ 10k nodes   109,480
Search @ 100k nodes  77,939
===================  ===================


Memory usage
============

PySkipList tries to be efficient with regards to memory usage. The numbers
below are for Python 3.4.2 on my Linux laptop. This specific test stores pairs
of integer keys and an integer values in a skiplist. The total size of the two
integers on this Python version is 56 bytes.

=====  ============  ===============
Nodes  Bytes / node  Overhead / node
=====  ============  ===============
1k     164           108
10k    162           106
100k   162           106
=====  ============  ===============


Implementation notes
====================

Reference papers on skiplists:

* ftp://ftp.cs.umd.edu/pub/skipLists/skiplists.pdf (original paper)
* http://drum.lib.umd.edu/bitstream/1903/544/2/CS-TR-2286.1.pdf (cookbook)

This implementation uses a novel (as far as I know) technique where it stores
just a single link width per node, and only in nodes with level > 0. The link
corresponds to the number of nodes skipped by the highest incoming link. Other
implementations that I've seen all store a width for every link. The approach
taken here saves a lot of memory. The overhead should just be 1/e (0.37)
integer per node.

Duplicate keys are allowed in this implementation, and insertion order is
maintained. That said, no special API support is provided for working with
duplicate keys.  For example, the `remove()` function removes the first pair it
encounters with the given key, irrespective of the key's value.

Skiplist nodes are plain lists instead of objects. This saves memory. Kudos to
http://pythonsweetness.tumblr.com/post/45227295342 for the idea.

The built-in Mersenne Twister is used as the random number source. This is
preferable over SystemRandom since it doesn't require a system call and there
is no need for cryptographically secure numbers.
