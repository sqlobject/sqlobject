from __future__ import absolute_import

from sqlobject.dbconnection import registerConnection

def builder():
    import maxdbconnection
    return maxdbconnection.MaxdbConnection

registerConnection(['maxdb','sapdb'],builder)
