"""
sqlobject.sqlbuilder
  17 Oct 2002, Ian Bicking <ianb@colorstudy.com>
Builds SQL expressions from normal Python expressions.  Python
2.1 or higher IS REQUIRED.

Disclaimer
----------

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation; either version 2.1 of the
License, or (at your option any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
USA.

Instructions
------------

To begin a SQL expression, you must use some sort of SQL object -- a
field, table, or SQL statement (``SELECT``, ``INSERT``, etc.)  You can
then use normal operators, with the exception of: `and`, `or`, `not`,
and `in`.  You can use the `AND`, `OR`, `NOT`, and `IN` functions
instead, or you can also use `&`, `|`, and `~` for `and`, `or`, and
`not` respectively (however -- the precidence for these operators
doesn't work as you would want, so you must use many parenthesis).

To create a sql field, table, or constant/function, use the namespaces
`table`, `const`, and `func`.  For instance, ``table.address`` refers
to the ``address`` table, and ``table.address.state`` refers to the
``state`` field in the address table.  ``const.NULL`` is the ``NULL``
SQL constant, and ``func.NOW()`` is the ``NOW()`` function call
(`const` and `func` are actually identicle, but the two names are
provided for clarity).  Once you create this object, expressions
formed with it will produce SQL statements.

The ``sqlrepr(obj)`` function gets the SQL representation of these
objects, as well as the proper SQL representation of basic Python
types (None==NULL).

There are a number of DB-specific SQL features that this does not
implement.  There are a bunch of normal ANSI features also not present
-- particularly left joins, among others.  You may wish to only use
this to generate ``WHERE`` clauses.

See the bottom of this module for some examples, and run it (i.e.
``python sql.py``) to see the results of those examples.

"""

########################################
## Constants
########################################

class VersionError(Exception):
    pass
class NoDefault:
    pass

True, False = (1==1), (0==1)

import re, fnmatch
import operator
from converters import sqlrepr, registerConverter, TRUE, FALSE

safeSQLRE = re.compile(r'^[a-zA-Z][a-zA-Z0-9_\.]*$')
def sqlIdentifier(obj):
    return type(obj) is type("") and not not safeSQLRE.search(obj.strip())


def execute(expr, executor):
    if hasattr(expr, 'execute'):
        return expr.execute(executor)
    else:
        return expr

########################################
## Expression generation
########################################

class SQLExpression:
    def __add__(self, other):
        return SQLOp("+", self, other)
    def __radd__(self, other):
        return SQLOp("+", other, self)
    def __sub__(self, other):
        return SQLOp("-", self, other)
    def __rsub__(self, other):
        return SQLOp("-", other, self)
    def __mul__(self, other):
        return SQLOp("*", self, other)
    def __rmul__(self, other):
        return SQLOp("*", other, self)
    def __div__(self, other):
        return SQLOp("/", self, other)
    def __rdiv__(self, other):
        return SQLOp("/", other, self)
    def __pos__(self):
        return SQLPrefix("+", self)
    def __neg__(self):
        return SQLPrefix("-", self)
    def __pow__(self, other):
        return SQLConstant("POW")(self, other)
    def __rpow__(self, other):
        return SQLConstant("POW")(other, self)
    def __abs__(self):
        return SQLConstant("ABS")(self)
    def __mod__(self, other):
        return SQLConstant("MOD")(self, other)
    def __rmod__(self, other):
        return SQLConstant("MOD")(other, self)

    def __lt__(self, other):
        return SQLOp("<", self, other)
    def __le__(self, other):
        return SQLOp("<=", self, other)
    def __gt__(self, other):
        return SQLOp(">", self, other)
    def __ge__(self, other):
        return SQLOp(">=", self, other)
    def __eq__(self, other):
        if other is None:
            return ISNULL(self)
        else:
            return SQLOp("=", self, other)
    def __ne__(self, other):
        if other is None:
            return ISNOTNULL(self)
        else:
            return SQLOp("<>", self, other)

    def __and__(self, other):
        return SQLOp("AND", self, other)
    def __rand__(self, other):
        return SQLOp("AND", other, self)
    def __or__(self, other):
        return SQLOp("OR", self, other)
    def __ror__(self, other):
        return SQLOp("OR", other, self)
    def __invert__(self):
        return SQLPrefix("NOT", self)

    def __call__(self, *args):
        return SQLCall(self, args)

    def __repr__(self):
        return self.__sqlrepr__(None)
    def __str__(self):
        return self.__sqlrepr__(None)

    def __cmp__(self, other):
        raise VersionError, "Python 2.1+ required"
    def __rcmp__(self, other):
        raise VersionError, "Python 2.1+ required"

    def startswith(self, s):
        return STARTSWITH(self, s)
    def endswith(self, s):
        return ENDSWITH(self, s)
    def contains(self, s):
        return CONTAINSSTRING(self, s)

    def components(self):
        return []

    def tablesUsed(self):
        return self.tablesUsedDict().keys()
    def tablesUsedDict(self):
        tables = {}
        for table in self.tablesUsedImmediate():
            tables[table] = 1
        for component in self.components():
            tables.update(tablesUsedDict(component))
        return tables
    def tablesUsedImmediate(self):
        return []

