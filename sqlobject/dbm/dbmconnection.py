from sqlobject.dbconnection import DBConnection
import re
anydbm = None
pickle = None

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
        return sqlbuilder.AND(*clauses)

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
        self.host = self.user = self.password = None
        FileConnection.__init__(self, **kw)

    def connectionFromURI(cls, uri):
        user, password, host, path, args = self._parseURI(uri, expectHost=False)
        assert host is None
        assert user is None and password is None, \
               "DBM cannot accept usernames or passwords"
        path = '/' + path
        return cls(path, **args)
    connectionFromURI = classmethod(connectionFromURI)

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
            if sqlbuilder.execute(self.select.clause, self):
                if not self._maxNext:
                    raise StopIteration
                self._maxNext -= 1
                return self.select.sourceClass.get(int(idList[self.tableDict[self.select.sourceClass._table]]))
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
