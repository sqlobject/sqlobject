import sqlbuilder
import dbconnection

class SelectResults(object):
    IterationClass = dbconnection.Iteration

    def __init__(self, sourceClass, clause, clauseTables=None,
                 **ops):
        self.sourceClass = sourceClass
        if clause is None or isinstance(clause, str) and clause == 'all':
            clause = sqlbuilder.SQLTrueClause
        self.clause = clause
        tablesDict = sqlbuilder.tablesUsedDict(self.clause)
        tablesDict[sourceClass.sqlmeta.table] = 1
        if clauseTables:
            for table in clauseTables:
                tablesDict[table] = 1
        self.clauseTables = clauseTables
        self.tables = tablesDict.keys()
        self.ops = ops
        if self.ops.get('orderBy', sqlbuilder.NoDefault) is sqlbuilder.NoDefault:
            self.ops['orderBy'] = sourceClass.sqlmeta.defaultOrder
        orderBy = self.ops['orderBy']
        if isinstance(orderBy, list) or isinstance(orderBy, tuple):
            orderBy = map(self._mungeOrderBy, orderBy)
        else:
            orderBy = self._mungeOrderBy(orderBy)
        self.ops['dbOrderBy'] = orderBy
        if ops.has_key('connection') and ops['connection'] is None:
            del ops['connection']

    def _mungeOrderBy(self, orderBy):
        if isinstance(orderBy, str) and orderBy.startswith('-'):
            orderBy = orderBy[1:]
            desc = True
        else:
            desc = False
        if isinstance(orderBy, (str, unicode)):
            if self.sourceClass.sqlmeta._columnDict.has_key(orderBy):
                val = self.sourceClass.sqlmeta._columnDict[orderBy].dbName
                if desc:
                    return '-' + val
                else:
                    return val
            else:
                if desc:
                    return '-' + orderBy
                else:
                    return orderBy
        else:
            return orderBy

    def clone(self, **newOps):
        ops = self.ops.copy()
        ops.update(newOps)
        return self.__class__(self.sourceClass, self.clause,
                              self.clauseTables, **ops)

    def orderBy(self, orderBy):
        return self.clone(orderBy=orderBy)

    def connection(self, conn):
        return self.clone(connection=conn)

    def limit(self, limit):
        return self[:limit]

    def lazyColumns(self, value):
        return self.clone(lazyColumns=value)

    def reversed(self):
        return self.clone(reversed=not self.ops.get('reversed', False))

    def distinct(self):
        return self.clone(distinct=True)

    def __getitem__(self, value):
        if type(value) is type(slice(1)):
            assert not value.step, "Slices do not support steps"
            if not value.start and not value.stop:
                # No need to copy, I'm immutable
                return self

            # Negative indexes aren't handled (and everything we
            # don't handle ourselves we just create a list to
            # handle)
            if (value.start and value.start < 0) \
               or (value.stop and value.stop < 0):
                if value.start:
                    if value.stop:
                        return list(self)[value.start:value.stop]
                    return list(self)[value.start:]
                return list(self)[:value.stop]


            if value.start:
                assert value.start >= 0
                start = self.ops.get('start', 0) + value.start
                if value.stop is not None:
                    assert value.stop >= 0
                    if value.stop < value.start:
                        # an empty result:
                        end = start
                    else:
                        end = value.stop + self.ops.get('start', 0)
                        if self.ops.get('end', None) is not None \
                           and value['end'] < end:
                            # truncated by previous slice:
                            end = self.ops['end']
                else:
                    end = self.ops.get('end', None)
            else:
                start = self.ops.get('start', 0)
                end = value.stop + start
                if self.ops.get('end', None) is not None \
                   and self.ops['end'] < end:
                    end = self.ops['end']
            return self.clone(start=start, end=end)
        else:
            if value < 0:
                return list(iter(self))[value]
            else:
                start = self.ops.get('start', 0) + value
                return list(self.clone(start=start, end=start+1))[0]

    def __iter__(self):
        conn = self.ops.get('connection', self.sourceClass._connection)
        return conn.iterSelect(self)

    def accumulate(self, *expressions):
        """ Use accumulate expression(s) to select result
            using another SQL select through current
            connection.
            Return the accumulate result
        """
        conn = self.ops.get('connection', self.sourceClass._connection)
        return conn.accumulateSelect(self, *expressions)

    def count(self):
        """ Counting elements of current select results """
        assert not self.ops.get('distinct'), "It is not currently supported to count distinct objects"

        count = self.accumulate('COUNT(*)')
        if self.ops.get('start'):
            count -= self.ops['start']
        if self.ops.get('end'):
            count = min(self.ops['end'] - self.ops.get('start', 0), count)
        return count

    def _accumulateOne(self, func_name, attribute):
        """ Making the sum/min/max/avg of a given select result attribute.
            `attribute` can be a column name (like 'a_column')
            or a dot-q attribute (like Table.q.aColumn)
        """
        return self.accumulate(*accumulateMany((func_name, attribute)))

    def sum(self, attribute):
        return self._accumulateOne("SUM", attribute)

    def min(self, attribute):
        return self._accumulateOne("MIN", attribute)

    def avg(self, attribute):
        return self._accumulateOne("AVG", attribute)

    def max(self, attribute):
        return self._accumulateOne("MAX", attribute)

StringType = type('')

def accumulateMany(*attributes):
    """ Making the expressions for sum/min/max/avg
        of a given select result attributes.
        `attributes` must be a list/tuple of pairs (func_name, attribute);
        `attribute` can be a column name (like 'a_column')
        or a dot-q attribute (like Table.q.aColumn)
    """
    expressions = []
    for func_name, attribute in attributes:
        if type(attribute) == StringType:
            expression = '%s(%s)' % (func_name, attribute)
        else:
            expression = getattr(sqlbuilder.func, func_name)(attribute)
        expressions.append(expression)
    return expressions

__all__ = ['SelectResults', 'accumulateMany']
