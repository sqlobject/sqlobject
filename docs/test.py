import sys, os

if sys.version_info >= (2, 4):
    import doctest
else:
    raise ImportError("Python 2.4 doctest required")

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test():
    for doc in ['SQLObject.txt']:
        doctest.testfile(doc, optionflags=doctest.ELLIPSIS)

if __name__ == '__main__':
    test()
