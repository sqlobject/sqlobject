from sqlobject.sqlbuilder import AND, SQLOp, sqlrepr

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
