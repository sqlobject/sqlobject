import unittest
from sqlobject.cache import CacheSet

class Something(object):
    pass

class CacheTest(unittest.TestCase):

    def testPurge1(self):
        x = CacheSet()
        y = Something()
        obj = x.get(1, y.__class__)
        self.assertEqual(obj, None)
        x.put(1, y.__class__, y)
        x.finishPut(y.__class__)
        j = x.get(1, y.__class__)
        self.assertEqual(j, y)
        x.expire(1, y.__class__)
        j = x.get(1, y.__class__)
        self.assertEqual(j, None)
        x.finishPut(y.__class__)
        j = x.get(1, y.__class__)
        self.assertEqual(j, None)
        x.finishPut(y.__class__)

if __name__ == "__main__":
    unittest.main()
