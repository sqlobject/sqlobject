from sqlobject.dbconnection import DBAPI
sqlite = None

class SQLiteConnection(DBAPI):

    supportTransactions = True
    dbName = 'sqlite'
    schemes = [dbName]

    def __init__(self, filename, autoCommit=1, **kw):
        global sqlite
        if sqlite is None:
            import sqlite
        self.module = sqlite
        self.filename = filename  # full path to sqlite-db-file
        if not autoCommit and not kw.has_key('pool'):
            # Pooling doesn't work with transactions...
            kw['pool'] = 0
        # use only one connection for sqlite - supports multiple
        # cursors per connection
        self._conn = sqlite.connect(self.filename)
        DBAPI.__init__(self, **kw)

    def connectionFromURI(cls, uri):
        user, password, host, path, args = cls._parseURI(uri)
        assert host is None, "SQLite can only be used locally (with a URI like sqlite:///file or sql:/file, not %r)" % uri
        assert user is None and password is None, "You may not provide usernames or passwords for SQLite databases"
        return cls(filename=path, **args)
    connectionFromURI = classmethod(connectionFromURI)

    def _setAutoCommit(self, conn, auto):
        conn.autocommit = auto

    def makeConnection(self):
        return self._conn

    def _queryInsertID(self, conn, soInstance, id, names, values):
        table = soInstance._table
        idName = soInstance._idName
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

    def createIndexSQL(self, soClass, index):
        return index.sqliteCreateIndexSQL(soClass)
