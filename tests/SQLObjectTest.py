import unittest
from sqlobject import *
import os

True, False = 1==1, 0==1

def d(**kw): return kw

defaultOptions = d(
    # Add columns at runtime
    supportDynamic=True,
    # Automatically detect the columns
    supportAuto=True,
    # ENUM() columns that complain if you mis-assign
    supportRestrictedEnum=True,
    # Transcations, of course:
    supportTransactions=True,
    # If you can index on expressions
    supportExpressionIndex=True,
    )

def mysqlConnection():
    return 'mysql://test@localhost/test', d(
        # @@: MySQL *should* support this, but it appears not to
        # care when you assign incorrect to an ENUM...
        supportRestrictedEnum=False,
        # Technically it does, but not how we're using it:
        supportTransactions=False,
        supportExpressionIndex=False)

def postgresConnection():
    return 'postgres:///test', d()

def pygresConnection():
    return 'pygresql://localhost/test', d()

def sqliteConnection():
    SQLObjectTest.supportTransactions = True
    return 'sqlite:///%s/data/sqlite.data' % os.getcwd(), d(
        supportDynamic=False,
        supportAuto=False,
        supportRestrictedEnum=False,
        supportExpressionIndex=False)

def sybaseConnection():
    return 'sybase://test:test123@sybase/test?autoCommit=0', d(
        # This seems awfully pessimistic:
        supportDynamic=False,
        supportAuto=False,
        supportRestrictedEnum=False)

def firebirdConnection():
    return 'firebird://sysdba:masterkey@localhost/var/lib/firebird/data/test.gdb', d(
        supportAuto=False,
        supportExpressionIndex=False)


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

    requireSupport = ()

    def hasSupport(self):
        for attr in self.requireSupport:
            if not getattr(self, attr):
                return False
        return True

    def setUp(self):
        global __connection__
        if isinstance(__connection__, str):
            __connection__ = connectionForURI(__connection__)
        if self.debugSQL:
            print
            print '#' * 70
        unittest.TestCase.setUp(self)
        if not self.hasSupport():
            return
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
        if not self.hasSupport():
            return
        __connection__.debug = 0
        classes = self.classes[:]
        classes.reverse()
        for c in classes:
            if hasattr(c, 'drop'):
                __connection__.query(c.drop)

def setDatabaseType(t):
    global __connection__
    try:
        conn, ops = globals()[t + "Connection"]()
        default = defaultOptions.copy()
        default.update(ops)
        ops = default
        for name, value in ops.items():
            setattr(SQLObjectTest, name, value)
        
    except KeyError:
        raise KeyError, 'No connection by the type %s is known' % t
    SQLObjectTest.databaseName = t
    __connection__ = conn

def connection():
    return __connection__

__all__ = ['SQLObjectTest', 'setDatabaseType', 'connection',
           'supportedDatabases']
