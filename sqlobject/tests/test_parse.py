from sqlobject.dbconnection import DBConnection

########################################
## Test _parseURI
########################################

def test_parse():
    _parseURI = DBConnection._parseURI

    user, password, host, path, args = _parseURI("mysql://user:passwd@host/database")
    assert user == "user"
    assert password == "passwd"
    assert host == "host"
    assert path == "/database"
    assert args == {}

    user, password, host, path, args = _parseURI("mysql://host/database")
    assert user == None
    assert password == None
    assert host == "host"
    assert path == "/database"
    assert args == {}

    user, password, host, path, args = _parseURI("postgres://user@host/database")
    assert user == "user"
    assert password == None
    assert host == "host"
    assert path == "/database"
    assert args == {}

    user, password, host, path, args = _parseURI("postgres://host:5432/database")
    assert user == None
    assert password == None
    assert host == "host:5432"
    assert path == "/database"
    assert args == {}

    user, password, host, path, args = _parseURI("sqlite:///full/path/to/database")
    assert user == None
    assert password == None
    assert host == None
    assert path == "/full/path/to/database"
    assert args == {}

    user, password, host, path, args = _parseURI("sqlite:/:memory:")
    assert user == None
    assert password == None
    assert host == None
    assert path == "/:memory:"
    assert args == {}
