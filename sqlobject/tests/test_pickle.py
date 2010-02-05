import pickle
from sqlobject import *
from sqlobject.tests.dbtest import *

########################################
## Pickle instances
########################################

class TestPickle(SQLObject):
    question = StringCol()
    answer = IntCol()

test_question = 'The Ulimate Question of Life, the Universe and Everything'
test_answer = 42

def test_pickleCol():
    setupClass(TestPickle)
    test = TestPickle(question=test_question, answer=test_answer)

    pickle_data = pickle.dumps(test, pickle.HIGHEST_PROTOCOL)
    test = pickle.loads(pickle_data)

    assert test.question == test_question
    assert test.answer == test_answer
