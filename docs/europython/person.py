from SQLObject import *
conn = PostgresConnection(db = 'merchant_test', user = 'merchant_test', passwd = 'mtest')

class Role(SQLObject):
    _connection = conn

    name = StringCol(length = 20)
    people = RelatedJoin('Person')
    
class Person(SQLObject):
    _cacheValues = False

    _connection = conn
    
    firstName = StringCol(length = 100)
    middleInitial = StringCol(length = 1)
    lastName = StringCol(length = 150)
    phoneNumbers = MultipleJoin("PhoneNumber") 

    roles = RelatedJoin('Role')

class PhoneNumber(SQLObject):
    _connection = conn

    person = ForeignKey('Person')
    phoneNumber = StringCol(length = 10)
