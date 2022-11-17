import os
import sys
import types

# Credit to six authors: https://pypi.org/project/six/
# License: MIT


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.

    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})

# Compatability definitions (inspired by six)
PY2 = sys.version_info[0] < 3
if PY2:
    # disable flake8 checks on python 3
    string_type = basestring  # noqa
    unicode_type = unicode  # noqa
    class_types = (type, types.ClassType)
    buffer_type = buffer  # noqa
else:
    string_type = str
    unicode_type = str
    class_types = (type,)
    buffer_type = memoryview

if PY2:
    import imp

    def load_module_from_file(base_name, module_name, filename):
        fp, pathname, description = imp.find_module(
            base_name, [os.path.dirname(filename)])
        try:
            module = imp.load_module(module_name, fp, pathname, description)
        finally:
            fp.close()
        return module
else:
    import importlib.util

    def load_module_from_file(base_name, module_name, filename):
        specs = importlib.util.spec_from_file_location(module_name, filename)
        loader = specs.loader
        if hasattr(loader, 'create_module'):
            module = loader.create_module(specs)
        else:
            module = None
        if module is None:
            return specs.loader.load_module()
        else:
            loader.exec_module(module)
            return module
