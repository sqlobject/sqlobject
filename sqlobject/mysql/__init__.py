from sqlobject.dbconnection import registerConnection

def builder():
    import mysqlconnection
    return mysqlconnection.MySQLConnection

def isSupported():
    try:
        import MySQLdb
    except ImportError:
        return False
    return True

registerConnection(['mysql'], builder, isSupported)
