"""
Main (um, only) unit testing for SQLObject.

Use -vv to see SQL queries, -vvv to also see output from queries,
and together with --inserts to see the SQL from the standard
insert statements (which are often boring).
"""

from __future__ import generators

import sys
if '--coverage' in sys.argv:
    import coverage
    print 'Starting coverage'
    coverage.erase()
    coverage.start()

from SQLObjectTest import *
from SQLObject import *
from SQLObject.include import Validator
from mx import DateTime

########################################
## Basic operation
########################################

class TestSO1(SQLObject):

    name = StringCol(length=50, dbName='name_col')
    _cacheValues = False
    _columns = [
        StringCol('passwd', length=10),
        ]

    def _set_passwd(self, passwd):
        self._SO_set_passwd(passwd.encode('rot13'))

class TestCase1(SQLObjectTest):

    classes = [TestSO1]
    MyClass = TestSO1

    info = [('bob', 'god'), ('sally', 'sordid'),
            ('dave', 'dremel'), ('fred', 'forgo')]

    def inserts(self):
        for name, passwd in self.info:
            self.MyClass.new(name=name, passwd=passwd)

    def testGet(self):
        bob = self.MyClass.selectBy(name='bob')[0]
        self.assertEqual(bob.name, 'bob')
        self.assertEqual(bob.passwd, 'god'.encode('rot13'))

    def testNewline(self):
        bob = self.MyClass.selectBy(name='bob')[0]
        testString = 'hey\nyou\\can\'t you see me?\t'
        bob.name = testString
        self.assertEqual(bob.name, testString)


class TestCaseGetSet(TestCase1):

    def testGet(self):
        bob = TestSO1.selectBy(name='bob')[0]
        self.assertEqual(bob.name, 'bob')
        bob.name = 'joe'
        self.assertEqual(bob.name, 'joe')


class TestSO2(SQLObject):
    name = StringCol(length=50, dbName='name_col')
    passwd = StringCol(length=10)

    def _set_passwd(self, passwd):
        self._SO_set_passwd(passwd.encode('rot13'))

class TestCase2(TestCase1):

    classes = [TestSO2]
    MyClass = TestSO2

class TestSO3(SQLObject):
    name = StringCol(length=10, dbName='name_col')
    other = ForeignKey('TestSO4', default=None)
    other2 = KeyCol(foreignKey='TestSO4', default=None)

class TestSO4(SQLObject):
    me = StringCol(length=10)

class Student(SQLObject):
    is_smart = BoolCol()

class BoolColTest(SQLObjectTest):
    classes = [Student]

    def testBoolCol(self):
        student = Student.new(is_smart = False)
        self.assertEqual(student.is_smart, False)

class TestCase34(SQLObjectTest):

    classes = [TestSO3, TestSO4]

    def testForeignKey(self):
        tc3 = TestSO3.new(name='a')
        self.assertEqual(tc3.other, None)
        self.assertEqual(tc3.other2, None)
        self.assertEqual(tc3.otherID, None)
        self.assertEqual(tc3.other2ID, None)
        tc4a = TestSO4.new(me='1')
        tc3.other = tc4a
        self.assertEqual(tc3.other, tc4a)
        self.assertEqual(tc3.otherID, tc4a.id)
        tc4b = TestSO4.new(me='2')
        tc3.other = tc4b.id
        self.assertEqual(tc3.other, tc4b)
        self.assertEqual(tc3.otherID, tc4b.id)
        tc4c = TestSO4.new(me='3')
        tc3.other2 = tc4c
        self.assertEqual(tc3.other2, tc4c)
        self.assertEqual(tc3.other2ID, tc4c.id)
        tc4d = TestSO4.new(me='4')
        tc3.other2 = tc4d.id
        self.assertEqual(tc3.other2, tc4d)
        self.assertEqual(tc3.other2ID, tc4d.id)
        tcc = TestSO3.new(name='b', other=tc4a)
        self.assertEqual(tcc.other, tc4a)
        tcc2 = TestSO3.new(name='c', other=tc4a.id)
        self.assertEqual(tcc2.other, tc4a)

class TestSO5(SQLObject):
    name = StringCol(length=10, dbName='name_col')
    other = ForeignKey('TestSO6', default=None, cascade=True)
    another = ForeignKey('TestSO7', default=None, cascade=True)

class TestSO6(SQLObject):
    name = StringCol(length=10, dbName='name_col')
    other = ForeignKey('TestSO7', default=None, cascade=True)

