from sqlobject import *
from sqlobject.sqlbuilder import *
from sqlobject.tests.dbtest import *

class TestSQLBuilder(SQLObject):
    name = StringCol()
    value = IntCol()

def test_Select():
    setupClass(TestSQLBuilder)

    select1 = Select([const.id, func.MAX(const.salary)], staticTables=['employees'])
    assert sqlrepr(select1) == 'SELECT id, MAX(salary) FROM employees'

    select2 = Select([TestSQLBuilder.q.name, TestSQLBuilder.q.value])
    assert sqlrepr(select2) == 'SELECT test_sql_builder.name, test_sql_builder.value FROM test_sql_builder'

    union = Union(select1, select2)
    assert sqlrepr(union) == 'SELECT id, MAX(salary) FROM employees UNION SELECT test_sql_builder.name, test_sql_builder.value FROM test_sql_builder'

    union = Union(TestSQLBuilder.select().queryForSelect())
    assert sqlrepr(union) == 'SELECT test_sql_builder.id, test_sql_builder.name, test_sql_builder.value FROM test_sql_builder WHERE 1 = 1'

def test_empty_AND():
    assert AND() == None
    assert AND(True) == True

    # sqlrepr() is needed because AND() returns an SQLExpression that overrides
    # comparison. The following
    #     AND('x', 'y') == "foo bar"
    # is True! (-: Eeek!
    assert sqlrepr(AND(1, 2)) == sqlrepr(SQLOp("AND", 1, 2)) == "((1) AND (2))"
    assert sqlrepr(AND(1, 2, '3'), "sqlite") == \
        sqlrepr(SQLOp("AND", 1, SQLOp("AND", 2, '3')), "sqlite") == \
        "((1) AND ((2) AND ('3')))"

def test_str_or_sqlrepr():
    select = Select(['id', 'name'], staticTables=['employees'],
        where='value>0', orderBy='id')
    assert sqlrepr(select, 'sqlite') == \
        'SELECT id, name FROM employees WHERE value>0 ORDER BY id'

    select = Select(['id', 'name'], staticTables=['employees'],
        where='value>0', orderBy='id', lazyColumns=True)
    assert sqlrepr(select, 'sqlite') == \
        'SELECT id FROM employees WHERE value>0 ORDER BY id'
