"""
This is a not-very-formal outline of the interface that SQLObject
provides.  While its in the form of a formal interface, it doesn't
use any interface system.
"""


class Interface(object):
    pass


class ISQLObject(Interface):

    sqlmeta = """
    A class or instance representing internal state and methods for
    introspecting this class.

    ``MyClass.sqlmeta`` is a class, and ``myInstance.sqlmeta`` is an
    instance of this class.  So every instance gets its own instance
    of the metadata.

    This object follows the ``Isqlmeta`` interface.
    """

    # classmethod
    def get(id, connection=None):
        """
        Returns the object with the given `id`.  If `connection` is
        given, then get the object from the given connection
        (otherwise use the default or configured connection)

        It raises ``SQLObjectNotFound`` if no row exists with that ID.
        """

    # classmethod
    def selectBy(connection=None, **attrs):
        """
        Performs a ``SELECT`` in the given `connection` (or default
        connection).

        Each of the keyword arguments should be a column, and the
        equality comparisons will be ``ANDed`` together to produce the
        result.
        """

    # classmethod
    def dropTable(ifExists=False, dropJoinTables=True, cascade=False,
                  connection=None):
        """
        Drops this table from the database.  If ``ifExists`` is true,
        then it is not an error if the table doesn't exist.

        Join tables (mapping tables for many-to-many joins) are
        dropped if this class comes alphabetically before the other
        join class, and if ``dropJoinTables`` is true.

        ``cascade`` is passed to the connection, and if true tries to
        drop tables that depend on this table.
        """

    # classmethod
    def createTable(ifNotExists=False, createJoinTables=True,
                    createIndexes=True, connection=None):
        """
        Creates the table.  If ``ifNotExists`` is true, then it is not
        an error if the table already exists.

        Join tables (mapping tables for many-to-many joins) are
        created if this class comes alphabetically before the other
        join class, and if ``createJoinTables`` is true.

        If ``createIndexes`` is true, indexes are also created.
        """

    # classmethod
    def createTableSQL(createJoinTables=True, connection=None,
                       createIndexes=True):
        """
        Returns the SQL that would be sent with the analogous call
        to ``Class.createTable(...)``
        """

    def sync():
        """
        This will refetch the data from the database, putting it in
        sync with the database (in case another process has modified
        the database since this object was fetched).  It will raise
        ``SQLObjectNotFound`` if the row has been deleted.

        This will call ``self.syncUpdate()`` if ``lazyUpdates`` are
        on.
        """

    def syncUpdate():
        """
        If ``.sqlmeta.lazyUpdates`` is true, then this method must be
        called to push accumulated updates to the server.
        """

    def expire():
        """
        This will remove all the column information from the object.
        The next time this information is used, a ``SELECT`` will be
        made to re-fetch the data.  This is like a lazy ``.sync()``.
        """

    def set(**attrs):
        """
        This sets many column attributes at once.  ``obj.set(a=1,
        b=2)`` is equivalent to ``obj.a=1; obj.b=2``, except that it
        will be grouped into one ``UPDATE``
        """

    def destroySelf():
        """
        Deletes this row from the database.  This is called on
        instances, not on the class.  The object still persists,
        because objects cannot be deleted from the Python process
        (they can only be forgotten about, at which time they are
        garbage collected).  The object becomes obsolete, and further
        activity on it will raise errors.
        """

    def sqlrepr(obj, connection=None):
        """
        Returns the SQL representation of the given object, for the
        configured database connection.
        """


