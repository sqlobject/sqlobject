from __future__ import generators

True, False = 1==1, 0==1

import threading
import re
import warnings
import atexit
import os
import new
import SQLBuilder
from Cache import CacheSet
import Col
from Join import sorter
from Converters import sqlrepr

# We set these up as globals, which will be set if we end up
# needing the drivers:
anydbm = None
pickle = None
MySQLdb = None
psycopg = None
pgdb = None
sqlite = None
kinterbasdb = None
Sybase = None

warnings.filterwarnings("ignore", "DB-API extension cursor.lastrowid used")

__all__ = ['MySQLConnection', 'PostgresConnection', 'SQLiteConnection',
           'DBMConnection', 'FirebirdConnection', 'SybaseConnection']

_connections = {}

class DBConnection:

    def __init__(self, name=None, debug=False, debugOutput=False,
                 cache=True, style=None, autoCommit=True):
        if name:
            assert not _connections.has_key(name), 'A database by the name %s has already been created: %s' % (name, _connections[name])
            _connections[name] = self
            self.name = name
        self.debug = debug
        self.debugOutput = debugOutput
        self.cache = CacheSet(cache=cache)
        self.doCache = cache
        self.style = style
        self._connectionNumbers = {}
        self._connectionCount = 1
        self.autoCommit = autoCommit

def connectionForName(name):
    return _connections[name]

