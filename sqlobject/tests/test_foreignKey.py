from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject.tests.dbtest import InstalledTestDatabase

class TestComposerKey(SQLObject):
    name = StringCol()

class TestWorkKey(SQLObject):
    class sqlmeta:
        idName = "work_id"

    composer = ForeignKey('TestComposerKey', cascade=True)
    title = StringCol()

class TestWorkKey2(SQLObject):
    title = StringCol()

def test1():
    setupClass([TestComposerKey, TestWorkKey])

    c = TestComposerKey(name='Mahler, Gustav')
    w1 = TestWorkKey(composer=c, title='Symphony No. 9')
    w2 = TestWorkKey(composer=None, title=None)

    # Select by usual way
    s = TestWorkKey.selectBy(composerID=c.id, title='Symphony No. 9')
    assert s.count() == 1
    assert s[0]==w1
    # selectBy object.id
    s = TestWorkKey.selectBy(composer=c.id, title='Symphony No. 9')
    assert s.count() == 1
    assert s[0]==w1
    # selectBy object
    s = TestWorkKey.selectBy(composer=c, title='Symphony No. 9')
    assert s.count() == 1
    assert s[0]==w1
    # selectBy id
    s = TestWorkKey.selectBy(id=w1.id)
    assert s.count() == 1
    assert s[0]==w1
    # is None handled correctly?
    s = TestWorkKey.selectBy(composer=None, title=None)
    assert s.count() == 1
    assert s[0]==w2

    s = TestWorkKey.selectBy()
    assert s.count() == 2

    # select with objects
    s = TestWorkKey.select(TestWorkKey.q.composerID==c.id)
    assert s.count() == 1
    assert s[0]==w1
    s = TestWorkKey.select(TestWorkKey.q.composer==c.id)
    assert s.count() == 1
    assert s[0]==w1
    s = TestWorkKey.select(TestWorkKey.q.composerID==c)
    assert s.count() == 1
    assert s[0]==w1
    s = TestWorkKey.select(TestWorkKey.q.composer==c)
    assert s.count() == 1
    assert s[0]==w1
    s = TestWorkKey.select((TestWorkKey.q.composer==c) & \
        (TestWorkKey.q.title=='Symphony No. 9'))
    assert s.count() == 1
    assert s[0]==w1

def test2():
    TestWorkKey._connection = getConnection()
    InstalledTestDatabase.drop(TestWorkKey)
    setupClass([TestComposerKey, TestWorkKey2], force=True)
    TestWorkKey2.sqlmeta.addColumn(ForeignKey('TestComposerKey'), changeSchema=True)
