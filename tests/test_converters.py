import unittest
from SQLObject.SQLBuilder import sqlrepr, TRUE, FALSE
from SQLObject.SQLBuilder import SQLExpression, SQLObjectField, \
     Select, Insert, Update, Delete, Replace, \
     SQLTrueClauseClass, SQLConstant, SQLPrefix, SQLCall, SQLOp
from SQLObject.Converters import registerConverter

class TestClass:

    def __repr__(self):
        return '<TestClass>'

def TestClassConverter(value):
    return repr(value)

registerConverter(TestClass, TestClassConverter)

class NewTestClass:

    __metaclass__ = type

    def __repr__(self):
        return '<NewTestClass>'

def NewTestClassConverter(value):
    return repr(value)

registerConverter(NewTestClass, NewTestClassConverter)

def _sqlrepr(self):
    return '<%s>' % self.__class__.__name__

SQLExpression.sqlrepr = _sqlrepr

class ConvertersTest(unittest.TestCase):

    def test_simple_string(self):
        self.assertEqual(sqlrepr('A String'), "'A String'")

    def test_string_newline(self):
        self.assertEqual(sqlrepr('A String\nAnother', 'postgres'), "'A String\\nAnother'")
        self.assertEqual(sqlrepr('A String\nAnother', 'sqlite'), "'A String\nAnother'")

    def test_string_tab(self):
        self.assertEqual(sqlRepr('A String\tAnother', 'postgres'), "'A String\\tAnother'")

    def test_string_r(self):
        self.assertEqual(sqlRepr('A String\rAnother', 'postgres'), "'A String\\rAnother'")

    def test_string_b(self):
        self.assertEqual(sqlRepr('A String\bAnother', 'postgres'), "'A String\\bAnother'")

    def test_string_000(self):
        self.assertEqual(sqlRepr('A String\000Another', 'postgres'), "'A String\\0Another'")

    def test_string_(self):
        self.assertEqual(sqlRepr('A String\'Another', 'postgres'), "'A String\\\'Another'")
        self.assertEqual(sqlRepr('A String\'Another', 'firebird'), "'A String''Another'")

    def test_simple_unicode(self):
        self.assertEqual(sqlrepr(u'A String', 'postgres'), "'A String'")

    def test_integer(self):
        self.assertEqual(sqlrepr(10), "10")

    def test_float(self):
        self.assertEqual(sqlrepr(10.01), "10.01")

    def test_none(self):
        self.assertEqual(sqlrepr(None), "NULL")

    def test_list(self):
        self.assertEqual(sqlrepr(['one','two','three'], 'postgres'), "('one', 'two', 'three')")

    def test_tuple(self):
        self.assertEqual(sqlrepr(('one','two','three'), 'postgres'), "('one', 'two', 'three')")

    def test_bool(self):
        self.assertEqual(sqlRepr(TRUE, 'postgres'), "'t'")
        self.assertEqual(sqlRepr(FALSE, 'postgres'), "'f'")
        self.assertEqual(sqlRepr(TRUE, 'mysql'), "1")
        self.assertEqual(sqlRepr(FALSE, 'mysql'), "0")

    def test_instance(self):
        instance = TestClass()
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_newstyle(self):
        instance = NewTestClass()
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_sqlexpr(self):
        instance = SQLExpression()
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_sqlobjectfield(self):
        instance = SQLObjectField('test', 'test', 'test')
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_select(self):
        instance = Select('test')
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_insert(self):
        instance = Insert('test', ('test',))
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_update(self):
        instance = Update('test', {'test':'test'})
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_delete(self):
        instance = Delete('test', None)
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_replace(self):
        instance = Replace('test', {'test':'test'})
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_trueclause(self):
        instance = SQLTrueClauseClass()
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_op(self):
        instance = SQLOp('and', 'this', 'that')
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_call(self):
        instance = SQLCall('test', 'test')
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_constant(self):
        instance = SQLConstant('test')
        self.assertEqual(sqlrepr(instance), repr(instance))

    def test_prefix(self):
        instance = SQLPrefix('test', 'test')
        self.assertEqual(sqlrepr(instance), repr(instance))

if __name__ == "__main__":
    unittest.main()