class DBAPI(DBConnection):

    """
    Subclass must define a `makeConnection()` method, which
    returns a newly-created connection object.

    ``queryInsertID`` must also be defined.
    """

    dbName = None

    def __init__(self, **kw):
        self._pool = []
        self._poolLock = threading.Lock()
        DBConnection.__init__(self, **kw)

    def _runWithConnection(self, meth, *args):
        conn = self.getConnection()
        try:
            val = meth(conn, *args)
        finally:
            self.releaseConnection(conn)
        return val

    def getConnection(self):
        self._poolLock.acquire()
        try:
            if not self._pool:
                newConn = self.makeConnection()
                self._pool.append(newConn)
                self._connectionNumbers[id(newConn)] = self._connectionCount
                self._connectionCount += 1
            val = self._pool.pop()
            return val
        finally:
            self._poolLock.release()

    def releaseConnection(self, conn):
        if self.supportTransactions:
            if self.autoCommit == 'exception':
                if self.debug:
                    self.printDebug(conn, 'auto/exception', 'ROLLBACK')
                conn.rollback()
                raise Exception, 'Object used outside of a transaction; implicit COMMIT or ROLLBACK not allowed'
            elif self.autoCommit:
                if self.debug:
                    self.printDebug(conn, 'auto', 'COMMIT')
                conn.commit()
            else:
                if self.debug:
                    self.printDebug(conn, 'auto', 'ROLLBACK')
                conn.rollback()
        if self._pool is not None:
            self._pool.append(conn)

    def printDebug(self, conn, s, name, type='query'):
        if type == 'query':
            sep = ': '
        else:
            sep = '->'
            s = repr(s)
        n = self._connectionNumbers[id(conn)]
        spaces = ' '*(8-len(name))
        print '%(n)2i/%(name)s%(spaces)s%(sep)s %(s)s' % locals()

    def _query(self, conn, s):
        if self.debug:
            self.printDebug(conn, s, 'Query')
        conn.cursor().execute(s)

    def query(self, s):
        return self._runWithConnection(self._query, s)

    def _queryAll(self, conn, s):
        if self.debug:
            self.printDebug(conn, s, 'QueryAll')
        c = conn.cursor()
        c.execute(s)
        value = c.fetchall()
        if self.debugOutput:
            self.printDebug(conn, value, 'QueryAll', 'result')
        return value

    def queryAll(self, s):
        return self._runWithConnection(self._queryAll, s)

    def _queryOne(self, conn, s):
        if self.debug:
            self.printDebug(conn, s, 'QueryOne')
        c = conn.cursor()
        c.execute(s)
        value = c.fetchone()
        if self.debugOutput:
            self.printDebug(conn, value, 'QueryOne', 'result')
        return value

    def queryOne(self, s):
        return self._runWithConnection(self._queryOne, s)

    def _insertSQL(self, table, names, values):
        return ("INSERT INTO %s (%s) VALUES (%s)" %
                (table, ', '.join(names),
                 ', '.join([self.sqlrepr(v) for v in values])))

    def transaction(self):
        return Transaction(self)

    def queryInsertID(self, table, idName, id, names, values):
        return self._runWithConnection(self._queryInsertID, table, idName, id, names, values)

    def _iterSelect(self, conn, select, withConnection=None,
                    keepConnection=False):
        cursor = conn.cursor()
        query = self.queryForSelect(select)
        if self.debug:
            self.printDebug(conn, query, 'Select')
        cursor.execute(query)
        while 1:
            result = cursor.fetchone()
            if result is None:
                if not keepConnection:
                    self.releaseConnection(conn)
                break
            if select.ops.get('lazyColumns', 0):
                obj = select.sourceClass(result[0], connection=withConnection)
                yield obj
            else:
                obj = select.sourceClass(result[0], selectResults=result[1:], connection=withConnection)
                yield obj

    def iterSelect(self, select):
        return self._runWithConnection(self._iterSelect, select, self,
                                       False)

    def countSelect(self, select):
        q = "SELECT COUNT(*) FROM %s WHERE" % \
            ", ".join(select.tables)
        q = self._addWhereClause(select, q, limit=0, order=0)
        val = int(self.queryOne(q)[0])
        return val

    def queryForSelect(self, select):
        ops = select.ops
        cls = select.sourceClass
        if ops.get('lazyColumns', 0):
            q = "SELECT %s.%s FROM %s WHERE " % \
                (cls._table, cls._idName,
                 ", ".join(select.tables))
        else:
            q = "SELECT %s.%s, %s FROM %s WHERE " % \
                (cls._table, cls._idName,
                 ", ".join(["%s.%s" % (cls._table, col.dbName)
                            for col in cls._SO_columns]),
                 ", ".join(select.tables))

        return self._addWhereClause(select, q)

    def _addWhereClause(self, select, startSelect, limit=1, order=1):

        q = select.clause
        if type(q) not in [type(''), type(u'')]:
            q = self.sqlrepr(q)
        ops = select.ops

        def clauseList(lst, desc=False):
            if type(lst) not in (type([]), type(())):
                lst = [lst]
            lst = [clauseQuote(i) for i in lst]
            if desc:
                lst = [SQLBuilder.DESC(i) for i in lst]
            return ', '.join([self.sqlrepr(i) for i in lst])

        def clauseQuote(s):
            if type(s) is type(""):
                if s.startswith('-'):
                    desc = True
                    s = s[1:]
                else:
                    desc = False
                assert SQLBuilder.sqlIdentifier(s), "Strings in clauses are expected to be column identifiers.  I got: %r" % s
                if select.sourceClass._SO_columnDict.has_key(s):
                    s = select.sourceClass._SO_columnDict[s].dbName
                if desc:
                    return SQLBuilder.DESC(SQLBuilder.SQLConstant(s))
                else:
                    return SQLBuilder.SQLConstant(s)
            else:
                return s

        if order and ops.get('dbOrderBy'):
            q = "%s ORDER BY %s" % (q, clauseList(ops['dbOrderBy'], ops.get('reversed', False)))

        start = ops.get('start', 0)
        end = ops.get('end', None)

        q = startSelect + ' ' + q

        if limit and (start or end):
            # @@: Raising an error might be an annoyance, but some warning is
            # in order.
            #assert ops.get('orderBy'), "Getting a slice of an unordered set is unpredictable!"
            q = self._queryAddLimitOffset(q, start, end)

        return q

    def _SO_createJoinTable(self, join):
        self.query('CREATE TABLE %s (\n%s %s,\n%s %s\n)' %
                   (join.intermediateTable,
                    join.joinColumn,
                    self.joinSQLType(join),
                    join.otherColumn,
                    self.joinSQLType(join)))

    def _SO_dropJoinTable(self, join):
        self.query("DROP TABLE %s" % join.intermediateTable)

    def createTable(self, soClass):
        self.query('CREATE TABLE %s (\n%s\n)' % \
                   (soClass._table, self.createColumns(soClass)))

    def createColumns(self, soClass):
        columnDefs = [self.createIDColumn(soClass)] \
                     + [self.createColumn(soClass, col)
                        for col in soClass._SO_columns]
        return ",\n".join(["    %s" % c for c in columnDefs])

    def createColumn(self, soClass, col):
        assert 0, "Implement in subclasses"

    def dropTable(self, tableName, cascade=False):
        self.query("DROP TABLE %s" % tableName)

    def clearTable(self, tableName):
        # 3-03 @@: Should this have a WHERE 1 = 1 or similar
        # clause?  In some configurations without the WHERE clause
        # the query won't go through, but maybe we shouldn't override
        # that.
        self.query("DELETE FROM %s" % tableName)

    # The _SO_* series of methods are sorts of "friend" methods
    # with SQLObject.  They grab values from the SQLObject instances
    # or classes freely, but keep the SQLObject class from accessing
    # the database directly.  This way no SQL is actually created
    # in the SQLObject class.

    def _SO_update(self, so, values):
        self.query("UPDATE %s SET %s WHERE %s = %s" %
                   (so._table,
                    ", ".join(["%s = %s" % (dbName, self.sqlrepr(value))
                               for dbName, value in values]),
                    so._idName,
                    self.sqlrepr(so.id)))

    def _SO_selectOne(self, so, columnNames):
        return self.queryOne("SELECT %s FROM %s WHERE %s = %s" %
                             (", ".join(columnNames),
                              so._table,
                              so._idName,
                              self.sqlrepr(so.id)))

    def _SO_selectOneAlt(self, cls, columnNames, column, value):
        return self.queryOne("SELECT %s FROM %s WHERE %s = %s" %
                             (", ".join(columnNames),
                              cls._table,
                              column,
                              self.sqlrepr(value)))

    def _SO_delete(self, so):
        self.query("DELETE FROM %s WHERE %s = %s" %
                   (so._table,
                    so._idName,
                    self.sqlrepr(so.id)))

    def _SO_selectJoin(self, soClass, column, value):
        return self.queryAll("SELECT %s FROM %s WHERE %s = %s" %
                             (soClass._idName,
                              soClass._table,
                              column,
                              self.sqlrepr(value)))

    def _SO_intermediateJoin(self, table, getColumn, joinColumn, value):
        return self.queryAll("SELECT %s FROM %s WHERE %s = %s" %
                             (getColumn,
                              table,
                              joinColumn,
                              self.sqlrepr(value)))

    def _SO_intermediateDelete(self, table, firstColumn, firstValue,
                               secondColumn, secondValue):
        self.query("DELETE FROM %s WHERE %s = %s AND %s = %s" %
                   (table,
                    firstColumn,
                    self.sqlrepr(firstValue),
                    secondColumn,
                    self.sqlrepr(secondValue)))

    def _SO_intermediateInsert(self, table, firstColumn, firstValue,
                               secondColumn, secondValue):
        self.query("INSERT INTO %s (%s, %s) VALUES (%s, %s)" %
                   (table,
                    firstColumn,
                    secondColumn,
                    self.sqlrepr(firstValue),
                    self.sqlrepr(secondValue)))

    def _SO_columnClause(self, soClass, kw):
        return ' '.join(['%s = %s' %
                         (soClass._SO_columnDict[key].dbName,
                          self.sqlrepr(value))
                         for key, value
                         in kw.items()])

    def sqlrepr(self, v):
        return sqlrepr(v, self.dbName)


