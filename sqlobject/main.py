"""
SQLObject.py
    Ian Bicking <ianb@colorstudy.com> 17 Oct 2002
SQLObject is a object-relational mapper.  See SQLObject.html or
SQLObject.txt for more.

Modified by
    Daniel Savard, Xsoli Inc <sqlobject xsoli.com> 7 Feb 2004
    - Added support for simple table inheritance.

    Oleg Broytmann, SIA "ANK" <phd@phd.pp.ru> 3 Feb 2005
    - Split inheritance support into a number of separate modules and classes -
      InheritableSQLObject at al.

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
import declarative
from sresults import SelectResults

import sys
if sys.version_info[:3] < (2, 2, 0):
    raise ImportError, "SQLObject requires Python 2.2.0 or later"

NoDefault = sqlbuilder.NoDefault

class SQLObjectNotFound(LookupError): pass
class SQLObjectIntegrityError(Exception): pass

True, False = 1==1, 0==1

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

def findDependencies(name, registry=None):
    depends = []
    for klass in classregistry.registry(registry).allClasses():
        if findDependantColumns(name, klass):
            depends.append(klass)
    return depends

def findDependantColumns(name, klass):
    depends = []
    for col in klass.sqlmeta._columns:
        if col.foreignKey == name and col.cascade is not None:
            depends.append(col)
    return depends

class CreateNewSQLObject:
    """
    Dummy singleton to use in place of an ID, to signal we want
    a new object.
    """
    pass

class sqlmeta(object):

    """
    This object is the object we use to keep track of all sorts of
    information.  Subclasses are made for each SQLObject subclass
    (dynamically if necessary), and instances are created to go
    alongside every SQLObject instance.
    """

    table = None
    idName = None
    style = None
    lazyUpdate = False
    defaultOrder = None
    cacheValues = True
    registry = None

    __metaclass__ = declarative.DeclarativeMeta

    # These attributes shouldn't be shared with superclasses:
    _unshared_attributes = ['table', 'idName']

    # These are internal bookkeeping attributes; the class-level
    # definition is a default for the instances, instances will
    # reset these values.

    # When an object is being created, it has an instance
    # variable _creating, which is true.  This way all the
    # setters can be captured until the object is complete,
    # and then the row is inserted into the database.  Once
    # that happens, _creating is deleted from the instance,
    # and only the class variable (which is always false) is
    # left.
    _creating = False
    _obsolete = False
    _perConnection = False

    def __classinit__(cls, new_attrs):
        for attr in cls._unshared_attributes:
            if not new_attrs.has_key(attr):
                setattr(cls, attr, None)

    def __init__(self, instance):
        self.instance = instance

    def setClass(cls, soClass):
        cls.soClass = soClass
        if not cls.style:
            if cls.soClass._connection and cls.soClass._connection.style:
                cls.style = cls.soClass._connection.style
            else:
                cls.style = styles.defaultStyle
        if cls.table is None:
            cls.table = cls.style.pythonClassToDBTable(cls.soClass.__name__)
        if cls.idName is None:
            cls.idName = cls.style.idForTable(cls.table)

        # plainSetters are columns that haven't been overridden by the
        # user, so we can contact the database directly to set them.
        # Note that these can't set these in the SQLObject class
        # itself, because they specific to this subclass of SQLObject,
        # and cannot be shared among classes.
        cls._plainSetters = {}
        cls._plainGetters = {}
        cls._plainForeignSetters = {}
        cls._plainForeignGetters = {}
        cls._plainJoinGetters = {}
        cls._plainJoinAdders = {}
        cls._plainJoinRemovers = {}

        # This is a dictionary of columnName: columnObject
        cls._columnDict = {}
        cls._columns = []

        # We keep track of the different joins by index,
        # putting them in this list.
        cls._joinList = []
        cls._joinDict = {}
        cls._indexList = []

    setClass = classmethod(setClass)

class _sqlmeta_attr(object):

    def __init__(self, name, deprecation_level):
        self.name = name
        self.deprecation_level = deprecation_level

    def __get__(self, obj, type=None):
        if self.deprecation_level is not None:
            deprecated(
                'Use of this attribute should be replaced with '
                '.sqlmeta.%s' % self.name, level=self.deprecation_level)
        return getattr((type or obj).sqlmeta, self.name)


# @@: This should become a public interface or documented or
# something.  Turning it on gives earlier warning about things
# that will be deprecated (having this off we won't flood people
# with warnings right away).
warnings_level = 1
exception_level = None
# Current levels:
#  1) Actively deprecated in version after 0.6.1 (0.7?); removed after
#  2) Deprecated after 1 (0.8?)
#  3) Deprecated after 2 (0.9?)

def deprecated(message, level=1, stacklevel=2):
    if exception_level is not None and exception_level <= level:
        raise NotImplementedError(message)
    if warnings_level is not None and warnings_level <= level:
        warnings.warn(message, DeprecationWarning, stacklevel=stacklevel)

# SQLObject is the superclass for all SQLObject classes, of
# course.  All the deeper magic is done in MetaSQLObject, and
# only lesser magic is done here.  All the actual work is done
# here, though -- just automatic method generation (like
# methods and properties for each column) is done in
# MetaSQLObject.
class SQLObject(object):

    __metaclass__ = declarative.DeclarativeMeta

    # Sometimes an intance is attached to a connection, not
    # globally available.  In that case, self._SO_perConnection
    # will be true.  It's false by default:
    _SO_perConnection = False

    _connection = None

    _columns = []

    _joins = []

    _indexes = []

    _fromDatabase = False

    # Default is false, but we set it to true for the *instance*
    # when necessary: (bad clever? maybe)
    _expired = False

    # This function is used to coerce IDs into the proper format,
    # so you should replace it with str, or another function, if you
    # aren't using integer IDs
    _idType = int

    sqlmeta = sqlmeta

    #DSM: The _inheritable attribute controls wheter the class can by
    #DSM: inherited 'logically' with a foreignKey and back reference.
    _inheritable = False # Does this class is inheritable
    _parentClass = None # A reference to the parent class
    _parent = None # A reference to the parent instance
    _childClasses = {} # Reference to child classes
    childName = None # Children name (to be able to get a subclass)

    # The law of Demeter: the class should not call another classes by name
    SelectResultsClass = SelectResults

    def __classinit__(cls, new_attrs):

        # This is true if we're initializing the SQLObject class,
        # instead of a subclass:
        is_base = cls.__bases__ == (object,)
        #assert cls.__name__ != 'Reparented1'

        if (not new_attrs.has_key('sqlmeta')
            and not is_base):
            # We have to create our own subclass, usually.
            # type(className, bases_tuple, attr_dict) creates a new
            # subclass:
            #cls.sqlmeta = cls.sqlmeta.clone()
            cls.sqlmeta = type('sqlmeta', (cls.sqlmeta,), {})
        if not issubclass(cls.sqlmeta, sqlmeta):
            # We allow no superclass and an object superclass, instead
            # of inheriting from sqlmeta; but in that case we replace
            # the class and just move over its attributes:
            assert cls.sqlmeta.__bases__ in ((), (object,)), (
                "If you do not inherit your sqlmeta class from "
                "sqlobject.sqlmeta, it must not inherit from any other "
                "class (your sqlmeta inherits from: %s)"
                % cls.sqlmeta.__bases__)
            for base in cls.__bases__:
                superclass = getattr(base, 'sqlmeta', None)
                if superclass:
                    break
            else:
                assert 0, (
                    "No sqlmeta class could be found in any superclass "
                    "(while fixing up sqlmeta %r inheritance)"
                    % cls.sqlmeta)
            values = dict(cls.sqlmeta.__dict__)
            for key in values.keys():
                if key.startswith('__') and key.endswith('__'):
                    # Magic values shouldn't be passed through:
                    del values[key]
            cls.sqlmeta = type('sqlmeta', (superclass,), values)

        cls.sqlmeta.setClass(cls)

        implicitColumns = []
        implicitJoins = []
        implicitIndexes = []
        for attr, value in new_attrs.items():
            if isinstance(value, col.Col):
                value.name = attr
                implicitColumns.append(value)
                delattr(cls, attr)
                continue
            if isinstance(value, joins.Join):
                value.joinMethodName = attr
                implicitJoins.append(value)
                delattr(cls, attr)
                continue
            if isinstance(value, index.DatabaseIndex):
                value.setName(attr)
                implicitIndexes.append(value)
                delattr(cls, attr)
                continue

        if not is_base:
            cls._cleanDeprecatedAttrs(new_attrs)

        if new_attrs.has_key('_connection'):
            connection = new_attrs['_connection']
            del cls._connection
            assert not new_attrs.has_key('connection')
        elif new_attrs.has_key('connection'):
            connection = new_attrs['connection']
            del cls.connection
        else:
            connection = None

        cls._SO_finishedClassCreation = False

        # We fix up the columns here -- replacing any strings with
        # simply-contructed Col objects, and searching the class
        # variables for instances of Col objects (which get put into
        # the _columns instance variable and deleted).
        columns = []
        for column in new_attrs.get('_columns', []):
            if isinstance(column, str):
                column = col.Col(column)
            columns.append(column)
        if columns:
            cls._columns = columns

        # We append to _columns, but we don't want to change the
        # superclass's _columns list, so we make a copy if necessary
        if not new_attrs.has_key('_columns'):
            cls._columns = cls._columns[:]

        #DSM: Need to know very soon if the class is a child of an
        #DSM: inheritable class. If so, we keep a link to our parent class.
        cls._childClasses = {}
        for _cls in cls.__bases__:
            if hasattr(_cls, '_inheritable') and _cls._inheritable:
                cls._parentClass = _cls
                cls._parent = None
                _cls._childClasses[cls.__name__] = cls

        #DSM: If this class is a child of a parent class, we need to do some
        #DSM: attribute check and a a foreign key to the parent.
        if cls._parentClass:
            #DSM: First, look for invalid column name:
            #DSM: reserved ones or same as a parent
            parentCols = [column.name for column in cls._columns]
            for column in implicitColumns:
                cname = column.name
                if cname in ['childName']:
                    raise AttributeError, \
                        "The column name '%s' is reserved" % cname
                if cname in parentCols:
                    raise AttributeError, "The column '%s' is already " \
                        "defined in an inheritable parent" % cname
            #DSM: Remove columns if inherited from an inheritable class
            #DSM: as we don't want them.  All we want is a foreign key
            #DSM: that will link to our parent
            cls._columns = []
        #DSM: If this is inheritable, add some default columns
        #    to be able to link to children
        if hasattr(cls, '_inheritable') and cls._inheritable:
            cls._columns.append(
                col.StringCol(name='childName',default=None))

        cls._columns.extend(implicitColumns)
        if not new_attrs.has_key('_joins'):
            cls._joins = cls._joins[:]
        cls._joins.extend(implicitJoins)
        if not new_attrs.has_key('_indexes'):
            cls._indexes = cls._indexes[:]
        cls._indexes.extend(implicitIndexes)

        ######################################################
        # Set some attributes to their defaults, if necessary.
        # First we get the connection:
        if not connection and not getattr(cls, '_connection', None):
            mod = sys.modules[cls.__module__]
            # See if there's a __connection__ global in
            # the module, use it if there is.
            if hasattr(mod, '__connection__'):
                connection = mod.__connection__

        if connection or not hasattr(cls, '_connection'):
            cls.setConnection(connection)

        # We have to check if there are columns in the inherited
        # _columns where the attribute has been set to None in this
        # class.  If so, then we need to remove that column from
        # _columns.
        for column in cls._columns[:]:
            if (new_attrs.has_key(column.name)
                and new_attrs[column.name] is None):
                cls._columns.remove(column)

        for column in cls._columns:
            cls.addColumn(column)
        if cls._fromDatabase:
            cls.addColumnsFromDatabase()

        ########################################
        # Now we do the joins:

        for join in cls._joins:
            cls.addJoin(join)

        # We don't setup the properties until we're finished with the
        # batch adding of all the columns...
        cls._SO_finishedClassCreation = True
        makeProperties(cls)

        for idx in cls._indexes:
            cls.addIndex(idx)

        # We use the magic "q" attribute for accessing lazy
        # SQL where-clause generation.  See the sql module for
        # more.
        if not is_base:
            cls.q = sqlbuilder.SQLObjectTable(cls)

            #DSM: If we are a child, get the q magic from the parent
            currentClass = cls
            while currentClass._parentClass:
                currentClass = currentClass._parentClass
                for column in currentClass._columns:
                    if type(column) == col.ForeignKey: continue
                    setattr(cls.q, column.name,
                        getattr(currentClass.q, column.name))

        classregistry.registry(cls.sqlmeta.registry).addClass(cls)

    _style = _sqlmeta_attr('style', 2)
    _table = _sqlmeta_attr('table', 2)
    _idName = _sqlmeta_attr('idName', 2)
    _lazyUpdate = _sqlmeta_attr('lazyUpdate', 2)
    _defaultOrder = _sqlmeta_attr('defaultOrder', 2)
    _cacheValues = _sqlmeta_attr('cacheValues', 2)
    _registry = _sqlmeta_attr('registry', 2)

    def _cleanDeprecatedAttrs(cls, new_attrs):
        for attr in ['_table', '_lazyUpdate', '_style', '_idName',
                     '_defaultOrder', '_cacheValues', '_registry']:
            if new_attrs.has_key(attr):
                new_name = attr[1:]
                deprecated("'%s' is deprecated; please set the '%s' "
                           "attribute in sqlmeta instead" %
                           (attr, new_name), level=2,
                           stacklevel=5)
                setattr(cls.sqlmeta, new_name, new_attrs[attr])
                delattr(cls, attr)

    _cleanDeprecatedAttrs = classmethod(_cleanDeprecatedAttrs)

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
        cls.sqlmeta._indexList.append(index)
    addIndex = classmethod(addIndex)

    def addColumn(cls, columnDef, changeSchema=False, connection=None):
        column = columnDef.withClass(cls)
        name = column.name
        assert name != 'id', "The 'id' column is implicit, and should not be defined as a column"
        cls.sqlmeta._columnDict[name] = column
        cls.sqlmeta._columns.append(column)

        if columnDef not in cls._columns:
            cls._columns.append(columnDef)

        ###################################################
        # Create the getter function(s).  We'll start by
        # creating functions like _SO_get_columnName,
        # then if there's no function named _get_columnName
        # we'll alias that to _SO_get_columnName.  This
        # allows a sort of super call, even though there's
        # no superclass that defines the database access.
        if cls.sqlmeta.cacheValues:
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
        if not hasattr(cls, getterName(name)) or (name == 'childName'):
            setattr(cls, getterName(name), getter)
            cls.sqlmeta._plainGetters[name] = 1

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
            if not hasattr(cls, setterName(name)) or (name == 'childName'):
                setattr(cls, setterName(name), setter)
                # We keep track of setters that haven't been
                # overridden, because we can combine these
                # set columns into one SQL UPDATE query.
                cls.sqlmeta._plainSetters[name] = 1

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
            if cls.sqlmeta.cacheValues:
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
                cls.sqlmeta._plainForeignGetters[name[:-2]] = 1

            if not column.immutable:
                # The setter just gets the ID of the object,
                # and then sets the real column.
                setter = eval('lambda self, val: setattr(self, %s, self._SO_getID(val))' % (repr(name)))
                setattr(cls, rawSetterName(name)[:-2], setter)
                if not hasattr(cls, setterName(name)[:-2]):
                    setattr(cls, setterName(name)[:-2], setter)
                    cls.sqlmeta._plainForeignSetters[name[:-2]] = 1

            # We'll need to put in a real reference at
            # some point.  See needSet at the top of the
            # file for more on this.
            classregistry.registry(cls.sqlmeta.registry).addClassCallback(
                column.foreignKey,
                lambda foreign, me, attr: setattr(me, attr, foreign),
                cls, '_SO_class_%s' % column.foreignKey)

        if column.alternateMethodName:
            func = eval('lambda cls, val, connection=None: cls._SO_fetchAlternateID(%s, %s, val, connection=connection)' % (repr(column.name), repr(column.dbName)))
            setattr(cls, column.alternateMethodName, classmethod(func))

        if changeSchema:
            conn = connection or cls._connection
            conn.addColumn(cls.sqlmeta.table, column)

        if cls._SO_finishedClassCreation:
            makeProperties(cls)

    addColumn = classmethod(addColumn)

    def addColumnsFromDatabase(cls, connection=None):
        conn = connection or cls._connection
        for columnDef in conn.columnsFromSchema(cls.sqlmeta.table, cls):
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
            column = cls.sqlmeta._columnDict[column]
        if isinstance(column, col.Col):
            for c in cls.sqlmeta._columns:
                if column is c.columnDef:
                    column = c
                    break
        cls.sqlmeta._columns.remove(column)
        cls._columns.remove(column.columnDef)
        name = column.name
        del cls.sqlmeta._columnDict[name]
        delattr(cls, rawGetterName(name))
        if cls.sqlmeta._plainGetters.has_key(name):
            delattr(cls, getterName(name))
        delattr(cls, rawSetterName(name))
        if cls.sqlmeta._plainSetters.has_key(name):
            delattr(cls, setterName(name))
        if column.foreignKey:
            delattr(cls, rawGetterName(name)[:-2])
            if cls.sqlmeta._plainForeignGetters.has_key(name[:-2]):
                delattr(cls, getterName(name)[:-2])
            delattr(cls, rawSetterName(name)[:-2])
            if cls.sqlmeta._plainForeignSetters.has_key(name[:-2]):
                delattr(cls, setterName(name)[:-2])
        if column.alternateMethodName:
            delattr(cls, column.alternateMethodName)

        if changeSchema:
            conn = connection or cls._connection
            conn.delColumn(cls.sqlmeta.table, column)

        if cls._SO_finishedClassCreation:
            unmakeProperties(cls)

    delColumn = classmethod(delColumn)

    def addJoin(cls, joinDef):
        # The name of the method we'll create.  If it's
        # automatically generated, it's generated by the
        # join class.
        join = joinDef.withClass(cls)
        meth = join.joinMethodName
        cls.sqlmeta._joinDict[joinDef] = join

        cls.sqlmeta._joinList.append(join)
        index = len(cls.sqlmeta._joinList)-1
        if joinDef not in cls._joins:
            cls._joins.append(joinDef)

        # The function fetches the join by index, and
        # then lets the join object do the rest of the
        # work:
        func = eval('lambda self: self.sqlmeta._joinList[%i].performJoin(self)' % index)

        # And we do the standard _SO_get_... _get_... deal
        setattr(cls, rawGetterName(meth), func)
        if not hasattr(cls, getterName(meth)):
            setattr(cls, getterName(meth), func)
            cls.sqlmeta._plainJoinGetters[meth] = 1

        # Some joins allow you to remove objects from the
        # join.
        if hasattr(join, 'remove'):

            # Again, we let it do the remove, and we do the
            # standard naming trick.
            func = eval('lambda self, obj: self.sqlmeta._joinList[%i].remove(self, obj)' % index)
            setattr(cls, '_SO_remove' + join.addRemoveName, func)
            if not hasattr(cls, 'remove' + join.addRemoveName):
                setattr(cls, 'remove' + join.addRemoveName, func)
                cls.sqlmeta._plainJoinRemovers[meth] = 1

        # Some joins allow you to add objects.
        if hasattr(join, 'add'):

            # And again...
            func = eval('lambda self, obj: self.sqlmeta._joinList[%i].add(self, obj)' % (len(cls.sqlmeta._joinList)-1))
            setattr(cls, '_SO_add' + join.addRemoveName, func)
            if not hasattr(cls, 'add' + join.addRemoveName):
                setattr(cls, 'add' + join.addRemoveName, func)
                cls.sqlmeta._plainJoinAdders[meth] = 1

        if cls._SO_finishedClassCreation:
            makeProperties(cls)

    addJoin = classmethod(addJoin)

    def delJoin(cls, joinDef):
        join = cls.sqlmeta._joinDict[joinDef]
        meth = join.joinMethodName
        cls._joins.remove(joinDef)
        del cls.sqlmeta._joinDict[joinDef]
        for i in range(len(cls.sqlmeta._joinList)):
            if cls.sqlmeta._joinList[i] is joinDef:
                # Have to leave None, because we refer to joins
                # by index.
                cls.sqlmeta._joinList[i] = None
        delattr(cls, rawGetterName(meth))
        if cls.sqlmeta._plainJoinGetters.has_key(meth):
            delattr(cls, getterName(meth))
        if hasattr(join, 'remove'):
            delattr(cls, '_SO_remove' + join.addRemovePrefix)
            if cls.sqlmeta._plainJoinRemovers.has_key(meth):
                delattr(cls, 'remove' + join.addRemovePrefix)
        if hasattr(join, 'add'):
            delattr(cls, '_SO_add' + join.addRemovePrefix)
            if cls.sqlmeta._plainJoinAdders.has_key(meth):
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
        # We shadow the sqlmeta class with an instance of sqlmeta
        # that points to us (our sqlmeta buddy object; where the
        # sqlmeta class is our class's buddy class)
        self.sqlmeta = self.__class__.sqlmeta(self)
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
            dbNames = [col.dbName for col in self.sqlmeta._columns]
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
                dbNames = [col.dbName for col in self.sqlmeta._columns]
                selectResults = self._connection._SO_selectOne(self, dbNames)
                if not selectResults:
                    raise SQLObjectNotFound, "The object %s by the ID %s has been deleted" % (self.__class__.__name__, self.id)
                self._SO_selectInit(selectResults)
                result = getattr(self, attrName)
                return result
            finally:
                self._SO_writeLock.release()

    def sync(self):
        if self.sqlmeta.lazyUpdate and self._SO_createValues:
            self.syncUpdate()
        self._SO_writeLock.acquire()
        try:
            dbNames = [col.dbName for col in self.sqlmeta._columns]
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
            if self.sqlmeta._columnDict:
                values = [(self.sqlmeta._columnDict[v[0]].dbName, v[1])
                          for v in self._SO_createValues.items()]
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
            for column in self.sqlmeta._columns:
                delattr(self, instanceName(column.name))
            self._expired = True
            self._connection.cache.expire(self.id, self.__class__)
        finally:
            self._SO_writeLock.release()

    def _SO_setValue(self, name, value, fromPython, toPython):
        # This is the place where we actually update the
        # database.

        # If we are _creating, the object doesn't yet exist
        # in the database, and we can't insert it until all
        # the parts are set.  So we just keep them in a
        # dictionary until later:
        if fromPython:
            dbValue = fromPython(value, self._SO_validatorState)
        else:
            dbValue = value
        if toPython:
            value = toPython(dbValue, self._SO_validatorState)
        if self.sqlmeta._creating or self.sqlmeta.lazyUpdate:
            self.dirty = True
            self._SO_createValues[name] = dbValue
            setattr(self, instanceName(name), value)
            return

        self._connection._SO_update(
            self, [(self.sqlmeta._columnDict[name].dbName,
                    dbValue)])

        if self.sqlmeta.cacheValues:
            setattr(self, instanceName(name), value)

    def set(self, **kw):
        # set() is used to update multiple values at once,
        # potentially with one SQL statement if possible.

        # Filter out items that don't map to column names.
        # Those will be set directly on the object using
        # setattr(obj, name, value).
        is_column = self.sqlmeta._plainSetters.has_key
        f_is_column = lambda item: is_column(item[0])
        f_not_column = lambda item: not is_column(item[0])
        items = kw.items()
        extra = dict(filter(f_not_column, items))
        kw = dict(filter(f_is_column, items))

        # _creating is special, see _SO_setValue
        if self.sqlmeta._creating or self.sqlmeta.lazyUpdate:
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
                    if name not in self.sqlmeta._columnDict:
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
                if self.sqlmeta.cacheValues:
                    setattr(self, instanceName(name), value)
                toUpdate[name] = dbValue
            for name, value in extra.items():
                try:
                    getattr(self.__class__, name)
                except AttributeError:
                    if name not in self.sqlmeta._columnDict:
                        raise TypeError, "%s.set() got an unexpected keyword argument %s" % (self.__class__.__name__, name)
                try:
                    setattr(self, name, value)
                except AttributeError, e:
                    raise AttributeError, '%s (with attribute %r)' % (e, name)

            if toUpdate:
                args = [(self.sqlmeta._columnDict[name].dbName, value)
                        for name, value in toUpdate.items()]
                self._connection._SO_update(self, args)
        finally:
            self._SO_writeLock.release()

    def _SO_selectInit(self, row):
        for col, colValue in zip(self.sqlmeta._columns, row):
            if col.toPython:
                colValue = col.toPython(colValue, self._SO_validatorState)
            setattr(self, instanceName(col.name), colValue)

    def _SO_getValue(self, name):
        # Retrieves a single value from the database.  Simple.
        assert not self.sqlmeta._obsolete, (
            "%s with id %s has become obsolete" \
            % (self.__class__.__name__, self.id))
        # @@: do we really need this lock?
        #self._SO_writeLock.acquire()
        column = self.sqlmeta._columnDict[name]
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

        self.sqlmeta._creating = True
        self._SO_createValues = {}
        self._SO_validatorState = SQLObjectState(self)

        # First we do a little fix-up on the keywords we were
        # passed:
        for column in self.sqlmeta._columns:

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
        names = [self.sqlmeta._columnDict[v[0]].dbName for v in setters]
        values = [v[1] for v in setters]
        # Get rid of _SO_create*, we aren't creating anymore.
        # Doesn't have to be threadsafe because we're still in
        # new(), which doesn't need to be threadsafe.
        self.dirty = False
        if not self.sqlmeta.lazyUpdate:
            del self._SO_createValues
        else:
            self._SO_createValues = {}
        del self.sqlmeta._creating

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

    def _findAlternateID(cls, name, dbName, value, connection=None):
        return (connection or cls._connection)._SO_selectOneAlt(
            cls,
            [cls.sqlmeta.idName] +
            [col.dbName for col in cls.sqlmeta._columns],
            dbName,
            value), None
    _findAlternateID = classmethod(_findAlternateID)

    def _SO_fetchAlternateID(cls, name, dbName, value, connection=None):
        result, obj = cls._findAlternateID(name, dbName, value, connection)
        if not result:
            raise SQLObjectNotFound, "The %s by alternateID %s=%s does not exist" % (cls.__name__, name, repr(value))
        if obj:
           return obj
        if connection:
            obj = cls.get(result[0], connection=connection)
        else:
            obj = cls.get(result[0])
        if not obj.sqlmeta.cacheValues:
            obj._SO_writeLock.acquire()
            try:
                obj._SO_selectInit(result[1:])
            finally:
                obj._SO_writeLock.release()
        return obj
    _SO_fetchAlternateID = classmethod(_SO_fetchAlternateID)

    def _SO_depends(cls):
        return findDependencies(cls.__name__, cls.sqlmeta.registry)
    _SO_depends = classmethod(_SO_depends)

    def select(cls, clause=None, clauseTables=None,
               orderBy=NoDefault, limit=None,
               lazyColumns=False, reversed=False,
               distinct=False,
               connection=None):
        return cls.SelectResultsClass(cls, clause,
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
        return cls.SelectResultsClass(cls,
                             conn._SO_columnClause(cls, kw),
                             connection=conn)

    selectBy = classmethod(selectBy)

    def dropTable(cls, ifExists=False, dropJoinTables=True, cascade=False,
                  connection=None):
        conn = connection or cls._connection
        if ifExists and not conn.tableExists(cls.sqlmeta.table):
            return
        conn.dropTable(cls.sqlmeta.table, cascade)
        if dropJoinTables:
            cls.dropJoinTables(ifExists=ifExists, connection=conn)
    dropTable = classmethod(dropTable)

    def createTable(cls, ifNotExists=False, createJoinTables=True,
                    createIndexes=True,
                    connection=None):
        conn = connection or cls._connection
        if ifNotExists and conn.tableExists(cls.sqlmeta.table):
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
        for index in cls.sqlmeta._indexList:
            if not index:
                continue
            conn._SO_createIndex(cls, index)
    createIndexes = classmethod(createIndexes)

    def _getJoinsToCreate(cls):
        joins = []
        for join in cls.sqlmeta._joinList:
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
        for join in cls.sqlmeta._joinList:
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
        conn.clearTable(cls.sqlmeta.table)
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
        self.sqlmeta._obsolete = True
        self._connection._SO_delete(self)
        self._connection.cache.expire(self.id, self.__class__)

    def delete(cls, id, connection=None):
        obj = cls.get(id, connection=connection)
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
        for col in self.sqlmeta._columns:
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

__all__ = ['NoDefault', 'SQLObject', 'sqlmeta',
           'getID', 'getObject',
           'SQLObjectNotFound']
