"""
Main unit testing for SQLObject.

Use -vv to see SQL queries, -vvv to also see output from queries,
and together with --inserts to see the SQL from the standard
insert statements (which are often boring).
"""

from __future__ import generators

import sys, os
if '--coverage' in sys.argv:
    import coverage
    print 'Starting coverage'
    coverage.erase()
    coverage.start()

from SQLObjectTest import *
from sqlobject import *
from sqlobject import col
from sqlobject.include import validators
from sqlobject import classregistry
if default_datetime_implementation == DATETIME_IMPLEMENTATION:
    from datetime import datetime
    now = datetime.now
elif default_datetime_implementation == MXDATETIME_IMPLEMENTATION:
    from mx.DateTime import now
global curr_db
curr_db = None
from sqlobject import cache

class ClassRegistryTest(SQLObjectTest):
    def testErrorOnDuplicateClassDefinition(self):
        """Raise an error if a class is defined more than once."""
        class Duplicate(SQLObject):
            pass

        try:
            class Duplicate(SQLObject):
                pass
        except ValueError, err:
            assert str(err).startswith("class Duplicate is already in the registry")
        else:
            self.fail("should have raised an error on duplicate class definition")

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
            self.MyClass(name=name, passwd=passwd)

    def testGet(self):
        bob = self.MyClass.selectBy(name='bob')[0]
        self.assertEqual(bob.name, 'bob')
        self.assertEqual(bob.passwd, 'god'.encode('rot13'))

    def testNewline(self):
        bob = self.MyClass.selectBy(name='bob')[0]
        testString = 'hey\nyou\\can\'t you see me?\t'
        bob.name = testString
        self.failUnless(bob.name == testString, (bob.name, testString))

    def testCount(self):
        self.assertEqual(self.MyClass.selectBy(name='bob').count(), 1)
        self.assertEqual(self.MyClass.select(self.MyClass.q.name == 'bob').count(), 1)
        self.assertEqual(self.MyClass.select().count(), len(list(self.MyClass.select())))

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
        student = Student(is_smart=False)
        self.assertEqual(student.is_smart, False)
        student2 = Student(is_smart='false')
        self.assertEqual(student2.is_smart, True)

class TestCase34(SQLObjectTest):

    classes = [TestSO4, TestSO3]

    def testForeignKey(self):
        tc3 = TestSO3(name='a')
        self.assertEqual(tc3.other, None)
        self.assertEqual(tc3.other2, None)
        self.assertEqual(tc3.otherID, None)
        self.assertEqual(tc3.other2ID, None)
        tc4a = TestSO4(me='1')
        tc3.other = tc4a
        self.assertEqual(tc3.other, tc4a)
        self.assertEqual(tc3.otherID, tc4a.id)
        tc4b = TestSO4(me='2')
        tc3.other = tc4b.id
        self.assertEqual(tc3.other, tc4b)
        self.assertEqual(tc3.otherID, tc4b.id)
        tc4c = TestSO4(me='3')
        tc3.other2 = tc4c
        self.assertEqual(tc3.other2, tc4c)
        self.assertEqual(tc3.other2ID, tc4c.id)
        tc4d = TestSO4(me='4')
        tc3.other2 = tc4d.id
        self.assertEqual(tc3.other2, tc4d)
        self.assertEqual(tc3.other2ID, tc4d.id)
        tcc = TestSO3(name='b', other=tc4a)
        self.assertEqual(tcc.other, tc4a)
        tcc2 = TestSO3(name='c', other=tc4a.id)
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
        tc5 = TestSO5(name='a')
        tc6a = TestSO6(name='1')
        tc5.other = tc6a
        tc7a = TestSO7(name='2')
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
        tc6b = TestSO6(name='3')
        tc6c = TestSO6(name='4')
        tc7b = TestSO7(name='5')
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
        if curr_db == 'sybase':
            # XXX This test doesn't pass with sybase.
            return
        tc5a = TestSO5(name='a')
        tc6a = TestSO6(name='1')
        tc5a.other = tc6a
        tc7a = TestSO7(name='2')
        tc6a.other = tc7a
        tc5a.another = tc7a
        tc5b = TestSO5(name='b')
        tc5c = TestSO5(name='c')
        tc6b = TestSO6(name='3')
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
        tc6c = TestSO6(name='3')
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
        tc8a = TestSO8(name='a')
        tc9a = TestSO9(name='1')
        tc8a.other = tc9a
        tc8b = TestSO8(name='b')
        tc9b = TestSO9(name='2')
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

    firstName = StringCol(length=30)
    lastName = StringCol(length=30)

    _defaultOrder = ['lastName', 'firstName']

