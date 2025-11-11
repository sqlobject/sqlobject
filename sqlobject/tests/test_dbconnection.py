from pytest import raises
from sqlobject.dbconnection import DBConnection


def test_name():
    connection = DBConnection(name='test')
    connection.close = lambda: True

    with raises(AssertionError) as error:
        DBConnection(name='test')
    assert str(error.value) == 'An instance has already been registered ' \
        'with the name test'

    with raises(AssertionError) as error:
        DBConnection(name='test:test')
    assert str(error.value) == "You cannot include ':' " \
        "in your DB connection names ('test:test')"
