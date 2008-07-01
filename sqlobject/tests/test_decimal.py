from decimal import Decimal
from sqlobject import *
from sqlobject.tests.dbtest import *

########################################
## Decimal columns
########################################

class DecimalTable(SQLObject):
    col1 = DecimalCol(size=6, precision=4)
    col2 = DecimalStringCol(size=6, precision=4)

if supports('decimalColumn'):
    def test_1_decimal():
        setupClass(DecimalTable)
        d = DecimalTable(col1=21.12, col2='10.01')
        # psycopg2 returns float as Decimal
        if isinstance(d.col1, Decimal):
            assert d.col1 == Decimal("21.12")
        else:
            assert d.col1 == 21.12
        assert d.col2 == Decimal("10.01")

    def test_2_decimal():
        setupClass(DecimalTable)
        d = DecimalTable(col1=Decimal("21.12"), col2=Decimal('10.01'))
        if isinstance(d.col1, Decimal):
            assert d.col1 == Decimal("21.12")
        else:
            assert d.col1 == 21.12
        assert d.col2 == Decimal("10.01")
