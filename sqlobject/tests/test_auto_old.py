from datetime import datetime
now = datetime.now

from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject import classregistry

########################################
## Auto class generation
########################################

class TestAuto:

    mysqlCreate = """
    CREATE TABLE IF NOT EXISTS old_auto_test (
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
    CREATE TABLE old_auto_test (
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

    sqliteCreate = """
    CREATE TABLE old_auto_test (
      auto_id INTEGER PRIMARY KEY AUTOINCREMENT ,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT NULL,
      created DATETIME NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL,
      long_field TEXT,
      wannahavefun INT DEFAULT 0 NOT NULL
    )
    """

    sybaseCreate = """
    CREATE TABLE old_auto_test (
      auto_id integer,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT 0,
      created VARCHAR(40) NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL,
      long_field TEXT
    )
    """

    mssqlCreate = """
    CREATE TABLE old_auto_test (
      auto_id int IDENTITY(1,1) primary key,
      first_name VARCHAR(100),
      last_name VARCHAR(200) NOT NULL,
      age INT DEFAULT 0,
      created VARCHAR(40) NOT NULL,
      happy char(1) DEFAULT 'Y' NOT NULL,
      long_field TEXT,
      wannahavefun BIT default(0) NOT NULL
    )
    """

    mysqlDrop = """
    DROP TABLE IF EXISTS old_auto_test
    """

    postgresDrop = """
    DROP TABLE old_auto_test
    """

    sqliteDrop = sybaseDrop = mssqlDrop = postgresDrop

    def setup_method(self, meth):
        conn = getConnection()
        dbName = conn.dbName
        creator = getattr(self, dbName + 'Create', None)
        if creator:
            conn.query(creator)

    def teardown_method(self, meth):
        conn = getConnection()
        dbName = conn.dbName
        dropper = getattr(self, dbName + 'Drop', None)
        if dropper:
            conn.query(dropper)

    def test_classCreate(self):
        class OldAutoTest(SQLObject):
            _connection = getConnection()
            class sqlmeta(sqlmeta):
                idName = 'auto_id'
                fromDatabase = True
        john = OldAutoTest(firstName='john',
                           lastName='doe',
                           age=10,
                           created=now(),
                           wannahavefun=False,
                           longField='x'*1000)
        jane = OldAutoTest(firstName='jane',
                           lastName='doe',
                           happy='N',
                           created=now(),
                           wannahavefun=True,
                           longField='x'*1000)
        assert not john.wannahavefun
        assert jane.wannahavefun
        assert john.longField == 'x'*1000
        assert jane.longField == 'x'*1000
        del classregistry.registry(
            OldAutoTest.sqlmeta.registry).classes['OldAutoTest']

teardown_module()
