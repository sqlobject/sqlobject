from SQLObject import *
import setup

__connection__ = setup.conn

True, False = 1==1, 0==1

## Snippet "userrole-classes"
class User(SQLObject):

    # user is a reserved word in some databases, so we won't
    # use that for the table name:
    _table = "user_table"

    username = StringCol(alternateID=True, length=20)
    # We'd probably define more attributes, but we'll leave
    # that excersize to the reader...

    roles = RelatedJoin('Role')

class Role(SQLObject):

    name = StringCol(alternateID=True, length=20)

    users = RelatedJoin('User')
## end snippet

#def reset():
#    User.dropTable(ifExists=True)
#    User.createTable()
#    Role.dropTable(ifExists=True)
#    Role.createTable()

setup.reset()

## Snippet "userrole-use"
bob = User.new(username='bob')
tim = User.new(username='tim')
jay = User.new(username='jay')

admin = Role.new(name='admin')
editor = Role.new(name='editor')

bob.addRole(admin)
bob.addRole(editor)
tim.addRole(editor)

print bob.roles
#>> [<Role 1 name='admin'>, <Role 2 name='editor'>]
print tim.roles
#>> [<Role 2 name='editor'>]
print jay.roles
#>> []
print admin.users
#>> [<User 1 username='bob'>]
print editor.users
#>> [<User 1 username='bob'>, <User 2 username='tim'>]
## end snippet

## Snippet "userrole-use-alternate"
print User.byUsername('bob')
#>> <User 1 username='bob'>
print Role.byName('admin')
#>> <Role 1 name='admin'>
## End snippet
