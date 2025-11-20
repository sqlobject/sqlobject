from uuid import UUID
from sqlobject import SQLObject, UuidCol
from sqlobject.tests.dbtest import setupClass


########################################
# Uuid columns
########################################


testuuid = UUID('7e3b5c1e-3402-4b10-a3c6-8ee6dbac7d1a')


class UuidContainer(SQLObject):
    uuiddata = UuidCol(alternateID=True, default=None)


def test_uuidCol():
    setupClass([UuidContainer])

    my_uuid = UuidContainer(uuiddata=testuuid)
    iid = my_uuid.id

    UuidContainer._connection.cache.clear()

    my_uuid_2 = UuidContainer.get(iid)

    assert my_uuid_2.uuiddata == testuuid


def test_alternate_id():
    setupClass([UuidContainer])

    UuidContainer(uuiddata=testuuid)

    UuidContainer._connection.cache.clear()

    my_uuid_2 = UuidContainer.byUuiddata(testuuid)

    assert my_uuid_2.uuiddata == testuuid
