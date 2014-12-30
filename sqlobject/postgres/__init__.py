from __future__ import absolute_import

from sqlobject.dbconnection import registerConnection

def builder():
    import pgconnection
    return pgconnection.PostgresConnection

registerConnection(['postgres', 'postgresql', 'psycopg'], builder)
