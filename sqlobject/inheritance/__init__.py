from sqlobject import sqlbuilder
from sqlobject import classregistry
from sqlobject import col
from sqlobject.main import sqlmeta, SQLObject, SelectResults, True, False, \
   makeProperties, getterName, setterName
import iteration


try:
    basestring
except NameError: # Python 2.2
    import types
    basestring = (types.StringType, types.UnicodeType)


class InheritableSelectResults(SelectResults):
    IterationClass = iteration.InheritableIteration

    def __init__(self, sourceClass, clause, clauseTables=None,
                 **ops):
        if clause is None or isinstance(clause, str) and clause == 'all':
            clause = sqlbuilder.SQLTrueClause
        tablesDict = sqlbuilder.tablesUsedDict(clause)
        tablesDict[sourceClass.sqlmeta.table] = 1
        orderBy = ops.get('orderBy')
        if orderBy and not isinstance(orderBy, basestring):
            tablesDict.update(sqlbuilder.tablesUsedDict(orderBy))
        #DSM: if this class has a parent, we need to link it
        #DSM: and be sure the parent is in the table list.
        #DSM: The following code is before clauseTables
        #DSM: because if the user uses clauseTables
        #DSM: (and normal string SELECT), he must know what he wants
        #DSM: and will do himself the relationship between classes.
        if type(clause) is not str:
            tableRegistry = {}
            allClasses = classregistry.registry(
                sourceClass.sqlmeta.registry).allClasses()
            for registryClass in allClasses:
                if registryClass.sqlmeta.table in tablesDict:
                    #DSM: By default, no parents are needed for the clauses
                    tableRegistry[registryClass] = registryClass
            for registryClass in allClasses:
                if registryClass.sqlmeta.table in tablesDict:
                    currentClass = registryClass.sqlmeta.parentClass
                    while currentClass:
                        if tableRegistry.has_key(currentClass):
                            #DSM: Must keep the last parent needed
                            #DSM: (to limit the number of join needed)
                            tableRegistry[registryClass] = currentClass
                            #DSM: Remove this class as it is a parent one
                            #DSM: of a needed children
                            del tableRegistry[currentClass]
                        currentClass = currentClass.sqlmeta.parentClass
            #DSM: Table registry contains only the last children
            #DSM: or standalone classes
            parentClause = []
            for (currentClass, minParentClass) in tableRegistry.items():
                while (currentClass != minParentClass) \
                and currentClass.sqlmeta.parentClass:
                    parentClass = currentClass.sqlmeta.parentClass
                    parentClause.append(currentClass.q.id == parentClass.q.id)
                    currentClass = parentClass
                    tablesDict[currentClass.sqlmeta.table] = 1
            clause = reduce(sqlbuilder.AND, parentClause, clause)

        super(InheritableSelectResults, self).__init__(sourceClass,
            clause, clauseTables, **ops)


