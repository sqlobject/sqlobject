import unittest
from SQLObject import *

True, False = 1==1, 0==1

def mysqlConnection():
    SQLObjectTest.supportDynamic = True
    SQLObjectTest.supportAuto = True
    # @@: MySQL *should* support this, but it appears not to
    # care when you assign incorrect to an ENUM...
    SQLObjectTest.supportRestrictedEnum = False
    # Technically it does, but now how we're using it:
    SQLObjectTest.supportTransactions = False
    return MySQLConnection(host='localhost',
                           db='test',
                           user='test',
                           passwd='',
                           debug=0)

def dbmConnection():
    SQLObjectTest.supportDynamic = True
    SQLObjectTest.supportAuto = False
    SQLObjectTest.supportRestrictedEnum = False
    SQLObjectTest.supportTransactions = False
    return DBMConnection('data')

def postgresConnection():
    SQLObjectTest.supportDynamic = True
    SQLObjectTest.supportAuto = True
    SQLObjectTest.supportRestrictedEnum = True
    SQLObjectTest.supportTransactions = True
    return PostgresConnection(db='test')

def pygresConnection():
    SQLObjectTest.supportDynamic = True
    SQLObjectTest.supportAuto = True
    SQLObjectTest.supportRestrictedEnum = True
    SQLObjectTest.supportTransactions = True
    return PostgresConnection(db='test', usePygresql=True)

def sqliteConnection():
    SQLObjectTest.supportDynamic = False
    SQLObjectTest.supportAuto = False
    SQLObjectTest.supportRestrictedEnum = False
    SQLObjectTest.supportTransactions = True
    return SQLiteConnection('data/sqlite.data')


def sybaseConnection():
    SQLObjectTest.supportDynamic = False
    SQLObjectTest.supportAuto = False
    SQLObjectTest.supportRestrictedEnum = False
    SQLObjectTest.supportTransactions = True
    return SybaseConnection(host='localhost',
                            db='test',
                            user='sa',
                            passwd='sybasesa',
                            autoCommit=1)

def firebirdConnection():
    SQLObjectTest.supportDynamic = True
    SQLObjectTest.supportAuto = False
    SQLObjectTest.supportRestrictedEnum = True
    SQLObjectTest.supportTransactions = True
    return FirebirdConnection('localhost', '/var/lib/firebird/data/test.gdb',
                              user='sysdba', passwd='masterkey')


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
        if self.debugSQL:
            print
            print '#' * 70
        unittest.TestCase.setUp(self)
        if self.debugInserts:
            __connection__.debug = True
            __connection__.debugOuput = self.debugOutput

        for c in self.classes:
            c._connection = __connection__
        for c in self.classes + [self]:
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
        for c in self.classes:
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
