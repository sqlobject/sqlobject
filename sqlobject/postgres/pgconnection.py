from sqlobject.dbconnection import DBAPI
psycopg = None
pgdb = None

class PostgresConnection(DBAPI):

    supportTransactions = True
    dbName = 'postgres'
    schemes = [dbName, 'postgresql', 'psycopg']

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

    def connectionFromURI(cls, uri):
        user, password, host, path = self._parseURI(uri)
        return cls(host=host, db=path, user=user, passwd=password)
    connectionFromURI = classmethod(connectionFromURI)

    def isSupported(cls):
        global psycopg
        if psycopg is None:
            try:
                import psycopg
            except ImportError:
                return False
        return False
    isSupported = classmethod(isSupported)

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
                kw['default'] = getattr(sqlbuilder.const, defaultstr)
            if keymap.has_key(field):
                kw['foreignKey'] = keymap[field]
            results.append(colClass(**kw))
        return results

    def guessClass(self, t):
        if t.count('int'):
            return col.IntCol, {}
        elif t.count('varying'):
            return col.StringCol, {'length': int(t[t.index('(')+1:-1])}
        elif t.startswith('character('):
            return col.StringCol, {'length': int(t[t.index('(')+1:-1]),
                                   'varchar': False}
        elif t == 'text':
            return col.StringCol, {}
        elif t.startswith('datetime'):
            return col.DateTimeCol, {}
        elif t.startswith('bool'):
            return col.BoolCol, {}
        else:
            return col.Col, {}