class Transaction(object):

    def __init__(self, dbConnection):
        self._dbConnection = dbConnection
        self._connection = dbConnection.getConnection()
        self._dbConnection._setAutoCommit(self._connection, 0)
        self.cache = CacheSet(cache=dbConnection.doCache)

    def query(self, s):
        return self._dbConnection._query(self._connection, s)

    def queryAll(self, s):
        return self._dbConnection._queryAll(self._connection, s)

    def queryOne(self, s):
        return self._dbConnection._queryOne(self._connection, s)

    def queryInsertID(self, table, idName, id, names, values):
        return self._dbConnection._queryInsertID(
            self._connection, table, idName, id, names, values)

    def iterSelect(self, select):
        # @@: Bad stuff here, because the connection will be used
        # until the iteration is over, or at least a cursor from
        # the connection, which not all database drivers support.
        return self._dbConnection._iterSelect(
            self._connection, select, withConnection=self,
            keepConnection=True)

    def commit(self):
        if self._dbConnection.debug:
            self._dbConnection.printDebug(self._connection, '', 'COMMIT')
        self._connection.commit()

    def rollback(self):
        if self._dbConnection.debug:
            self._dbConnection.printDebug(self._connection, '', 'ROLLBACK')
        subCaches = [(sub, sub.allIDs()) for sub in self.cache.allSubCaches()]
        self._connection.rollback()

        for subCache, ids in subCaches:
            for id in ids:
                inst = subCache.tryGet(id)
                if inst is not None:
                    inst.expire()

    def __getattr__(self, attr):
        """
        If nothing else works, let the parent connection handle it.
        Except with this transaction as 'self'.  Poor man's
        acquisition?  Bad programming?  Okay, maybe.
        """
        attr = getattr(self._dbConnection, attr)
        try:
            func = attr.im_func
        except AttributeError:
            return attr
        else:
            meth = new.instancemethod(func, self, self.__class__)
            return meth

    def __del__(self):
        self.rollback()
        self._dbConnection.releaseConnection(self._connection)

########################################
## MySQL connection
########################################

class MySQLConnection(DBAPI):

    supportTransactions = False
    dbName = 'mysql'

    def __init__(self, db, user, passwd='', host='localhost', **kw):
        global MySQLdb
        if MySQLdb is None:
            import MySQLdb
        self.host = host
        self.db = db
        self.user = user
        self.passwd = passwd
        DBAPI.__init__(self, **kw)

    def makeConnection(self):
        return MySQLdb.connect(host=self.host, db=self.db,
                               user=self.user, passwd=self.passwd)

    def _queryInsertID(self, conn, table, idName, id, names, values):
        c = conn.cursor()
        if id is not None:
            names = [idName] + names
            values = [id] + values
        q = self._insertSQL(table, names, values)
        if self.debug:
            self.printDebug(conn, q, 'QueryIns')
        c.execute(q)
        if id is None:
            id = c.insert_id()
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    def _queryAddLimitOffset(self, query, start, end):
        if not start:
            return "%s LIMIT %i" % (query, end)
        if not end:
            return "%s LIMIT %i, -1" % (query, start)
        return "%s LIMIT %i, %i" % (query, start, end-start)

    def createColumn(self, soClass, col):
        return col.mysqlCreateSQL()

    def createIDColumn(self, soClass):
        return '%s INT PRIMARY KEY AUTO_INCREMENT' % soClass._idName

    def joinSQLType(self, join):
        return 'INT NOT NULL'

    def tableExists(self, tableName):
        for (table,) in self.queryAll('SHOW TABLES'):
            if table.lower() == tableName.lower():
                return True
        return False

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD COLUMN %s' %
                   (tableName,
                    column.mysqlCreateSQL()))

    def delColumn(self, tableName, column):
        self.query('ALTER TABLE %s DROP COLUMN %s' %
                   (tableName,
                    column.dbName))

    def columnsFromSchema(self, tableName, soClass):
        colData = self.queryAll("SHOW COLUMNS FROM %s"
                                % tableName)
        results = []
        for field, t, nullAllowed, key, default, extra in colData:
            if field == 'id':
                continue
            colClass, kw = self.guessClass(t)
            kw['name'] = soClass._style.dbColumnToPythonAttr(field)
            kw['notNone'] = not nullAllowed
            kw['default'] = default
            # @@ skip key...
            # @@ skip extra...
            results.append(colClass(**kw))
        return results

    def guessClass(self, t):
        if t.startswith('int'):
            return Col.IntCol, {}
        elif t.startswith('varchar'):
            return Col.StringCol, {'length': int(t[8:-1])}
        elif t.startswith('char'):
            return Col.StringCol, {'length': int(t[5:-1]),
                                   'varchar': False}
        elif t.startswith('datetime'):
            return Col.DateTimeCol, {}
        elif t.startswith('bool'):
            return Col.BoolCol, {}
        else:
            return Col.Col, {}

