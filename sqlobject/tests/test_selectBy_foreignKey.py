from sqlobject import *
from sqlobject.tests.dbtest import *

class TestComposerKey(SQLObject):
    name = StringCol()

class TestWork(SQLObject):
    class sqlmeta:
        idName = "work_id"

    composer = ForeignKey('TestComposer')
    title = StringCol()

def test1():
    setupClass([TestComposerKey,
                TestWork])

    c = TestComposerKey(name='Mahler, Gustav')
    w1 = TestWork(composer=c, title='Symphony No. 9')
    w2 = TestWork(composer=None, title=None)

    # Select by usual way
    s = TestWork.selectBy(composerID=c.id, title='Symphony No. 9')
    assert s[0]==w1
    # selectBy object
    s = TestWork.selectBy(composer=c, title='Symphony No. 9')
    assert s[0]==w1
    # selectBy id
    s = TestWork.selectBy(id=w1.id)
    assert s[0]==w1
    # is None handled correctly?
    s = TestWork.selectBy(composer=None, title=None)
    assert s[0]==w2
