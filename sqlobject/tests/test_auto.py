from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject import classregistry
    
########################################
## Dynamic column tests
########################################

class Person(SQLObject):

    _columns = [StringCol('name', length=100, dbName='name_col')]
    _defaultOrder = 'name'

class Phone(SQLObject):

    _columns = [StringCol('phone', length=12)]
    _defaultOrder = 'phone'

class TestPeople:

    def setup_method(self, meth):
        setupClass(Person)
        setupClass(Phone)
        for n in ['jane', 'tim', 'bob', 'jake']:
            Person(name=n)
        for p in ['555-555-5555', '555-394-2930',
                  '444-382-4854']:
            Phone(phone=p)

    def test_defaultOrder(self):
        assert (list(Person.select('all')) ==
                list(Person.select('all', orderBy=Person._defaultOrder)))

    def test_dynamicColumn(self):
        if not supports('dynamicColumn'):
            return
        nickname = StringCol('nickname', length=10)
        Person.addColumn(nickname, changeSchema=True)
        n = Person(name='robert', nickname='bob')
        assert ([p.name for p in Person.select('all')]
                == ['bob', 'jake', 'jane', 'robert', 'tim'])
        Person.delColumn(nickname, changeSchema=True)

    def test_dynamicJoin(self):
        if not supports('dynamicColumn'):
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
        assert l == ['555-394-2930', '555-555-5555']
        Phone.delColumn(col, changeSchema=True)
        Person.delJoin(join)

########################################
## Auto class generation
########################################

class TestAuto:

    mysqlCreate = """
    CREATE TABLE IF NOT EXISTS auto_test (
      auto_id INT AUTO_INCREMENT PRIMARY KEY,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT NULL,
      created DATETIME NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL,
      long_field TEXT,
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
      long_field TEXT,
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
      happy char(1) DEFAULT 'Y' NOT NULL,
      long_field TEXT
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

    def test_classCreate(self):
        if not supports('fromDatabase'):
            return
        class AutoTest(SQLObject):
            _fromDatabase = True
            _idName = 'auto_id'
            _connection = connection()
        john = AutoTest(firstName='john',
                        lastName='doe',
                        age=10,
                        created=now(),
                        wannahavefun=False,
                        long_field='x'*1000)
        jane = AutoTest(firstName='jane',
                        lastName='doe',
                        happy='N',
                        created=now(),
                        wannahavefun=True,
                        long_field='x'*1000)
        assert not john.wannahavefun
        assert jane.wannahavefun
        assert john.long_field == 'x'*1000
        assert jane.long_field == 'x'*1000
        del classregistry.registry(AutoTest._registry).classes['AutoTest']