#######################################
# Converter for SQLExpression instances
#######################################

def SQLExprConverter(value, db):
    return value.__sqlrepr__()

registerConverter(SQLExpression, SQLExprConverter)

def tablesUsedDict(obj):
    if hasattr(obj, "tablesUsedDict"):
        return obj.tablesUsedDict()
    else:
        return {}

operatorMap = {
    "+": operator.add,
    "/": operator.div,
    "-": operator.sub,
    "*": operator.mul,
    "<": operator.lt,
    "<=": operator.le,
    "=": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt,
    "IN": operator.contains,
    "IS": operator.eq,
    }

class SQLOp(SQLExpression):
    def __init__(self, op, expr1, expr2):
        self.op = op.upper()
        self.expr1 = expr1
        self.expr2 = expr2
    def __sqlrepr__(self, db):
        return "(%s %s %s)" % (sqlrepr(self.expr1, db), self.op, sqlrepr(self.expr2, db))
    def components(self):
        return [self.expr1, self.expr2]
    def execute(self, executor):
        if self.op == "AND":
            return execute(self.expr1, executor) \
                   and execute(self.expr2, executor)
        elif self.op == "OR":
            return execute(self.expr1, executor) \
                   or execute(self.expr2, executor)
        elif self.op == "LIKE":
            if not hasattr(self, '_regex'):
                # @@: Crude, not entirely accurate
                dest = self.expr2
                dest = dest.replace("%%", "\001")
                dest = dest.replace("*", "\002")
                dest = dest.replace("%", "*")
                dest = dest.replace("\001", "%")
                dest = dest.replace("\002", "[*]")
                self._regex = re.compile(fnmatch.translate(dest), re.I)
            return self._regex.search(execute(self.expr1, executor))
        else:
            return operatorMap[self.op.upper()](execute(self.expr1, executor),
                                                execute(self.expr2, executor))

registerConverter(SQLOp, SQLExprConverter)

class SQLCall(SQLExpression):
    def __init__(self, expr, args):
        self.expr = expr
        self.args = args
    def __sqlrepr__(self, db):
        return "%s%s" % (sqlrepr(self.expr, db), sqlrepr(self.args, db))
    def components(self):
        return [self.expr] + list(self.args)
    def execute(self, executor):
        raise ValueError, "I don't yet know how to locally execute functions"

registerConverter(SQLCall, SQLExprConverter)

class SQLPrefix(SQLExpression):
    def __init__(self, prefix, expr):
        self.prefix = prefix
        self.expr = expr
    def __sqlrepr__(self, db):
        return "%s %s" % (self.prefix, sqlrepr(self.expr, db))
    def components(self):
        return [self.expr]
    def execute(self, executor):
        expr = execute(self.expr, executor)
        if prefix == "+":
            return expr
        elif prefix == "-":
            return -expr
        elif prefix.upper() == "NOT":
            return not expr

registerConverter(SQLPrefix, SQLExprConverter)

class SQLConstant(SQLExpression):
    def __init__(self, const):
        self.const = const
    def __sqlrepr__(self, db):
        return self.const
    def execute(self, executor):
        raise ValueError, "I don't yet know how to execute SQL constants"

registerConverter(SQLConstant, SQLExprConverter)

class SQLTrueClauseClass(SQLExpression):
    def __sqlrepr__(self, db):
        return "1 = 1"
    def execute(self, executor):
        return 1

SQLTrueClause = SQLTrueClauseClass()

registerConverter(SQLTrueClauseClass, SQLExprConverter)

########################################
## Namespaces
########################################

class TableSpace:
    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        return Table(attr)

class Table(SQLExpression):
    def __init__(self, tableName):
        self.tableName = tableName
    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        return Field(self.tableName, attr)
    def __sqlrepr__(self, db):
        return str(self.tableName)
    def execute(self, executor):
        raise ValueError, "Tables don't have values"