class InheritableSQLMeta(sqlmeta):
    def addColumn(sqlmeta, columnDef, changeSchema=False, connection=None, childUpdate=False):
        soClass = sqlmeta.soClass
        #DSM: Try to add parent properties to the current class
        #DSM: Only do this once if possible at object creation and once for
        #DSM: each new dynamic column to refresh the current class
        if sqlmeta.parentClass:
            for col in sqlmeta.parentClass.sqlmeta.columnList:
                cname = col.name
                if cname == 'childName': continue
                if cname.endswith("ID"): cname = cname[:-2]
                setattr(soClass, getterName(cname), eval(
                    'lambda self: self._parent.%s' % cname))
                if not col.immutable:
                    setattr(soClass, setterName(cname), eval(
                        'lambda self, val: setattr(self._parent, %s, val)'
                        % repr(cname)))
            if childUpdate:
                makeProperties(soClass)
                return

        if columnDef:
            super(InheritableSQLMeta, sqlmeta).addColumn(columnDef, changeSchema, connection)

        #DSM: Update each child class if needed and existing (only for new
        #DSM: dynamic column as no child classes exists at object creation)
        for c in sqlmeta.childClasses.values():
            c.sqlmeta.addColumn(columnDef, connection=connection, childUpdate=True)

    addColumn = classmethod(addColumn)

    def delColumn(sqlmeta, column, changeSchema=False, connection=None):
        soClass = sqlmeta.soClass
        super(InheritableSQLMeta, sqlmeta).delColumn(column, changeSchema, connection)

        #DSM: Update each child class if needed
        #DSM: and delete properties for this column
        for c in sqlmeta.childClasses.values():
            delattr(c, name)

    delColumn = classmethod(delColumn)

    def addJoin(sqlmeta, joinDef, childUpdate=False):
        soClass = sqlmeta.soClass
        #DSM: Try to add parent properties to the current class
        #DSM: Only do this once if possible at object creation and once for
        #DSM: each new dynamic join to refresh the current class
        if sqlmeta.parentClass:
            for join in sqlmeta.parentClass.sqlmeta.joins:
                jname = join.joinMethodName
                jarn  = join.addRemoveName
                setattr(soClass, getterName(jname),
                    eval('lambda self: self._parent.%s' % jname))
                if hasattr(join, 'remove'):
                    setattr(soClass, 'remove' + jarn,
                        eval('lambda self,o: self._parent.remove%s(o)' % jarn))
                if hasattr(join, 'add'):
                    setattr(soClass, 'add' + jarn,
                        eval('lambda self,o: self._parent.add%s(o)' % jarn))
            if childUpdate:
                makeProperties(soClass)
                return

        if joinDef:
            super(InheritableSQLMeta, sqlmeta).addJoin(joinDef)

        #DSM: Update each child class if needed and existing (only for new
        #DSM: dynamic join as no child classes exists at object creation)
        for c in sqlmeta.childClasses.values():
            c.sqlmeta.addJoin(joinDef, childUpdate=True)

    addJoin = classmethod(addJoin)

    def delJoin(sqlmeta, joinDef):
        soClass = sqlmeta.soClass
        super(InheritableSQLMeta, sqlmeta).delJoin(joinDef)

        #DSM: Update each child class if needed
        #DSM: and delete properties for this join
        for c in sqlmeta.childClasses.values():
            # FIXME: what is ``meth``?
            delattr(c, meth)

    delJoin = classmethod(delJoin)


