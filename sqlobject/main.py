"""
SQLObject.py
    Ian Bicking <ianb@colorstudy.com> 17 Oct 2002
SQLObject is a object-relational mapper.  See SQLObject.html or
SQLObject.txt for more.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation; either version 2.1 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
USA.
"""

import threading
import sqlbuilder
import dbconnection
import col
import styles
import types
import warnings
import joins
import index
import classregistry

import sys
if sys.version_info[:3] < (2, 2, 0):
    raise ImportError, "SQLObject requires Python 2.2.0 or later"

NoDefault = sqlbuilder.NoDefault

class SQLObjectNotFound(LookupError): pass
class SQLObjectIntegrityError(Exception): pass

True, False = 1==1, 0==1

# This is the metaclass.  It essentially takes a dictionary
# of all the attributes (and thus methods) defined in the
# class definition.  It futzes with them, and spits out the
# new class definition.
class MetaSQLObject(type):

    def __new__(cls, className, bases, d):

        # We fix up the columns here -- replacing any strings with
        # simply-contructed Col objects, and searching the class
        # variables for instances of Col objects (which get put into
        # the _columns instance variable and deleted).
        columns = []
        for column in d.get('_columns', []):
            if isinstance(column, str):
                column = col.Col(column)
            columns.append(column)
        if columns:
            d['_columns'] = columns

        implicitColumns = []
        implicitJoins = []
        implicitIndexes = []
        for attr, value in d.items():
            if isinstance(value, col.Col):
                value.name = attr
                implicitColumns.append(value)
                del d[attr]
                continue
            if isinstance(value, joins.Join):
                value.joinMethodName = attr
                implicitJoins.append(value)
                del d[attr]
                continue
            if isinstance(value, index.DatabaseIndex):
                value.setName(attr)
                implicitIndexes.append(value)
                del d[attr]
                continue                

        # We *don't* want to inherit _table, so we make sure it
        # is defined in this class (not a superclass)
        if not d.has_key('_table'):
            d['_table'] = None


        if d.has_key('_connection'):
            connection = d['_connection']
            del d['_connection']
            assert not d.has_key('connection')
        elif d.has_key('connection'):
            connection = d['connection']
            del d['connection']
        else:
            connection = None

        # We actually create the class.
        newClass = type.__new__(cls, className, bases, d)
        newClass._SO_finishedClassCreation = False

        # We append to _columns, but we don't want to change the
        # superclass's _columns list, so we make a copy if necessary
        if not d.has_key('_columns'):
            newClass._columns = newClass._columns[:]
        newClass._columns.extend(implicitColumns)
        if not d.has_key('_joins'):
            newClass._joins = newClass._joins[:]
        newClass._joins.extend(implicitJoins)
        if not d.has_key('_indexes'):
            newClass._indexes = newClass._indexes[:]
        newClass._indexes.extend(implicitIndexes)

        ######################################################
        # Set some attributes to their defaults, if necessary.
        # First we get the connection:
        if not connection and not getattr(newClass, '_connection', None):
            mod = sys.modules[newClass.__module__]
            # See if there's a __connection__ global in
            # the module, use it if there is.
            if hasattr(mod, '__connection__'):
                connection = mod.__connection__

        if connection or not hasattr(newClass, '_connection'):
            newClass.setConnection(connection)

        # The style object tells how to map between Python
        # identifiers and Database identifiers:
        if not newClass._style:
            if newClass._connection and newClass._connection.style:
                newClass._style = newClass._connection.style
            else:
                newClass._style = styles.defaultStyle

        # plainSetters are columns that haven't been overridden by the
        # user, so we can contact the database directly to set them.
        # Note that these can't set these in the SQLObject class
        # itself, because they specific to this subclass of SQLObject,
        # and cannot be shared among classes.
        newClass._SO_plainSetters = {}
        newClass._SO_plainGetters = {}
        newClass._SO_plainForeignSetters = {}
        newClass._SO_plainForeignGetters = {}
        newClass._SO_plainJoinGetters = {}
        newClass._SO_plainJoinAdders = {}
        newClass._SO_plainJoinRemovers = {}

        # This is a dictionary of columnName: columnObject
        newClass._SO_columnDict = {}
        newClass._SO_columns = []

        # If _table isn't given, use style default
        if not newClass._table:
            newClass._table = newClass._style.pythonClassToDBTable(className)

        # If _idName isn't given, use style default
        if not d.has_key('_idName'):
            newClass._idName = newClass._style.idForTable(newClass._table)

        # We use the magic "q" attribute for accessing lazy
        # SQL where-clause generation.  See the sql module for
        # more.
        newClass.q = sqlbuilder.SQLObjectTable(newClass)

        # We have to check if there are columns in the inherited
        # _columns where the attribute has been set to None in this
        # class.  If so, then we need to remove that column from
        # _columns.
        for column in newClass._columns[:]:
            if d.has_key(column.name) and d[column.name] is None:
                newClass._columns.remove(column)

        for column in newClass._columns:
            newClass.addColumn(column)
        if newClass._fromDatabase:
            newClass.addColumnsFromDatabase()

        ########################################
        # Now we do the joins:

        # We keep track of the different joins by index,
        # putting them in this list.
        newClass._SO_joinList = []
        newClass._SO_joinDict = {}

        for join in newClass._joins:
            newClass.addJoin(join)

        # We don't setup the properties until we're finished with the
        # batch adding of all the columns...
        newClass._SO_finishedClassCreation = True
        makeProperties(newClass)

        newClass._SO_indexList = []
        for idx in newClass._indexes:
            newClass.addIndex(idx)

        classregistry.registry(newClass._registry).addClass(newClass)

        # And return the class
        return newClass

