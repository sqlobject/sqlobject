from sqlobject import *
"""
This contains basic configuration for all the examples.  Since they
all require a connection, you can configure that just in this file.
"""

## Use one of these to define your connection:
"""
## Snippet "connections"
conn = MySQLConnection(user='test', db='testdb')
conn = PostgresConnection('user=test dbname=testdb')
conn = SQLiteConnect('database.db')
conn = DBMConnection('database/')
## end snippet
"""
conn = MySQLConnection(user='test', db='test')