class InheritableSQLObject(SQLObject):

    sqlmeta = InheritableSQLMeta
    _inheritable = True
    SelectResultsClass = InheritableSelectResults

    def __classinit__(cls, new_attrs):
        SQLObject.__classinit__(cls, new_attrs)
        # if we are a child class, add sqlbuilder fields from parents
        currentClass = cls.sqlmeta.parentClass
        while currentClass:
            for column in currentClass.sqlmeta.columnDefinitions.values():
                if type(column) == col.ForeignKey:
                    continue
                setattr(cls.q, column.name,
                    getattr(currentClass.q, column.name))
            currentClass = currentClass.sqlmeta.parentClass

    # @classmethod
    def _SO_setupSqlmeta(cls, new_attrs, is_base):
        # Note: cannot use super(InheritableSQLObject, cls)._SO_setupSqlmeta -
        #       InheritableSQLObject is not defined when it's __classinit__
        #       is run.  Cannot use SQLObject._SO_setupSqlmeta, either:
        #       the method would be bound to wrong class.
        if cls.__name__ == "InheritableSQLObject":
            call_super = super(cls, cls)
        else:
            # InheritableSQLObject must be in globals yet
            call_super = super(InheritableSQLObject, cls)
        call_super._SO_setupSqlmeta(new_attrs, is_base)
        sqlmeta = cls.sqlmeta
        sqlmeta.childClasses = {}
        # locate parent class and register this class in it's children
        sqlmeta.parentClass = None
        for superclass in cls.__bases__:
            if getattr(superclass, '_inheritable', False) \
            and (superclass.__name__ != 'InheritableSQLObject'):
                if sqlmeta.parentClass:
                    # already have a parent class;
                    # cannot inherit from more than one
                    raise NotImplementedError(
                        "Multiple inheritance is not implemented")
                sqlmeta.parentClass = superclass
                superclass.sqlmeta.childClasses[cls.__name__] = cls
        if sqlmeta.parentClass:
            # remove inherited column definitions
            cls.sqlmeta.columns = {}
            cls.sqlmeta.columnList = []
            cls.sqlmeta.columnDefinitions = {}
            # default inheritance child name
            if not sqlmeta.childName:
                sqlmeta.childName = cls.__name__

    _SO_setupSqlmeta = classmethod(_SO_setupSqlmeta)

    def get(cls, id, connection=None, selectResults=None, childResults=None, childUpdate=False):

        val = super(InheritableSQLObject, cls).get(id, connection, selectResults)

        #DSM: If we are updating a child, we should never return a child...
        if childUpdate: return val
        #DSM: If this class has a child, return the child
        if 'childName' in cls.sqlmeta.columns:
             childName = val.childName
             if childName is not None:
                 return cls.sqlmeta.childClasses[childName].get(id,
                     connection=connection, selectResults=childResults)
        #DSM: Now, we know we are alone or the last child in a family...
        #DSM: It's time to find our parents
        inst = val
        while inst.sqlmeta.parentClass and not inst._parent:
            inst._parent = inst.sqlmeta.parentClass.get(id,
                connection=connection, childUpdate=True)
            inst = inst._parent
        #DSM: We can now return ourself
        return val

    get = classmethod(get)

    def _notifyFinishClassCreation(cls):
        sqlmeta = cls.sqlmeta
        # verify names of added columns
        if sqlmeta.parentClass:
            # FIXME: this does not check for grandparent column overrides
            parentCols = sqlmeta.parentClass.sqlmeta.columns.keys()
            for column in sqlmeta.columnList:
                if column.name == 'childName':
                    raise AttributeError(
                        "The column name 'childName' is reserved")
                if column.name in parentCols:
                    raise AttributeError("The column '%s' is"
                        " already defined in an inheritable parent"
                        % column.name)
        # if this class is inheritable, add column for children distinction
        if cls._inheritable and (cls.__name__ != 'InheritableSQLObject'):
            sqlmeta.addColumn(col.StringCol(name='childName',
                # limit string length to get VARCHAR and not CLOB
                length=255, default=None))
        if not sqlmeta.columnList:
            # There are no columns - call addColumn to propagate columns
            # from parent classes to children
            sqlmeta.addColumn(None)
        if not sqlmeta.joins:
            # There are no joins - call addJoin to propagate joins
            # from parent classes to children
            sqlmeta.addJoin(None)
    _notifyFinishClassCreation = classmethod(_notifyFinishClassCreation)

    def _create(self, id, **kw):

        #DSM: If we were called by a children class,
        #DSM: we must retreive the properties dictionary.
        #DSM: Note: we can't use the ** call paremeter directly
        #DSM: as we must be able to delete items from the dictionary
        #DSM: (and our children must know that the items were removed!)
        if kw.has_key('kw'):
            kw = kw['kw']
        #DSM: If we are the children of an inheritable class,
        #DSM: we must first create our parent
        if self.sqlmeta.parentClass:
            parentClass = self.sqlmeta.parentClass
            new_kw = {}
            parent_kw = {}
            for (name, value) in kw.items():
                if hasattr(parentClass, name):
                    parent_kw[name] = value
                else:
                    new_kw[name] = value
            kw = new_kw
            parent_kw["childName"] = self.sqlmeta.childName
            self._parent = parentClass(kw=parent_kw,
                connection=self._connection)

            id = self._parent.id

        super(InheritableSQLObject, self)._create(id, **kw)

    def _findAlternateID(cls, name, dbName, value, connection=None):
        result = list(cls.selectBy(connection, **{name: value}))
        if not result:
            return result, None
        obj = result[0]
        return [obj.id], obj
    _findAlternateID = classmethod(_findAlternateID)

    def selectBy(cls, connection=None, **kw):
        clause = []
        for name, value in kw.items():
            clause.append(getattr(cls.q, name) == value)
        clause = reduce(sqlbuilder.AND, clause)
        conn = connection or cls._connection
        return cls.SelectResultsClass(cls, clause, connection=conn)

    selectBy = classmethod(selectBy)

    def destroySelf(self):
        #DSM: If this object has parents, recursivly kill them
        if hasattr(self, '_parent') and self._parent:
            self._parent.destroySelf()
        super(InheritableSQLObject, self).destroySelf()

    def _reprItems(self):
        items = super(InheritableSQLObject, self)._reprItems()
        # add parent attributes (if any)
        if self.sqlmeta.parentClass:
            items.extend(self._parent._reprItems())
        # filter out our special column
        return [item for item in items if item[0] != 'childName']

__all__ = ['InheritableSQLObject']
