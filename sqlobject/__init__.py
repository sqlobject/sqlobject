from main import *
from col import *
from sqlbuilder import AND, OR, NOT, IN, LIKE, CONTAINSSTRING, const, func
from styles import *
from joins import *
from include import validators
from dbconnection import connectionForURI

## Each of these imports allows the driver to install itself
## Then we set up some backward compatibility

def _warn(msg):
    import warnings
    warnings.warn(msg, DeprecationWarning, stacklevel=2)

import firebird
_firebird = firebird
del firebird
def FirebirdConnection(*args, **kw):
    _warn('FirebirdConnection is deprecated; use connectionForURI("firebird://...") or "from sqlobject.firebird import builder; FirebirdConnection = builder()"')
    _firebird.builder()(*args, **kw)

import mysql
_mysql = mysql
del mysql
def MySQLConnection(*args, **kw):
    _warn('MySQLConnection is deprecated; use connectionForURI("mysql://...") or "from sqlobject.mysql import builder; MySQLConnection = builder()"')
    _mysql.builder()(*args, **kw)

import postgres
_postgres = postgres
del postgres
def PostgresConnection(*args, **kw):
    _warn('PostgresConnection is deprecated; use connectionForURI("postgres://...") or "from sqlobject.postgres import builder; PostgresConnection = builder()"')
    _postgres.builder()(*args, **kw)

import sqlite
_sqlite = sqlite
del sqlite
def SQLiteConnection(*args, **kw):
    _warn('SQLiteConnection is deprecated; use connectionForURI("sqlite://...") or "from sqlobject.sqlite import builder; SQLiteConnection = builder()"')
    _sqlite.builder()(*args, **kw)

import dbm
_dbm = dbm
del dbm
def DBMConnection(*args, **kw):
    _warn('DBMConnection is deprecated; use connectionForURI("dbm://...") or "from sqlobject.dbm import builder; DBMConnection = builder()"')
    _dbm.builder()(*args, **kw)

import sybase
_sybase = sybase
del sybase
def SybaseConnection(*args, **kw):
    _warn('SybaseConnection is deprecated; use connectionForURI("sybase://...") or "from sqlobject.sybase import builder; SybaseConnection = builder()"')
    _sybase.builder()(*args, **kw)


import maxdb
_maxdb = maxdb
del maxdb
def MaxdbConnection(*args, **kw):
    _warn('MaxdbConnection is deprecated; use connectionForURI("maxdb://...") or "from sqlobject.maxdb import builder; MaxdbConnection = builder()"')
    _maxdb.builder()(*args, **kw)