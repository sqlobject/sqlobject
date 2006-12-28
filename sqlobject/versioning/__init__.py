from sqlobject import *
from datetime import datetime

class Version(SQLObject):
    def restore(self):
        values = self.sqlmeta.asDict()
        del values['id']
        del values['masterID']
        del values['dateArchived']
        self.masterClass.get(self.masterID).set(**values)

def getColumns(columns, cls):
    for column, defi in cls.sqlmeta.columnDefinitions.items():
        columns[column] = defi.__class__()
        
    #ascend heirarchy
    if cls.sqlmeta.parentClass:
        getColumns(columns, cls.sqlmeta.parentClass)


class Versioning(object):
    def __init__(self):
        pass
    def __addtoclass__(self, soClass, name):
        self.name = name
        self.soClass = soClass
        self.versionClass = None
        events.listen(self.createTable,
                      soClass, events.CreateTableSignal)
        events.listen(self.rowUpdate, soClass,
                      events.RowUpdateSignal)

    def createVersionTable(self, cls, conn):
        columns = {'dateArchived': DateTimeCol(default=datetime.now), 
                   'masterID': IntCol(),
                   'masterClass' : self.soClass,
                   }

        getColumns (columns, self.soClass)

        self.versionClass = type(self.soClass.__name__+'Versions',
                                 (Version,),
                                 columns)

        self.versionClass.createTable(connection=conn)

    def createTable(self, soClass, connection, extra_sql, post_funcs):
        assert soClass is self.soClass
        post_funcs.append(self.createVersionTable)

    def rowUpdate(self, instance, kwargs):
        if instance.childName and instance.childName != self.soClass.__name__:
            return #if you want your child class versioned, version it.

        values = instance.sqlmeta.asDict()
        del values['id']
        values['masterID'] = instance.id
        self.versionClass(connection=instance._connection, **values)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return self.versionClass.select(
            self.versionClass.q.masterID==obj.id, connection=obj._connection)

