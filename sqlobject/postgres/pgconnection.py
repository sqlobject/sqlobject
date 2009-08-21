from sqlobject.dbconnection import DBAPI
import re
from sqlobject import col
from sqlobject import sqlbuilder
from sqlobject.converters import registerConverter

class PostgresConnection(DBAPI):

    supportTransactions = True
    dbName = 'postgres'
    schemes = [dbName, 'postgresql', 'psycopg']

    def __init__(self, dsn=None, host=None, port=None, db=None,
                 user=None, password=None, usePygresql=False, unicodeCols=False,
                 **kw):
        self.usePygresql = usePygresql
        if usePygresql:
            import pgdb
            self.module = pgdb
        else:
            try:
                import psycopg2 as psycopg
            except ImportError:
                import psycopg
            self.module = psycopg

            # Register a converter for psycopg Binary type.
            registerConverter(type(psycopg.Binary('')),
                              PsycoBinaryConverter)

        self.user = user
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.dsn_dict = dsn_dict = {}
        if host:
            dsn_dict["host"] = host
        if port:
            if usePygresql:
                dsn_dict["host"] = "%s:%d" % (host, port)
            else:
                if psycopg.__version__.split('.')[0] == '1':
                    dsn_dict["port"] = str(port)
                else:
                    dsn_dict["port"] = port
        if db:
            dsn_dict["database"] = db
        if user:
            dsn_dict["user"] = user
        if password:
            dsn_dict["password"] = password
        self.use_dsn = dsn is not None
        if dsn is None:
            if usePygresql:
                dsn = ''
                if host:
                    dsn += host
                dsn += ':'
                if db:
                    dsn += db
                dsn += ':'
                if user:
                    dsn += user
                dsn += ':'
                if password:
                    dsn += password
            else:
                dsn = []
                if db:
                    dsn.append('dbname=%s' % db)
                if user:
                    dsn.append('user=%s' % user)
                if password:
                    dsn.append('password=%s' % password)
                if host:
                    dsn.append('host=%s' % host)
                if port:
                    dsn.append('port=%d' % port)
                dsn = ' '.join(dsn)
        self.dsn = dsn
        self.unicodeCols = unicodeCols
        self.schema = kw.pop('schema', None)
        if "charset" in kw:
            self.dbEncoding = self.kw["charset"] = kw.pop("charset")
        else:
            self.dbEncoding = None
        DBAPI.__init__(self, **kw)

    def connectionFromURI(cls, uri):
        user, password, host, port, path, args = cls._parseURI(uri)
        path = path.strip('/')
        if (host is None) and path.count('/'): # Non-default unix socket
            path_parts = path.split('/')
            host = '/' + '/'.join(path_parts[:-1])
            path = path_parts[-1]
        return cls(host=host, port=port, db=path, user=user, password=password, **args)
    connectionFromURI = classmethod(connectionFromURI)

    def _setAutoCommit(self, conn, auto):
        # psycopg2 does not have an autocommit method.
        if hasattr(conn, 'autocommit'):
            conn.autocommit(auto)

    def makeConnection(self):
        try:
            if self.use_dsn:
                conn = self.module.connect(self.dsn)
            else:
                conn = self.module.connect(**self.dsn_dict)
        except self.module.OperationalError, e:
            raise self.module.OperationalError("%s; used connection string %r" % (e, self.dsn))
        if self.autoCommit:
            # psycopg2 does not have an autocommit method.
            if hasattr(conn, 'autocommit'):
                conn.autocommit(1)
        if self.schema:
            c = conn.cursor()
            c.execute("SET search_path TO " + self.schema)
        dbEncoding = self.dbEncoding
        if dbEncoding:
            conn.query("SET client_encoding TO %s" % dbEncoding)
        return conn

    def _queryInsertID(self, conn, soInstance, id, names, values):
        table = soInstance.sqlmeta.table
        idName = soInstance.sqlmeta.idName
        sequenceName = soInstance.sqlmeta.idSequence or \
                               '%s_%s_seq' % (table, idName)
        c = conn.cursor()
        if id is None:
            c.execute("SELECT NEXTVAL('%s')" % sequenceName)
            id = c.fetchone()[0]
        names = [idName] + names
        values = [id] + values
        q = self._insertSQL(table, names, values)
        if self.debug:
            self.printDebug(conn, q, 'QueryIns')
        c.execute(q)
        if self.debugOutput:
            self.printDebug(conn, id, 'QueryIns', 'result')
        return id

    def _queryAddLimitOffset(cls, query, start, end):
        if not start:
            return "%s LIMIT %i" % (query, end)
        if not end:
            return "%s OFFSET %i" % (query, start)
        return "%s LIMIT %i OFFSET %i" % (query, end-start, start)
    _queryAddLimitOffset = classmethod(_queryAddLimitOffset)

    def createColumn(self, soClass, col):
        return col.postgresCreateSQL()

    def createReferenceConstraint(self, soClass, col):
        return col.postgresCreateReferenceConstraint()

    def createIndexSQL(self, soClass, index):
        return index.postgresCreateIndexSQL(soClass)

    def createIDColumn(self, soClass):
        key_type = {int: "SERIAL", str: "TEXT"}[soClass.sqlmeta.idType]
        return '%s %s PRIMARY KEY' % (soClass.sqlmeta.idName, key_type)

    def dropTable(self, tableName, cascade=False):
        self.query("DROP TABLE %s %s" % (tableName,
                                         cascade and 'CASCADE' or ''))

    def joinSQLType(self, join):
        return 'INT NOT NULL'

    def tableExists(self, tableName):
        result = self.queryOne("SELECT COUNT(relname) FROM pg_class WHERE relname = %s"
                               % self.sqlrepr(tableName))
        return result[0]

    def addColumn(self, tableName, column):
        self.query('ALTER TABLE %s ADD COLUMN %s' %
                   (tableName,
                    column.postgresCreateSQL()))

    def delColumn(self, sqlmeta, column):
        self.query('ALTER TABLE %s DROP COLUMN %s' % (sqlmeta.table, column.dbName))

    def columnsFromSchema(self, tableName, soClass):

        keyQuery = """
        SELECT pg_catalog.pg_get_constraintdef(oid) as condef
        FROM pg_catalog.pg_constraint r
        WHERE r.conrelid = %s::regclass AND r.contype = 'f'"""

        colQuery = """
        SELECT a.attname,
        pg_catalog.format_type(a.atttypid, a.atttypmod), a.attnotnull,
        (SELECT substring(d.adsrc for 128) FROM pg_catalog.pg_attrdef d
        WHERE d.adrelid=a.attrelid AND d.adnum = a.attnum)
        FROM pg_catalog.pg_attribute a
        WHERE a.attrelid =%s::regclass
        AND a.attnum > 0 AND NOT a.attisdropped
        ORDER BY a.attnum"""

        primaryKeyQuery = """
        SELECT pg_index.indisprimary,
            pg_catalog.pg_get_indexdef(pg_index.indexrelid)
        FROM pg_catalog.pg_class c, pg_catalog.pg_class c2,
            pg_catalog.pg_index AS pg_index
        WHERE c.relname = %s
            AND c.oid = pg_index.indrelid
            AND pg_index.indexrelid = c2.oid
            AND pg_index.indisprimary
        """

        keyData = self.queryAll(keyQuery % self.sqlrepr(tableName))
        keyRE = re.compile(r"\((.+)\) REFERENCES (.+)\(")
        keymap = {}

        for (condef,) in keyData:
            match = keyRE.search(condef)
            if match:
                field, reftable = match.groups()
                keymap[field] = reftable.capitalize()

        primaryData = self.queryAll(primaryKeyQuery % self.sqlrepr(tableName))
        primaryRE = re.compile(r'CREATE .*? USING .* \((.+?)\)')
        primaryKey = None
        for isPrimary, indexDef in primaryData:
            match = primaryRE.search(indexDef)
            assert match, "Unparseable contraint definition: %r" % indexDef
            assert primaryKey is None, "Already found primary key (%r), then found: %r" % (primaryKey, indexDef)
            primaryKey = match.group(1)
        assert primaryKey, "No primary key found in table %r" % tableName
        if primaryKey.startswith('"'):
            assert primaryKey.endswith('"')
            primaryKey = primaryKey[1:-1]

        colData = self.queryAll(colQuery % self.sqlrepr(tableName))
        results = []
        if self.unicodeCols:
            client_encoding = self.queryOne("SHOW client_encoding")[0]
        for field, t, notnull, defaultstr in colData:
            if field == primaryKey:
                continue
            if keymap.has_key(field):
                colClass = col.ForeignKey
                kw = {'foreignKey': soClass.sqlmeta.style.dbTableToPythonClass(keymap[field])}
                name = soClass.sqlmeta.style.dbColumnToPythonAttr(field)
                if name.endswith('ID'):
                    name = name[:-2]
                kw['name'] = name
            else:
                colClass, kw = self.guessClass(t)
                if self.unicodeCols and colClass is col.StringCol:
                    colClass = col.UnicodeCol
                    kw['dbEncoding'] = client_encoding
                kw['name'] = soClass.sqlmeta.style.dbColumnToPythonAttr(field)
            kw['dbName'] = field
            kw['notNone'] = notnull
            if defaultstr is not None:
                kw['default'] = self.defaultFromSchema(colClass, defaultstr)
            elif not notnull:
                kw['default'] = None
            results.append(colClass(**kw))
        return results

    def guessClass(self, t):
        if t.count('point'): # poINT before INT
            return col.StringCol, {}
        elif t.count('int'):
            return col.IntCol, {}
        elif t.count('varying') or t.count('varchar'):
            if '(' in t:
                return col.StringCol, {'length': int(t[t.index('(')+1:-1])}
            else: # varchar without length in Postgres means any length
                return col.StringCol, {}
        elif t.startswith('character('):
            return col.StringCol, {'length': int(t[t.index('(')+1:-1]),
                                   'varchar': False}
        elif t.count('float') or t.count('real') or t.count('double'):
            return col.FloatCol, {}
        elif t == 'text':
            return col.StringCol, {}
        elif t.startswith('timestamp'):
            return col.DateTimeCol, {}
        elif t.startswith('datetime'):
            return col.DateTimeCol, {}
        elif t.startswith('date'):
            return col.DateCol, {}
        elif t.startswith('bool'):
            return col.BoolCol, {}
        elif t.startswith('bytea'):
            return col.BLOBCol, {}
        else:
            return col.Col, {}

    def defaultFromSchema(self, colClass, defaultstr):
        """
        If the default can be converted to a python constant, convert it.
        Otherwise return is as a sqlbuilder constant.
        """
        if colClass == col.BoolCol:
            if defaultstr == 'false':
                return False
            elif defaultstr == 'true':
                return True
        return getattr(sqlbuilder.const, defaultstr)

    def _createOrDropDatabase(self, op="CREATE"):
        # We have to connect to *some* database, so we'll connect to
        # template1, which is a common open database.
        # @@: This doesn't use self.use_dsn or self.dsn_dict
        if self.usePygresql:
            dsn = '%s:template1:%s:%s' % (
                self.host or '', self.user or '', self.password or '')
        else:
            dsn = 'dbname=template1'
            if self.user:
                dsn += ' user=%s' % self.user
            if self.password:
                dsn += ' password=%s' % self.password
            if self.host:
                dsn += ' host=%s' % self.host
        conn = self.module.connect(dsn)
        cur = conn.cursor()
        # We must close the transaction with a commit so that
        # the CREATE DATABASE can work (which can't be in a transaction):
        cur.execute('COMMIT')
        cur.execute('%s DATABASE %s' % (op, self.db))
        cur.close()
        conn.close()

    def createEmptyDatabase(self):
        self._createOrDropDatabase()

    def dropDatabase(self):
        self._createOrDropDatabase(op="DROP")


# Converter for psycopg Binary type.
def PsycoBinaryConverter(value, db):
    assert db == 'postgres'
    return str(value)