class NamesTest(SQLObjectTest):

    classes = [Names]

    def inserts(self):
        for firstName, lastName in [('aj', 'baker'), ('joe', 'robbins'),
                                    ('tim', 'jackson'), ('joe', 'baker'),
                                    ('zoe', 'robbins')]:
            Names(firstName=firstName, lastName=lastName)

    def testDefaultOrder(self):
        self.assertEqual([(n.firstName, n.lastName) for n in Names.select()],
                         [('aj', 'baker'), ('joe', 'baker'),
                          ('tim', 'jackson'), ('joe', 'robbins'),
                          ('zoe', 'robbins')])

    def testOtherOrder(self):
        self.assertEqual([(n.firstName, n.lastName) for n in Names.select().orderBy(['firstName', 'lastName'])],
                         [('aj', 'baker'), ('joe', 'baker'),
                          ('joe', 'robbins'), ('tim', 'jackson'),
                          ('zoe', 'robbins')])

    def testUntranslatedColumnOrder(self):
        self.assertEqual([(n.firstName, n.lastName) for n in Names.select().orderBy(['first_name', 'last_name'])],
                         [('aj', 'baker'), ('joe', 'baker'),
                          ('joe', 'robbins'), ('tim', 'jackson'),
                          ('zoe', 'robbins')])

    def testSingleUntranslatedColumnOrder(self):
        self.assertEqual([n.firstName for n in
                          Names.select().orderBy('firstName')],
                         ['aj', 'joe', 'joe', 'tim', 'zoe'])
        self.assertEqual([n.firstName for n in
                          Names.select().orderBy('first_name')],
                         ['aj', 'joe', 'joe', 'tim', 'zoe'])
        self.assertEqual([n.firstName for n in
                          Names.select().orderBy('-firstName')],
                         ['zoe', 'tim', 'joe', 'joe', 'aj'])
        self.assertEqual([n.firstName for n in
                          Names.select().orderBy('-first_name')],
                         ['zoe', 'tim', 'joe', 'joe', 'aj'])
        self.assertEqual([n.firstName for n in
                          Names.select().orderBy(Names.q.firstName)],
                         ['aj', 'joe', 'joe', 'tim', 'zoe'])

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
            IterTest(name=name)

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
## Delete without caching
########################################

class NoCache(SQLObject):
    name = StringCol()

class TestNoCache(SQLObjectTest):

    classes=[NoCache]

    def setUp(self):
        SQLObjectTest.setUp(self)
        NoCache._connection.cache = cache.CacheSet(cache=False)

    def tearDown(self):
        NoCache._connection.cache = cache.CacheSet(cache=True)
        SQLObjectTest.tearDown(self)

    def testDestroySelf(self):
        value = NoCache(name='test')
        value.destroySelf()

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
        TestSOTrans(name='bob')
        TestSOTrans(name='tim')

    def testTransaction(self):
        if not self.supportTransactions: return
        trans = TestSOTrans._connection.transaction()
        try:
            TestSOTrans._connection.autoCommit = 'exception'
            TestSOTrans(name='joe', connection=trans)
            trans.rollback()
            trans.begin()
            self.assertEqual([n.name for n in TestSOTrans.select(connection=trans)],
                             ['bob', 'tim'])
            b = TestSOTrans.byName('bob', connection=trans)
            b.name = 'robert'
            trans.commit()
            self.assertEqual(b.name, 'robert')
            b.name = 'bob'
            trans.rollback()
            trans.begin()
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
            Enum1(l=l)

    def testBad(self):
        if self.supportRestrictedEnum:
            try:
                v = Enum1(l='b')
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
            Counter(number=i)

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
                Counter2(n1=i, n2=j)

    def counterEqual(self, counters, value):
        self.assertEquals([(c.n1, c.n2) for c in counters], value)

    def accumulateEqual(self, func, counters, value):
        self.assertEqual(func([ c.n1 for c in counters]), value)

    def test1(self):
        self.accumulateEqual(sum,Counter2.select(orderBy='n1'),
                             sum(range(10)) * 10)

    def test2(self):
        self.accumulateEqual(len,Counter2.select('all'), 100)

    
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
            Person(name=n)
        for p in ['555-555-5555', '555-394-2930',
                  '444-382-4854']:
            Phone(phone=p)

    def testDefaultOrder(self):
        self.assertEqual(list(Person.select('all')),
                         list(Person.select('all', orderBy=Person._defaultOrder)))

    def testDynamicColumn(self):
        if not self.supportDynamic:
            return
        nickname = StringCol('nickname', length=10)
        Person.addColumn(nickname, changeSchema=True)
        n = Person(name='robert', nickname='bob')
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
      auto_id INT AUTO_INCREMENT PRIMARY KEY,
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
      auto_id SERIAL PRIMARY KEY,
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
      auto_id integer,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT 0,
      created VARCHAR(40) NOT NULL,
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
        class AutoTest(SQLObject):
            _fromDatabase = True
            _idName = 'auto_id'
            _connection = connection()
        john = AutoTest(firstName='john',
                        lastName='doe',
                        age=10,
                        created=now(),
                        wannahavefun=False)
        jane = AutoTest(firstName='jane',
                        lastName='doe',
                        happy='N',
                        created=now(),
                        wannahavefun=True)
        self.failIf(john.wannahavefun)
        self.failUnless(jane.wannahavefun)
        del classregistry.registry(AutoTest._registry).classes['AutoTest']

