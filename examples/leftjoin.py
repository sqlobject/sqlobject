from sqlobject import *
from setup import *

class Customer(SQLObject):

    firstName = StringCol(length=100)
    lastName = StringCol(length=100)
    contacts = MultipleJoin('Contact')

class Contact(SQLObject):

    customer = ForeignKey('Customer')
    phoneNumber = StringCol(length=20)

Customer.dropTable(ifExists=True)
Customer.createTable()
Contact.dropTable(ifExists=True)
Contact.createTable()

data = [
    ['Joe Henry', '384-374-3584', '984-384-8594', '384-957-3948'],
    ['Tim Jackson', '204-485-9384'],
    ['Jane Austin'],
    ]

for insert in data:
    firstName, lastName = insert[0].split(' ', 1)
    customer = Customer(firstName=firstName, lastName=lastName)
    for number in insert[1:]:
        contact = Contact(customer=customer, phoneNumber=number)

## Snippet "leftjoin-simple"
for customer in Customer.select():
    print customer.firstName, customer.lastName
    for contact in customer.contacts:
        print '   ', contact.phoneNumber
## end snippet

## Snippet "leftjoin-more"
custContacts = {}
for contact in Contact.select():
    custContacts.setdefault(contact.customerID, []).append(contact)
for customer in Customer.select():
    print customer.firstName, customer.lastName
    for contact in custContacts.get(customer.id, []):
        print '   ', contact.phoneNumber
## end snippet

## Snippet "leftjoin-more-query"
query = Customer.q.firstName.startswith('J')
custContacts = {}
for contact in Contact.select(AND(Contact.q.customerID == Customer.q.id,
                                  query)):
    custContacts.setdefault(contact.customerID, []).append(contact)
for customer in Customer.select(query):
    print customer.firstName, customer.lastName
    for contact in custContacts.get(customer.id, []):
        print '   ', contact.phoneNumber
## end snippet