class Isqlmeta(Interface):

    table = """
    The name of the table in the database.  This is derived from
    ``style`` and the class name if no explicit name is given.
    """

    idName = """
    The name of the primary key column in the database.  This is
    derived from ``style`` if no explicit name is given.
    """

    idType = """
    A function that coerces/normalizes IDs when setting IDs.  This
    is ``int`` by default (all IDs are normalized to integers).
    """

    style = """
    An instance of the ``IStyle`` interface.  This maps Python
    identifiers to database names.
    """

    lazyUpdate = """
    A boolean (default false).  If true, then setting attributes on
    instances (or using ``inst.set(...)`` will not send ``UPDATE``
    queries immediately (you must call ``inst.syncUpdates()`` or
    ``inst.sync()`` first).
    """

    defaultOrder = """
    When selecting objects and not giving an explicit order, this
    attribute indicates the default ordering.  It is like this value
    is passed to ``.select()`` and related methods; see those method's
    documentation for details.
    """

    cacheValues = """
    A boolean (default true).  If true, then the values in the row are
    cached as long as the instance is kept (and ``inst.expire()`` is
    not called).  If false, then every attribute access causes a
    ``SELECT`` (which is absurdly inefficient).
    """

    registry = """
    Because SQLObject uses strings to relate classes, and these
    strings do not respect module names, name clashes will occur if
    you put different systems together.  This string value serves
    as a namespace for classes.
    """

    fromDatabase = """
    A boolean (default false).  If true, then on class creation the
    database will be queried for the table's columns, and any missing
    columns (possible all columns) will be added automatically.
    """

    columns = """
    A dictionary of ``{columnName: anSOColInstance}``.  You can get
    information on the columns via this read-only attribute.
    """

    columnList = """
    A list of the values in ``columns``.  Sometimes a stable, ordered
    version of the columns is necessary; this is used for that.
    """

    columnDefinitions = """
    A dictionary like ``columns``, but contains the original column
    definitions (which are not class-specific, and have no logic).
    """

    joins = """
    A list of all the Join objects for this class.
    """

    indexes = """
    A list of all the indexes for this class.
    """

    # Instance attributes

    expired = """
    A boolean.  If true, then the next time this object's column
    attributes are accessed a query will be run.
    """

    # Methods

    def addColumn(columnDef, changeSchema=False, connection=None):
        """
        Adds the described column to the table.  If ``changeSchema``
        is true, then an ``ALTER TABLE`` query is called to change the
        database.

        Attributes given in the body of the SQLObject subclass are
        collected and become calls to this method.
        """

    def delColumn(column, changeSchema=False, connection=None):
        """
        Removes the given column (either the definition from
        ``columnDefinition`` or the SOCol object from ``columns``).

        If ``changeSchema`` is true, then an ``ALTER TABLE`` query is
        made.
        """

    def addColumnsFromDatabase(connection=None):
        """
        Adds all the columns from the database that are not already
        defined.  If the ``fromDatabase`` attribute is true, then
        this is called on class instantiation.
        """

    def addJoin(joinDef):
        """
        Adds a join to the class.
        """

    def delJoin(joinDef):
        """
        Removes a join from the class.
        """

    def addIndex(indexDef):
        """
        Adds the index to the class.
        """

    def asDict():
        """
        Returns the SQLObject instance as a dictionary (column names
        as keys, column values as values).

        Use like::

            ASQLObjectClass(a=1, b=2).asDict()

        Which should return ``{'a': 1, 'b': 2}``.

        Note: this is a *copy* of the object's columns; changing the
        dictionary will not effect the object it was created from.
        """


class ICol(Interface):

    def __init__(name=None, **kw):
        """
        Creates a column definition.  This is an object that describes
        a column, basically just holding the keywords for later
        creating an ``SOCol`` (or subclass) instance.  Subclasses of
        ``Col`` (which implement this interface) typically create the
        related subclass of ``SOCol``.
        """

    name = """
    The name of the column.  If this is not given in the constructor,
    ``SQLObject`` will set this attribute from the variable name this
    object is assigned to.
    """


class ISOCol(Interface):

    """
    This is a column description that is bound to a single class.
    This cannot be shared by subclasses, so a new instance is created
    for every new class (in cases where classes share columns).

    These objects are created by ``Col`` instances, you do not create
    them directly.
    """

    name = """
    The name of the attribute that points to this column.  This is the
    Python name of the column.
    """

    columnDef = """
    The ``Col`` object that created this instance.
    """

    immutable = """
    Boolean, default false.  If true, then this column cannot be
    modified.  It cannot even be modified at construction, rendering
    the table read-only.  This will probably change in the future, as
    it renders the option rather useless.
    """

    cascade = """
    If a foreign key, then this indicates if deletes in that foreign
    table should cascade into this table.  This can be true (deletes
    cascade), false (the default, they do not cascade), or ``'null'``
    (this column is set to ``NULL`` if the foreign key is deleted).
    """

    constraints = """
    A list of ... @@?
    """

    notNone = """
    Boolean, default false.  It true, then ``None`` (aka ``NULL``) is
    not allowed in this column.  Also the ``notNull`` attribute can be
    used.
    """

    foreignKey = """
    If not None, then this column points to another table.  The
    attribute is the name (a string) of that table/class.
    """

    dbName = """
    The name of this column in the database.
    """

    alternateID = """
    Boolean, default false.  If true, then this column is assumed to
    be unique, and you can fetch individual rows based on this
    column's value.  This will add a method ``byAttributeName`` to the
    parent SQLObject subclass.
    """

    unique = """
    Boolean, default false.  If this column is unique; effects the
    database ``CREATE`` statement, and is implied by
    ``alternateID=True``.
    """

    validator = """
    A IValidator object.  All setting of this column goes through the
    ``fromPython`` method of the validator.  All getting of this
    column from the database goes through ``toPython``.
    """

    default = """
    A value that holds the default value for this column.  If the
    default value passed in is a callable, then that value is called
    to return a default (a typical example being ``DateTime.now``).
    """

    sqlType = """
    The SQL type of the column, overriding the default column type.
    """