########################################
## Joins
########################################

class PersonJoiner(SQLObject):

    _columns = [StringCol('name', length=40, alternateID=True)]
    _joins = [RelatedJoin('AddressJoiner')]

class AddressJoiner(SQLObject):

    _columns = [StringCol('zip', length=5, alternateID=True)]
    _joins = [RelatedJoin('PersonJoiner')]

class ImplicitJoiningSO(SQLObject):
    foo = RelatedJoin('Bar')

class ExplicitJoiningSO(SQLObject):
    _joins = [MultipleJoin('Bar', joinMethodName='foo')]

class JoinTest(SQLObjectTest):

    classes = [PersonJoiner, AddressJoiner]

    def inserts(self):
        for n in ['bob', 'tim', 'jane', 'joe', 'fred', 'barb']:
            PersonJoiner(name=n)
        for z in ['11111', '22222', '33333', '44444']:
            AddressJoiner(zip=z)

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

    def testJoinAttributeWithUnderscores(self):
        # Make sure that the implicit setting of joinMethodName works
        self.failUnless(hasattr(ImplicitJoiningSO, 'foo'))
        self.failIf(hasattr(ImplicitJoiningSO, 'bars'))

        # And make sure explicit setting also works
        self.failUnless(hasattr(ExplicitJoiningSO, 'foo'))
        self.failIf(hasattr(ExplicitJoiningSO, 'bars'))

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
        p1 = PersonJoiner2(name='bob')
        p2 = PersonJoiner2(name='sally')
        for z in ['11111', '22222', '33333']:
            a = AddressJoiner2(zip=z, personJoiner2=p1)
            #p1.addAddressJoiner2(a)
        AddressJoiner2(zip='00000', personJoiner2=p2)

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
        z = AddressJoiner2.get(id)
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
        s1 = Super(name='one')
        s2 = Super(name='two')
        s3 = Super.get(s1.id)
        self.assertEqual(s1, s3)

    def testSub(self):
        s1 = Sub(name='one', name2='1')
        s2 = Sub(name='two', name2='2')
        s3 = Sub.get(s1.id)
        self.assertEqual(s1, s3)


########################################
## Expiring, syncing
########################################

class SyncTest(SQLObject):
    name = StringCol(length=50, alternateID=True, dbName='name_col')

class ExpireTest(SQLObjectTest):

    classes = [SyncTest]

    def inserts(self):
        SyncTest(name='bob')
        SyncTest(name='tim')

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

    name = StringCol(validator=validators.PlainText(), default='x', dbName='name_col')
    name2 = StringCol(validator=validators.ConfirmType(str), default='y')
    name3 = IntCol(validator=validators.Wrapper(fromPython=int), default=100)

class ValidationTest(SQLObjectTest):

    classes = [SOValidation]

    def testValidate(self):
        t = SOValidation(name='hey')
        self.assertRaises(validators.InvalidField, setattr, t,
                          'name', '!!!')
        t.name = 'you'

    def testConfirmType(self):
        t = SOValidation(name2='hey')
        self.assertRaises(validators.InvalidField, setattr, t,
                          'name2', 1)
        t.name2 = 'you'

    def testWrapType(self):
        t = SOValidation(name3=1)
        self.assertRaises(validators.InvalidField, setattr, t,
                          'name3', 'x')
        t.name3 = 1L
        self.assertEqual(t.name3, 1)
        t.name3 = 0
        self.assertEqual(t.name3, 0)


