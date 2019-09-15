import pytest
from sqlobject import SQLObject, SQLObjectNotFound, StringCol
from sqlobject.tests.dbtest import raises, setupClass, supports
from sqlobject import events
from sqlobject.main import sqlmeta

########################################
# Transaction test
########################################


try:
    support_transactions = supports('transactions')
except NameError:
    # The module was imported during documentation building
    pass
else:
    if not support_transactions:
        pytestmark = pytest.mark.skip("These tests require transactions")


class SOTestSOTrans(SQLObject):
    class sqlmeta:
        defaultOrder = 'name'
    name = StringCol(length=10, alternateID=True, dbName='name_col')


def make_watcher():
    log = []

    def watch(*args):
        log.append(args)

    watch.log = log
    return watch


def make_listen(signal):
    watcher = make_watcher()
    events.listen(watcher, sqlmeta, signal)
    return watcher


def test_transaction():
    commit_watcher = make_listen(events.CommitSignal)
    rollback_watcher = make_listen(events.RollbackSignal)
    setupClass(SOTestSOTrans)
    SOTestSOTrans(name='bob')
    SOTestSOTrans(name='tim')
    trans = SOTestSOTrans._connection.transaction()
    try:
        SOTestSOTrans._connection.autoCommit = 'exception'
        SOTestSOTrans(name='joe', connection=trans)
        trans.rollback()
        trans.begin()
        assert ([n.name for n in SOTestSOTrans.select(connection=trans)]
                == ['bob', 'tim'])
        b = SOTestSOTrans.byName('bob', connection=trans)
        b.name = 'robert'
        trans.commit()
        assert b.name == 'robert'
        b.name = 'bob'
        trans.rollback()
        trans.begin()
        assert b.name == 'robert'
        assert len(commit_watcher.log) == 1
        assert commit_watcher.log[0][0][0][0] == 'SOTestSOTrans'
        assert commit_watcher.log[0][0][0][1] == [1, 2]
        assert len(rollback_watcher.log) == 2
        assert rollback_watcher.log[0][0][0][0] == 'SOTestSOTrans'
        assert rollback_watcher.log[0][0][0][1] == [3]
        assert rollback_watcher.log[1][0][0][0] == 'SOTestSOTrans'
        assert rollback_watcher.log[1][0][0][1] == [1, 2]
    finally:
        SOTestSOTrans._connection.autoCommit = True


def test_transaction_commit_sync():
    setupClass(SOTestSOTrans)
    connection = SOTestSOTrans._connection
    trans = connection.transaction()
    try:
        SOTestSOTrans(name='bob')
        bOut = SOTestSOTrans.byName('bob')
        bIn = SOTestSOTrans.byName('bob', connection=trans)
        bIn.name = 'robert'
        assert bOut.name == 'bob'
        trans.commit()
        assert bOut.name == 'robert'
    finally:
        trans.rollback()
        connection.autoCommit = True
        connection.close()


def test_transaction_delete(close=False):
    setupClass(SOTestSOTrans)
    connection = SOTestSOTrans._connection
    if (connection.dbName == 'sqlite') and connection._memory:
        pytest.skip("The test doesn't work with sqlite memory connection")
    trans = connection.transaction()
    try:
        SOTestSOTrans(name='bob')
        bIn = SOTestSOTrans.byName('bob', connection=trans)
        bIn.destroySelf()
        bOut = SOTestSOTrans.select(SOTestSOTrans.q.name == 'bob')
        assert bOut.count() == 1
        bOutInst = bOut[0]
        bOutID = bOutInst.id  # noqa: bOutID is used in the string code below
        trans.commit(close=close)
        assert bOut.count() == 0
        raises(SQLObjectNotFound, SOTestSOTrans.get, bOutID)
        with raises(SQLObjectNotFound):
            bOutInst.name
    finally:
        trans.rollback()
        connection.autoCommit = True
        connection.close()


def test_transaction_delete_with_close():
    test_transaction_delete(close=True)
