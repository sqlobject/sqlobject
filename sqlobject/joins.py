import sqlbuilder
NoDefault = sqlbuilder.NoDefault
import styles
import classregistry
from col import popKey

__all__ = ['MultipleJoin', 'RelatedJoin']

def getID(obj):
    try:
        return obj.id
    except AttributeError:
        return int(id)

class Join(object):

    def __init__(self, otherClass=None, **kw):
        kw['otherClass'] = otherClass
        kw['joinDef'] = self
        self.kw = kw
        if self.kw.has_key('joinMethodName'):
            self._joinMethodName = popKey(self.kw, 'joinMethodName')
        else:
            self._joinMethodName = None

    def _set_joinMethodName(self, value):
        assert self._joinMethodName == value or self._joinMethodName is None, "You have already given an explicit joinMethodName (%s), and you are now setting it to %s" % (self._joinMethodName, value)
        self._joinMethodName = value

    def _get_joinMethodName(self):
        return self._joinMethodName

    joinMethodName = property(_get_joinMethodName, _set_joinMethodName)

    def withClass(self, soClass):
        if self.kw.has_key('joinMethodName'):
            self._joinMethodName = self.kw['joinMethodName']
            del self.kw['joinMethodName'] 
        return self.baseClass(soClass=soClass,
                              joinMethodName=self._joinMethodName,
                              **self.kw)

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
        classregistry.registry(soClass._registry).addClassCallback(
            otherClass, self._setOtherClass)
        self.joinColumn = joinColumn
        self.joinMethodName = joinMethodName
        self.orderBy = orderBy
        if not self.joinColumn:
            # Here we set up the basic join, which is
            # one-to-many, where the other class points to
            # us.
            self.joinColumn = styles.getStyle(self.soClass).tableReference(self.soClass._table)

    def _setOtherClass(self, cls):
        self.otherClass = cls

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
    if isinstance(orderBy, sqlbuilder.DESC) \
       and isinstance(orderBy.expr, sqlbuilder.SQLObjectField):
        orderBy = '-' + orderBy.expr.original
    elif isinstance(orderBy, sqlbuilder.SQLObjectField):
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
        return self._applyOrderBy([self.otherClass.get(id, conn) for (id,) in ids if id is not None], self.otherClass)

class MultipleJoin(Join):
    baseClass = SOMultipleJoin

# This is a many-to-many join, with an intermediary table
class SORelatedJoin(SOMultipleJoin):

    def __init__(self,
                 otherColumn=None,
                 intermediateTable=None, **kw):
        self.intermediateTable = intermediateTable
        self.otherColumn = otherColumn
        SOMultipleJoin.__init__(self, **kw)
        classregistry.registry(self.soClass._registry).addClassCallback(
            self.otherClassName, self._setOtherRelatedClass)

    def _setOtherRelatedClass(self, otherClass):
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
        return self._applyOrderBy([self.otherClass.get(id, conn) for (id,) in ids if id is not None], self.otherClass)

    def remove(self, inst, other):
        inst._connection._SO_intermediateDelete(
            self.intermediateTable,
            self.joinColumn,
            getID(inst),
            self.otherColumn,
            getID(other))

    def add(self, inst, other):
        inst._connection._SO_intermediateInsert(
            self.intermediateTable,
            self.joinColumn,
            getID(inst),
            self.otherColumn,
            getID(other))

class RelatedJoin(MultipleJoin):
    baseClass = SORelatedJoin

def capitalize(name):
    return name[0].capitalize() + name[1:]

