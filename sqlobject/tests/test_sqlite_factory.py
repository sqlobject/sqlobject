from sqlobject import *
from sqlobject.tests.dbtest import *
from sqlobject.tests.dbtest import installOrClear

class SQLiteFactoryTest(SQLObject):
    name = StringCol()

def test_sqlite_factory():
    setupClass(SQLiteFactoryTest)

    if SQLiteFactoryTest._connection.dbName == "sqlite":
        from sqlobject.sqlite import sqliteconnection
        if not sqliteconnection.using_sqlite2:
            return

        factory = [None]
        def SQLiteConnectionFactory(sqlite):
            class MyConnection(sqlite.Connection):
                pass
            factory[0] = MyConnection
            return MyConnection

        conn = SQLiteFactoryTest._connection
        SQLiteFactoryTest._connection = sqliteconnection.SQLiteConnection(
            filename=conn.filename,
            name=conn.name, debug=conn.debug, debugOutput=conn.debugOutput,
            cache=conn.cache, style=conn.style, autoCommit=conn.autoCommit,
            debugThreading=conn.debugThreading, registry=conn.registry,
            factory=SQLiteConnectionFactory
        )
        conn = SQLiteFactoryTest._connection.makeConnection()
        assert factory[0]
        assert isinstance(conn, factory[0])

def test_sqlite_factory_str():
    setupClass(SQLiteFactoryTest)

    if SQLiteFactoryTest._connection.dbName == "sqlite":
        from sqlobject.sqlite import sqliteconnection
        if not sqliteconnection.using_sqlite2:
            return

        factory = [None]
        def SQLiteConnectionFactory(sqlite):
            class MyConnection(sqlite.Connection):
                pass
            factory[0] = MyConnection
            return MyConnection
        sqliteconnection.SQLiteConnectionFactory = SQLiteConnectionFactory

        conn = SQLiteFactoryTest._connection
        SQLiteFactoryTest._connection = sqliteconnection.SQLiteConnection(
            filename=conn.filename,
            name=conn.name, debug=conn.debug, debugOutput=conn.debugOutput,
            cache=conn.cache, style=conn.style, autoCommit=conn.autoCommit,
            debugThreading=conn.debugThreading, registry=conn.registry,
            factory="SQLiteConnectionFactory"
        )
        conn = SQLiteFactoryTest._connection.makeConnection()
        assert factory[0]
        assert isinstance(conn, factory[0])
        del sqliteconnection.SQLiteConnectionFactory

def test_sqlite_aggregate():
    setupClass(SQLiteFactoryTest)

    if SQLiteFactoryTest._connection.dbName == "sqlite":
        from sqlobject.sqlite import sqliteconnection
        if not sqliteconnection.using_sqlite2:
            return

        def SQLiteConnectionFactory(sqlite):
            class MyConnection(sqlite.Connection):
                def __init__(self, *args, **kwargs):
                    super(MyConnection, self).__init__(*args, **kwargs)
                    self.create_aggregate("group_concat", 1, self.group_concat)

                class group_concat:
                    def __init__(self):
                        self.acc = []
                    def step(self, value):
                        if isinstance(value, basestring):
                            self.acc.append(value)
                        else:
                            self.acc.append(str(value))
                    def finalize(self):
                        self.acc.sort()
                        return ", ".join(self.acc)

            return MyConnection

        conn = SQLiteFactoryTest._connection
        SQLiteFactoryTest._connection = sqliteconnection.SQLiteConnection(
            filename=conn.filename,
            name=conn.name, debug=conn.debug, debugOutput=conn.debugOutput,
            cache=conn.cache, style=conn.style, autoCommit=conn.autoCommit,
            debugThreading=conn.debugThreading, registry=conn.registry,
            factory=SQLiteConnectionFactory
        )
        installOrClear([SQLiteFactoryTest])

        SQLiteFactoryTest(name='sqlobject')
        SQLiteFactoryTest(name='sqlbuilder')
        assert SQLiteFactoryTest.select(orderBy="name").accumulateOne("group_concat", "name") == \
            "sqlbuilder, sqlobject"
