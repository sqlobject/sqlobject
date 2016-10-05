import pytest
from sqlobject import BLOBCol, DateTimeCol, ForeignKey, IntCol, SQLObject, \
    StringCol, sqlmeta
from sqlobject.tests.dbtest import getConnection, supports


class SOTestCyclicReferenceA(SQLObject):
    class sqlmeta(sqlmeta):
        idName = 'test_id_here'
        table = 'test_cyclic_reference_a_table'
    name = StringCol()
    number = IntCol()
    time = DateTimeCol()
    short = StringCol(length=10)
    blobcol = BLOBCol()
    fkeyb = ForeignKey('SOTestCyclicReferenceB')


class SOTestCyclicReferenceB(SQLObject):
    class sqlmeta(sqlmeta):
        idName = 'test_id_here'
        table = 'test_cyclic_reference_b_table'
    name = StringCol()
    number = IntCol()
    time = DateTimeCol()
    short = StringCol(length=10)
    blobcol = BLOBCol()
    fkeya = ForeignKey('SOTestCyclicReferenceA')


def test_cyclic_reference():
    if not supports('dropTableCascade'):
        pytest.skip("dropTableCascade isn't supported")
    conn = getConnection()
    SOTestCyclicReferenceA.setConnection(conn)
    SOTestCyclicReferenceB.setConnection(conn)
    SOTestCyclicReferenceA.dropTable(ifExists=True, cascade=True)
    assert not conn.tableExists(SOTestCyclicReferenceA.sqlmeta.table)
    SOTestCyclicReferenceB.dropTable(ifExists=True, cascade=True)
    assert not conn.tableExists(SOTestCyclicReferenceB.sqlmeta.table)

    constraints = SOTestCyclicReferenceA.createTable(ifNotExists=True,
                                                     applyConstraints=False)
    assert conn.tableExists(SOTestCyclicReferenceA.sqlmeta.table)
    constraints += SOTestCyclicReferenceB.createTable(ifNotExists=True,
                                                      applyConstraints=False)
    assert conn.tableExists(SOTestCyclicReferenceB.sqlmeta.table)

    for constraint in constraints:
        conn.query(constraint)

    SOTestCyclicReferenceA.dropTable(ifExists=True, cascade=True)
    assert not conn.tableExists(SOTestCyclicReferenceA.sqlmeta.table)
    SOTestCyclicReferenceB.dropTable(ifExists=True, cascade=True)
    assert not conn.tableExists(SOTestCyclicReferenceB.sqlmeta.table)