class SQLObjectTable(Table):

    def __init__(self, soClass):
        self.soClass = soClass
        Table.__init__(self, soClass._table)

    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        if attr == 'id':
            return SQLObjectField(self.tableName, self.soClass._idName, attr)
        else:
            return SQLObjectField(self.tableName,
                                  self.soClass._SO_columnDict[attr].dbName,
                                  attr)

class Field(SQLExpression):
    def __init__(self, tableName, fieldName):
        self.tableName = tableName
        self.fieldName = fieldName
    def __sqlrepr__(self, db):
        return self.tableName + "." + self.fieldName
    def tablesUsedImmediate(self):
        return [self.tableName]
    def execute(self, executor):
        return executor.field(self.tableName, self.fieldName)

class SQLObjectField(Field):
    def __init__(self, tableName, fieldName, original):
        self.original = original
        Field.__init__(self, tableName, fieldName)

registerConverter(SQLObjectField, SQLExprConverter)

class ConstantSpace:
    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        return SQLConstant(attr)


########################################
## SQL Statements
########################################

class Select(SQLExpression):
    def __init__(self, items, where=NoDefault, groupBy=NoDefault,
                 having=NoDefault, orderBy=NoDefault, limit=NoDefault):
        if type(items) is not type([]) and type(items) is not type(()):
            items = [items]
        self.items = items
        self.whereClause = where
        self.groupBy = groupBy
        self.having = having
        self.orderBy = orderBy
        self.limit = limit

    def __sqlrepr__(self, db):
        select = "SELECT %s" % ", ".join([sqlrepr(v, db) for v in self.items])

        tables = {}
        things = self.items
        if self.whereClause is not NoDefault:
            things.append(self.whereClause)
        for thing in things:
            if isinstance(thing, SQLExpression):
                tables.update(tablesUsedDict(thing))
        tables = tables.keys()
        if tables:
            select += " FROM %s" % ", ".join(tables)

        if self.whereClause is not NoDefault:
            select += " WHERE %s" % sqlrepr(self.whereClause, db)
        if self.groupBy is not NoDefault:
            select += " GROUP BY %s" % sqlrepr(self.groupBy, db)
        if self.having is not NoDefault:
            select += " HAVING %s" % sqlrepr(self.having, db)
        if self.orderBy is not NoDefault:
            select += " ORDER BY %s" % sqlrepr(self.orderBy, db)
        if self.limit is not NoDefault:
            select += " LIMIT %s" % sqlrepr(self.limit, db)
        return select

registerConverter(Select, SQLExprConverter)

class Insert(SQLExpression):
    def __init__(self, table, valueList=None, values=None, template=NoDefault):
        self.template = template
        self.table = table
        if valueList:
            if values:
                raise TypeError, "You may only give valueList *or* values"
            self.valueList = valueList
        else:
            self.valueList = [values]
    def __sqlrepr__(self, db):
        if not self.valueList:
            return ''
        insert = "INSERT INTO %s" % self.table
        allowNonDict = True
        template = self.template
        if template is NoDefault and type(self.valueList[0]) is type({}):
            template = self.valueList[0].keys()
            allowNonDict = False
        if template is not NoDefault:
            insert += " (%s)" % ", ".join(template)
        first = True
        insert += " VALUES "
        for value in self.valueList:
            if first:
                first = False
            else:
                insert += ", "
            if type(value) is type({}):
                if template is NoDefault:
                    raise TypeError, "You can't mix non-dictionaries with dictionaries in an INSERT if you don't provide a template (%s)" % repr(value)
                value = dictToList(template, value)
            elif not allowNonDict:
                raise TypeError, "You can't mix non-dictionaries with dictionaries in an INSERT if you don't provide a template (%s)" % repr(value)
            insert += "(%s)" % ", ".join([sqlrepr(v, db) for v in value])
        return insert

registerConverter(Insert, SQLExprConverter)

def dictToList(template, dict):
    list = []
    for key in template:
        list.append(dict[key])
    if len(dict.keys()) > len(template):
        raise TypeError, "Extra entries in dictionary that aren't asked for in template (template=%s, dict=%s)" % (repr(template), repr(dict))
    return list