class TestSO7(SQLObject):
    name = StringCol(length=10, dbName='name_col')

class TestCase567(SQLObjectTest):

    classes = [TestSO7, TestSO6, TestSO5]

    def testForeignKeyDestroySelfCascade(self):
        tc5 = TestSO5.new(name='a')
        tc6a = TestSO6.new(name='1')
        tc5.other = tc6a
        tc7a = TestSO7.new(name='2')
        tc6a.other = tc7a
        tc5.another = tc7a
        self.assertEqual(tc5.other, tc6a)
        self.assertEqual(tc5.otherID, tc6a.id)
        self.assertEqual(tc6a.other, tc7a)
        self.assertEqual(tc6a.otherID, tc7a.id)
        self.assertEqual(tc5.other.other, tc7a)
        self.assertEqual(tc5.other.otherID, tc7a.id)
        self.assertEqual(tc5.another, tc7a)
        self.assertEqual(tc5.anotherID, tc7a.id)
        self.assertEqual(tc5.other.other, tc5.another)
        self.assertEqual(TestSO5.select().count(), 1)
        self.assertEqual(TestSO6.select().count(), 1)
        self.assertEqual(TestSO7.select().count(), 1)
        tc6b = TestSO6.new(name='3')
        tc6c = TestSO6.new(name='4')
        tc7b = TestSO7.new(name='5')
        tc6b.other = tc7b
        tc6c.other = tc7b
        self.assertEqual(TestSO5.select().count(), 1)
        self.assertEqual(TestSO6.select().count(), 3)
        self.assertEqual(TestSO7.select().count(), 2)
        tc6b.destroySelf()
        self.assertEqual(TestSO5.select().count(), 1)
        self.assertEqual(TestSO6.select().count(), 2)
        self.assertEqual(TestSO7.select().count(), 2)
        tc7b.destroySelf()
        self.assertEqual(TestSO5.select().count(), 1)
        self.assertEqual(TestSO6.select().count(), 1)
        self.assertEqual(TestSO7.select().count(), 1)
        tc7a.destroySelf()
        self.assertEqual(TestSO5.select().count(), 0)
        self.assertEqual(TestSO6.select().count(), 0)
        self.assertEqual(TestSO7.select().count(), 0)

    def testForeignKeyDropTableCascade(self):
        tc5a = TestSO5.new(name='a')
        tc6a = TestSO6.new(name='1')
        tc5a.other = tc6a
        tc7a = TestSO7.new(name='2')
        tc6a.other = tc7a
        tc5a.another = tc7a
        tc5b = TestSO5.new(name='b')
        tc5c = TestSO5.new(name='c')
        tc6b = TestSO6.new(name='3')
        tc5c.other = tc6b
        self.assertEqual(TestSO5.select().count(), 3)
        self.assertEqual(TestSO6.select().count(), 2)
        self.assertEqual(TestSO7.select().count(), 1)
        TestSO7.dropTable(cascade=True)
        self.assertEqual(TestSO5.select().count(), 3)
        self.assertEqual(TestSO6.select().count(), 2)
        tc6a.destroySelf()
        self.assertEqual(TestSO5.select().count(), 2)
        self.assertEqual(TestSO6.select().count(), 1)
        tc6b.destroySelf()
        self.assertEqual(TestSO5.select().count(), 1)
        self.assertEqual(TestSO6.select().count(), 0)
        self.assertEqual(iter(TestSO5.select()).next(), tc5b)
        tc6c = TestSO6.new(name='3')
        tc5b.other = tc6c
        self.assertEqual(TestSO5.select().count(), 1)
        self.assertEqual(TestSO6.select().count(), 1)
        tc6c.destroySelf()
        self.assertEqual(TestSO5.select().count(), 0)
        self.assertEqual(TestSO6.select().count(), 0)

class TestSO8(SQLObject):
    name = StringCol(length=10, dbName='name_col')
    other = ForeignKey('TestSO9', default=None, cascade=False)

class TestSO9(SQLObject):
    name = StringCol(length=10, dbName='name_col')