########################################
## Postgres connection
########################################

class PostgresConnection(DBAPI):

    supportTransactions = True
    dbName = 'postgres'

    def __init__(self, dsn=None, host=None, db=None,
                 user=None, passwd=None, autoCommit=1,
                 usePygresql=False,
                 **kw):
        global psycopg, pgdb
        if usePygresql:
            if pgdb is None:
                import pgdb
            self.pgmodule = pgdb
        else:
            if psycopg is None:
                import psycopg
            self.pgmodule = psycopg

        self.autoCommit = autoCommit
        if not autoCommit and not kw.has_key('pool'):
            # Pooling doesn't work with transactions...
            kw['pool'] = 0
        if dsn is None:
            dsn = []
            if db:
                dsn.append('dbname=%s' % db)
            if user:
                dsn.append('user=%s' % user)
            if passwd:
                dsn.append('password=%s' % passwd)
            if host:
                # @@: right format?
                dsn.append('host=%s' % host)
            dsn = ' '.join(dsn)
        self.dsn = dsn
        DBAPI.__init__(self, **kw)

    def _setAutoCommit(self, conn, auto):
        conn.autocommit(auto)

    def makeConnection(self):
        conn = self.pgmodule.connect(self.dsn)
        if self.autoCommit:
            conn.autocommit(1)
        return conn

    def _queryInsertID(self, conn, table, idName, id, names, values):
        c = conn.cursor()
        if id is not None:
            names = [idName] + names
            values = [id] + values
        q = self._insertSQL(table, names, values)
        if self.debug:
            self.printDebug(conn, q, 'QueryIns')
        c.execute(q)
        if id is None:
            c.execute('SELECT %s FROM %s WHERE oid = %s'
                      % (idName, table, c.lastoid()))
            id = c.fetchone()[0]
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    def _queryAddLimitOffset(self, query, start, end):
        if not start:
            return "%s LIMIT %i" % (query, end)
        if not end:
            return "%s OFFSET %i" % (query, start)
        return "%s LIMIT %i OFFSET %i" % (query, end-start, start)

    def createColumn(self, soClass, col):
        return col.postgresCreateSQL()

    def createIDColumn(self, soClass):
        return '%s SERIAL PRIMARY KEY' % soClass._idName

    def dropTable(self, tableName, cascade=False):
        self.query("DROP TABLE %s %s" % (tableName,
                                         cascade and 'CASCADE' or ''))

    def joinSQLType(self, join):
        return 'INT NOT NULL'

    def tableExists(self, tableName):
        # @@: obviously broken
        result = self.queryOne("SELECT COUNT(relname) FROM pg_class WHERE relname = '%s'"
                               % tableName)
        return result[0]

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD COLUMN %s' %
                   (tableName,
                    column.postgresCreateSQL()))

    def delColumn(self, tableName, column):
        self.query('ALTER TABLE %s DROP COLUMN %s' %
                   (tableName,
                    column.dbName))

    def columnsFromSchema(self, tableName, soClass):

        keyQuery = """
        SELECT pg_catalog.pg_get_constraintdef(oid) as condef
        FROM pg_catalog.pg_constraint r
        WHERE r.conrelid = '%s'::regclass AND r.contype = 'f'"""

        colQuery = """
        SELECT a.attname,
        pg_catalog.format_type(a.atttypid, a.atttypmod), a.attnotnull,
        (SELECT substring(d.adsrc for 128) FROM pg_catalog.pg_attrdef d
        WHERE d.adrelid=a.attrelid AND d.adnum = a.attnum)
        FROM pg_catalog.pg_attribute a
        WHERE a.attrelid ='%s'::regclass
        AND a.attnum > 0 AND NOT a.attisdropped
        ORDER BY a.attnum"""

        keyData = self.queryAll(keyQuery % tableName)
        keyRE = re.compile("\((.+)\) REFERENCES (.+)\(")
        keymap = {}
        for (condef,) in keyData:
            match = keyRE.search(condef)
            if match:
                field, reftable = match.groups()
                keymap[field] = reftable.capitalize()
        colData = self.queryAll(colQuery % tableName)
        results = []
        for field, t, notnull, defaultstr in colData:
            if field == 'id':
                continue
            colClass, kw = self.guessClass(t)
            kw['name'] = soClass._style.dbColumnToPythonAttr(field)
            kw['notNone'] = notnull
            if defaultstr is not None:
                kw['default'] = getattr(SQLBuilder.const, defaultstr)
            if keymap.has_key(field):
                kw['foreignKey'] = keymap[field]
            results.append(colClass(**kw))
        return results

    def guessClass(self, t):
        if t.count('int'):
            return Col.IntCol, {}
        elif t.count('varying'):
            return Col.StringCol, {'length': int(t[t.index('(')+1:-1])}
        elif t.startswith('character('):
            return Col.StringCol, {'length': int(t[t.index('(')+1:-1]),
                                   'varchar': False}
        elif t == 'text':
            return Col.StringCol, {}
        elif t.startswith('datetime'):
            return Col.DateTimeCol, {}
        elif t.startswith('bool'):
            return Col.BoolCol, {}
        else:
            return Col.Col, {}


