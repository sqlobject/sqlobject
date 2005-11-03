from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject import events
import sys

class EventTester(SQLObject):
    name = StringCol()

def make_watcher():
    log = []
    def watch(*args):
        log.append(args)
    watch.log = log
    return watch

def test_create():
    watcher = make_watcher()
    events.listen(watcher, EventTester, events.ClassCreateSignal)
    class EventTesterSub1(EventTester):
        pass
    class EventTesterSub2(EventTesterSub1):
        pass
    assert len(watcher.log) == 2
    assert len(watcher.log[0]) == 4
    assert watcher.log[0][0] == 'EventTesterSub1'
    assert watcher.log[0][1] == (EventTester,)
    assert isinstance(watcher.log[0][2], dict)
    assert isinstance(watcher.log[0][3], list)
    