class TestCase89(SQLObjectTest):

    classes = [TestSO9, TestSO8]

    def testForeignKeyDestroySelfRestrict(self):
        tc8a = TestSO8.new(name='a')
        tc9a = TestSO9.new(name='1')
        tc8a.other = tc9a
        tc8b = TestSO8.new(name='b')
        tc9b = TestSO9.new(name='2')
        self.assertEqual(tc8a.other, tc9a)
        self.assertEqual(tc8a.otherID, tc9a.id)
        self.assertEqual(TestSO8.select().count(), 2)
        self.assertEqual(TestSO9.select().count(), 2)
        self.assertRaises(Exception, tc9a.destroySelf)
        tc9b.destroySelf()
        self.assertEqual(TestSO8.select().count(), 2)
        self.assertEqual(TestSO9.select().count(), 1)
        tc8a.destroySelf()
        tc8b.destroySelf()
        tc9a.destroySelf()
        self.assertEqual(TestSO8.select().count(), 0)
        self.assertEqual(TestSO9.select().count(), 0)

########################################
## Fancy sort
########################################

class Names(SQLObject):

    _table = 'names_table'

    fname = StringCol(length=30)
    lname = StringCol(length=30)

    _defaultOrder = ['lname', 'fname']

class NamesTest(SQLObjectTest):

    classes = [Names]

    def inserts(self):
        for fname, lname in [('aj', 'baker'), ('joe', 'robbins'),
                             ('tim', 'jackson'), ('joe', 'baker'),
                             ('zoe', 'robbins')]:
            Names.new(fname=fname, lname=lname)

    def testDefaultOrder(self):
        self.assertEqual([(n.fname, n.lname) for n in Names.select()],
                         [('aj', 'baker'), ('joe', 'baker'),
                          ('tim', 'jackson'), ('joe', 'robbins'),
                          ('zoe', 'robbins')])

    def testOtherOrder(self):
        self.assertEqual([(n.fname, n.lname) for n in Names.select().orderBy(['fname', 'lname'])],
                         [('aj', 'baker'), ('joe', 'baker'),
                          ('joe', 'robbins'), ('tim', 'jackson'),
                          ('zoe', 'robbins')])

########################################
## Select results
########################################

class IterTest(SQLObject):
    name = StringCol(dbName='name_col')

class IterationTestCase(SQLObjectTest):
    '''Test basic iteration techniques'''

    classes = [IterTest]

    names = ('a', 'b', 'c')

    def inserts(self):
        for name in self.names:
            IterTest.new(name=name)

    def test_00_normal(self):
        count = 0
        for test in IterTest.select():
            count += 1
        self.failIf(count != len(self.names))

    def test_01_turn_to_list(self):
        count = 0
        for test in list(IterTest.select()):
            count += 1
        self.failIf(count != len(self.names))

    def test_02_generator(self):
        def enumerate(iterable):
            i = 0
            for obj in iterable:
                yield i, obj
                i += 1
        all = IterTest.select()
        count = 0
        for i, test in enumerate(all):
            count += 1
        self.failIf(count != len(self.names))

    def test_03_ranged_indexed(self):
        all = IterTest.select()
        count = 0
        for i in range(all.count()):
            test = all[i]
            count += 1
        self.failIf(count != len(self.names))

    def test_04_indexed_ended_by_exception(self):
        all = IterTest.select()
        count = 0
        try:
            while 1:
                test = all[count]
                count = count+1
                # Stop the test if it's gone on too long
                if count > len(self.names):
                    break
        except IndexError:
            pass
        self.assertEqual(count, len(self.names))


########################################
## Delete during select
########################################


class DeleteSelectTest(TestCase1):

    def testGet(self):
        return

    def testSelect(self):
        for obj in TestSO1.select('all'):
            obj.destroySelf()
        self.assertEqual(list(TestSO1.select('all')), [])


########################################
## Transaction test
########################################

class TestSOTrans(SQLObject):
    #_cacheValues = False
    name = StringCol(length=10, alternateID=True, dbName='name_col')
    _defaultOrderBy = 'name'

class TransactionTest(SQLObjectTest):

    classes = [TestSOTrans]

    def inserts(self):
        TestSOTrans.new(name='bob')
        TestSOTrans.new(name='tim')

    def testTransaction(self):
        if not self.supportTransactions: return
        trans = TestSOTrans._connection.transaction()
        try:
            TestSOTrans._connection.autoCommit = 'exception'
            TestSOTrans.new(name='joe', connection=trans)
            trans.rollback()
            self.assertEqual([n.name for n in TestSOTrans.select(connection=trans)],
                             ['bob', 'tim'])
            b = TestSOTrans.byName('bob', connection=trans)
            b.name = 'robert'
            trans.commit()
            self.assertEqual(b.name, 'robert')
            b.name = 'bob'
            trans.rollback()
            self.assertEqual(b.name, 'robert')
        finally:
            TestSOTrans._connection.autoCommit = True


