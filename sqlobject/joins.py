import SQLBuilder
NoDefault = SQLBuilder.NoDefault
import Style
import SQLObject

__all__ = ['MultipleJoin', 'RelatedJoin']

class Join(object):

    def __init__(self, otherClass=None, **kw):
        kw['otherClass'] = otherClass
        kw['joinDef'] = self
        self.kw = kw

    def setName(self, value):
        assert self.kw.get('joinMethodName') is None or self.kw['joinMethodName'] == value, "You have already given an explicit joinMethodName (%s), and you are now setting it to %s" % (self.kw['joinMethodName'], value)
        self.kw['joinMethodName'] = value

    def withClass(self, soClass):
        return self.baseClass(soClass=soClass, **self.kw)

# A join is separate from a foreign key, i.e., it is
# many-to-many, or one-to-many where the *other* class
# has the foreign key.
class SOJoin(object):

    def __init__(self,
                 soClass=None,
                 otherClass=None,
                 joinColumn=None,
                 joinMethodName=None,
                 orderBy=NoDefault,
                 joinDef=None):
        self.soClass = soClass
        self.otherClassName = otherClass
        SQLObject.addNeedSet(self, otherClass, soClass._registry,
                             'otherClass')
        self.joinColumn = joinColumn
        self.joinMethodName = joinMethodName
        self.orderBy = orderBy
        if not self.joinColumn:
            # Here we set up the basic join, which is
            # one-to-many, where the other class points to
            # us.
            self.joinColumn = Style.getStyle(self.soClass).tableReference(self.soClass._table)

    def hasIntermediateTable(self):
        return False

    def _applyOrderBy(self, results, defaultSortClass):
        if self.orderBy is NoDefault:
            self.orderBy = defaultSortClass._defaultOrder
        if self.orderBy is not None:
            results.sort(sorter(self.orderBy))
        return results

def sorter(orderBy):
    if isinstance(orderBy, tuple) or isinstance(orderBy, list):
        if len(orderBy) == 1:
            orderBy = orderBy[0]
        else:
            fhead = sorter(orderBy[0])
            frest = sorter(orderBy[1:])
            return lambda a, b, fhead=fhead, frest=frest: fhead(a, b) or frest(a, b)
    if isinstance(orderBy, SQLBuilder.DESC) \
       and isinstance(orderBy.expr, SQLBuilder.SQLObjectField):
        orderBy = '-' + orderBy.expr.original
    elif isinstance(orderBy, SQLBuilder.SQLObjectField):
        orderBy = orderBy.original
    # @@: but we don't handle more complex expressions for orderings
    if orderBy.startswith('-'):
        orderBy = orderBy[1:]
        def cmper(a, b, attr=orderBy):
            return cmp(getattr(b, attr), getattr(a, attr))
    else:
        def cmper(a, b, attr=orderBy):
            return cmp(getattr(a, attr), getattr(b, attr))
    return cmper

# This is a one-to-many
class SOMultipleJoin(SOJoin):

    def __init__(self, addRemoveName=None, **kw):
        # addRemovePrefix is something like @@
        SOJoin.__init__(self, **kw)

        # Here we generate the method names
        if not self.joinMethodName:
            name = self.otherClassName[0].lower() + self.otherClassName[1:]
            if name.endswith('s'):
                name = name + "es"
            else:
                name = name + "s"
            self.joinMethodName = name
        if not addRemoveName:
            self.addRemoveName = capitalize(self.otherClassName)
        else:
            self.addRemoveName = addRemoveName

    def performJoin(self, inst):
        ids = inst._connection._SO_selectJoin(
            self.otherClass,
            self.joinColumn,
            inst.id)
        if inst._SO_perConnection:
            conn = inst._connection
        else:
            conn = None
        return self._applyOrderBy([self.otherClass(id, conn) for (id,) in ids if id is not None], self.otherClass)

class MultipleJoin(Join):
    baseClass = SOMultipleJoin

# This is a many-to-many join, with an intermediary table
class SORelatedJoin(SOMultipleJoin):

    def __init__(self,
                 otherColumn=None,
                 intermediateTable=None, **kw):
        SOMultipleJoin.__init__(self, **kw)
        self.intermediateTable = intermediateTable
        self.otherColumn = otherColumn
        SQLObject.addNeedSet(self, self.otherClassName,
                             self.soClass._registry, '_setOtherClass')

    def _setOtherClass(self, otherClass):
        if not self.intermediateTable:
            names = [self.soClass._table,
                     otherClass._table]
            names.sort()
            self.intermediateTable = '%s_%s' % (names[0], names[1])
        if not self.otherColumn:
            self.otherColumn = self.soClass._style.tableReference(otherClass._table)


    def hasIntermediateTable(self):
        return True

    def performJoin(self, inst):
        ids = inst._connection._SO_intermediateJoin(
            self.intermediateTable,
            self.otherColumn,
            self.joinColumn,
            inst.id)
        if inst._SO_perConnection:
            conn = inst._connection
        else:
            conn = None
        return self._applyOrderBy([self.otherClass(id, conn) for (id,) in ids if id is not None], self.otherClass)

    def remove(self, inst, other):
        inst._connection._SO_intermediateDelete(
            self.intermediateTable,
            self.joinColumn,
            SQLObject.getID(inst),
            self.otherColumn,
            SQLObject.getID(other))

    def add(self, inst, other):
        inst._connection._SO_intermediateInsert(
            self.intermediateTable,
            self.joinColumn,
            SQLObject.getID(inst),
            self.otherColumn,
            SQLObject.getID(other))

class RelatedJoin(MultipleJoin):
    baseClass = SORelatedJoin

def capitalize(name):
    return name[0].capitalize() + name[1:]
