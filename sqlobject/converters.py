from __future__ import absolute_import

from array import array
import datetime
from decimal import Decimal
import sys
import time
from types import ClassType, InstanceType, NoneType


try:
    from mx.DateTime import DateTimeType, DateTimeDeltaType
except ImportError:
    try:
        from DateTime import DateTimeType, DateTimeDeltaType
    except ImportError:
        DateTimeType = None
        DateTimeDeltaType = None

try:
    import Sybase
    NumericType=Sybase.NumericType
except ImportError:
    NumericType = None


########################################
## Quoting
########################################

sqlStringReplace = [
    ("'", "''"),
    ('\\', '\\\\'),
    ('\000', '\\0'),
    ('\b', '\\b'),
    ('\n', '\\n'),
    ('\r', '\\r'),
    ('\t', '\\t'),
]

class ConverterRegistry:

    def __init__(self):
        self.basic = {}
        self.klass = {}

    def registerConverter(self, typ, func):
        if type(typ) is ClassType:
            self.klass[typ] = func
        else:
            self.basic[typ] = func

    def lookupConverter(self, value, default=None):
        if type(value) is InstanceType:
            # lookup on klasses dict
            return self.klass.get(value.__class__, default)
        return self.basic.get(type(value), default)

converters = ConverterRegistry()
registerConverter = converters.registerConverter
lookupConverter = converters.lookupConverter

def StringLikeConverter(value, db):
    if isinstance(value, array):
        try:
            value = value.tounicode()
        except ValueError:
            value = value.tostring()
    elif isinstance(value, buffer):
        value = str(value)

    if db in ('mysql', 'postgres', 'rdbhost'):
        for orig, repl in sqlStringReplace:
            value = value.replace(orig, repl)
    elif db in ('sqlite', 'firebird', 'sybase', 'maxdb', 'mssql'):
        value = value.replace("'", "''")
    else:
        assert 0, "Database %s unknown" % db
    if db in ('postgres', 'rdbhost') and ('\\' in value):
        return "E'%s'" % value
    return "'%s'" % value

registerConverter(str, StringLikeConverter)
registerConverter(unicode, StringLikeConverter)
registerConverter(array, StringLikeConverter)
registerConverter(buffer, StringLikeConverter)

def IntConverter(value, db):
    return repr(int(value))

registerConverter(int, IntConverter)

def LongConverter(value, db):
    return str(value)

registerConverter(long, LongConverter)

if NumericType:
    registerConverter(NumericType, IntConverter)

def BoolConverter(value, db):
    if db in ('postgres', 'rdbhost'):
        if value:
            return "'t'"
        else:
            return "'f'"
    else:
        if value:
            return '1'
        else:
            return '0'

registerConverter(bool, BoolConverter)

def FloatConverter(value, db):
    return repr(value)

registerConverter(float, FloatConverter)

if DateTimeType:
    def DateTimeConverter(value, db):
        return "'%s'" % value.strftime("%Y-%m-%d %H:%M:%S.%s")

    registerConverter(DateTimeType, DateTimeConverter)

    def TimeConverter(value, db):
        return "'%s'" % value.strftime("%H:%M:%S")

    registerConverter(DateTimeDeltaType, TimeConverter)

def NoneConverter(value, db):
    return "NULL"

registerConverter(NoneType, NoneConverter)

def SequenceConverter(value, db):
    return "(%s)" % ", ".join([sqlrepr(v, db) for v in value])

registerConverter(tuple, SequenceConverter)
registerConverter(list, SequenceConverter)
registerConverter(dict, SequenceConverter)
registerConverter(set, SequenceConverter)
registerConverter(frozenset, SequenceConverter)

if hasattr(time, 'struct_time'):
    def StructTimeConverter(value, db):
        return time.strftime("'%Y-%m-%d %H:%M:%S'", value)

    registerConverter(time.struct_time, StructTimeConverter)

def DateTimeConverter(value, db):
    return "'%04d-%02d-%02d %02d:%02d:%02d.%06d'" % (
        value.year, value.month, value.day,
        value.hour, value.minute, value.second, value.microsecond)

registerConverter(datetime.datetime, DateTimeConverter)

def DateConverter(value, db):
    return "'%04d-%02d-%02d'" % (value.year, value.month, value.day)

registerConverter(datetime.date, DateConverter)

def TimeConverter(value, db):
    return "'%02d:%02d:%02d.%06d'" % (value.hour, value.minute, value.second, value.microsecond)

registerConverter(datetime.time, TimeConverter)

def DecimalConverter(value, db):
    return value.to_eng_string()

registerConverter(Decimal, DecimalConverter)

def TimedeltaConverter(value, db):

    return """INTERVAL '%d days %d seconds'""" % \
        (value.days, value.seconds)

registerConverter(datetime.timedelta, TimedeltaConverter)


def sqlrepr(obj, db=None):
    try:
        reprFunc = obj.__sqlrepr__
    except AttributeError:
        converter = lookupConverter(obj)
        if converter is None:
            raise ValueError("Unknown SQL builtin type: %s for %s" % \
                  (type(obj), repr(obj)))
        return converter(obj, db)
    else:
        return reprFunc(db)


def quote_str(s, db):
    if db in ('postgres', 'rdbhost') and ('\\' in s):
        return "E'%s'" % s
    return "'%s'" % s

def unquote_str(s):
    if s[:2].upper().startswith("E'") and s.endswith("'"):
        return s[2:-1]
    elif s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    else:
        return s