########################################
## Enum test
########################################

class Enum1(SQLObject):

    _columns = [
        EnumCol('l', enumValues=['a', 'bcd', 'e']),
        ]

class TestEnum1(SQLObjectTest):

    classes = [Enum1]

    def inserts(self):
        for l in ['a', 'bcd', 'a', 'e']:
            Enum1.new(l=l)

    def testBad(self):
        if self.supportRestrictedEnum:
            try:
                v = Enum1.new(l='b')
            except Exception, e:
                pass
            else:
                print v
                assert 0, "This should cause an error"


########################################
## Slicing tests
########################################

class Counter(SQLObject):

    _columns = [
        IntCol('number', notNull=True),
        ]

class SliceTest(SQLObjectTest):

    classes = [Counter]

    def inserts(self):
        for i in range(100):
            Counter.new(number=i)

    def counterEqual(self, counters, value):
        self.assertEquals([c.number for c in counters], value)

    def test1(self):
        self.counterEqual(Counter.select('all', orderBy='number'), range(100))

    def test2(self):
        self.counterEqual(Counter.select('all', orderBy='number')[10:20],
                          range(10, 20))

    def test3(self):
        self.counterEqual(Counter.select('all', orderBy='number')[20:30][:5],
                          range(20, 25))

    def test4(self):
        self.counterEqual(Counter.select('all', orderBy='number')[:-10],
                          range(0, 90))

    def test5(self):
        self.counterEqual(Counter.select('all', orderBy='number', reversed=True), range(99, -1, -1))

    def test6(self):
        self.counterEqual(Counter.select('all', orderBy='-number'), range(99, -1, -1))


########################################
## Select tests
########################################

class Counter2(SQLObject):

    _columns = [
        IntCol('n1', notNull=True),
        IntCol('n2', notNull=True),
        ]

class SelectTest(SQLObjectTest):

    classes = [Counter2]

    def inserts(self):
        for i in range(10):
            for j in range(10):
                Counter2.new(n1=i, n2=j)

    def counterEqual(self, counters, value):
        self.assertEquals([(c.n1, c.n2) for c in counters], value)

########################################
## Dynamic column tests
########################################

class Person(SQLObject):

    _columns = [StringCol('name', length=100, dbName='name_col')]
    _defaultOrder = 'name'

class Phone(SQLObject):

    _columns = [StringCol('phone', length=12)]
    _defaultOrder = 'phone'

class PeopleTest(SQLObjectTest):

    classes = [Person, Phone]

    def inserts(self):
        for n in ['jane', 'tim', 'bob', 'jake']:
            Person.new(name=n)
        for p in ['555-555-5555', '555-394-2930',
                  '444-382-4854']:
            Phone.new(phone=p)

    def testDefaultOrder(self):
        self.assertEqual(list(Person.select('all')),
                         list(Person.select('all', orderBy=Person._defaultOrder)))

    def testDynamicColumn(self):
        if not self.supportDynamic:
            return
        nickname = StringCol('nickname', length=10)
        Person.addColumn(nickname, changeSchema=True)
        n = Person.new(name='robert', nickname='bob')
        self.assertEqual([p.name for p in Person.select('all')],
                         ['bob', 'jake', 'jane', 'robert', 'tim'])
        Person.delColumn(nickname, changeSchema=True)

    def testDynamicJoin(self):
        if not self.supportDynamic:
            return
        col = KeyCol('personID', foreignKey='Person')
        Phone.addColumn(col, changeSchema=True)
        join = MultipleJoin('Phone')
        Person.addJoin(join)
        for phone in Phone.select('all'):
            if phone.phone.startswith('555'):
                phone.person = Person.selectBy(name='tim')[0]
            else:
                phone.person = Person.selectBy(name='bob')[0]
        l = [p.phone for p in Person.selectBy(name='tim')[0].phones]
        l.sort()
        self.assertEqual(l,
                         ['555-394-2930', '555-555-5555'])
        Phone.delColumn(col, changeSchema=True)
        Person.delJoin(join)

########################################
## Auto class generation
########################################

