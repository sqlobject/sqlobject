from sqlobject.dbconnection import registerConnection

def builder():
    import sqliteconnection
    return sqliteconnection.SQLiteConnection

def isSupported():
    try:
        import sqlite
    except ImportError:
        return False
    return True

registerConnection(['sqlite'], builder, isSupported)
