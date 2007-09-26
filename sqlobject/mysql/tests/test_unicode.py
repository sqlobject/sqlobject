#!/usr/bin/python

from py.test import raises

from sqlobject import *

sqlhub.processConnection = connectionForURI('mysql://nz:newzed@localhost/nz')

from sqlobject.tests.dbtest import *

class MyTable(SQLObject):
    strc = StringCol()
    unic = UnicodeCol()
    bloc = BLOBCol()    
    


def test_unicode():

    #MyTable.dropTable(ifExists=True)
    MyTable.createTable(ifNotExists=True)
    
    #test plain text
    MyTable(strc="plain", unic="text", bloc="col")

    #test unicode objects that are plain text
    MyTable(strc=u"plain", unic=u"text", bloc="col")    

    #test string that contain non-plain-text
    #note: unicode column should be in unicode.
    #blob column should be text.  
    MyTable(strc="", unic=u"\x82", bloc="\x82")

