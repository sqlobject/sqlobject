class Event(object):
    """
    Base event for all SQLObject events.

    In general the sender for these methods is the class, not the
    instance.
    """

class ClassCreateEvent(Event):
    """
    Event raised before class creation.  The sender is the superclass
    (in case of multiple superclasses, the first superclass).  The
    arguments are ``(new_class_name, bases, new_attrs, post_funcs)``.
    ``new_attrs`` is a dictionary and may be modified (but
    ``new_class_name`` and ``bases`` are immutable).  ``post_funcs``
    is an initially-empty list that can have callbacks appended to it.

    Note: at the time this event is called, the new class has not yet
    been created.  The functions in ``post_funcs`` will be called
    after the class is created, with the single arguments of
    ``(new_class)``.
    """

class InstanceCreateEvent(Event):
    """
    Called before an instance is created, with the class as the
    sender.  Called with the arguments ``(varargs, kwargs,
    post_funcs)``.  Both ``kwargs`` and ``varargs`` may be usefully
    modified (``varargs`` is converted from a tuple to a list before
    calling).  ``post_funcs`` is a list of callbacks, intended to have
    functions appended to it, and are called with the arguments
    ``(new_instance)``.

    Note: this is not called when an instance is created from an
    existing database row. (@@: Show the name be RowCreateEvent, or
    RowInsertEvent?)
    """

# @@: An event for getting a row?  But for each row, when doing a
# select?  For .sync, .syncUpdate, .expire?

class InstanceDestroyEvent(Event):
    """
    Called before an instance is deleted.  Sender is the instance's
    class.  Arguments are ``(instance)``.  You cannot cancel the delete,
    but you can raise an exception (which will probably cancel the
    delete, but also cause an uncaught exception if not expected).

    Note: this is not called when an instance is destroyed through
    garbage collection (@@: Should this be called RowDestroyEvent or
    RowDeleteEvent?)

    @@: Should this allow ``instance`` to be a primary key, so that a
    row can be deleted without first fetching it?
    """
    
class InstanceUpdateEvent(Event):
    """
    Called when an instance is updated through a call to ``.set()``.
    The arguments are ``(instance, kwargs)``.  ``kwargs`` can be
    modified.  This is run *before* the instance is updated; if you
    want to look at the current values, simply look at ``instance``.

    @@: Should this also catch single-column updates?  Should this
    only be run before updates go to the server?  Should this be
    called RowUpdateEvent?
    """

class AddColumnEvent(Event):
    """
    Called when a column is added to a class, with arguments ``(cls,
    column_name, column_definition)``.  This is called *after* the
    column has been added, and is called for each column after class
    creation.
    """

class DeleteColumnEvent(Event):
    """
    Called when a column is removed from a class, with the arguments
    ``(cls, column_name, column_definition)``.  Like
    ``AddColumnEvent`` this is called after the action has been
    performed, and is called for subclassing (when a column is
    implicitly removed by setting it to ``None``).
    """

# @@: Events for indexes and joins?  These are mostly event consumers,
# though.

class CreateTableEvent(Event):
    """
    Called when a table is created.  If ``ifNotExists==True`` and the
    table exists, this event is not called.

    Called with ``(cls, connection, post_funcs)``.  ``post_funcs``
    functions are called with ``(cls, connection)`` after the table
    has been created.
    """

class DropTableEvent(Event):
    """
    Called when a table is dropped.  If ``ifExists==True`` and the
    table doesn't exist, this event is not called.

    Called with ``(cls, connection, post_funcs)``.  ``post_funcs``
    functions are called with ``(cls, connection)`` after the table
    has been dropped.
    """

