# This isn't a full example...

## Snippet "person_magicmethod"
class Person(SQLObject):
    # ...

    def imageFilename(self):
        return 'images/person-%s.jpg' % self.id

    def _get_image(self):
        if not os.path.exists(self.imageFilename()):
            return None
        f = open(self.imageFilename())
        v = f.read()
        f.close()
        return v

    def _set_image(self, value):
        # assume we get a string for the image
        f = open(self.imageFilename(), 'w')
        f.write(value)
        f.close()

    def _del_image(self, value):
        # I usually wouldn't include a method like this, but for
        # instructional purposes...
        os.unlink(self.imageFilename())

    _doc_image = 'The headshot for the person'
## end snippet

## Snippet "person_magicoverride"
class Person(SQLObject):
    lastName = StringCol()
    firstName = StringCol()

    def _set_lastName(self, value):
        self.notifyLastNameChange(value)
        self._SO_set_lastName(value)
## end snippet

## Snippet "phonenumber_magicoverride"
import re

class PhoneNumber(SQLObject):
    phoneNumber = StringCol(length=30)

    _garbageCharactersRE = re.compile(r'[\-\.\(\) ]')
    _phoneNumberRE = re.compile(r'^[0-9]+$')
    def _set_phoneNumber(self, value):
        value = self._garbageCharactersRE.sub('', value)
        if not len(value) >= 10:
            raise ValueError, 'Phone numbers must be at least 10 digits long'
        if not self._phoneNumberRE.match(value):
            raise ValueError, 'Phone numbers can contain only digits'
        self._SO_set_phoneNumber(value)

    def _get_phoneNumber(self):
        value = self._SO_get_phoneNumber()
        number = '(%s) %s-%s' % (value[0:3], value[3:6], value[6:10])
        if len(value) > 10:
            number += ' ext.%s' % value[10:]
        return number
## end snippet


## Snippet "transactions1"
conn = DBConnection.PostgresConnection('yada')
trans = conn.transaction()
p = Person(1, trans)
p.firstName = 'Bob'
trans.commit()
p.firstName = 'Billy'
trans.rollback()
## end snippet

## Snippet "transactions2"
class Person(SQLObject):
    _cacheValue = False
    # ...
## end snippet

## Snippet "site-sqlobject"
class SiteSQLObject(SQLObject):
    _connection = DBConnection.MySQLConnection(user='test', db='test')
    _style = MixedCaseStyle()

    # And maybe you want a list of the columns, to autogenerate
    # forms from:
    def columns(self):
        return [col.name for col in self._columns]
## end snippet

## Snippet "inheritance"
class Person(SQLObject):
    firstName = StringCol()
    lastName = StringCol()

class Employee(Person):
    position = StringCol()
## end snippet

"""
## Snippet "inheritance-schema"
CREATE TABLE person (
    id INT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT
);

CREATE TABLE employee (
    id INT PRIMARY KEY
    first_name TEXT,
    last_name TEXT,
    position TEXT
)
## end snippet
"""

## Snippet "inheritance-faked"
class Person(SQLObject):
    firstName = StringCol()
    lastName = StringCol()

    def _get_employee(self):
        value = Employee.selectBy(person=self)
        if value:
            return value[0]
        else:
            raise AttributeError, '%r is not an employee' % self
    def _get_isEmployee(self):
        value = Employee.selectBy(person=self)
        # turn into a bool:
        return not not value
    def _set_isEmployee(self, value):
        if value:
            # Make sure we are an employee...
            if not self.isEmployee:
                Empoyee.new(person=self, position=None)
        else:
            if self.isEmployee:
                self.employee.destroySelf()
    def _get_position(self):
        return self.employee.position
    def _set_position(self, value):
        self.employee.position = value

class Employee(SQLObject):
    person = ForeignKey('Person')
    position = StringCol()
## end snippet

"""
## Snippet "composite-schema"
CREATE TABLE invoice_item (
    id INT PRIMARY KEY,
    amount NUMERIC(10, 2),
    currency CHAR(3)
);
## end snippet
"""

## Snippet "composite"
class InvoiceItem(SQLObject):
    amount = Currency()
    currency = StringChar(length=3)

    def _get_price(self):
        return Price(self.amount, self.currency)
    def _set_price(self, price):
        self.amount = price.amount
        self.currency = price.currency

class Price(object):
    def __init__(self, amount, currency):
        self._amount = amount
        self._currency = currency

    def _get_amount(self):
        return self._amount
    amount = property(_get_amount)

    def _get_currency(self):
        return self._currency
    currency = property(_get_currency)

    def __repr__(self):
        return '<Price: %s %s>' % (self.amount, self.currency)
## end snippet

## Snippet "composite-mutable"
class Address(SQLObject):
    street = StringCol()
    city = StringCol()
    state = StringCol(length=2)

    latitude = FloatCol()
    longitude = FloatCol()

    def _init(self, id):
        SQLObject._init(self, id)
        self._coords = SOCoords(self)

    def _get_coords(self):
        return self._coords

class SOCoords(object):
    def __init__(self, so):
        self._so = so

    def _get_latitude(self):
        return self._so.latitude
    def _set_latitude(self, value):
        self._so.latitude = value
    latitude = property(_get_latitude, set_latitude)

    def _get_longitude(self):
        return self._so.longitude
    def _set_longitude(self, value):
        self._so.longitude = value
    longitude = property(_get_longitude, set_longitude)
## end snippet

## Snippet "image-binary"
class Image(SQLObject):

    data = StringCol()
    height = IntCol()
    width = IntCol()

    def _set_data(self, value):
        self._SO_set_data(value.encode('base64'))

    def _get_data(self, value):
        return self._SO_get_data().decode('base64')
## end snippet

## Snippet "image-binary-sqlite"
class Image(SQLObject):
    data = StringCol()

    def _set_data(self, value):
        # base64 just ignores whitespace, so we can get rid of \n's
        self._SO_set_data(value.encode('base64').replace('\n', ''))

    def _get_data(self):
        return self._SO_get_data().decode('base64')
## end snippet

## Snippet "slicing-batch"
start = 20
size = 10
query = Table.select()
results = query[start:start+size]
total = query.count()
print "Showing page %i of %i" % (start/size + 1, total/size + 1)
## end snippet
