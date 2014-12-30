from __future__ import absolute_import

import sys, os
import doctest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test():
    for doc in ['SQLObject.txt']:
        doctest.testfile(doc, optionflags=doctest.ELLIPSIS)

if __name__ == '__main__':
    test()