########################################
## SQLite connection
########################################

class SQLiteConnection(DBAPI):

    supportTransactions = True
    dbName = 'sqlite'

    def __init__(self, filename, autoCommit=1, **kw):
        global sqlite
        if sqlite is None:
            import sqlite
        self.filename = filename  # full path to sqlite-db-file
        if not autoCommit and not kw.has_key('pool'):
            # Pooling doesn't work with transactions...
            kw['pool'] = 0
        # use only one connection for sqlite - supports multiple
        # cursors per connection
        self._conn = sqlite.connect(self.filename)
        DBAPI.__init__(self, **kw)

    def _setAutoCommit(self, conn, auto):
        conn.autocommit = auto

    def makeConnection(self):
        return self._conn

    def _queryInsertID(self, conn, table, idName, id, names, values):
        c = conn.cursor()
        if id is not None:
            names = [idName] + names
            values = [id] + values
        q = self._insertSQL(table, names, values)
        if self.debug:
            self.printDebug(conn, q, 'QueryIns')
        c.execute(q)
        # lastrowid is a DB-API extension from "PEP 0249":
        if id is None:
            id = int(c.lastrowid)
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    def _queryAddLimitOffset(self, query, start, end):
        if not start:
            return "%s LIMIT %i" % (query, end)
        if not end:
            return "%s LIMIT 0 OFFSET %i" % (query, start)
        return "%s LIMIT %i OFFSET %i" % (query, end-start, start)

    def createColumn(self, soClass, col):
        return col.sqliteCreateSQL()

    def createIDColumn(self, soClass):
        return '%s INTEGER PRIMARY KEY' % soClass._idName

    def joinSQLType(self, join):
        return 'INT NOT NULL'

    def tableExists(self, tableName):
        result = self.queryOne("SELECT tbl_name FROM sqlite_master WHERE type='table' AND tbl_name = '%s'" % tableName)
        # turn it into a boolean:
        return not not result

########################################
## Sybase connection
########################################

class SybaseConnection(DBAPI):

    supportTransactions = True
    dbName = 'sybase'

    def __init__(self, db, user, passwd='', host='localhost',
                 autoCommit=0, **kw):
        global Sybase
        if Sybase is None:
            import Sybase
            from Sybase import NumericType
            from Converters import registerConverter, IntConverter
            registerConverter(NumericType, IntConverter)
        if not autoCommit and not kw.has_key('pool'):
            # Pooling doesn't work with transactions...
            kw['pool'] = 0
        self.autoCommit=autoCommit
        self.host = host
        self.db = db
        self.user = user
        self.passwd = passwd
        DBAPI.__init__(self, **kw)

    def insert_id(self, conn):
        """
        Sybase adapter/cursor does not support the
        insert_id method.
        """
        c = conn.cursor()
        c.execute('SELECT @@IDENTITY')
        return c.fetchone()[0]

    def makeConnection(self):
        return Sybase.connect(self.host, self.user, self.passwd,
                              database=self.db, auto_commit=self.autoCommit)

    def _queryInsertID(self, conn, table, idName, id, names, values):
        c = conn.cursor()
        if id is not None:
            names = [idName] + names
            values = [id] + values
            c.execute('SET IDENTITY_INSERT %s ON' % table)
        else:
            c.execute('SET IDENTITY_INSERT %s OFF' % table)
        q = self._insertSQL(table, names, values)
        if self.debug:
            print 'QueryIns: %s' % q
        c.execute(q)
        if id is None:
            id = self.insert_id(conn)
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    def _queryAddLimitOffset(self, query, start, end):
        # XXX Sybase doesn't support LIMIT
        return query

    def createColumn(self, soClass, col):
        return col.sybaseCreateSQL()

    def createIDColumn(self, soClass):
        return '%s NUMERIC(18,0) IDENTITY' % soClass._idName

    def joinSQLType(self, join):
        return 'NUMERIC(18,0) NOT NULL'

    SHOW_TABLES="SELECT name FROM sysobjects WHERE type='U'"
    def tableExists(self, tableName):
        for (table,) in self.queryAll(self.SHOW_TABLES):
            if table.lower() == tableName.lower():
                return True
        return False

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD COLUMN %s' %
                   (tableName,
                    column.sybaseCreateSQL()))

    def delColumn(self, tableName, column):
        self.query('ALTER TABLE %s DROP COLUMN %s' %
                   (tableName,
                    column.dbName))

    SHOW_COLUMNS=("select 'column' = COL_NAME(id, colid) "
                  "from syscolumns where id = OBJECT_ID(%s)")
    def columnsFromSchema(self, tableName, soClass):
        colData = self.queryAll(self.SHOW_COLUMNS
                                % tableName)
        results = []
        for field, t, nullAllowed, key, default, extra in colData:
            if field == 'id':
                continue
            colClass, kw = self.guessClass(t)
            kw['name'] = soClass._style.dbColumnToPythonAttr(field)
            kw['notNone'] = not nullAllowed
            kw['default'] = default
            # @@ skip key...
            # @@ skip extra...
            results.append(colClass(**kw))
        return results

    def guessClass(self, t):
        if t.startswith('int'):
            return Col.IntCol, {}
        elif t.startswith('varchar'):
            return Col.StringCol, {'length': int(t[8:-1])}
        elif t.startswith('char'):
            return Col.StringCol, {'length': int(t[5:-1]),
                                   'varchar': False}
        elif t.startswith('datetime'):
            return Col.DateTimeCol, {}
        else:
            return Col.Col, {}

