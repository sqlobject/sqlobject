"""
The framework for making database tests.
"""

import os
import re
import sqlobject
from py.test import raises

connectionShortcuts = {
    'mysql': 'mysql://test@localhost/test',
    'dbm': 'dbm:///data',
    'postgres': 'postgres:///test',
    'postgresql': 'postgres:///test',
    'pygresql': 'pygresql://localhost/test',
    'sqlite': 'sqlite:///%s/data/sqlite.data' % os.getcwd(),
    'sybase': 'sybase://test:test123@sybase/test?autoCommit=0',
    'firebird': 'firebird://sysdba:masterkey@localhost/var/lib/firebird/data/test.gdb',
    }

"""
supportsMatrix defines what database backends support what features.
Each feature has a name, if you see a key like '+featureName' then
only the databases listed support the feature.  Conversely,
'-featureName' means all databases *except* the ones listed support
the feature.  The databases are given by their SQLObject string name,
separated by spaces.

The function supports(featureName) returns True or False based on this,
and you can use it like::

    def test_featureX():
        if not supports('featureX'):
            return
"""
supportsMatrix = {
    '+restrictedEnum': 'postgres',
    '-transactions': 'mysql',
    '-dropTableCascade': 'sybase',
    '-dynamicColumn': 'sqlite sybase',
    '-fromDatabase': 'sqlite sybase firebird',
    '-expressionIndex': 'mysql sqlite firebird',
    }


def setupClass(soClasses):
    """
    Makes sure the classes have a corresponding and correct table.
    This won't recreate the table if it already exists.  It will check
    that the table is properly defined (in case you change your table
    definition).

    You can provide a single class or a list of classes; if a list
    then classes will be created in the order you provide, and
    destroyed in the opposite order.  So if class A depends on class
    B, then do setupClass([B, A]) and B won't be destroyed or cleared
    until after A is destroyed or cleared.
    """
    if not isinstance(soClasses, (list, tuple)):
        soClasses = [soClasses]
    connection = getConnection()
    for soClass in soClasses:
        soClass._connection = connection
    installOrClear(soClasses)
    return soClasses

installedDBFilename = os.path.join(os.getcwd(), 'dbs_data.tmp')

installedDBTracker = sqlobject.connectionForURI(
    'sqlite:///' + installedDBFilename)

def getConnection():
    name = os.environ.get('TESTDB')
    assert name, 'You must set $TESTDB to do database operations'
    if connectionShortcuts.has_key(name):
        name = connectionShortcuts[name]
    return sqlobject.connectionForURI(name)

connection = getConnection()

class InstalledTestDatabase(sqlobject.SQLObject):
    """
    This table is set up in SQLite (always, regardless of $TESTDB) and
    tracks what tables have been set up in the 'real' database.  This
    way we don't keep recreating the tables over and over when there
    are multiple tests that use a table.
    """

    _connection = installedDBTracker
    tableName = sqlobject.StringCol(notNull=True)
    createSQL = sqlobject.StringCol(notNull=True)
    connectionURI = sqlobject.StringCol(notNull=True)

    def installOrClear(cls, soClasses):
        cls.setup()
        reversed = list(soClasses)[:]
        reversed.reverse()
        for soClass in reversed:
            table = soClass._table
            if not soClass._connection.tableExists(table):
                continue
            items = list(cls.selectBy(
                tableName=table,
                connectionURI=soClass._connection.uri()))
            if items:
                instance = items[0]
                sql = instance.createSQL
            else:
                sql = None
            newSQL = soClass.createTableSQL()
            if sql != newSQL:
                if sql is not None:
                    instance.destroySelf()
                cls.drop(soClass)
            else:
                cls.clear(soClass)
        for soClass in soClasses:
            table = soClass._table
            if not soClass._connection.tableExists(table):
                cls.install(soClass)
    installOrClear = classmethod(installOrClear)

    def install(cls, soClass):
        """
        Creates the given table in its database.
        """
        sql = getattr(soClass, soClass._connection.dbName + 'Create',
                      None)
        if sql:
            soClass._connection.query(sql)
        else:
            sql = soClass.createTableSQL()
            soClass.createTable()
        cls(tableName=soClass._table,
            createSQL=sql,
            connectionURI=soClass._connection.uri())
    install = classmethod(install)

    def drop(cls, soClass):
        """
        Drops a the given table from its database
        """
        sql = getattr(soClass, soClass._connection.dbName + 'Drop', None)
        if sql:
            soClass._connection.query(sql)
        else:
            soClass.dropTable()
    drop = classmethod(drop)

    def clear(cls, soClass):
        """
        Removes all the rows from a table.
        """
        soClass.clearTable()
    clear = classmethod(clear)

    def setup(cls):
        """
        This sets up *this* table.
        """
        if not cls._connection.tableExists(cls._table):
            cls.createTable()
    setup = classmethod(setup)

installOrClear = InstalledTestDatabase.installOrClear

class Dummy(object):

    """
    Used for creating fake objects; a really poor 'mock object'.
    """

    def __init__(self, **kw):
        for name, value in kw.items():
            setattr(self, name, value)
        
def d(**kw):
    """
    Because dict(**kw) doesn't work in Python 2.2, this is a
    replacement.
    """
    return kw

def inserts(cls, data, schema=None):
    """
    Creates a bunch of rows.  You can use it like::

        inserts(Person, [{'fname': 'blah', 'lname': 'doe'}, ...])

    Or::

        inserts(Person, [('blah', 'doe')], schema=
                ['fname', 'lname'])

    If you give a single string for the `schema` then it'll split
    that string to get the list of column names.
    """
    if schema:
        if isinstance(schema, str):
            schema = schema.split()
        keywordData = []
        for item in data:
            itemDict = {}
            for name, value in zip(schema, item):
                itemDict[name] = value
            keywordData.append(itemDict)
        data = keywordData
    results = []
    for args in data:
        results.append(cls(**args))
    return results

def supports(feature):
    dbName = connection.dbName
    support = supportsMatrix.get('+' + feature, None)
    notSupport = supportsMatrix.get('-' + feature, None)
    if support is not None and dbName in support.split():
        return True
    else:
        return False
    if notSupport is not None and dbName in notSupport.split():
        return False
    else:
        return True
    assert notSupport is not None or support is not None, (
        "The supportMatrix does not list this feature: %r"
        % feature)

# To avoid name clashes:
_inserts = inserts

__all__ = ['getConnection', 'setupClass', 'Dummy', 'raises',
           'd', 'inserts', 'supports']