def makeProperties(obj):
    """
    This function takes a dictionary of methods and finds
    methods named like:
    * _get_attr
    * _set_attr
    * _del_attr
    * _doc_attr
    Except for _doc_attr, these should be methods.  It
    then creates properties from these methods, like
    property(_get_attr, _set_attr, _del_attr, _doc_attr).
    Missing methods are okay.
    """

    if isinstance(obj, dict):
        def setFunc(var, value):
            obj[var] = value
        d = obj
    else:
        def setFunc(var, value):
            setattr(obj, var, value)
        d = obj.__dict__

    props = {}
    for var, value in d.items():
        if var.startswith('_set_'):
            props.setdefault(var[5:], {})['set'] = value
        elif var.startswith('_get_'):
            props.setdefault(var[5:], {})['get'] = value
        elif var.startswith('_del_'):
            props.setdefault(var[5:], {})['del'] = value
        elif var.startswith('_doc_'):
            props.setdefault(var[5:], {})['doc'] = value
    for var, setters in props.items():
        if len(setters) == 1 and setters.has_key('doc'):
            continue
        if d.has_key(var):
            if isinstance(d[var], types.MethodType) \
                   or isinstance(d[var], types.FunctionType):
                warnings.warn(
                    "I tried to set the property %r, but it was "
                    "already set, as a method (%r).  Methods have "
                    "significantly different semantics than properties, "
                    "and this may be a sign of a bug in your code."
                    % (var, d[var]))
            continue
        setFunc(var,
                property(setters.get('get'), setters.get('set'),
                         setters.get('del'), setters.get('doc')))

def unmakeProperties(obj):
    if isinstance(obj, dict):
        def delFunc(obj, var):
            del obj[var]
        d = obj
    else:
        delFunc = delattr
        d = obj.__dict__

    for var, value in d.items():
        if isinstance(value, property):
            for prop in [value.fget, value.fset, value.fdel]:
                if prop and not d.has_key(prop.__name__):
                    delFunc(obj, var)
                    break

def findClass(name, registry=None):
    #assert classRegistry.get(registry, {}).has_key(name), "No class by the name %s found (I have %s)" % (repr(name), ', '.join(map(str, classRegistry.keys())))
    return classregistry.registry(registry).getClass(name)

def findDependencies(name, registry=None):
    depends = []
    for klass in classregistry.registry(registry).allClasses():
        if findDependantColumns(name, klass):
            depends.append(klass)
    return depends

def findDependantColumns(name, klass):
    depends = []
    for col in klass._SO_columns:
        if col.foreignKey == name and col.cascade is not None:
            depends.append(col)
    return depends

class CreateNewSQLObject:
    """
    Dummy singleton to use in place of an ID, to signal we want
    a new object.
    """
    pass

