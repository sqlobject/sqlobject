import os
import sys
from sqlobject.compat import load_module_from_file


def load_module(module_name):
    mod = __import__(module_name)
    components = module_name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def load_module_from_name(filename, module_name):
    if module_name in sys.modules:
        return sys.modules[module_name]
    init_filename = os.path.join(os.path.dirname(filename), '__init__.py')
    if not os.path.exists(init_filename):
        try:
            f = open(init_filename, 'w')
        except (OSError, IOError) as e:
            raise IOError(
                'Cannot write __init__.py file into directory %s (%s)\n'
                % (os.path.dirname(filename), e))
        f.write('#\n')
        f.close()
    if module_name in sys.modules:
        return sys.modules[module_name]
    if '.' in module_name:
        parent_name = '.'.join(module_name.split('.')[:-1])
        base_name = module_name.split('.')[-1]
        load_module_from_name(os.path.dirname(filename), parent_name)
    else:
        base_name = module_name
    return load_module_from_file(base_name, module_name, filename)
