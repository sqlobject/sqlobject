from sqlobject import *
from sqlobject.tests.dbtest import *

########################################
## Transaction test
########################################

class TestSOTrans(SQLObject):
    #_cacheValues = False
    class sqlmeta:
        defaultOrder = 'name'
    name = StringCol(length=10, alternateID=True, dbName='name_col')

def test_transaction():
    if not supports('transactions'):
        return
    setupClass(TestSOTrans)
    TestSOTrans(name='bob')
    TestSOTrans(name='tim')
    trans = TestSOTrans._connection.transaction()
    try:
        TestSOTrans._connection.autoCommit = 'exception'
        TestSOTrans(name='joe', connection=trans)
        trans.rollback()
        trans.begin()
        assert ([n.name for n in TestSOTrans.select(connection=trans)]
                == ['bob', 'tim'])
        b = TestSOTrans.byName('bob', connection=trans)
        b.name = 'robert'
        trans.commit()
        assert b.name == 'robert'
        b.name = 'bob'
        trans.rollback()
        trans.begin()
        assert b.name == 'robert'
    finally:
        TestSOTrans._connection.autoCommit = True