class AutoTest(SQLObjectTest):

    mysqlCreate = """
    CREATE TABLE IF NOT EXISTS auto_test (
      id INT AUTO_INCREMENT PRIMARY KEY,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT NULL,
      created DATETIME NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL,
      wannahavefun TINYINT DEFAULT 0 NOT NULL
    )
    """

    postgresCreate = """
    CREATE TABLE auto_test (
      id SERIAL,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT 0,
      created VARCHAR(40) NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL,
      wannahavefun BOOL DEFAULT FALSE NOT NULL
    )
    """

    sybaseCreate = """
    CREATE TABLE auto_test (
      id integer,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT 0,
      created VARCHAT(40) NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL
    )
    """

    mysqlDrop = """
    DROP TABLE IF EXISTS auto_test
    """

    postgresDrop = """
    DROP TABLE auto_test
    """

    sybaseDrop = """
    DROP TABLE auto_test
    """

    _table = 'auto_test'

    def testClassCreate(self):
        if not self.supportAuto:
            return
        import sys
        class AutoTest(SQLObject):
            _fromDatabase = True
            _connection = connection()
        john = AutoTest.new(firstName='john',
                            lastName='doe',
                            age=10,
                            created=DateTime.now(),
                            wannahavefun=False)
        jane = AutoTest.new(firstName='jane',
                            lastName='doe',
                            happy='N',
                            created=DateTime.now(),
                            wannahavefun=True)
        self.failIf(john.wannahavefun)
        self.failUnless(jane.wannahavefun)
        reg = sys.modules[SQLObject.__module__].classRegistry[AutoTest._registry]
        del reg['AutoTest']

########################################
## Joins
########################################

class PersonJoiner(SQLObject):

    _columns = [StringCol('name', length=40, alternateID=True)]
    _joins = [RelatedJoin('AddressJoiner')]

class AddressJoiner(SQLObject):

    _columns = [StringCol('zip', length=5, alternateID=True)]
    _joins = [RelatedJoin('PersonJoiner')]

class JoinTest(SQLObjectTest):

    classes = [PersonJoiner, AddressJoiner]

    def inserts(self):
        for n in ['bob', 'tim', 'jane', 'joe', 'fred', 'barb']:
            PersonJoiner.new(name=n)
        for z in ['11111', '22222', '33333', '44444']:
            AddressJoiner.new(zip=z)

    def testJoin(self):
        b = PersonJoiner.byName('bob')
        self.assertEqual(b.addressJoiners, [])
        z = AddressJoiner.byZip('11111')
        b.addAddressJoiner(z)
        self.assertZipsEqual(b.addressJoiners, ['11111'])
        self.assertNamesEqual(z.personJoiners, ['bob'])
        z2 = AddressJoiner.byZip('22222')
        b.addAddressJoiner(z2)
        self.assertZipsEqual(b.addressJoiners, ['11111', '22222'])
        self.assertNamesEqual(z2.personJoiners, ['bob'])
        b.removeAddressJoiner(z)
        self.assertZipsEqual(b.addressJoiners, ['22222'])
        self.assertNamesEqual(z.personJoiners, [])

    def assertZipsEqual(self, zips, dest):
        self.assertEqual([a.zip for a in zips], dest)

    def assertNamesEqual(self, people, dest):
        self.assertEqual([p.name for p in people], dest)

class PersonJoiner2(SQLObject):

    _columns = [StringCol('name', length=40, alternateID=True)]
    _joins = [MultipleJoin('AddressJoiner2')]

class AddressJoiner2(SQLObject):

    _columns = [StringCol('zip', length=5),
                StringCol('plus4', length=4, default=None),
                ForeignKey('PersonJoiner2')]
    _defaultOrder = ['-zip', 'plus4']

class JoinTest2(SQLObjectTest):

    classes = [PersonJoiner2, AddressJoiner2]

    def inserts(self):
        p1 = PersonJoiner2.new(name='bob')
        p2 = PersonJoiner2.new(name='sally')
        for z in ['11111', '22222', '33333']:
            a = AddressJoiner2.new(zip=z, personJoiner2=p1)
            #p1.addAddressJoiner2(a)
        AddressJoiner2.new(zip='00000', personJoiner2=p2)

    def test(self):
        bob = PersonJoiner2.byName('bob')
        sally = PersonJoiner2.byName('sally')
        self.assertEqual(len(bob.addressJoiner2s), 3)
        self.assertEqual(len(sally.addressJoiner2s), 1)
        bob.addressJoiner2s[0].destroySelf()
        self.assertEqual(len(bob.addressJoiner2s), 2)
        z = bob.addressJoiner2s[0]
        z.zip = 'xxxxx'
        id = z.id
        del z
        z = AddressJoiner2(id)
        self.assertEqual(z.zip, 'xxxxx')

    def testDefaultOrder(self):
        p1 = PersonJoiner2.byName('bob')
        self.assertEqual([i.zip for i in p1.addressJoiner2s],
                         ['33333', '22222', '11111'])