########################################
## Firebird connection
########################################

class FirebirdConnection(DBAPI):

    supportTransactions = False
    dbName = 'firebird'

    def __init__(self, host, db, user='sysdba',
                 passwd='masterkey', autoCommit=1, **kw):
        global kinterbasdb
        if kinterbasdb is None:
            import kinterbasdb

        self.limit_re = re.compile('^\s*(select )(.*)', re.IGNORECASE)

        if not autoCommit and not kw.has_key('pool'):
            # Pooling doesn't work with transactions...
            kw['pool'] = 0

        self.host = host
        self.db = db
        self.user = user
        self.passwd = passwd

        DBAPI.__init__(self, **kw)

    def _runWithConnection(self, meth, *args):
        conn = self.getConnection()
        # @@: Horrible auto-commit implementation.  Just horrible!
        try:
            conn.begin()
        except kinterbasdb.ProgrammingError:
            pass
        try:
            val = meth(conn, *args)
            try:
                conn.commit()
            except kinterbasdb.ProgrammingError:
                pass
        finally:
            self.releaseConnection(conn)
        return val

    def _setAutoCommit(self, conn, auto):
        # Only _runWithConnection does "autocommit", so we don't
        # need to worry about that.
        pass

    def makeConnection(self):
        return kinterbasdb.connect(
            host = self.host, database = self.db,
            user = self.user, password = self.passwd
            )

    def _queryInsertID(self, conn, table, idName, id, names, values):
        """Firebird uses 'generators' to create new ids for a table.
        The users needs to create a generator named GEN_<tablename>
        for each table this method to work."""

        if id is None:
            row = self.queryOne('SELECT gen_id(GEN_%s,1) FROM rdb$database'
                                % table)
            id = row[0]
        names = [idName] + names
        values = [id] + values
        q = self._insertSQL(table, names, values)
        if self.debug:
            self.printDebug(conn, q, 'QueryIns')
        self.query(q)
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    def _queryAddLimitOffset(self, query, start, end):
        """Firebird slaps the limit and offset (actually 'first' and
        'skip', respectively) statement right after the select."""
        if not start:
            limit_str =  "SELECT FIRST %i" % end
        if not end:
            limit_str = "SELECT SKIP %i" % start
        else:
            limit_str = "SELECT FIRST %i SKIP %i" % (end-start, start)

        match = self.limit_re.match(query)
        if match and len(match.groups()) == 2:
            return ' '.join([limit_str, match.group(2)])
        else:
            return query

    def createTable(self, soClass):
        self.query('CREATE TABLE %s (\n%s\n)' % \
                   (soClass._table, self.createColumns(soClass)))
        self.query("CREATE GENERATOR GEN_%s" % soClass._table)

    def createColumn(self, soClass, col):
        return col.firebirdCreateSQL()

    def createIDColumn(self, soClass):
        return '%s INT NOT NULL PRIMARY KEY' % soClass._idName

    def joinSQLType(self, join):
        return 'INT NOT NULL'

    def tableExists(self, tableName):
        # there's something in the database by this name...let's
        # assume it's a table.  By default, fb 1.0 stores EVERYTHING
        # it cares about in uppercase.
        result = self.queryOne("SELECT COUNT(rdb$relation_name) FROM rdb$relations WHERE rdb$relation_name = '%s'"
                               % tableName.upper())
        return result[0]

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD %s' %
                   (tableName,
                    column.firebirdCreateSQL()))

    def dropTable(self, tableName, cascade=False):
        self.query("DROP TABLE %s" % tableName)
        self.query("DROP GENERATOR GEN_%s" % tableName)

    def delColumn(self, tableName, column):
        self.query('ALTER TABLE %s DROP %s' %
                   (tableName,
                    column.dbName))

    def columnsFromSchema(self, tableName, soClass):
        """
        Look at the given table and create Col instances (or
        subclasses of Col) for the fields it finds in that table.
        """

        fieldqry = """\
        SELECT RDB$RELATION_FIELDS.RDB$FIELD_NAME as field,
               RDB$TYPES.RDB$TYPE_NAME as t,
               RDB$FIELDS.RDB$FIELD_LENGTH as flength,
               RDB$FIELDS.RDB$FIELD_SCALE as fscale,
               RDB$RELATION_FIELDS.RDB$NULL_FLAG as nullAllowed,
               RDB$RELATION_FIELDS.RDB$DEFAULT_VALUE as thedefault,
               RDB$FIELDS.RDB$FIELD_SUB_TYPE as blobtype
        FROM RDB$RELATION_FIELDS
        INNER JOIN RDB$FIELDS ON
            (RDB$RELATION_FIELDS.RDB$FIELD_SOURCE = RDB$FIELDS.RDB$FIELD_NAME)
        INNER JOIN RDB$TYPES ON (RDB$FIELDS.RDB$FIELD_TYPE =
                                 RDB$TYPES.RDB$TYPE)
        WHERE
            (RDB$RELATION_FIELDS.RDB$RELATION_NAME = '%s')
            AND (RDB$TYPES.RDB$FIELD_NAME = 'RDB$FIELD_TYPE')"""

        colData = self.queryAll(fieldqry % tableName.upper())
        results = []
        for field, t, flength, fscale, nullAllowed, thedefault, blobType in colData:
            if field == 'id':
                continue
            colClass, kw = self.guessClass(t, flength, fscale)
            kw['name'] = soClass._style.dbColumnToPythonAttr(field)
            kw['notNone'] = not nullAllowed
            kw['default'] = thedefault
            results.append(colClass(**kw))
        return results

    _intTypes=['INT64', 'SHORT','LONG']
    _dateTypes=['DATE','TIME','TIMESTAMP']

    def guessClass(self, t, flength, fscale=None):
        """
        An internal method that tries to figure out what Col subclass
        is appropriate given whatever introspective information is
        available -- both very database-specific.
        """

        if t in self._intTypes:
            return Col.IntCol, {}
        elif t == 'VARYING':
            return Col.StringCol, {'length': flength}
        elif t == 'TEXT':
            return Col.StringCol, {'length': flength,
                                   'varchar': False}
        elif t in self._dateTypes:
            return Col.DateTimeCol, {}
        else:
            return Col.Col, {}

