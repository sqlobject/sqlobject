"""
Bound attributes are attributes that are bound to a specific class and
a specific name.  In SQLObject a typical example is a column object,
which knows its name and class.

A bound attribute should define a method ``__addtoclass__(added_class,
name)`` (attributes without this method will simply be treated as
normal).  The return value is ignored; if the attribute wishes to
change the value in the class, it must call ``setattr(added_class,
name, new_value)``.

BoundAttribute is a class that facilitates lazy attribute creation.

``bind_attributes(cls, new_attrs)`` is a function that looks for
attributes with this special method.  ``new_attrs`` is a dictionary,
as typically passed into ``__classinit__`` with declarative (calling
``bind_attributes`` in ``__classinit__`` would be typical).

Note if you do this that attributes defined in a superclass will not
be rebound in subclasses.  If you want to rebind attributes in
subclasses, use ``bind_attributes_local``, which adds a
``__bound_attributes__`` variable to your class to track these active
attributes.
"""

__all__ = ['BoundAttribute', 'BoundFactory', 'bind_attributes',
           'bind_attributes_local']

import declarative

class BoundAttribute(declarative.Declarative):

    """
    This is a declarative class that passes all the values given to it
    to another object.  So you can pass it arguments (via
    __init__/__call__) or give it the equivalent of keyword arguments
    through subclassing.  Then a bound object will be added in its
    place.

    To hook this other object in, override ``make_object(added_class,
    name, **attrs)`` and maybe ``set_object(added_class, name,
    **attrs)`` (the default implementation of ``set_object``
    just resets the attribute to whatever ``make_object`` returned).
    """

    _private_variables = (
        '_private_variables',
        '_all_attributes',
        '__classinit__',
        '__addtoclass__',
        '_add_attrs',
        'set_object',
        'make_object',
        )

    _all_attrs = ()

    def __classinit__(cls, new_attrs):
        declarative.Declarative.__classinit__(cls, new_attrs)
        cls._all_attrs = cls._add_attrs(cls, new_attrs)

    def __instanceinit__(self, new_attrs):
        declarative.Declarative.__instanceinit__(self, new_attrs)
        self._all_attrs = self._add_attrs(self, new_attrs)

    def _add_attrs(this_object, new_attrs):
        private = this_object._private_variables
        all_attrs = list(this_object._all_attrs)
        for key in new_attrs.keys():
            if key.startswith('_') or key in private:
                continue
            if key not in all_attrs:
                all_attrs.append(key)
        return tuple(all_attrs)
    _add_attrs = staticmethod(_add_attrs)

    def __addtoclass__(self, cls, added_class, attr_name):
        me = self or cls
        attrs = {}
        for name in me._all_attrs:
            attrs[name] = getattr(me, name)
        attrs['added_class'] = added_class
        attrs['attr_name'] = attr_name
        obj = me.make_object(**attrs)
        me.set_object(added_class, attr_name, obj)

    __addtoclass__ = declarative.classinstancemethod(__addtoclass__)

    def set_object(cls, added_class, attr_name, obj):
        setattr(added_class, attr_name, obj)

    set_object = classmethod(set_object)

    def make_object(cls, added_class, attr_name, *args, **attrs):
        raise NotImplementedError

    make_object = classmethod(make_object)

class BoundFactory(BoundAttribute):

    factory_class = None

    def make_object(cls, added_class, attr_name, *args, **kw):
        return cls.factory_class(added_class, attr_name, *args, **kw)

def bind_attributes(cls, new_attrs):
    for name, value in new_attrs.items():
        if hasattr(value, '__addtoclass__'):
            value.__addtoclass__(cls, name)

def bind_attributes_local(cls, new_attrs):
    new_bound_attributes = {}
    for name, value in getattr(cls, '__bound_attributes__', {}).items():
        if new_attrs.has_key(name):
            # The attribute is being REbound, so don't try to bind it
            # again.
            continue
        value.__addtoclass__(cls, name)
        new_bound_attributes[name] = value
    for name, value in new_attrs.items():
        if hasattr(value, '__addtoclass__'):
            value.__addtoclass__(cls, name)
            new_bound_attributes[name] = value
    cls.__bound_attributes__ = new_bound_attributes
