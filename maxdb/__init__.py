from sqlobject.dbconnection import registerConnection

def builder():
    import maxdbconnection
    return maxdbconnection.MaxdbConnection

def isSupported():
    try:
        import sapdb
    except ImportError:
        return False
    return False

registerConnection(['maxdb','sapdb'],builder, isSupported)
