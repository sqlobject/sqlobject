# -*- coding: koi8-r -*-

from decimal import Decimal
from sqlobject import *
from sqlobject.tests.dbtest import *

########################################
## Decimal columns
########################################

class DecimalTable(SQLObject):
    name = UnicodeCol(length=255)
    col1 = DecimalCol(size=6, precision=4)

if supports('decimalColumn'):
    def test_1_decimal():
        setupClass(DecimalTable)
        d = DecimalTable(name='test', col1=21.12)
        # psycopg2 returns float as Decimal
        if isinstance(d.col1, Decimal):
            assert d.col1 == Decimal("21.12")
        else:
            assert d.col1 == 21.12

    def test_2_decimal():
        setupClass(DecimalTable)
        d = DecimalTable(name='test', col1=Decimal("21.12"))
        assert d.col1 == Decimal("21.12")

    # See http://mail.python.org/pipermail/python-dev/2008-March/078189.html
    if isinstance(Decimal(u'123').to_eng_string(), unicode): # a bug in Python 2.5.2
        def test_3_unicode():
            setupClass(DecimalTable)
            d = DecimalTable(name='test', col1=Decimal(u"21.12"))
            assert d.col1 == Decimal("21.12")
            d = DecimalTable(name=unicode('тест', 'koi8-r'), col1=Decimal(u"21.12"))
            assert d.col1 == Decimal("21.12")
