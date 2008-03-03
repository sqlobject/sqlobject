from decimal import Decimal
from sqlobject import *
from sqlobject.tests.dbtest import *

########################################
## Decimal columns
########################################

class DecimalTable(SQLObject):
    col1 = DecimalCol(size=6, precision=4)

if supports('decimalColumn'):
    def test_1decimal():
        """Tests new instance with a float in col1."""
        setupClass(DecimalTable)
        d = DecimalTable(col1=21.12)
        # psycopg2 returns float as Decimal
        if isinstance(d.col1, Decimal):
            assert d.col1 == Decimal("21.12")
        else:
            assert d.col1 == 21.12

    def test_2Decimal():
        """Tests new instance with a Decimal in col1."""
        setupClass(DecimalTable)
        d = DecimalTable(col1=Decimal("21.12"))
        if isinstance(d.col1, Decimal):
            assert d.col1 == Decimal("21.12")
        else:
            assert d.col1 == 21.12
