from sqlobject import *
from sqlobject.sqlbuilder import *
from sqlobject.tests.dbtest import *

########################################
## Table aliases and self-joins
########################################

class TestJoinAlias(SQLObject):
    name = StringCol()
    parent = StringCol()

def test_1syntax():
    setupClass(TestJoinAlias)
    alias = Alias(TestJoinAlias)
    select = TestJoinAlias.select(TestJoinAlias.q.parent == alias.q.name)
    assert str(select) == \
        "SELECT test_join_alias.id, test_join_alias.name, test_join_alias.parent FROM test_join_alias, test_join_alias AS test_join_alias_alias1 WHERE (test_join_alias.parent = test_join_alias_alias1.name)"

def test_2perform_join():
    setupClass(TestJoinAlias)
    TestJoinAlias(name="grandparent", parent=None)
    TestJoinAlias(name="parent", parent="grandparent")
    TestJoinAlias(name="child", parent="parent")
    alias = Alias(TestJoinAlias)
    select = TestJoinAlias.select(TestJoinAlias.q.parent == alias.q.name)
    assert select.count() == 2
