from sqlobject import *
from config import conn

__connection__ = conn

## Snippet "style1"
class Person(SQLObject):
    _style = MixedCaseStyle(longID=True)

    firstName = StringCol()
    lastName = StringCol()
## end snippet

"""
## Snippet "default-style"
__connection__.style = MixedCaseStyle(longID=True)
## end snippet
"""

## Snippet "style-table"
class User(SQLObject):
    _table = "user_table"
    _idName = "userid"

    username = StringCol(length=20, dbName='name')
## end snippet
