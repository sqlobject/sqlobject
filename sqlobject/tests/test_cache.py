from sqlobject.cache import CacheSet

class Something(object):
    pass

def test_purge1():
    x = CacheSet()
    y = Something()
    obj = x.get(1, y.__class__)
    assert obj is None
    x.put(1, y.__class__, y)
    x.finishPut(y.__class__)
    j = x.get(1, y.__class__)
    assert j == y
    x.expire(1, y.__class__)
    j = x.get(1, y.__class__)
    assert j == None
    x.finishPut(y.__class__)
    j = x.get(1, y.__class__)
    assert j == None
    x.finishPut(y.__class__)
