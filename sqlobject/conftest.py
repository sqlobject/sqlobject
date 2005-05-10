"""
This module is used by py.test to configure testing for this
application.
"""

# Override some options (doesn't override command line):
verbose = 0
exitfirst = True

import py
import os

connectionShortcuts = {
    'mysql': 'mysql://test@localhost/test',
    'dbm': 'dbm:///data',
    'postgres': 'postgres:///test',
    'postgresql': 'postgres:///test',
    'pygresql': 'pygresql://localhost/test',
    'sqlite': 'sqlite:///%s/data/sqlite.data' % os.getcwd(),
    'sybase': 'sybase://test:test123@sybase/test?autoCommit=0',
    'firebird': 'firebird://sysdba:masterkey@localhost/var/lib/firebird/data/test.gdb',
    }

Option = py.test.Config.Option
option = py.test.Config.addoptions(
    "SQLObject options",
    Option('-D', '--Database',
           action="store", dest="Database", default='sqlite',
           help="The database to run the tests under (default sqlite).  "
           "Can also use an alias from: %s"
           % (', '.join(connectionShortcuts.keys()))))