########################################
## Inheritance
########################################

class Super(SQLObject):

    _columns = [StringCol('name', length=10)]

class Sub(Super):

    _columns = Super._columns + [StringCol('name2', length=10)]

class InheritanceTest(SQLObjectTest):

    classes = [Super, Sub]

    def testSuper(self):
        s1 = Super.new(name='one')
        s2 = Super.new(name='two')
        s3 = Super(s1.id)
        self.assertEqual(s1, s3)

    def testSub(self):
        s1 = Sub.new(name='one', name2='1')
        s2 = Sub.new(name='two', name2='2')
        s3 = Sub(s1.id)
        self.assertEqual(s1, s3)


########################################
## Expiring, syncing
########################################

class SyncTest(SQLObject):
    name = StringCol(length=50, alternateID=True, dbName='name_col')

class ExpireTest(SQLObjectTest):

    classes = [SyncTest]

    def inserts(self):
        SyncTest.new(name='bob')
        SyncTest.new(name='tim')

    def testExpire(self):
        conn = SyncTest._connection
        b = SyncTest.byName('bob')
        conn.query("UPDATE sync_test SET name_col = 'robert' WHERE id = %i"
                   % b.id)
        self.assertEqual(b.name, 'bob')
        b.expire()
        self.assertEqual(b.name, 'robert')
        conn.query("UPDATE sync_test SET name_col = 'bobby' WHERE id = %i"
                   % b.id)
        b.sync()
        self.assertEqual(b.name, 'bobby')

########################################
## Validation/conversion
########################################

class SOValidation(SQLObject):

    name = StringCol(validator=Validator.PlainText(), default='x', dbName='name_col')
    name2 = StringCol(validator=Validator.ConfirmType(str), default='y')
    name3 = IntCol(validator=Validator.Wrapper(fromPython=int), default=100)

class ValidationTest(SQLObjectTest):

    classes = [SOValidation]

    def testValidate(self):
        t = SOValidation.new(name='hey')
        self.assertRaises(Validator.InvalidField, setattr, t,
                          'name', '!!!')
        t.name = 'you'

    def testConfirmType(self):
        t = SOValidation.new(name2='hey')
        self.assertRaises(Validator.InvalidField, setattr, t,
                          'name2', 1)
        t.name2 = 'you'

    def testWrapType(self):
        t = SOValidation.new(name3=1)
        self.assertRaises(Validator.InvalidField, setattr, t,
                          'name3', 'x')
        t.name3 = 1L
        self.assertEqual(t.name3, 1)
        t.name3 = '1'
        self.assertEqual(t.name3, 1)
        t.name3 = 0
        self.assertEqual(t.name3, 0)


########################################
## String ID test
########################################

class SOStringID(SQLObject):

    _table = 'so_string_id'
    val = StringCol(alternateID=True)

    mysqlCreate = """
    CREATE TABLE IF NOT EXISTS so_string_id (
      id VARCHAR(50) PRIMARY KEY,
      val TEXT
    )
    """

    postgresCreate = """
    CREATE TABLE so_string_id (
      id VARCHAR(50) PRIMARY KEY,
      val TEXT
    )
    """

    firebirdCreate = """
    CREATE TABLE so_string_id (
      id VARCHAR(50) NOT NULL PRIMARY KEY,
      val BLOB SUB_TYPE TEXT
    )
    """

    sqliteCreate = postgresCreate

    mysqlDrop = """
    DROP TABLE IF EXISTS so_string_id
    """

    postgresDrop = """
    DROP TABLE so_string_id
    """

    sqliteDrop = postgresDrop
    firebirdDrop = postgresDrop

class StringIDTest(SQLObjectTest):

    classes = [SOStringID]

    def testStringID(self):
        t = SOStringID.new(id='hey', val='whatever')
        t2 = SOStringID.byVal('whatever')
        self.assertEqual(t, t2)
        t3 = SOStringID.new(id='you', val='nowhere')
        t4 = SOStringID('you')
        self.assertEqual(t3, t4)



