from sqlobject import *
from sqlobject.tests.dbtest import *

try:
    from decimal import Decimal
except ImportError:
    Decimal = None

########################################
## Deciaml columns
########################################

class DecimalTable(SQLObject):
    col1 = DecimalCol(size=6, precision=4)

def test_1decimal():
    setupClass(DecimalTable)
    d = DecimalTable(col1=21.12)
    assert d.col1 == 21.12

if Decimal:
    def test_2Decimal():
        setupClass(DecimalTable)
        d = DecimalTable(col1=Decimal("21.12"))
        if isinstance(d.col1, Decimal):
            assert d.col1 == Decimal("21.12")
        else:
            assert d.col1 == 21.12