########################################
## File-based connections
########################################

class FileConnection(DBConnection):

    """
    Files connections should deal with setup, and define the
    methods:

    * ``_fetchDict(self, table, id)``
    * ``_saveDict(self, table, id, d)``
    * ``_newID(table)``
    * ``tableExists(table)``
    * ``createTable(soClass)``
    * ``dropTable(table)``
    * ``clearTable(table)``
    * ``_SO_delete(so)``
    * ``_allIDs()``
    * ``_SO_createJoinTable(join)``
    """

    def queryInsertID(self, table, idName, id, names, values):
        if id is None:
            id = self._newID(table)
        self._saveDict(table, id, dict(zip(names, values)))
        return id

    def createColumns(self, soClass):
        pass

    def _SO_update(self, so, values):
        d = self._fetchDict(so._table, so.id)
        for dbName, value in values:
            d[dbName] = value
        self._saveDict(so._table, so.id, d)

    def _SO_selectOne(self, so, columnNames):
        d = self._fetchDict(so._table, so.id)
        return [d[name] for name in columnNames]

    def _SO_selectOneAlt(self, cls, columnNames, column, value):
        for id in self._allIDs(cls._table):
            d = self._fetchDict(cls._table, id)
            if d[column] == value:
                d['id'] = id
                return [d[name] for name in columnNames]

    _createRE = re.compile('CREATE TABLE\s+(IF NOT EXISTS\s+)?([^ ]*)', re.I)
    _dropRE = re.compile('DROP TABLE\s+(IF EXISTS\s+)?([^ ]*)', re.I)

    def query(self, q):
        match = self._createRE.search(q)
        if match:
            if match.group(1) and self.tableExists(match.group(2)):
                return
            class X: pass
            x = X()
            x._table = match.group(2)
            return self.createTable(x)
        match = self._dropRE.search(q)
        if match:
            if match.group(1) and not self.tableExists(match.group(2)):
                return
            return self.dropTable(match.group(2))

    def addColumn(self, tableName, column):
        for id in self._allIDs(tableName):
            d = self._fetchDict(tableName, id)
            d[column.dbName] = None
            self._saveDict(tableName, id, d)

    def delColumn(self, tableName, column):
        for id in self._allIDs(tableName):
            d = self._fetchDict(tableName, id)
            del d[column.dbName]
            self._saveDict(tableName, id, d)

    def _SO_columnClause(self, soClass, kw):
        clauses = []
        for name, value in kw.items():
            clauses.append(getattr(soClass.q, name) == value)
        return SQLBuilder.AND(*clauses)

    def _SO_selectJoin(self, soClass, column, value):
        results = []
        # @@: seems lame I need to do this...
        value = int(value)
        for id in self._allIDs(soClass._table):
            d = self._fetchDict(soClass._table, id)
            if d[column] == value:
                results.append((id,))
        return results

########################################
## DBM connection
########################################

