import py.test
from sqlobject import *
from sqlobject.tests.dbtest import *


########################################
# Transaction test
########################################


class TestSOTrans(SQLObject):
    class sqlmeta:
        defaultOrder = 'name'
    name = StringCol(length=10, alternateID=True, dbName='name_col')


def test_transaction():
    if not supports('transactions'):
        py.test.skip("Transactions aren't supported")
    setupClass(TestSOTrans)
    TestSOTrans(name='bob')
    TestSOTrans(name='tim')
    trans = TestSOTrans._connection.transaction()
    try:
        TestSOTrans._connection.autoCommit = 'exception'
        TestSOTrans(name='joe', connection=trans)
        trans.rollback()
        trans.begin()
        assert ([n.name for n in TestSOTrans.select(connection=trans)] ==
                ['bob', 'tim'])
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


def test_transaction_commit_sync():
    if not supports('transactions'):
        py.test.skip("Transactions aren't supported")
    setupClass(TestSOTrans)
    trans = TestSOTrans._connection.transaction()
    try:
        TestSOTrans(name='bob')
        bOut = TestSOTrans.byName('bob')
        bIn = TestSOTrans.byName('bob', connection=trans)
        bIn.name = 'robert'
        assert bOut.name == 'bob'
        trans.commit()
        assert bOut.name == 'robert'
    finally:
        TestSOTrans._connection.autoCommit = True


def test_transaction_delete(close=False):
    if not supports('transactions'):
        py.test.skip("Transactions aren't supported")
    setupClass(TestSOTrans)
    connection = TestSOTrans._connection
    if (connection.dbName == 'sqlite') and connection._memory:
        py.test.skip("The following test requires a different connection")
    trans = connection.transaction()
    try:
        TestSOTrans(name='bob')
        bIn = TestSOTrans.byName('bob', connection=trans)
        bIn.destroySelf()
        bOut = TestSOTrans.select(TestSOTrans.q.name == 'bob')
        assert bOut.count() == 1
        bOutInst = bOut[0]
        bOutID = bOutInst.id  # noqa: bOutID is used in the string code below
        trans.commit(close=close)
        assert bOut.count() == 0
        raises(SQLObjectNotFound, "TestSOTrans.get(bOutID)")
        raises(SQLObjectNotFound, "bOutInst.name")
    finally:
        trans.rollback()
        connection.autoCommit = True
        connection.close()


def test_transaction_delete_with_close():
    test_transaction_delete(close=True)
