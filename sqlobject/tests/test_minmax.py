from sqlobject import *
from sqlobject.tests.dbtest import *

# Test MIN, AVG, MAX, SUM

class Accumulator(SQLObject):
    value = IntCol()

def test_minmax():
    setupClass(Accumulator)
    Accumulator(value=1)
    Accumulator(value=2)
    Accumulator(value=3)

    assert Accumulator.select().min(Accumulator.q.value) == 1
    assert Accumulator.select().avg(Accumulator.q.value) == 2
    assert Accumulator.select().max(Accumulator.q.value) == 3
    assert Accumulator.select().sum(Accumulator.q.value) == 6

    assert Accumulator.select(Accumulator.q.value > 1).max(Accumulator.q.value) == 3
    assert Accumulator.select(Accumulator.q.value > 1).sum(Accumulator.q.value) == 5
