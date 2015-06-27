#
# This file is part of PySkiplist. PySkiplist is Copyright (c) 2012-2015 by
# the PySkiplist authors.
#
# PySkiplist is free software available under the MIT license. See the file
# named LICENSE distributed with this file for the exact licensing terms.

from __future__ import absolute_import, print_function

from setuptools import setup


version_info = {
    'name': 'pyskiplist',
    'version': '1.0.0.dev0',
    'description': 'Fast pure python indexable skiplist',
    'author': 'Geert Jansen',
    'author_email': 'geertj@gmail.com',
    'url': 'https://github.com/geertj/pyskiplist',
    'license': 'MIT',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ]
}


def main():
    setup(packages=['pyskiplist'], **version_info)


if __name__ == '__main__':
    main()
