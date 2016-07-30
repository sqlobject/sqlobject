import pickle
import py.test
from sqlobject import IntCol, SQLObject, StringCol
from sqlobject.tests.dbtest import getConnection, raises, setupClass


########################################
# Pickle instances
########################################


class TestPickle(SQLObject):
    question = StringCol()
    answer = IntCol()


test_question = 'The Ulimate Question of Life, the Universe and Everything'
test_answer = 42


def test_pickleCol():
    setupClass(TestPickle)
    connection = TestPickle._connection
    test = TestPickle(question=test_question, answer=test_answer)

    pickle_data = pickle.dumps(test, pickle.HIGHEST_PROTOCOL)
    connection.cache.clear()
    test = pickle.loads(pickle_data)
    test2 = connection.cache.tryGet(test.id, TestPickle)

    assert test2 is test
    assert test.question == test_question
    assert test.answer == test_answer

    if (connection.dbName == 'sqlite') and connection._memory:
        py.test.skip("The following test requires a different connection")

    test = TestPickle.get(
        test.id,
        # make a different DB URI and open another connection
        connection=getConnection(registry=''))
    raises(pickle.PicklingError, pickle.dumps, test, pickle.HIGHEST_PROTOCOL)
