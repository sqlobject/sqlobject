import unittest
from sqlobject import *
import os

True, False = 1==1, 0==1

def mysqlConnection():
    SQLObjectTest.supportDynamic = True
    SQLObjectTest.supportAuto = True
    # @@: MySQL *should* support this, but it appears not to
    # care when you assign incorrect to an ENUM...
    SQLObjectTest.supportRestrictedEnum = False
    # Technically it does, but now how we're using it:
    SQLObjectTest.supportTransactions = False
    return 'mysql://test@localhost/test'

def dbmConnection():
    SQLObjectTest.supportDynamic = True
    SQLObjectTest.supportAuto = False
    SQLObjectTest.supportRestrictedEnum = False
    SQLObjectTest.supportTransactions = False
    return 'dbm:///data'

def postgresConnection():
    SQLObjectTest.supportDynamic = True
    SQLObjectTest.supportAuto = True
    SQLObjectTest.supportRestrictedEnum = True
    SQLObjectTest.supportTransactions = True
    return 'postgres:///test'

def pygresConnection():
    SQLObjectTest.supportDynamic = True
    SQLObjectTest.supportAuto = True
    SQLObjectTest.supportRestrictedEnum = True
    SQLObjectTest.supportTransactions = True
    return 'pygresql://localhost/test'

def sqliteConnection():
    SQLObjectTest.supportDynamic = False
    SQLObjectTest.supportAuto = False
    SQLObjectTest.supportRestrictedEnum = False
    SQLObjectTest.supportTransactions = True
    return 'sqlite:///%s/data/sqlite.data' % os.getcwd()

def sybaseConnection():
    SQLObjectTest.supportDynamic = False
    SQLObjectTest.supportAuto = False
    SQLObjectTest.supportRestrictedEnum = False
    SQLObjectTest.supportTransactions = False
    return 'sybase://test:test123@sybase/test?autoCommit=0'

def firebirdConnection():
    SQLObjectTest.supportDynamic = True
    SQLObjectTest.supportAuto = False
    SQLObjectTest.supportRestrictedEnum = True
    SQLObjectTest.supportTransactions = True
    return 'firebird://sysdba:masterkey@localhost/var/lib/firebird/data/test.gdb'

_supportedDatabases = {
    'mysql': 'MySQLdb',
    'postgres': 'psycopg',
    'sqlite': 'sqlite',
    'sybase': 'Sybase',
    'firebird': 'kinterbasdb',
    }

def supportedDatabases():
    result = []
    for name, module in _supportedDatabases.items():
        try:
            exec 'import %s' % module
        except ImportError:
            pass
        else:
            result.append(name)
    return result

class SQLObjectTest(unittest.TestCase):

    classes = []

    debugSQL = False
    debugOutput = False
    debugInserts = False

    databaseName = None

    def setUp(self):
        global __connection__
        if isinstance(__connection__, str):
            __connection__ = connectionForURI(__connection__)
        if self.debugSQL:
            print
            print '#' * 70
        unittest.TestCase.setUp(self)
        if self.debugInserts:
            __connection__.debug = True
            __connection__.debugOuput = self.debugOutput

        classes = self.classes[:] + [self]
        r_classes = classes[:]
        r_classes.reverse()
        for c in classes:
            c._connection = __connection__
        for c in r_classes:
            if hasattr(c, '%sDrop' % self.databaseName):
                if __connection__.tableExists(c._table):
                    sql = getattr(c, '%sDrop' % self.databaseName)
                    #if self.debugInserts:
                    #    print sql
                    __connection__.query(sql)

            elif hasattr(c, 'drop'):
                __connection__.query(c.drop)
            elif hasattr(c, 'dropTable'):
                c.dropTable(ifExists=True, cascade=True)

        for c in classes:
            if hasattr(c, '%sCreate' % self.databaseName):
                if not __connection__.tableExists(c._table):
                    sql = getattr(c, '%sCreate' % self.databaseName)
                    #if self.debugInserts:
                    #    print sql
                    __connection__.query(sql)

            elif hasattr(c, 'create'):
                __connection__.query(c.create)
            elif hasattr(c, 'createTable'):
                c.createTable(ifNotExists=True)
        self.inserts()
        __connection__.debug = self.debugSQL
        __connection__.debugOutput = self.debugOutput

    def inserts(self):
        pass

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        __connection__.debug = 0
        classes = self.classes[:]
        classes.reverse()
        for c in classes:
            if hasattr(c, 'drop'):
                __connection__.query(c.drop)

def setDatabaseType(t):
    global __connection__
    try:
        conn = globals()[t + "Connection"]()
    except KeyError:
        raise KeyError, 'No connection by the type %s is known' % t
    SQLObjectTest.databaseName = t
    __connection__ = conn

def connection():
    return __connection__

__all__ = ['SQLObjectTest', 'setDatabaseType', 'connection',
           'supportedDatabases']