########################################
## String ID test
########################################

class SOStringID(SQLObject):

    _table = 'so_string_id'
    _idType = str
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

    sybaseCreate = """
    CREATE TABLE so_string_id (
      id VARCHAR(50) UNIQUE,
      val VARCHAR(50) NULL
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
        t = SOStringID(id='hey', val='whatever')
        t2 = SOStringID.byVal('whatever')
        self.assertEqual(t, t2)
        t3 = SOStringID(id='you', val='nowhere')
        t4 = SOStringID.get('you')
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

    classes = [SOStyleTest2, SOStyleTest1]


    def test(self):
        st1 = SOStyleTest1(a='something', st2=None)
        st2 = SOStyleTest2(b='whatever')
        st1.st2 = st2
        self.assertEqual(st1._SO_columnDict['st2ID'].dbName, 'idst2')
        self.assertEqual(st1.st2, st2)

########################################
## Lazy updates
########################################

class Lazy(SQLObject):

    _lazyUpdate = True
    name = StringCol()
    other = StringCol(default='nothing')
    third = StringCol(default='third')

class LazyTest(SQLObjectTest):

    classes = [Lazy]

    def setUp(self):
        # All this stuff is so that we can track when the connection
        # does an actual update; we put in a new _SO_update method
        # that calls the original and sets an instance variable that
        # we can later check.
        SQLObjectTest.setUp(self)
        self.conn = Lazy._connection
        self.conn.didUpdate = False
        self._oldUpdate = self.conn._SO_update
        newUpdate = lambda so, values, s=self, c=self.conn, o=self._oldUpdate: self._alternateUpdate(so, values, c, o)
        self.conn._SO_update = newUpdate

    def tearDown(self):
        self.conn._SO_update = self._oldUpdate
        del self._oldUpdate

    def _alternateUpdate(self, so, values, conn, oldUpdate):
        conn.didUpdate = True
        return oldUpdate(so, values)

    def test(self):
        assert not self.conn.didUpdate
        obj = Lazy(name='tim')
        # We just did an insert, but not an update:
        assert not self.conn.didUpdate
        obj.set(name='joe')
        assert obj.dirty
        self.assertEqual(obj.name, 'joe')
        assert not self.conn.didUpdate
        obj.syncUpdate()
        self.assertEqual(obj.name, 'joe')
        assert self.conn.didUpdate
        assert not obj.dirty
        self.assertEqual(obj.name, 'joe')
        self.conn.didUpdate = False

        obj = Lazy(name='frank')
        obj.name = 'joe'
        assert not self.conn.didUpdate
        assert obj.dirty
        self.assertEqual(obj.name, 'joe')
        obj.name = 'joe2'
        assert not self.conn.didUpdate
        assert obj.dirty
        self.assertEqual(obj.name, 'joe2')
        obj.syncUpdate()
        self.assertEqual(obj.name, 'joe2')
        assert not obj.dirty
        assert self.conn.didUpdate
        self.conn.didUpdate = False

        obj = Lazy(name='loaded')
        assert not obj.dirty
        assert not self.conn.didUpdate
        self.assertEqual(obj.name, 'loaded')
        obj.name = 'unloaded'
        assert obj.dirty
        self.assertEqual(obj.name, 'unloaded')
        assert not self.conn.didUpdate
        obj.sync()
        assert not obj.dirty
        self.assertEqual(obj.name, 'unloaded')
        assert self.conn.didUpdate
        self.conn.didUpdate = False
        obj.name = 'whatever'
        assert obj.dirty
        self.assertEqual(obj.name, 'whatever')
        assert not self.conn.didUpdate
        obj._SO_loadValue('name')
        assert obj.dirty
        self.assertEqual(obj.name, 'whatever')
        assert not self.conn.didUpdate
        obj._SO_loadValue('other')
        self.assertEqual(obj.name, 'whatever')
        assert not self.conn.didUpdate
        obj.syncUpdate()
        assert self.conn.didUpdate
        self.conn.didUpdate = False

        # Now, check that get() doesn't screw
        # cached objects' validator state.
        obj_id = obj.id
        old_state = obj._SO_validatorState
        obj = Lazy.get(obj_id)
        assert not obj.dirty
        assert not self.conn.didUpdate
        assert obj._SO_validatorState is old_state
        self.assertEqual(obj.name, 'whatever')
        obj.name = 'unloaded'
        self.assertEqual(obj.name, 'unloaded')
        assert obj.dirty
        assert not self.conn.didUpdate
        # Fetch the object again with get() and
        # make sure dirty is still set, as the
        # object should come from the cache.
        obj = Lazy.get(obj_id)
        assert obj.dirty
        assert not self.conn.didUpdate
        self.assertEqual(obj.name, 'unloaded')
        obj.syncUpdate()
        assert self.conn.didUpdate
        assert not obj.dirty
        self.conn.didUpdate = False

        # Then clear the cache, and try a get()
        # again, to make sure stuf like _SO_createdValues
        # is properly initialized.
        self.conn.cache.clear()
        obj = Lazy.get(obj_id)
        assert not obj.dirty
        assert not self.conn.didUpdate
        self.assertEqual(obj.name, 'unloaded')
        obj.name = 'spongebob'
        self.assertEqual(obj.name, 'spongebob')
        assert obj.dirty
        assert not self.conn.didUpdate
        obj.syncUpdate()
        assert self.conn.didUpdate
        assert not obj.dirty
        self.conn.didUpdate = False

        obj = Lazy(name='last')
        assert not obj.dirty
        obj.syncUpdate()
        assert not self.conn.didUpdate
        assert not obj.dirty
        # Check that setting multiple values
        # actually works. This was broken
        # and just worked because we were testing
        # only one value at a time, so 'name'
        # had the right value after the for loop *wink*
        # Also, check that passing a name that is not
        # a valid column doesn't break, but instead
        # just does a plain setattr.
        obj.set(name='first', other='who', third='yes')
        self.assertEqual(obj.name, 'first')
        self.assertEqual(obj.other, 'who')
        self.assertEqual(obj.third, 'yes')
        assert obj.dirty
        assert not self.conn.didUpdate
        obj.syncUpdate()
        assert self.conn.didUpdate
        assert not obj.dirty


########################################
## Indexes
########################################

class SOIndex1(SQLObject):
    name = StringCol(length=100)
    number = IntCol()

    nameIndex = DatabaseIndex('name', unique=True)
    nameIndex2 = DatabaseIndex(name, number)
    nameIndex3 = DatabaseIndex({'column': name,
                                'length': 3})

class SOIndex2(SQLObject):

    name = StringCol()

    nameIndex = DatabaseIndex({'expression': 'lower(name)'})

class IndexTest1(SQLObjectTest):

    classes = [SOIndex1]

    def test(self):
        n = 0
        for name in 'blah blech boring yep yort snort'.split():
            n += 1
            SOIndex1(name=name, number=n)
        mod = SOIndex1._connection.module
        try:
            SOIndex1(name='blah', number=0)
        except (mod.ProgrammingError, mod.IntegrityError):
            # expected
            pass
        else:
            assert 0, "Exception expected."

class IndexTest2(SQLObjectTest):

    classes = [SOIndex2]

    requireSupport = ('supportExpressionIndex',)
    
    def test(self):
        # Not much to test, just want to make sure the table works
        # properly
        if not self.hasSupport():
            return
        SOIndex2(name='')


########################################
## Distinct
########################################

class Distinct1(SQLObject):
    n = IntCol()

class Distinct2(SQLObject):
    other = ForeignKey('Distinct1')

class DistinctTest(SQLObjectTest):

    classes = [Distinct1, Distinct2]

    def inserts(self):
        obs = [Distinct1(n=i) for i in range(3)]
        Distinct2(other=obs[0])
        Distinct2(other=obs[0])
        Distinct2(other=obs[1])

    def count(self, select):
        result = {}
        for ob in select:
            result[int(ob.n)] = result.get(int(ob.n), 0)+1
        return result

    def testDistinct(self):
        query = (Distinct2.q.otherID==Distinct1.q.id)
        sel = Distinct1.select(query)
        self.assertEqual(self.count(sel),
                         {0: 2, 1: 1})
        sel = Distinct1.select(query, distinct=True)
        self.assertEqual(self.count(sel),
                         {0: 1, 1:1})

########################################
## Unicode columns
########################################

class Unicode1(SQLObject):
    count = IntCol(alternateID=True)
    col1 = UnicodeCol()
    col2 = UnicodeCol(dbEncoding='latin-1')

class UnicodeTest(SQLObjectTest):

    classes = [Unicode1]

    data = [u'\u00f0', u'test', 'ascii test']

    def testCreate(self):
        items = []
        for i, n in enumerate(self.data):
            items.append(Unicode1(count=i, col1=n, col2=n))
        for n, item in zip(self.data, items):
            item.col1 = item.col2 = n
        for n, item in zip(self.data, items):
            self.assertEqual(item.col1, item.col2, n)
        conn = Unicode1._connection
        rows = conn.queryAll("""
        SELECT count, col1, col2
        FROM unicode1
        ORDER BY count
        """)
        for count, col1, col2 in rows:
            self.assertEqual(self.data[count].encode('utf-8'), col1)
            self.assertEqual(self.data[count].encode('latin1'), col2)

########################################
## Date/time columns
########################################

if datetime_available:
    col.default_datetime_implementation = DATETIME_IMPLEMENTATION
    from datetime import date, datetime

    class DateTime1(SQLObject):
        col1 = DateCol()
        col2 = DateTimeCol()

    class DateTimeTest1(SQLObjectTest):

        classes = [DateTime1]

        def testDateTime(self):
            _now = now()
            dt1 = DateTime1(col1=_now, col2=_now)
            self.failUnless(isinstance(dt1.col1, date))
            self.failUnless(isinstance(dt1.col2, datetime))

            today_str = _now.strftime("%Y-%m-%d")
            now_str = _now.strftime("%Y-%m-%d %T")
            self.assertEqual(str(dt1.col1), today_str)
            self.assertEqual(str(dt1.col2), now_str)

if mxdatetime_available:
    col.default_datetime_implementation = MXDATETIME_IMPLEMENTATION

    class DateTime2(SQLObject):
        col1 = DateCol()
        col2 = DateTimeCol()

    class DateTimeTest2(SQLObjectTest):

        classes = [DateTime2]

        def testMxDateTime(self):
            _now = now()
            dt2 = DateTime2(col1=_now, col2=_now)
            self.failUnless(isinstance(dt2.col1, col.DateTimeType))
            self.failUnless(isinstance(dt2.col2, col.DateTimeType))

            today_str = _now.strftime("%Y-%m-%d 00:00:00.00")
            now_str = _now.strftime("%Y-%m-%d %T.00")
            self.assertEqual(str(dt2.col1), today_str)
            self.assertEqual(str(dt2.col2), now_str)

########################################
## BLOB columns
########################################

class Profile(SQLObject):
    image = BLOBCol(default='emptydata', length=65535)

class BLOBColTest(SQLObjectTest):
    classes = [Profile]

    def testBLOBCol(self):
        data = ''.join([chr(x) for x in range(256)])

        prof = Profile()
        prof.image = data
        iid = prof.id

        connection().cache.clear()

        prof2 = Profile.get(iid)
        assert prof2.image == data

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


def main():
    import unittest
    from getopt import getopt, GetoptError

    try:
        options, arguments = getopt(sys.argv[1:], "d:v",
            ["database=", "extra-verbose", "super-verbose",
            "inserts", "coverage"])
    except GetoptError:
        sys.exit("Usage: %s [-d|--database all|type] [-v[v]] [--extra-verbose|--super-verbose] [--inserts] [--coverage]" % sys.argv[0])

    dbs = []
    newArgs = []
    doCoverage = False
    verbose = 0

    for option, value in options:
        if option in ('-d', '--database'):
            dbs.append(value)
        elif option == '--inserts':
            SQLObjectTest.debugInserts = True
        elif option == '--coverage':
            # Handled earlier, so we get better coverage
            doCoverage = True
        elif option == '--extra-verbose':
            verbose = 1
        elif option == '--super-verbose':
            verbose = 2
        elif option == '-v':
            verbose += 1

    if verbose >= 1:
        SQLObjectTest.debugSQL = True
    if verbose >= 2:
        SQLObjectTest.debugOutput = True
        newArgs.append('-vv')
    newArgs.extend(arguments)

    sys.argv = [sys.argv[0]] + newArgs
    if not dbs:
        dbs = ['mysql']
    if dbs == ['all']:
        dbs = supportedDatabases()
    for db in dbs:
        print 'Testing %s' % db
        curr_db = db
        setDatabaseType(db)
        try:
            unittest.main()
        except SystemExit:
            pass
    if doCoverage:
        coverage.stop()
        coverModules()

if __name__ == '__main__':
    main()