# SQLObject is the superclass for all SQLObject classes, of
# course.  All the deeper magic is done in MetaSQLObject, and
# only lesser magic is done here.  All the actual work is done
# here, though -- just automatic method generation (like
# methods and properties for each column) is done in
# MetaSQLObject.
class SQLObject(object):

    __metaclass__ = MetaSQLObject

    # When an object is being created, it has an instance
    # variable _SO_creating, which is true.  This way all the
    # setters can be captured until the object is complete,
    # and then the row is inserted into the database.  Once
    # that happens, _SO_creating is deleted from the instance,
    # and only the class variable (which is always false) is
    # left.
    _SO_creating = False
    _SO_obsolete = False

    # Sometimes an intance is attached to a connection, not
    # globally available.  In that case, self._SO_perConnection
    # will be true.  It's false by default:
    _SO_perConnection = False

    # The _cacheValues attribute controls if you cache
    # values fetched from the database.  We make sure
    # it's set (default 1).
    _cacheValues = True

    # The _defaultOrder is used by SelectResults
    _defaultOrder = None

    _connection = None

    _columns = []

    _joins = []

    _indexes = []

    _fromDatabase = False

    _style = None

    _registry = None

    # Default is false, but we set it to true for the *instance*
    # when necessary: (bad clever? maybe)
    _expired = False

    _lazyUpdate = False

    # This function is used to coerce IDs into the proper format,
    # so you should replace it with str, or another function, if you
    # aren't using integer IDs
    _idType = int

    def get(cls, id, connection=None, selectResults=None):

        assert id is not None, 'None is not a possible id for %s' % cls.__name
        
        id = cls._idType(id)

        if connection is None:
            cache = cls._connection.cache
        else:
            cache = connection.cache

        # This whole sequence comes from Cache.CacheFactory's
        # behavior, where a None returned means a cache miss.
        val = cache.get(id, cls)
        if val is None:
            try:
                val = cls(_SO_fetch_no_create=1)
                val._SO_validatorState = SQLObjectState(val)
                val._init(id, connection, selectResults)
                cache.put(id, cls, val)
            finally:
                cache.finishPut(cls)
        return val

    get = classmethod(get)

    def addIndex(cls, indexDef):
        index = indexDef.withClass(cls)
        cls._SO_indexList.append(index)
    addIndex = classmethod(addIndex)

    def addColumn(cls, columnDef, changeSchema=False, connection=None):
        column = columnDef.withClass(cls)
        name = column.name
        assert name != 'id', "The 'id' column is implicit, and should not be defined as a column"
        cls._SO_columnDict[name] = column
        cls._SO_columns.append(column)

        if columnDef not in cls._columns:
            cls._columns.append(columnDef)

        ###################################################
        # Create the getter function(s).  We'll start by
        # creating functions like _SO_get_columnName,
        # then if there's no function named _get_columnName
        # we'll alias that to _SO_get_columnName.  This
        # allows a sort of super call, even though there's
        # no superclass that defines the database access.
        if cls._cacheValues:
            # We create a method here, which is just a function
            # that takes "self" as the first argument.
            getter = eval('lambda self: self._SO_loadValue(%s)' % repr(instanceName(name)))

        else:
            # If we aren't caching values, we just call the
            # function _SO_getValue, which fetches from the
            # database.
            getter = eval('lambda self: self._SO_getValue(%s)' % repr(name))
        setattr(cls, rawGetterName(name), getter)

        # Here if the _get_columnName method isn't in the
        # definition, we add it with the default
        # _SO_get_columnName definition.
        if not hasattr(cls, getterName(name)):
            setattr(cls, getterName(name), getter)
            cls._SO_plainGetters[name] = 1

        #################################################
        # Create the setter function(s)
        # Much like creating the getters, we will create
        # _SO_set_columnName methods, and then alias them
        # to _set_columnName if the user hasn't defined
        # those methods themself.

        if not column.immutable:
            # We start by just using the _SO_setValue method
            setter = eval('lambda self, val: self._SO_setValue(%s, val, self.%s, self.%s)' % (repr(name), '_SO_fromPython_%s' % name, '_SO_toPython_%s' % name))
            setattr(cls, '_SO_fromPython_%s' % name, column.fromPython)
            setattr(cls, '_SO_toPython_%s' % name, column.toPython)
            setattr(cls, rawSetterName(name), setter)
            # Then do the aliasing
            if not hasattr(cls, setterName(name)):
                setattr(cls, setterName(name), setter)
                # We keep track of setters that haven't been
                # overridden, because we can combine these
                # set columns into one SQL UPDATE query.
                cls._SO_plainSetters[name] = 1

        ##################################################
        # Here we check if the column is a foreign key, in
        # which case we need to make another method that
        # fetches the key and constructs the sister
        # SQLObject instance.
        if column.foreignKey:

            # We go through the standard _SO_get_columnName
            # deal, except chopping off the "ID" ending since
            # we're giving the object, not the ID of the
            # object this time:
            if cls._cacheValues:
                # self._SO_class_className is a reference
                # to the class in question.
                getter = eval('lambda self: self._SO_foreignKey(self._SO_loadValue(%r), self._SO_class_%s)' % (instanceName(name), column.foreignKey))
            else:
                # Same non-caching version as above.
                getter = eval('lambda self: self._SO_foreignKey(self._SO_getValue(%s), self._SO_class_%s)' % (repr(name), column.foreignKey))
            if column.origName.upper().endswith('ID'):
                origName = column.origName[:-2]
            else:
                origName = column.origName
            setattr(cls, rawGetterName(origName), getter)

            # And we set the _get_columnName version
            # (sans ID ending)
            if not hasattr(cls, getterName(name)[:-2]):
                setattr(cls, getterName(name)[:-2], getter)
                cls._SO_plainForeignGetters[name[:-2]] = 1

            if not column.immutable:
                # The setter just gets the ID of the object,
                # and then sets the real column.
                setter = eval('lambda self, val: setattr(self, %s, self._SO_getID(val))' % (repr(name)))
                setattr(cls, rawSetterName(name)[:-2], setter)
                if not hasattr(cls, setterName(name)[:-2]):
                    setattr(cls, setterName(name)[:-2], setter)
                    cls._SO_plainForeignSetters[name[:-2]] = 1

            # We'll need to put in a real reference at
            # some point.  See needSet at the top of the
            # file for more on this.
            classregistry.registry(cls._registry).addClassCallback(
                column.foreignKey,
                lambda foreign, me, attr: setattr(me, attr, foreign),
                cls, '_SO_class_%s' % column.foreignKey)

        if column.alternateMethodName:
            func = eval('lambda cls, val, connection=None: cls._SO_fetchAlternateID(%s, val, connection=connection)' % repr(column.dbName))
            setattr(cls, column.alternateMethodName, classmethod(func))

        if changeSchema:
            conn = connection or cls._connection
            conn.addColumn(cls._table, column)

        if cls._SO_finishedClassCreation:
            makeProperties(cls)

    addColumn = classmethod(addColumn)

    def addColumnsFromDatabase(cls, connection=None):
        conn = connection or cls._connection
        for columnDef in conn.columnsFromSchema(cls._table, cls):
            alreadyExists = False
            for c in cls._columns:
                if c.name == columnDef.name:
                    alreadyExists = True
                    break
            if not alreadyExists:
                cls.addColumn(columnDef)

    addColumnsFromDatabase = classmethod(addColumnsFromDatabase)

    def delColumn(cls, column, changeSchema=False, connection=None):
        if isinstance(column, str):
            column = cls._SO_columnDict[column]
        if isinstance(column, col.Col):
            for c in cls._SO_columns:
                if column is c.columnDef:
                    column = c
                    break
        cls._SO_columns.remove(column)
        cls._columns.remove(column.columnDef)
        name = column.name
        del cls._SO_columnDict[name]
        delattr(cls, rawGetterName(name))
        if cls._SO_plainGetters.has_key(name):
            delattr(cls, getterName(name))
        delattr(cls, rawSetterName(name))
        if cls._SO_plainSetters.has_key(name):
            delattr(cls, setterName(name))
        if column.foreignKey:
            delattr(cls, rawGetterName(name)[:-2])
            if cls._SO_plainForeignGetters.has_key(name[:-2]):
                delattr(cls, getterName(name)[:-2])
            delattr(cls, rawSetterName(name)[:-2])
            if cls._SO_plainForeignSetters.has_key(name[:-2]):
                delattr(cls, setterName(name)[:-2])
        if column.alternateMethodName:
            delattr(cls, column.alternateMethodName)

        if changeSchema:
            conn = connection or cls._connection
            conn.delColumn(cls._table, column)

        if cls._SO_finishedClassCreation:
            unmakeProperties(cls)

    delColumn = classmethod(delColumn)

    def addJoin(cls, joinDef):
        # The name of the method we'll create.  If it's
        # automatically generated, it's generated by the
        # join class.
        join = joinDef.withClass(cls)
        meth = join.joinMethodName
        cls._SO_joinDict[joinDef] = join

        cls._SO_joinList.append(join)
        index = len(cls._SO_joinList)-1
        if joinDef not in cls._joins:
            cls._joins.append(joinDef)

        # The function fetches the join by index, and
        # then lets the join object do the rest of the
        # work:
        func = eval('lambda self: self._SO_joinList[%i].performJoin(self)' % index)

        # And we do the standard _SO_get_... _get_... deal
        setattr(cls, rawGetterName(meth), func)
        if not hasattr(cls, getterName(meth)):
            setattr(cls, getterName(meth), func)
            cls._SO_plainJoinGetters[meth] = 1

        # Some joins allow you to remove objects from the
        # join.
        if hasattr(join, 'remove'):

            # Again, we let it do the remove, and we do the
            # standard naming trick.
            func = eval('lambda self, obj: self._SO_joinList[%i].remove(self, obj)' % index)
            setattr(cls, '_SO_remove' + join.addRemoveName, func)
            if not hasattr(cls, 'remove' + join.addRemoveName):
                setattr(cls, 'remove' + join.addRemoveName, func)
                cls._SO_plainJoinRemovers[meth] = 1

        # Some joins allow you to add objects.
        if hasattr(join, 'add'):

            # And again...
            func = eval('lambda self, obj: self._SO_joinList[%i].add(self, obj)' % (len(cls._SO_joinList)-1))
            setattr(cls, '_SO_add' + join.addRemoveName, func)
            if not hasattr(cls, 'add' + join.addRemoveName):
                setattr(cls, 'add' + join.addRemoveName, func)
                cls._SO_plainJoinAdders[meth] = 1

        if cls._SO_finishedClassCreation:
            makeProperties(cls)

    addJoin = classmethod(addJoin)

    def delJoin(cls, joinDef):
        join = cls._SO_joinDict[joinDef]
        meth = join.joinMethodName
        cls._joins.remove(joinDef)
        del cls._SO_joinDict[joinDef]
        for i in range(len(cls._SO_joinList)):
            if cls._SO_joinList[i] is joinDef:
                # Have to leave None, because we refer to joins
                # by index.
                cls._SO_joinList[i] = None
        delattr(cls, rawGetterName(meth))
        if cls._SO_plainJoinGetters.has_key(meth):
            delattr(cls, getterName(meth))
        if hasattr(join, 'remove'):
            delattr(cls, '_SO_remove' + join.addRemovePrefix)
            if cls._SO_plainJoinRemovers.has_key(meth):
                delattr(cls, 'remove' + join.addRemovePrefix)
        if hasattr(join, 'add'):
            delattr(cls, '_SO_add' + join.addRemovePrefix)
            if cls._SO_plainJoinAdders.has_key(meth):
                delattr(cls, 'add' + join.addRemovePrefix)

        if cls._SO_finishedClassCreation:
            unmakeProperties(cls)

    delJoin = classmethod(delJoin)

    def _init(self, id, connection=None, selectResults=None):
        assert id is not None
        # This function gets called only when the object is
        # created, unlike __init__ which would be called
        # anytime the object was returned from cache.
        self.id = id
        self._SO_writeLock = threading.Lock()

        # If no connection was given, we'll inherit the class
        # instance variable which should have a _connection
        # attribute.
        if connection is not None:
            self._connection = connection
            # Sometimes we need to know if this instance is
            # global or tied to a particular connection.
            # This flag tells us that:
            self._SO_perConnection = True

        if not selectResults:
            dbNames = [col.dbName for col in self._SO_columns]
            selectResults = self._connection._SO_selectOne(self, dbNames)
            if not selectResults:
                raise SQLObjectNotFound, "The object %s by the ID %s does not exist" % (self.__class__.__name__, self.id)
        self._SO_selectInit(selectResults)
        self._SO_createValues = {}
        self.dirty = False

    def _SO_loadValue(self, attrName):
        try:
            return getattr(self, attrName)
        except AttributeError:
            try:
                self._SO_writeLock.acquire()
                try:
                    # Maybe, just in the moment since we got the lock,
                    # some other thread did a _SO_loadValue and we
                    # have the attribute!  Let's try and find out!  We
                    # can keep trying this all day and still beat the
                    # performance on the database call (okay, we can
                    # keep trying this for a few msecs at least)...
                    result = getattr(self, attrName)
                except AttributeError:
                    pass
                else:
                    return result
                self._expired = False
                dbNames = [col.dbName for col in self._SO_columns]
                selectResults = self._connection._SO_selectOne(self, dbNames)
                if not selectResults:
                    raise SQLObjectNotFound, "The object %s by the ID %s has been deleted" % (self.__class__.__name__, self.id)
                self._SO_selectInit(selectResults)
                result = getattr(self, attrName)
                return result
            finally:
                self._SO_writeLock.release()

    def sync(self):
        if self._lazyUpdate and self._SO_createValues:
            self.syncUpdate()
        self._SO_writeLock.acquire()
        try:
            dbNames = [col.dbName for col in self._SO_columns]
            selectResults = self._connection._SO_selectOne(self, dbNames)
            if not selectResults:
                raise SQLObjectNotFound, "The object %s by the ID %s has been deleted" % (self.__class__.__name__, self.id)
            self._SO_selectInit(selectResults)
            self._expired = False
        finally:
            self._SO_writeLock.release()

    def syncUpdate(self):
        if not self._SO_createValues:
            return
        self._SO_writeLock.acquire()
        try:
            if self._SO_columnDict:
                values = [(self._SO_columnDict[v[0]].dbName, v[1]) for v in self._SO_createValues.items()]
                self._connection._SO_update(self, values)
            self.dirty = False
            self._SO_createValues = {}
        finally:
            self._SO_writeLock.release()

    def expire(self):
        if self._expired:
            return
        self._SO_writeLock.acquire()
        try:
            if self._expired:
                return
            for column in self._SO_columns:
                delattr(self, instanceName(column.name))
            self._expired = True
            self._connection.cache.expire(self.id, self.__class__)
        finally:
            self._SO_writeLock.release()

    def _SO_setValue(self, name, value, fromPython, toPython):
        # This is the place where we actually update the
        # database.

        # If we are _SO_creating, the object doesn't yet exist
        # in the database, and we can't insert it until all
        # the parts are set.  So we just keep them in a
        # dictionary until later:
        if fromPython:
            dbValue = fromPython(value, self._SO_validatorState)
        else:
            dbValue = value
        if toPython:
            value = toPython(dbValue, self._SO_validatorState)
        if self._SO_creating or self._lazyUpdate:
            self.dirty = True
            self._SO_createValues[name] = dbValue
            setattr(self, instanceName(name), value)
            return

        self._connection._SO_update(self,
                                    [(self._SO_columnDict[name].dbName,
                                      dbValue)])

        if self._cacheValues:
            setattr(self, instanceName(name), value)

    def set(self, **kw):
        # set() is used to update multiple values at once,
        # potentially with one SQL statement if possible.

        # Filter out items that don't map to column names.
        # Those will be set directly on the object using
        # setattr(obj, name, value).
        is_column = self._SO_plainSetters.has_key
        f_is_column = lambda item: is_column(item[0])
        f_not_column = lambda item: not is_column(item[0])
        items = kw.items()
        extra = dict(filter(f_not_column, items))
        kw = dict(filter(f_is_column, items))

        # _SO_creating is special, see _SO_setValue
        if self._SO_creating or self._lazyUpdate:
            for name, value in kw.items():
                fromPython = getattr(self, '_SO_fromPython_%s' % name, None)
                if fromPython:
                    kw[name] = dbValue = fromPython(value, self._SO_validatorState)
                else:
                    dbValue = value
                toPython = getattr(self, '_SO_toPython_%s' % name, None)
                if toPython:
                    value = toPython(dbValue, self._SO_validatorState)
                setattr(self, instanceName(name), value)
            for name, value in extra.items():
                try:
                    getattr(self.__class__, name)
                except AttributeError:
                    if name not in self._SO_columnDict:
                        raise TypeError, "%s.set() got an unexpected keyword argument %s" % (self.__class__.__name__, name)
                try:
                    setattr(self, name, value)
                except AttributeError, e:
                    raise AttributeError, '%s (with attribute %r)' % (e, name)

            self._SO_createValues.update(kw)
            self.dirty = True
            return

        self._SO_writeLock.acquire()

        try:
            # We have to go through and see if the setters are
            # "plain", that is, if the user has changed their
            # definition in any way (put in something that
            # normalizes the value or checks for consistency,
            # for instance).  If so then we have to use plain
            # old setattr() to change the value, since we can't
            # read the user's mind.  We'll combine everything
            # else into a single UPDATE, if necessary.
            toUpdate = {}
            for name, value in kw.items():
                fromPython = getattr(self, '_SO_fromPython_%s' % name, None)
                if fromPython:
                    dbValue = fromPython(value, self._SO_validatorState)
                else:
                    dbValue = value
                toPython = getattr(self, '_SO_toPython_%s' % name, None)
                if toPython:
                    value = toPython(dbValue, self._SO_validatorState)
                if self._cacheValues:
                    setattr(self, instanceName(name), value)
                toUpdate[name] = dbValue
            for name, value in extra.items():
                try:
                    getattr(self.__class__, name)
                except AttributeError:
                    if name not in self._SO_columnDict:
                        raise TypeError, "%s.set() got an unexpected keyword argument %s" % (self.__class__.__name__, name)
                try:
                    setattr(self, name, value)
                except AttributeError, e:
                    raise AttributeError, '%s (with attribute %r)' % (e, name)

            if toUpdate:
                args = [(self._SO_columnDict[name].dbName, value)
                        for name, value in toUpdate.items()]
                self._connection._SO_update(self, args)
        finally:
            self._SO_writeLock.release()

    def _SO_selectInit(self, row):
        for col, colValue in zip(self._SO_columns, row):
            if col.toPython:
                colValue = col.toPython(colValue, self._SO_validatorState)
            setattr(self, instanceName(col.name), colValue)

    def _SO_getValue(self, name):
        # Retrieves a single value from the database.  Simple.
        assert not self._SO_obsolete, "%s with id %s has become obsolete" \
               % (self.__class__.__name__, self.id)
        # @@: do we really need this lock?
        #self._SO_writeLock.acquire()
        column = self._SO_columnDict[name]
        results = self._connection._SO_selectOne(self, [column.dbName])
        #self._SO_writeLock.release()
        assert results != None, "%s with id %s is not in the database" \
               % (self.__class__.__name__, self.id)
        value = results[0]
        if column.toPython:
            value = column.toPython(value, self._SO_validatorState)
        return value

    def _SO_foreignKey(self, id, joinClass):
        if id is None:
            return None
        elif self._SO_perConnection:
            return joinClass.get(id, connection=self._connection)
        else:
            return joinClass.get(id)

    def __init__(self, **kw):
        # The get() classmethod/constructor uses a magic keyword
        # argument when it wants an empty object, fetched from the
        # database.  So we have nothing more to do in that case:
        if kw.has_key('_SO_fetch_no_create'):
            return

        # Pass the connection object along if we were given one.
        # Passing None for the ID tells __init__ we want to create
        # a new object.
        if kw.has_key('connection'):
            self._connection = kw['connection']
            self._SO_perConnection = True
            del kw['connection']
        self._SO_writeLock = threading.Lock()

        if kw.has_key('id'):
            id = self._idType(kw['id'])
            del kw['id']
        else:
            id = None

        self._create(id, **kw)

    def _create(self, id, **kw):

        self._SO_creating = True
        self._SO_createValues = {}
        self._SO_validatorState = SQLObjectState(self)

        # First we do a little fix-up on the keywords we were
        # passed:
        for column in self._SO_columns:

            # If a foreign key is given, we get the ID of the object
            # and put that in instead
            if kw.has_key(column.foreignName):
                kw[column.name] = getID(kw[column.foreignName])
                del kw[column.foreignName]

            # Then we check if the column wasn't passed in, and
            # if not we try to get the default.
            if not kw.has_key(column.name):
                default = column.default

                # If we don't get it, it's an error:
                if default is NoDefault:
                    raise TypeError, "%s() did not get expected keyword argument %s" % (self.__class__.__name__, column.name)
                # Otherwise we put it in as though they did pass
                # that keyword:
                kw[column.name] = default

        self.set(**kw)

        # Then we finalize the process:
        self._SO_finishCreate(id)

    def _SO_finishCreate(self, id=None):
        # Here's where an INSERT is finalized.
        # These are all the column values that were supposed
        # to be set, but were delayed until now:
        setters = self._SO_createValues.items()
        # Here's their database names:
        names = [self._SO_columnDict[v[0]].dbName for v in setters]
        values = [v[1] for v in setters]
        # Get rid of _SO_create*, we aren't creating anymore.
        # Doesn't have to be threadsafe because we're still in
        # new(), which doesn't need to be threadsafe.
        self.dirty = False
        if not self._lazyUpdate:
            del self._SO_createValues
        else:
            self._SO_createValues = {}
        del self._SO_creating

        # Do the insert -- most of the SQL in this case is left
        # up to DBConnection, since getting a new ID is
        # non-standard.
        id = self._connection.queryInsertID(self,
                                            id, names, values)
        cache = self._connection.cache
        cache.created(id, self.__class__, self)
        self._init(id)

    def _SO_getID(self, obj):
        return getID(obj)

    def _SO_fetchAlternateID(cls, dbIDName, value, connection=None):
        result = (connection or cls._connection)._SO_selectOneAlt(
            cls,
            [cls._idName] +
            [col.dbName for col in cls._SO_columns],
            dbIDName,
            value)
        if not result:
            raise SQLObjectNotFound, "The %s by alternateID %s=%s does not exist" % (cls.__name__, dbIDName, repr(value))
        if connection:
            obj = cls.get(result[0], connection=connection)
        else:
            obj = cls.get(result[0])
        if not obj._cacheValues:
            obj._SO_writeLock.acquire()
            try:
                obj._SO_selectInit(result[1:])
            finally:
                obj._SO_writeLock.release()
        return obj
    _SO_fetchAlternateID = classmethod(_SO_fetchAlternateID)

    def _SO_depends(cls):
        return findDependencies(cls.__name__, cls._registry)
    _SO_depends = classmethod(_SO_depends)

    def select(cls, clause=None, clauseTables=None,
               orderBy=NoDefault, limit=None,
               lazyColumns=False, reversed=False,
               distinct=False,
               connection=None):
        return SelectResults(cls, clause,
                             clauseTables=clauseTables,
                             orderBy=orderBy,
                             limit=limit,
                             lazyColumns=lazyColumns,
                             reversed=reversed,
                             distinct=distinct,
                             connection=connection)
    select = classmethod(select)

    def selectBy(cls, connection=None, **kw):
        conn = connection or cls._connection
        return SelectResults(cls,
                             conn._SO_columnClause(cls, kw),
                             connection=conn)

    selectBy = classmethod(selectBy)

    def dropTable(cls, ifExists=False, dropJoinTables=True, cascade=False,
                  connection=None):
        conn = connection or cls._connection
        if ifExists and not conn.tableExists(cls._table):
            return
        conn.dropTable(cls._table, cascade)
        if dropJoinTables:
            cls.dropJoinTables(ifExists=ifExists, connection=conn)
    dropTable = classmethod(dropTable)

    def createTable(cls, ifNotExists=False, createJoinTables=True,
                    createIndexes=True,
                    connection=None):
        conn = connection or cls._connection
        if ifNotExists and conn.tableExists(cls._table):
            return
        conn.createTable(cls)
        if createJoinTables:
            cls.createJoinTables(ifNotExists=ifNotExists,
                                 connection=conn)
        if createIndexes:
            cls.createIndexes(ifNotExists=ifNotExists,
                              connection=conn)
    createTable = classmethod(createTable)

    def createTableSQL(cls, createJoinTables=True, connection=None):
        conn = connection or cls._connection
        sql = conn.createTableSQL(cls)
        if createJoinTables:
            sql += '\n' + cls.createJoinTablesSQL(connection=conn)
        return sql
    createTableSQL = classmethod(createTableSQL)

    def createJoinTables(cls, ifNotExists=False, connection=None):
        conn = connection or cls._connection
        for join in cls._getJoinsToCreate():
            if ifNotExists and \
               conn.tableExists(join.intermediateTable):
                continue
            conn._SO_createJoinTable(join)
    createJoinTables = classmethod(createJoinTables)

    def createJoinTablesSQL(cls, connection=None):
        conn = connection or cls._connection
        sql = []
        for join in cls._getJoinsToCreate():
            sql.append(conn._SO_createJoinTableSQL(join))
        return '\n'.join(sql)
    createJoinTablesSQL = classmethod(createJoinTablesSQL)

    def createIndexes(cls, ifNotExists=False, connection=None):
        conn = connection or cls._connection
        for index in cls._SO_indexList:
            if not index:
                continue
            conn._SO_createIndex(cls, index)
    createIndexes = classmethod(createIndexes)

    def _getJoinsToCreate(cls):
        joins = []
        for join in cls._SO_joinList:
            if not join:
                continue
            if not join.hasIntermediateTable():
                continue
            if join.soClass.__name__ > join.otherClass.__name__:
                continue
            joins.append(join)
        return joins
    _getJoinsToCreate = classmethod(_getJoinsToCreate)

    def dropJoinTables(cls, ifExists=False, connection=None):
        conn = connection or cls._connection
        for join in cls._SO_joinList:
            if not join:
                continue
            if not join.hasIntermediateTable():
                continue
            if join.soClass.__name__ > join.otherClass.__name__:
                continue
            if ifExists and \
               not conn.tableExists(join.intermediateTable):
                continue
            conn._SO_dropJoinTable(join)

    dropJoinTables = classmethod(dropJoinTables)

    def clearTable(cls, connection=None):
        # 3-03 @@: Maybe this should check the cache... but it's
        # kind of crude anyway, so...
        conn = connection or cls._connection
        conn.clearTable(cls._table)
    clearTable = classmethod(clearTable)

    def destroySelf(self):
        # Kills this object.  Kills it dead!
        depends = []
        klass = self.__class__
        depends = self._SO_depends()
        for k in depends:
            cols = findDependantColumns(klass.__name__, k)
            query = []
            restrict = False
            for col in cols:
                if col.cascade == False:
                    # Found a restriction
                    restrict = True
                query.append("%s = %s" % (col.dbName, self.id))
            query = ' OR '.join(query)
            results = k.select(query, connection=self._connection)
            if restrict and results.count():
                # Restrictions only apply if there are
                # matching records on the related table
                raise SQLObjectIntegrityError, (
                    "Tried to delete %s::%s but "
                    "table %s has a restriction against it" %
                    (klass.__name__, self.id, k.__name__))
            for row in results:
                row.destroySelf()
        self._SO_obsolete = True
        self._connection._SO_delete(self)
        self._connection.cache.expire(self.id, self.__class__)

    def delete(cls, id):
        obj = cls.get(id)
        obj.destroySelf()

    delete = classmethod(delete)

    def __repr__(self):
        return '<%s %r %s>' \
               % (self.__class__.__name__,
                  self.id,
                  ' '.join(['%s=%s' % (name, repr(value)) for name, value in self._reprItems()]))

    def sqlrepr(cls, value, connection=None):
        return (connection or cls._connection).sqlrepr(value)

    sqlrepr = classmethod(sqlrepr)

    def coerceID(cls, value):
        if isinstance(value, cls):
            return value.id
        else:
            return cls._idType(value)

    coerceID = classmethod(coerceID)

    def _reprItems(self):
        items = []
        for col in self._SO_columns:
            value = getattr(self, col.name)
            r = repr(value)
            if len(r) > 20:
                value = r[:17] + "..." + r[-1]
            items.append((col.name, getattr(self, col.name)))
        return items

    def setConnection(cls, value):
        if isinstance(value, (str, unicode)):
            value = dbconnection.connectionForURI(value)
        cls._connection = value
    setConnection = classmethod(setConnection)

