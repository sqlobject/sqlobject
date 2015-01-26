from sqlobject.dbconnection import registerConnection


def builder():
    import mysqlconnection
    return mysqlconnection.MySQLConnection

registerConnection(['mysql'], builder)
