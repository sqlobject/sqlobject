from sqlobject import *
"""
This contains basic configuration for all the examples.  Since they
all require a connection, you can configure that just in this file.
"""

## Use one of these to define your connection:
"""
## Snippet "connections"
conn = MySQLConnection(user='test', db='testdb')
conn = 'mysql://test@localhost/testdb'
conn = PostgresConnection('user=test dbname=testdb')
conn = 'postgres://test@localhost/testdb'
conn = SQLiteConnection('database.db')
conn = 'sqlite://path/to/database.db'
## end snippet
"""
#conn = MySQLConnection(user='test', db='test')
conn = 'mysql://test@localhost/test'
