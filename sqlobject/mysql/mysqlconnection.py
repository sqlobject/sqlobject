from sqlobject.dbconnection import DBAPI
from sqlobject import col
MySQLdb = None

class MySQLConnection(DBAPI):

    supportTransactions = False
    dbName = 'mysql'
    schemes = [dbName]

    def __init__(self, db, user, passwd='', host='localhost', **kw):
        global MySQLdb
        if MySQLdb is None:
            import MySQLdb
        self.module = MySQLdb
        self.host = host
        self.db = db
        self.user = user
        self.password = passwd
        DBAPI.__init__(self, **kw)

    def connectionFromURI(cls, uri):
        user, password, host, path, args = cls._parseURI(uri)
        return cls(db=path.strip('/'), user=user or '', passwd=password or '',
                   host=host or 'localhost', **args)
    connectionFromURI = classmethod(connectionFromURI)

    def makeConnection(self):
        return MySQLdb.connect(host=self.host, db=self.db,
                               user=self.user, passwd=self.password)

    def _executeRetry(self, conn, cursor, query):
        while 1:
            try:
                return cursor.execute(query)
            except MySQLdb.OperationalError, e:
                if e.args[0] == 2013: # SERVER_LOST error
                    if self.debug:
                        self.printDebug(conn, str(e), 'ERROR')
                else:
                    raise

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
        self._executeRetry(conn, c, q)
        if id is None:
            id = c.lastrowid
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

    def createIndexSQL(self, soClass, index):
        return index.mysqlCreateIndexSQL(soClass)

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
            return col.IntCol, {}
        elif t.startswith('varchar'):
            return col.StringCol, {'length': int(t[8:-1])}
        elif t.startswith('char'):
            return col.StringCol, {'length': int(t[5:-1]),
                                   'varchar': False}
        elif t.startswith('datetime'):
            return col.DateTimeCol, {}
        elif t.startswith('bool'):
            return col.BoolCol, {}
        elif t.startswith('tinyblob'):
            return col.BLOBCol, {"length": 2**8-1}
        elif t.startswith('tinytext'):
            return col.BLOBCol, {"length": 2**8-1, "varchar": True}
        elif t.startswith('blob'):
            return col.BLOBCol, {"length": 2**16-1}
        elif t.startswith('text'):
            return col.BLOBCol, {"length": 2**16-1, "varchar": True}
        elif t.startswith('mediumblob'):
            return col.BLOBCol, {"length": 2**24-1}
        elif t.startswith('mediumtext'):
            return col.BLOBCol, {"length": 2**24-1, "varchar": True}
        elif t.startswith('longblob'):
            return col.BLOBCol, {"length": 2**32}
        elif t.startswith('longtext'):
            return col.BLOBCol, {"length": 2**32, "varchar": True}
        else:
            return col.Col, {}
