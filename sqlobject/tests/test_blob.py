from sqlobject import *
from sqlobject.tests.dbtest import *

########################################
## BLOB columns
########################################

class ImageData(SQLObject):
    image = BLOBCol(default='emptydata', length=65535)

def test_BLOBCol():
    setupClass(ImageData)
    data = ''.join([chr(x) for x in range(256)])

    prof = ImageData()
    prof.image = data
    iid = prof.id

    ImageData._connection.cache.clear()

    prof2 = ImageData.get(iid)
    # @@: This seems to fail in SQLite, which trims off the
    # first and last character (\x00 and \xff).  We should write
    # a test for the upstream driver, as the error might be there.
    assert prof2.image == data
