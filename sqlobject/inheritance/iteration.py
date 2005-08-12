from sqlobject import sqlbuilder
from sqlobject.classregistry import findClass
from sqlobject.dbconnection import Iteration

class InheritableIteration(Iteration):
    # Default array size for cursor.fetchmany()
    defaultArraySize = 10000

    def __init__(self, dbconn, rawconn, select, keepConnection=False):
        super(InheritableIteration, self).__init__(dbconn, rawconn, select, keepConnection)
        self.lazyColumns = select.ops.get('lazyColumns', False)
        self.cursor.arraysize = self.defaultArraySize
        self._results = []
        # Find the index of the childName column
        childNameIdx = None
        columns = select.sourceClass.sqlmeta.columnList
        for i in range(len(columns)): # enumerate() is unavailable python 2.2
            if columns[i].name == "childName":
                childNameIdx = i
                break
        self._childNameIdx = childNameIdx

    def next(self):
        if not self._results:
            self._results = list(self.cursor.fetchmany())
            if not self.lazyColumns: self.fetchChildren()
        if not self._results:
            self._cleanup()
            raise StopIteration
        result = self._results[0]
        del self._results[0]
        if self.lazyColumns:
            obj = self.select.sourceClass.get(result[0], connection=self.dbconn)
            return obj
        else:
            id = result[0]
            if id in self._childrenResults:
                childResults = self._childrenResults[id]
                del self._childrenResults[id]
            else:
                childResults = None
            obj = self.select.sourceClass.get(id, selectResults=result[1:],
                childResults=childResults, connection=self.dbconn)
            return obj

    def fetchChildren(self):
        """Prefetch childrens' data

        Fetch childrens' data for every subclass in one big .select()
        to avoid .get() fetching it one by one.
        """
        self._childrenResults = {}
        if self._childNameIdx is None:
            return
        childIdsNames = {}
        childNameIdx = self._childNameIdx
        for result in self._results:
            childName = result[childNameIdx+1]
            if childName:
                ids = childIdsNames.get(childName)
                if ids is None:
                    ids = childIdsNames[childName] = []
                ids.append(result[0])
        dbconn = self.dbconn
        rawconn = self.rawconn
        cursor = rawconn.cursor()
        registry = self.select.sourceClass.sqlmeta.registry
        for childName, ids in childIdsNames.items():
            klass = findClass(childName, registry)
            select = klass.select(sqlbuilder.IN(sqlbuilder.SQLConstant("id"), ids))
            query = dbconn.queryForSelect(select)
            if dbconn.debug:
                dbconn.printDebug(rawconn, query, 'Select children of the class %s' % childName)
            self.dbconn._executeRetry(rawconn, cursor, query)
            for result in cursor.fetchall():
                self._childrenResults[result[0]] = result[1:]
