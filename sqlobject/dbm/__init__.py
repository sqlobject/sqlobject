from sqlobject.dbconnection import registerConnection

def builder():
    import dbmconnection
    return dbmconnection.DBMConnection

def isSupported():
    try:
        import anydbm
    except ImportError:
        return False
    return True

registerConnection(['dbm'], builder, isSupported)