class DBMConnection(FileConnection):

    supportTransactions = False
    dbName = 'dbm'

    def __init__(self, path, **kw):
        global anydbm, pickle
        if anydbm is None:
            import anydbm
        if pickle is None:
            try:
                import cPickle as pickle
            except ImportError:
                import pickle
        self.path = path
        try:
            self._meta = anydbm.open(os.path.join(path, "meta.db"), "w")
        except anydbm.error:
            self._meta = anydbm.open(os.path.join(path, "meta.db"), "c")
        self._tables = {}
        atexit.register(self.close)
        self._closed = 0
        FileConnection.__init__(self, **kw)

    def _newID(self, table):
        id = int(self._meta["%s.id" % table]) + 1
        self._meta["%s.id" % table] = str(id)
        return id

    def _saveDict(self, table, id, d):
        db = self._getDB(table)
        db[str(id)] = pickle.dumps(d)

    def _fetchDict(self, table, id):
        return pickle.loads(self._getDB(table)[str(id)])

    def _getDB(self, table):
        try:
            return self._tables[table]
        except KeyError:
            db = self._openTable(table)
            self._tables[table] = db
            return db

    def close(self):
        if self._closed:
            return
        self._closed = 1
        self._meta.close()
        del self._meta
        for table in self._tables.values():
            table.close()
        del self._tables

    def __del__(self):
        FileConnection.__del__(self)
        self.close()

    def _openTable(self, table):
        try:
            db = anydbm.open(os.path.join(self.path, "%s.db" % table), "w")
        except anydbm.error:
            db = anydbm.open(os.path.join(self.path, "%s.db" % table), "c")
        return db

    def tableExists(self, table):
        return self._meta.has_key("%s.id" % table) \
               or os.path.exists(os.path.join(self.path, table + ".db"))

    def createTable(self, soClass):
        self._meta["%s.id" % soClass._table] = "1"

    def dropTable(self, tableName, cascade=False):
        try:
            del self._meta["%s.id" % tableName]
        except KeyError:
            pass
        self.clearTable(tableName)

    def clearTable(self, tableName):
        if self._tables.has_key(tableName):
            del self._tables[tableName]
        filename = os.path.join(self.path, "%s.db" % tableName)
        if os.path.exists(filename):
            os.unlink(filename)

    def _SO_delete(self, so):
        db = self._getDB(so._table)
        del db[str(so.id)]

    def iterSelect(self, select):
        return DBMSelectResults(self, select)

    def _allIDs(self, tableName):
        return self._getDB(tableName).keys()

    def _SO_createJoinTable(self, join):
        pass

    def _SO_dropJoinTable(self, join):
        os.unlink(os.path.join(self.path, join.intermediateTable + ".db"))

    def _SO_intermediateJoin(self, table, get, join1, id1):
        db = self._openTable(table)
        try:
            results = db[join1 + str(id1)]
        except KeyError:
            return []
        if not results:
            return []
        return [(int(id),) for id in results.split(',')]

    def _SO_intermediateInsert(self, table, join1, id1, join2, id2):
        db = self._openTable(table)
        try:
            results = db[join1 + str(id1)]
        except KeyError:
            results = ""
        if results:
            db[join1 + str(id1)] = results + "," + str(id2)
        else:
            db[join1 + str(id1)] = str(id2)

        try:
            results = db[join2 + str(id2)]
        except KeyError:
            results = ""
        if results:
            db[join2 + str(id2)] = results + "," + str(id1)
        else:
            db[join2 + str(id2)] = str(id1)

    def _SO_intermediateDelete(self, table, join1, id1, join2, id2):
        db = self._openTable(table)
        try:
            results = db[join1 + str(id1)]
        except KeyError:
            results = ""
        results = map(int, results.split(","))
        results.remove(int(id2))
        db[join1 + str(id1)] = ",".join(map(str, results))
        try:
            results = db[join2 + str(id2)]
        except KeyError:
            results = ""
        results = map(int, results.split(","))
        results.remove(int(id1))
        db[join2 + str(id2)] = ",".join(map(str, results))

class DBMSelectResults(object):

    def __init__(self, conn, select):
        self.select = select
        self.conn = conn
        self.tables = select.tables
        self.tableDict = {}
        self._results = None
        for i in range(len(self.tables)):
            self.tableDict[self.tables[i]] = i
        self.comboIter = _iterAllCombinations(
            [self.conn._getDB(table).keys() for table in self.tables])
        if select.ops.get('orderBy'):
            self._maxNext = -1
            results = self.allResults()
            results.sort(sorter(select.ops['orderBy']))
            self._results = results
            if select.ops.get('start'):
                if select.ops.get('end'):
                    self._results = self._results[select.ops['start']:select.ops['end']]
                else:
                    self._results = self._results[select.ops['start']:]
            elif select.ops.get('end'):
                self._results = self._results[:select.ops['end']]
        elif select.ops.get('start'):
            for i in range(select.ops.get('start')):
                self.next()
            if select.ops.get('end'):
                self._maxNext = select.ops['end'] - select.ops['start']
        elif select.ops.get('end'):
            self._maxNext = select.ops['end']
        else:
            self._maxNext = -1

    def next(self):
        if self._results is not None:
            try:
                return self._results.pop(0)
            except IndexError:
                raise StopIteration

        for idList in self.comboIter:
            self.idList = idList
            if SQLBuilder.execute(self.select.clause, self):
                if not self._maxNext:
                    raise StopIteration
                self._maxNext -= 1
                return self.select.sourceClass(int(idList[self.tableDict[self.select.sourceClass._table]]))
        raise StopIteration

    def field(self, table, field):
        return self.conn._fetchDict(table, self.idList[self.tableDict[table]])[field]

    def allResults(self):
        results = []
        while 1:
            try:
                results.append(self.next())
            except StopIteration:
                return results


def _iterAllCombinations(l):
    if len(l) == 1:
        for id in l[0]:
            yield [id]
    else:
        for id in l[0]:
            for idList in _iterAllCombinations(l[1:]):
                yield [id] + idList
