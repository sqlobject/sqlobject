import sys
from config import conn
import sqlobject

main = sys.modules['__main__']

if '-v' in sys.argv:
    conn.debug = 1

def reset():
    classes = []
    for name in dir(main):
        value = getattr(main, name)
        if isinstance(value, type) \
               and issubclass(value, sqlobject.SQLObject)\
               and value is not sqlobject.SQLObject:
            value.dropTable(ifExists=True)
            value.createTable()