def capitalize(name):
    return name[0].capitalize() + name[1:]

def setterName(name):
    return '_set_%s' % name
def rawSetterName(name):
    return '_SO_set_%s' % name
def getterName(name):
    return '_get_%s' % name
def rawGetterName(name):
    return '_SO_get_%s' % name
def instanceName(name):
    return '_SO_val_%s' % name


class SelectResults(object):

    def __init__(self, sourceClass, clause, clauseTables=None,
                 **ops):
        self.sourceClass = sourceClass
        if clause is None or isinstance(clause, str) and clause == 'all':
            clause = sqlbuilder.SQLTrueClause
        self.clause = clause
        tablesDict = sqlbuilder.tablesUsedDict(self.clause)
        tablesDict[sourceClass._table] = 1
        if clauseTables:
            for table in clauseTables:
                tablesDict[table] = 1
        self.clauseTables = clauseTables
        self.tables = tablesDict.keys()
        self.ops = ops
        if self.ops.get('orderBy', NoDefault) is NoDefault:
            self.ops['orderBy'] = sourceClass._defaultOrder
        orderBy = self.ops['orderBy']
        if isinstance(orderBy, list) or isinstance(orderBy, tuple):
            orderBy = map(self._mungeOrderBy, orderBy)
        else:
            orderBy = self._mungeOrderBy(orderBy)
        #print "OUT: %r; in: %r" % (sourceClass.sqlrepr(orderBy), sourceClass.sqlrepr(self.ops['orderBy']))
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
            if self.sourceClass._SO_columnDict.has_key(orderBy):
                val = self.sourceClass._SO_columnDict[orderBy].dbName
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

    def accumulate(self, expression):
        """ Use an accumulate expression to select result
            using another SQL select through current
            connection.
            Return the accumulate result
        """
        conn = self.ops.get('connection', self.sourceClass._connection)
        return conn.accumulateSelect(self,expression)

    def count(self):
        """ Counting elements of current select results """
        assert not self.ops.get('distinct'), "It is not currently supported to count distinct objects"
            
        count = self.accumulate('COUNT(*)')
        if self.ops.get('start'):
            count -= self.ops['start']
        if self.ops.get('end'):
            count = min(self.ops['end'] - self.ops.get('start', 0), count)
        return count

    def sum(self, attribute):
        """ Making the sum of a given select result attribute.
            `attribute` can be a column name (like 'a_column')
            or a dot-q attribute (like Table.q.aColumn)
        """
        if type(attribute) == type(''):
            expression = 'SUM(%s)' % attribute
        else:
            expression = sqlbuilder.func.SUM(attribute)
        return self.accumulate(expression)

class SQLObjectState(object):

    def __init__(self, soObject):
        self.soObject = soObject
        self.protocol = 'sql'



########################################
## Utility functions (for external consumption)
########################################

def getID(obj):
    if isinstance(obj, SQLObject):
        return obj.id
    elif type(obj) is type(1):
        return obj
    elif type(obj) is type(1L):
        return int(obj)
    elif type(obj) is type(""):
        try:
            return int(obj)
        except ValueError:
            return obj
    elif obj is None:
        return None

def getObject(obj, klass):
    if type(obj) is type(1):
        return klass(obj)
    elif type(obj) is type(1L):
        return klass(int(obj))
    elif type(obj) is type(""):
        return klass(int(obj))
    elif obj is None:
        return None
    else:
        return obj

__all__ = ['NoDefault', 'SQLObject',
           'getID', 'getObject',
           'SQLObjectNotFound']