class Update(SQLExpression):
    def __init__(self, table, values, template=NoDefault, where=NoDefault):
        self.table = table
        self.values = values
        self.template = template
        self.whereClause = where
    def __sqlrepr__(self, db):
        update = "%s %s" % (self.sqlName(), self.table)
        update += " SET"
        first = True
        if self.template is not NoDefault:
            for i in range(len(self.template)):
                if first:
                    first = False
                else:
                    update += ","
                update += " %s=%s" % (self.template[i], sqlrepr(self.values[i], db))
        else:
            for key, value in self.values.items():
                if first:
                    first = False
                else:
                    update += ","
                update += " %s=%s" % (key, sqlrepr(value, db))
        if self.whereClause is not NoDefault:
            update += " WHERE %s" % sqlrepr(self.whereClause, db)
        return update
    def sqlName(self):
        return "UPDATE"

registerConverter(Update, SQLExprConverter)

class Delete(SQLExpression):
    """To be safe, this will signal an error if there is no where clause,
    unless you pass in where=None to the constructor."""
    def __init__(self, table, where=NoDefault):
        self.table = table
        if where is NoDefault:
            raise TypeError, "You must give a where clause or pass in None to indicate no where clause"
        self.whereClause = where
    def __sqlrepr__(self, db):
        if self.whereClause is None:
            return "DELETE FROM %s" % self.table
        return "DELETE FROM %s WHERE %s" \
               % (self.table, sqlrepr(self.whereClause, db))

registerConverter(Delete, SQLExprConverter)

class Replace(Update):
    def sqlName(self):
        return "REPLACE"

registerConverter(Replace, SQLExprConverter)

########################################
## SQL Builtins
########################################

class DESC(SQLExpression):

    def __init__(self, expr):
        self.expr = expr

    def __sqlrepr__(self, db):
        if isinstance(self.expr, DESC):
            return sqlrepr(self.expr.expr, db)
        return '%s DESC' % sqlrepr(self.expr, db)

def AND(*ops):
    op1 = ops[0]
    ops = ops[1:]
    if ops:
        return SQLOp("AND", op1, AND(*ops))
    else:
        return op1

def OR(*ops):
    op1 = ops[0]
    ops = ops[1:]
    if ops:
        return SQLOp("OR", op1, OR(*ops))
    else:
        return op1

def NOT(op):
    return SQLPrefix("NOT", op)

def IN(item, list):
    return SQLOp("IN", item, list)

def LIKE(expr, string):
    return SQLOp("LIKE", expr, string)

def STARTSWITH(expr, string):
    return SQLOp("LIKE", expr, _LikeQuoted(string) + '%')

def ENDSWITH(expr, string):
    return SQLOp("LIKE", expr, '%' + _LikeQuoted(string))

def CONTAINSSTRING(expr, string):
    return SQLOp("LIKE", expr, '%' + _LikeQuoted(string) + '%')

def ISNULL(expr):
    return SQLOp("IS", expr, None)

def ISNOTNULL(expr):
    return SQLOp("IS NOT", expr, None)

class _LikeQuoted:
    # @@: I'm not sure what the quoting rules really are for all the
    # databases

    def __init__(self, expr):
        self.expr = expr
        self.prefix = ''
        self.postfix = ''

    def __radd__(self, s):
        self.prefix = s + self.prefix
        return self

    def __add__(self, s):
        self.postfix += s
        return self

    def __sqlrepr__(self, db):
        s = sqlrepr(self.expr, db)[1:-1] # remove quotes
        if db in ('postgres', 'mysql'):
            s = s.replace('%', '\\%')
        else:
            s = s.replace('%', '%%')
        return "'%s%s%s'" % (self.prefix, s, self.postfix)

########################################
## Global initializations
########################################

table = TableSpace()
const = ConstantSpace()
func = const

########################################
## Testing
########################################

if __name__ == "__main__":
    tests = """
>>> AND(table.address.name == "Ian Bicking", table.address.zip > 30000)
>>> table.address.name
>>> AND(LIKE(table.address.name, "this"), IN(table.address.zip, [100, 200, 300]))
>>> Select([table.address.name, table.address.state], where=LIKE(table.address.name, "%ian%"))
>>> Select([table.user.name], where=AND(table.user.state == table.states.abbrev))
>>> Insert(table.address, [{"name": "BOB", "address": "3049 N. 18th St."}, {"name": "TIM", "address": "409 S. 10th St."}])
>>> Insert(table.address, [("BOB", "3049 N. 18th St."), ("TIM", "409 S. 10th St.")], template=('name', 'address'))
>>> Delete(table.address, where="BOB"==table.address.name)
>>> Update(table.address, {"lastModified": const.NOW()})
>>> Replace(table.address, [("BOB", "3049 N. 18th St."), ("TIM", "409 S. 10th St.")], template=('name', 'address'))
"""
    for expr in tests.split('\n'):
        if not expr.strip(): continue
        if expr.startswith('>>> '):
            expr = expr[4:]
