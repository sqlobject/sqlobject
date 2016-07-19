from sqlobject import ForeignKey, IntCol, SQLObject
from sqlobject.inheritance import InheritableSQLObject
from sqlobject.tests.dbtest import setupClass


class TestCascade1(InheritableSQLObject):
    dummy = IntCol()


class TestCascade2(TestCascade1):
    c = ForeignKey('TestCascade3', cascade='null')


class TestCascade3(SQLObject):
    dummy = IntCol()


def test_destroySelf():
    setupClass([TestCascade1, TestCascade3, TestCascade2])

    c = TestCascade3(dummy=1)
    TestCascade2(cID=c.id, dummy=1)
    c.destroySelf()
