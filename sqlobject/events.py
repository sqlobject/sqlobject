from sqlobject.include.pydispatch import dispatcher
from weakref import ref


subclassClones = {}

def listen(receiver, soClass, signal, alsoSubclasses=True):
    """
    Listen for the given ``signal`` on the SQLObject subclass
    ``soClass``, calling ``receiver()`` when ``send(soClass, signal,
    ...)`` is called.

    If ``alsoSubclasses`` is true, receiver will also be called when
    an event is fired on any subclass.
    """
    dispatcher.connect(receiver, signal=signal, sender=soClass)
    weakSOClass = ref(soClass)
    weakReceiver = ref(receiver)
    subclassClones.setdefault(weakSOClass, []).append((weakReceiver, signal))

# We export this function:
send = dispatcher.send

class Signal(object):
    """
    Base event for all SQLObject events.

    In general the sender for these methods is the class, not the
    instance.
    """

class ClassCreateSignal(Signal):
    """
    Signal raised before class creation.  The sender is the superclass
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

def _makeSubclassConnections(new_class_name, bases, new_attrs, post_funcs):
    post_funcs.append(_makeSubclassConnectionsPost)

def _makeSubclassConnectionsPost(new_class):
    for cls in new_class.__bases__:
        for weakReceiver, signal in subclassClones.get(cls, []):
            receiver = weakReceiver()
            if not receiver:
                continue
            dispatcher.connect(receiver, signal=signal, sender=new_class)

dispatcher.connect(_makeSubclassConnections, signal=ClassCreateSignal)

# @@: Should there be a class reload event?  This would allow modules
# to be reloaded, possibly.  Or it could even be folded into
# ClassCreateSignal, since anything that listens to that needs to pay
# attention to reloads (or else it is probably buggy).

class RowCreateSignal(Signal):
    """
    Called before an instance is created, with the class as the
    sender.  Called with the arguments ``(kwargs, post_funcs)``.
    There may be a ``connection`` argument.  ``kwargs``may be usefully
    modified.  ``post_funcs`` is a list of callbacks, intended to have
    functions appended to it, and are called with the arguments
    ``(new_instance)``.

    Note: this is not called when an instance is created from an
    existing database row.
    """

# @@: An event for getting a row?  But for each row, when doing a
# select?  For .sync, .syncUpdate, .expire?

class RowDestroySignal(Signal):
    """
    Called before an instance is deleted.  Sender is the instance's
    class.  Arguments are ``(instance)``.  You cannot cancel the delete,
    but you can raise an exception (which will probably cancel the
    delete, but also cause an uncaught exception if not expected).

    Note: this is not called when an instance is destroyed through
    garbage collection.

    @@: Should this allow ``instance`` to be a primary key, so that a
    row can be deleted without first fetching it?
    """
    
class RowUpdateSignal(Signal):
    """
    Called when an instance is updated through a call to ``.set()``.
    The arguments are ``(instance, kwargs)``.  ``kwargs`` can be
    modified.  This is run *before* the instance is updated; if you
    want to look at the current values, simply look at ``instance``.

    @@: Should this also catch single-column updates?  Should this
    only be run before updates go to the server?  Should this be
    called RowUpdateSignal?
    """

class AddColumnSignal(Signal):
    """
    Called when a column is added to a class, with arguments ``(cls,
    connection, column_name, column_definition, changeSchema,
    post_funcs)``.  This is called *after* the column has been added,
    and is called for each column after class creation.

    post_funcs are called with ``(cls, so_column_obj)``
    """

class DeleteColumnSignal(Signal):
    """
    Called when a column is removed from a class, with the arguments
    ``(cls, connection, column_name, so_column_obj, post_funcs)``.
    Like ``AddColumnSignal`` this is called after the action has been
    performed, and is called for subclassing (when a column is
    implicitly removed by setting it to ``None``).

    post_funcs are called with ``(cls, so_column_obj)``
    """

# @@: Signals for indexes and joins?  These are mostly event consumers,
# though.

class CreateTableSignal(Signal):
    """
    Called when a table is created.  If ``ifNotExists==True`` and the
    table exists, this event is not called.

    Called with ``(cls, connection, extra_sql, post_funcs)``.
    ``extra_sql`` is a list (which can be appended to) of extra SQL
    statements to be run after the table is created.  ``post_funcs``
    functions are called with ``(cls, connection)`` after the table
    has been created.  Those functions are *not* called simply when
    constructing the SQL.
    """

class DropTableSignal(Signal):
    """
    Called when a table is dropped.  If ``ifExists==True`` and the
    table doesn't exist, this event is not called.

    Called with ``(cls, connection, extra_sql, post_funcs)``.
    ``post_funcs`` functions are called with ``(cls, connection)``
    after the table has been dropped.
    """

__all__ = ['listen', 'send']
for name, value in globals().items():
    if isinstance(value, type) and issubclass(value, Signal):
        __all__.append('value')
