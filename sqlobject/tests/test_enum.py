from sqlobject import *
from sqlobject.tests.dbtest import *

########################################
## Enum test
########################################

class Enum1(SQLObject):

    _columns = [
        EnumCol('l', enumValues=['a', 'bcd', 'e']),
        ]

def testBad():
    setupClass(Enum1)
    for l in ['a', 'bcd', 'a', 'e']:
        Enum1(l=l)
    if supports('restrictedEnum'):
        raises(Enum1._connection.module.IntegrityError, Enum1, l='b')
