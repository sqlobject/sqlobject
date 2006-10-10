from sqlobject.dbconnection import DBAPI
from sqlobject.col import popKey
from sqlobject.dberrors import *
import thread

sqlite = None
using_sqlite2 = False
sqlite2_Binary = None

class ErrorMessage(str):
    def __new__(cls, e):
        obj = str.__new__(cls, e[0])
        obj.code = None
        obj.module = e.__module__
        obj.exception = e.__class__.__name__
        return obj

class SQLiteConnection(DBAPI):

    supportTransactions = True
    dbName = 'sqlite'
    schemes = [dbName]

    def __init__(self, filename, autoCommit=1, **kw):
        global sqlite
        global using_sqlite2
        if sqlite is None:
            try:
                import sqlite3 as sqlite
                using_sqlite2 = True
            except ImportError:
                try:
                    from pysqlite2 import dbapi2 as sqlite
                    using_sqlite2 = True
                except ImportError:
                    import sqlite
                    using_sqlite2 = False
        self.module = sqlite
        self.filename = filename  # full path to sqlite-db-file
        self._memory = filename == ':memory:'
        if self._memory:
            if not using_sqlite2:
                raise ValueError(
                    "You must use sqlite2 to use in-memory databases")
        # connection options
        opts = {}
        if using_sqlite2:
            if autoCommit:
                opts["isolation_level"] = None
            if 'encoding' in kw:
                import warnings
                warnings.warn(DeprecationWarning("pysqlite2 does not support the encoding option"))
            opts["detect_types"] = sqlite.PARSE_DECLTYPES
            for col_type in "text", "char", "varchar":
                sqlite.register_converter(col_type, stop_pysqlite2_converting_strings_to_unicode)
                sqlite.register_converter(col_type.upper(), stop_pysqlite2_converting_strings_to_unicode)
            try:
                from sqlite import encode, decode
            except ImportError:
                import base64
                sqlite.encode = base64.encodestring
                sqlite.decode = base64.decodestring
            else:
                sqlite.encode = encode
                sqlite.decode = decode
            global sqlite2_Binary
            if sqlite2_Binary is None:
                sqlite2_Binary = sqlite.Binary
                sqlite.Binary = lambda s: sqlite2_Binary(sqlite.encode(s))
            if 'factory' in kw:
                factory = popKey(kw, 'factory')
                if isinstance(factory, str):
                    factory = globals()[factory]
                opts['factory'] = factory(sqlite)
        else:
            opts['autocommit'] = bool(autoCommit)
            if 'encoding' in kw:
                opts['encoding'] = popKey(kw, 'encoding')
            if 'mode' in kw:
                opts['mode'] = int(popKey(kw, 'mode'), 0)
        if 'timeout' in kw:
            if using_sqlite2:
                opts['timeout'] = float(popKey(kw, 'timeout'))
            else:
                opts['timeout'] = int(float(popKey(kw, 'timeout')) * 1000)
        if 'check_same_thread' in kw:
            opts["check_same_thread"] = bool(popKey(kw, 'check_same_thread'))
        # use only one connection for sqlite - supports multiple)
        # cursors per connection
        self._connOptions = opts
        DBAPI.__init__(self, **kw)
        self._threadPool = {}
        self._threadOrigination = {}
        if self._memory:
            self._memoryConn = sqlite.connect(
                self.filename, **self._connOptions)

    def connectionFromURI(cls, uri):
        user, password, host, port, path, args = cls._parseURI(uri)
        assert host is None, (
            "SQLite can only be used locally (with a URI like "
            "sqlite:///file or sqlite:/file, not %r)" % uri)
        assert user is None and password is None, (
            "You may not provide usernames or passwords for SQLite "
            "databases")
        if path == "/:memory:":
            path = ":memory:"
        return cls(filename=path, **args)
    connectionFromURI = classmethod(connectionFromURI)

    def uri(self):
        return 'sqlite:///%s' % self.filename

    def getConnection(self):
        # SQLite can't share connections between threads, and so can't
        # pool connections.  Since we are isolating threads here, we
        # don't have to worry about locking as much.
        if self._memory:
            conn = self.makeConnection()
            self._connectionNumbers[id(conn)] = self._connectionCount
            self._connectionCount += 1
            return conn
        threadid = thread.get_ident()
        if (self._pool is not None
            and self._threadPool.has_key(threadid)):
            conn = self._threadPool[threadid]
            del self._threadPool[threadid]
            if conn in self._pool:
                self._pool.remove(conn)
        else:
            conn = self.makeConnection()
            if self._pool is not None:
                self._threadOrigination[id(conn)] = threadid
            self._connectionNumbers[id(conn)] = self._connectionCount
            self._connectionCount += 1
        if self.debug:
            s = 'ACQUIRE'
            if self._pool is not None:
                s += ' pool=[%s]' % ', '.join([str(self._connectionNumbers[id(v)]) for v in self._pool])
            self.printDebug(conn, s, 'Pool')
        return conn

    def releaseConnection(self, conn, explicit=False):
        if self._memory:
            return
        threadid = self._threadOrigination.get(id(conn))
        DBAPI.releaseConnection(self, conn, explicit=explicit)
        if (self._pool is not None and threadid
            and not self._threadPool.has_key(threadid)):
            self._threadPool[threadid] = conn
        else:
            if self._pool and conn in self._pool:
                self._pool.remove(conn)
            conn.close()

    def _setAutoCommit(self, conn, auto):
        if using_sqlite2:
            if auto:
                conn.isolation_level = None
            else:
                conn.isolation_level = ""
        else:
            conn.autocommit = auto

    def _setIsolationLevel(self, conn, level):
        if not using_sqlite2:
            return
        conn.isolation_level = level

    def makeConnection(self):
        if self._memory:
            return self._memoryConn
        return sqlite.connect(self.filename, **self._connOptions)

    def _executeRetry(self, conn, cursor, query):
        if self.debug:
            self.printDebug(conn, query, 'QueryR')
        try:
            return cursor.execute(query)
        except self.module.OperationalError, e:
            raise OperationalError(ErrorMessage(e))
        except self.module.IntegrityError, e:
            msg = ErrorMessage(e)
            if msg.startswith('column') and msg.endswith('not unique'):
                raise DuplicateEntryError(msg)
            else:
                raise IntegrityError(msg)
        except self.module.InternalError, e:
            raise InternalError(ErrorMessage(e))
        except self.module.ProgrammingError, e:
            raise ProgrammingError(ErrorMessage(e))
        except self.module.DataError, e:
            raise DataError(ErrorMessage(e))
        except self.module.NotSupportedError, e:
            raise NotSupportedError(ErrorMessage(e))
        except self.module.DatabaseError, e:
            raise DatabaseError(ErrorMessage(e))
        except self.module.InterfaceError, e:
            raise InterfaceError(ErrorMessage(e))
        except self.module.Warning, e:
            raise Warning(ErrorMessage(e))
        except self.module.Error, e:
            raise Error(ErrorMessage(e))

    def _queryInsertID(self, conn, soInstance, id, names, values):
        table = soInstance.sqlmeta.table
        idName = soInstance.sqlmeta.idName
        c = conn.cursor()
        if id is not None:
            names = [idName] + names
            values = [id] + values
        q = self._insertSQL(table, names, values)
        if self.debug:
            self.printDebug(conn, q, 'QueryIns')
        self._executeRetry(conn, c, q)
        # lastrowid is a DB-API extension from "PEP 0249":
        if id is None:
            id = int(c.lastrowid)
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    def _insertSQL(self, table, names, values):
        if not names:
            assert not values
            # INSERT INTO table () VALUES () isn't allowed in
            # SQLite (though it is in other databases)
            return ("INSERT INTO %s VALUES (NULL)" % table)
        else:
            return DBAPI._insertSQL(self, table, names, values)

    def _queryAddLimitOffset(self, query, start, end):
        if not start:
            return "%s LIMIT %i" % (query, end)
        if not end:
            return "%s LIMIT 0 OFFSET %i" % (query, start)
        return "%s LIMIT %i OFFSET %i" % (query, end-start, start)

    def createColumn(self, soClass, col):
        return col.sqliteCreateSQL()

    def createReferenceConstraint(self, soClass, col):
        return None

    def createIDColumn(self, soClass):
        key_type = {int: "INTEGER", str: "TEXT"}[soClass.sqlmeta.idType]
        return '%s %s PRIMARY KEY' % (soClass.sqlmeta.idName, key_type)

    def joinSQLType(self, join):
        return 'INT NOT NULL'

    def tableExists(self, tableName):
        result = self.queryOne("SELECT tbl_name FROM sqlite_master WHERE type='table' AND tbl_name = '%s'" % tableName)
        # turn it into a boolean:
        return not not result

    def createIndexSQL(self, soClass, index):
        return index.sqliteCreateIndexSQL(soClass)

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD COLUMN %s' %
                   (tableName,
                    column.sqliteCreateSQL()))

    def delColumn(self, tableName, column):
        pass # Oops! There is no DROP COLUMN in SQLite

def stop_pysqlite2_converting_strings_to_unicode(s):
    return s