class AnotherStyle(MixedCaseUnderscoreStyle):
    def pythonAttrToDBColumn(self, attr):
        if attr.lower().endswith('id'):
            return 'id'+MixedCaseUnderscoreStyle.pythonAttrToDBColumn(self, attr[:-2])
        else:
            return MixedCaseUnderscoreStyle.pythonAttrToDBColumn(self, attr)

class SOStyleTest1(SQLObject):
    a = StringCol()
    st2 = ForeignKey('SOStyleTest2')
    _style = AnotherStyle()

class SOStyleTest2(SQLObject):
    b = StringCol()
    _style = AnotherStyle()

class StyleTest(SQLObjectTest):

    classes = [SOStyleTest1, SOStyleTest2]


    def test(self):
        st1 = SOStyleTest1.new(a='something', st2=None)
        st2 = SOStyleTest2.new(b='whatever')
        st1.st2 = st2
        self.assertEqual(st1._SO_columnDict['st2ID'].dbName, 'idst2')
        self.assertEqual(st1.st2, st2)

########################################
## Run from command-line:
########################################

def coverModules():
    sys.stdout.write('Writing coverage...')
    sys.stdout.flush()
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    from SQLObject import DBConnection as tmp
    there = os.path.dirname(os.path.abspath(tmp.__file__))
    for name, mod in sys.modules.items():
        if not mod:
            continue
        try:
            modFile = os.path.abspath(mod.__file__)
        except AttributeError:
            # Probably a C extension
            continue
        if modFile.startswith(here) or modFile.startswith(there):
            writeCoverage(mod, there, os.path.join(here, 'SQLObject'))
    coverage.erase()
    sys.stdout.write('done.\n')


def writeCoverage(module, oldBase, newBase):
    filename, numbers, unexecuted, s = coverage.analysis(module)
    coverFilename = filename + ',cover'
    if coverFilename.startswith(oldBase):
        coverFilename = newBase + coverFilename[len(oldBase):]
    fout = open(coverFilename, 'w')
    fin = open(filename)
    i = 1
    lines = 0
    good = 0
    while 1:
        line = fin.readline()
        if not line: break
        assert line[-1] == '\n'
        fout.write(line[:-1])
        unused = i in unexecuted
        interesting = interestingLine(line, unused)
        if interesting:
            if unused:
                fout.write(' '*(72-len(line)))
                fout.write('#@@@@')
                lastUnused = True
            else:
                lastUnused = False
                good += 1
            lines += 1
        fout.write('\n')
        i += 1
    fout.write('\n# Coverage:\n')
    fout.write('# %i/%i, %i%%' % (
        good, lines, lines and int(good*100/lines)))
    fout.close()
    fin.close()

def interestingLine(line, unused):
    line = line.strip()
    if not line:
        return False
    if line.startswith('#'):
        return False
    if line in ('"""', '"""'):
        return False
    if line.startswith('global '):
        return False
    if line.startswith('def ') and not unused:
        # If a def *isn't* executed, that's interesting
        return False
    if line.startswith('class ') and not unused:
        return False
    return True

if __name__ == '__main__':
    import unittest, sys, os
    dbs = []
    newArgs = []
    doCoverage = False
    for arg in sys.argv[1:]:
        if arg.startswith('-d'):
            dbs.append(arg[2:])
            continue
        if arg.startswith('--database='):
            dbs.append(arg[11:])
            continue
        if arg in ('-vv', '--extra-verbose'):
            SQLObjectTest.debugSQL = True
        if arg in ('-vvv', '--super-verbose'):
            SQLObjectTest.debugSQL = True
            SQLObjectTest.debugOutput = True
            newArgs.append('-vv')
            continue
        if arg in ('--inserts',):
            SQLObjectTest.debugInserts = True
            continue
        if arg in ('--coverage',):
            # Handled earlier, so we get better coverage
            doCoverage = True
            continue
        newArgs.append(arg)
    sys.argv = [sys.argv[0]] + newArgs
    if not dbs:
        dbs = ['mysql']
    if dbs == ['all']:
        dbs = supportedDatabases()
    for db in dbs:
        setDatabaseType(db)
        print 'Testing %s' % db
        try:
            unittest.main()
        except SystemExit:
            pass
    if doCoverage:
        coverage.stop()
        coverModules()
