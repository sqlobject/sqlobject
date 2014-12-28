from __future__ import absolute_import

from sqlobject.dbconnection import registerConnection

def builder():
    import firebirdconnection
    return firebirdconnection.FirebirdConnection

registerConnection(['firebird', 'interbase'], builder)
