import pytest
from sqlobject import SQLObject, JSONCol
from sqlobject.tests.dbtest import setupClass


class JSONTest(SQLObject):
    json = JSONCol(default=None)


_json_test_data = (
    None, True, 1, 2.0,
    {u"test": [None, True, 1, 2.0,
     {u"unicode'with'apostrophes": u"unicode\"with\"quotes"},
     [],
     u"unicode"]},
    [None, True, 1, 2.0,
     [],
     {u"unicode'with'apostrophes": u"unicode\"with\"quotes"},
     u"unicode", u"unicode'with'apostrophes", u"unicode\"with\"quotes",
     ],
    u"unicode", u"unicode'with'apostrophes", u"unicode\"with\"quotes",
    {'test': 'Test'},
)


def _setup():
    setupClass(JSONTest)

    for _id, test_data in enumerate(_json_test_data):
        JSONTest(id=_id + 1, json=test_data)


def test_JSONCol():
    _setup()
    JSONTest._connection.cache.clear()

    for _id, test_data in enumerate(_json_test_data):
        json = JSONTest.get(_id + 1)
        assert json.json == test_data


def test_JSONCol_funcs():
    connection = JSONTest._connection
    if not hasattr(connection, 'can_use_json_funcs') \
            or not connection.can_use_json_funcs():
        pytest.skip(
            "The database doesn't support JSON functions; "
            "JSON functions are supported by MariaDB since version 10.2.7 "
            "and by MySQL since version 5.7.")
    _setup()

    rows = list(
        JSONTest.select(JSONTest.q.json.json_extract('test') == 'Test')
    )
    assert len(rows) == 1
    assert rows[0].json == {'test': 'Test'}
