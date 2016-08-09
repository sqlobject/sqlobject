#!/usr/bin/env python
import doctest
import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test():
    for doc in ['SQLObject.rst']:
        doctest.testfile(doc, optionflags=doctest.ELLIPSIS)

if __name__ == '__main__':
    test()
