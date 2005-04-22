#!/usr/bin/env python
import optparse
import fnmatch
import os
import sys
try:
    from paste import pyconfig
except ImportError:
    pyconfig = None

import sqlobject
from sqlobject.util import moduleloader
from sqlobject.declarative import DeclarativeMeta

class CommandRunner(object):

    def __init__(self):
        self.commands = {}
        self.command_aliases = {}

    def run(self, argv):
        invoked_as = argv[0]
        args = argv[1:]
        for i in range(len(args)):
            if not args[i].startswith('-'):
                # this must be a command
                command = args[i].lower()
                del args[i]
                break
        else:
            # no command found
            self.invalid('No COMMAND given (try "%s help")'
                         % os.path.basename(invoked_as))
        real_command = self.command_aliases.get(command, command)
        if real_command not in self.commands.keys():
            self.invalid('COMMAND %s unknown' % command)
        runner = self.commands[real_command](
            invoked_as, command, args, self)
        runner.run()

    def register(self, command):
        name = command.name
        self.commands[name] = command
        for alias in command.aliases:
            self.command_aliases[alias] = name

    def invalid(self, msg, code=2):
        print msg
        sys.exit(code)

the_runner = CommandRunner()
register = the_runner.register

def standard_parser(connection=True, simulate=True,
                    interactive=False, find_modules=True):
    parser = optparse.OptionParser()
    parser.add_option('-v', '--verbose',
                      help='Be verbose (multiple times for more verbosity)',
                      action='count',
                      dest='verbose',
                      default=0)
    if simulate:
        parser.add_option('-n', '--simulate',
                          help="Don't actually do anything (implies -v)",
                          action='store_true',
                          dest='simulate')
    if connection:
        parser.add_option('-c', '--connection',
                          help="The database connection URI",
                          metavar='URI',
                          dest='connection_uri')
        if pyconfig:
            parser.add_option('-f', '--config-file',
                              help="The Paste config file that contains the database URI (in the database key)",
                              metavar="FILE",
                              dest="config_file")
    if find_modules:
        parser.add_option('-m', '--module',
                          help="Module in which to find SQLObject classes",
                          action='append',
                          metavar='MODULE',
                          dest='modules',
                          default=[])
        parser.add_option('-p', '--package',
                          help="Package to search for SQLObject classes",
                          action="append",
                          metavar="PACKAGE",
                          dest="packages",
                          default=[])
        parser.add_option('--class',
                          help="Select only named classes (wildcards allowed)",
                          action="append",
                          metavar="NAME",
                          dest="class_matchers",
                          default=[])
    if interactive:
        parser.add_option('-i', '--interactive',
                          help="Ask before doing anything (use twice to be more careful)",
                          action="count",
                          dest="interactive",
                          default=0)
    return parser

class Command(object):

    __metaclass__ = DeclarativeMeta

    min_args = 0
    min_args_error = 'You must provide at least %(min_args)s arguments'
    max_args = 0
    max_args_error = 'You must provide no more than %(max_args)s arguments'
    aliases = ()
    required_args = []
    description = None

    def __classinit__(cls, new_args):
        if cls.__bases__ == (object,):
            # This abstract base class
            return
        register(cls)
    
    def __init__(self, invoked_as, command_name, args, runner):
        self.invoked_as = invoked_as
        self.command_name = command_name
        self.raw_args = args
        self.runner = runner

    def run(self):
        self.parser.usage = "%%prog [options]\n%s" % self.summary
        self.parser.prog = '%s %s' % (
            os.path.basename(self.invoked_as),
            self.command_name)
        if self.description:
            self.parser.description = description
        self.options, self.args = self.parser.parse_args(self.raw_args)
        if (getattr(self.options, 'simulate', False)
            and not self.options.verbose):
            self.options.verbose = 1
        if self.min_args is not None and len(self.args) < self.min_args:
            self.runner.invalid(
                self.min_args_error % {'min_args': self.min_args,
                                       'actual_args': len(self.args)})
        if self.max_args is not None and len(self.args) > self.max_args:
            self.runner.invalid(
                self.max_args_error % {'max_args': self.max_args,
                                       'actual_args': len(self.args)})
        for var_name, option_name in self.required_args:
            if not getattr(self.options, var_name, None):
                self.runner.invalid(
                    'You must provide the option %s' % option_name)
        conf = self.config()
        if conf and conf.get('sys_path'):
            update_sys_path(conf['sys_path'], self.options.verbose)
        self.command()

    def classes(self, require_connection=True):
        all = []
        for module_name in self.options.modules:
            all.extend(self.classes_from_module(
                moduleloader.load_module(module_name)))
        for package_name in self.options.packages:
            all.extend(self.classes_from_package(package_name))
        if self.options.class_matchers:
            filtered = []
            for soClass in all:
                name = soClass.__name__
                for matcher in self.options.class_matchers:
                    if fnmatch.fnmatch(name, matcher):
                        filtered.append(soClass)
                        break
            all = filtered
        conn = self.connection()
        if conn:
            for soClass in all:
                soClass._connection = conn
        else:
            missing = []
            for soClass in all:
                try:
                    if not soClass._connection:
                        missing.append(soClass)
                except AttributeError:
                    missing.append(soClass)
            if missing and require_connection:
                self.runner.invalid(
                    'These classes do not have connections set:\n  * %s\n'
                    'You must indicate --connection=URI'
                    % '\n  * '.join([soClass.__name__
                                     for soClass in missing]))
        return all

    def classes_from_module(self, module):
        all = []
        if hasattr(module, 'soClasses'):
            for name_or_class in module.soClasses:
                if isinstance(name_or_class, str):
                    name_or_class = getattr(module, name_or_class)
                all.append(name_or_class)
        else:
            for name in dir(module):
                value = getattr(module, name)
                if (isinstance(value, type)
                    and issubclass(value, sqlobject.SQLObject)
                    and value.__module__ == module.__name__):
                    all.append(value)
        return all

    def connection(self):
        config = self.config()
        if config is not None:
            assert config.get('database'), (
                "No database variable found in config file %s"
                % self.options.config_file)
            return sqlobject.connectionForURI(config['database'])
        elif getattr(self.options, 'connection_uri', None):
            return sqlobject.connectionForURI(self.options.connection_uri)
        else:
            return None

    def config(self):
        if getattr(self.options, 'config_file', None):
            assert pyconfig, (
                "The --config-file option should not be available without paste.pyconfig installed")
            config = pyconfig.Config()
            config.load(self.options.config_file)
            return config
        else:
            return None

    def classes_from_package(self, package_name):
        raise NotImplementedError

    def command(self):
        raise NotImplementedError

    def _get_prog_name(self):
        return os.path.basename(self.invoked_as)
    prog_name = property(_get_prog_name)

    def ask(self, prompt, safe=False, default=True):
        if self.options.interactive >= 2:
            default = safe
        if default:
            prompt += ' [Y/n]? '
        else:
            prompt += ' [y/N]? '
        while 1:
            response = raw_input(prompt).strip()
            if not response.strip():
                return default
            if response and response[0].lower() in ('y', 'n'):
                return response[0].lower() == 'y'
            print 'Y or N please'

class CommandSQL(Command):

    name = 'sql'
    summary = 'Show SQL CREATE statements'

    parser = standard_parser(simulate=False)

    def command(self):
        classes = self.classes()
        for cls in classes:
            if self.options.verbose >= 1:
                print '-- %s from %s' % (
                    cls.__name__, cls.__module__)
            print cls.createTableSQL().strip() + ';\n'

class CommandList(Command):

    name = 'list'
    summary = 'Show all SQLObject classes found'

    parser = standard_parser(simulate=False, connection=False)

    def command(self):
        if self.options.verbose >= 1:
            print 'Classes found:'
        classes = self.classes(require_connection=False)
        for soClass in classes:
            print '%s.%s' % (soClass.__module__, soClass.__name__)
            if self.options.verbose >= 1:
                print '  Table: %s' % soClass.sqlmeta.table

class CommandCreate(Command):

    name = 'create'
    summary = 'Create tables'

    parser = standard_parser(interactive=True)

    def command(self):
        v = self.options.verbose
        created = 0
        existing = 0
        for soClass in self.classes():
            exists = soClass._connection.tableExists(soClass.sqlmeta.table)
            if v >= 1:
                if exists:
                    existing += 1
                    print '%s already exists.' % soClass.__name__
                else:
                    print 'Creating %s' % soClass.__name__
            if v >= 2:
                print soClass.createTableSQL()
            if (not self.options.simulate
                and not exists):
                if self.options.interactive:
                    if self.ask('Create %s' % soClass.__name__):
                        created += 1
                        soClass.createTable()
                    else:
                        print 'Cancelled'
                else:
                    created += 1
                    soClass.createTable()
        if v >= 1:
            print '%i tables created (%i already exist)' % (
                created, existing)
        

class CommandDrop(Command):

    name = 'drop'
    summary = 'Drop tables'

    parser = standard_parser(interactive=True)

    def command(self):
        v = self.options.verbose
        dropped = 0
        not_existing = 0
        for soClass in self.classes():
            exists = soClass._connection.tableExists(soClass.sqlmeta.table)
            if v >= 1:
                if exists:
                    print 'Dropping %s' % soClass.__name__
                else:
                    not_existing += 1
                    print '%s does not exist.' % soClass.__name__
            if (not self.options.simulate
                and exists):
                if self.options.interactive:
                    if self.ask('Drop %s' % soClass.__name__):
                        dropped += 1
                        soClass.dropTable()
                    else:
                        print 'Cancelled'
                else:
                    dropped += 1
                    soClass.dropTable()
        if v >= 1:
            print '%i tables dropped (%i didn\'t exist)' % (
                dropped, not_existing)

class CommandStatus(Command):

    name = 'status'
    summary = 'Show status of classes vs. database'

    parser = standard_parser(simulate=False)

    def print_class(self, soClass):
        if self.printed:
            return
        self.printed = True
        print 'Checking %s...' % soClass.__name__

    def command(self):
        good = 0
        bad = 0
        missing_tables = 0
        columnsFromSchema_warning = False
        for soClass in self.classes():
            conn = soClass._connection
            self.printed = False
            if self.options.verbose:
                self.print_class(soClass)
            if not conn.tableExists(soClass.sqlmeta.table):
                self.print_class(soClass)
                print '  Does not exist in database'
                missing_tables += 1
                continue
            try:
                columns = conn.columnsFromSchema(soClass.sqlmeta.table,
                                                 soClass)
            except AttributeError:
                if not columnsFromSchema_warning:
                    print 'Database does not support reading columns'
                    columnsFromSchema_warning = True
                good += 1
                continue
            existing = {}
            for col in columns:
                col = col.withClass(soClass)
                existing[col.dbName] = col
            missing = {}
            for col in soClass.sqlmeta._columns:
                if existing.has_key(col.dbName):
                    del existing[col.dbName]
                else:
                    missing[col.dbName] = col
            if existing:
                self.print_class(soClass)
                for col in existing.values():
                    print '  Database has extra column: %s' % col.dbName
            if missing:
                self.print_class(soClass)
                for col in missing.values():
                    print '  Database missing column: %s' % col.dbName
            if existing or missing:
                bad += 1
            else:
                good += 1
        if self.options.verbose:
            print '%i in sync; %i out of sync; %i not in database' % (
                good, bad, missing_tables)
            

class CommandHelp(Command):

    name = 'help'
    summary = 'Show help'

    parser = optparse.OptionParser()

    max_args = 1

    def command(self):
        if self.args:
            the_runner.run([self.invoked_as, self.args[0], '-h'])
        else:
            print 'Available commands:'
            print '  (use "%s help COMMAND" or "%s COMMAND -h" ' % (
                self.prog_name, self.prog_name)
            print '  for more information)'
            items = the_runner.commands.items()
            items.sort()
            max_len = max([len(cn) for cn, c in items])
            for command_name, command in items:
                print '%s:%s %s' % (command_name,
                                    ' '*(max_len-len(command_name)),
                                    command.summary)
                if command.aliases:
                    print '%s (Aliases: %s)' % (
                        ' '*max_len, ', '.join(command.aliases))

class CommandExecute(Command):

    name = 'execute'
    summary = 'Execute SQL statements'

    parser = standard_parser(find_modules=False)
    parser.add_option('--stdin',
                      help="Read SQL from stdin (normally takes SQL from the command line)",
                      dest="use_stdin",
                      action="store_true")

    max_args = None

    def command(self):
        args = self.args
        if self.options.use_stdin:
            if self.options.verbose:
                print "Reading additional SQL from stdin (Ctrl-D or Ctrl-Z to finish)..."
            args.append(sys.stdin.read())
        self.conn = self.connection().getConnection()
        self.cursor = self.conn.cursor()
        for sql in args:
            self.execute_sql(sql)

    def execute_sql(self, sql):
        if self.options.verbose:
            print sql
        try:
            self.cursor.execute(sql)
        except Exception, e:
            if not self.options.verbose:
                print sql
            print "****Error:"
            print '    ', e
            return
        desc = self.cursor.description
        rows = self.cursor.fetchall()
        if self.options.verbose:
            if not self.cursor.rowcount:
                print "No rows accessed"
            else:
                print "%i rows accessed" % self.cursor.rowcount
        if desc:
            for name, type_code, display_size, internal_size, precision, scale, null_ok in desc:
                sys.stdout.write("%s\t" % name)
            sys.stdout.write("\n")
        for row in rows:
            for col in row:
                sys.stdout.write("%r\t" % col)
            sys.stdout.write("\n")
        print
                
def update_sys_path(paths, verbose):
    if isinstance(paths, (str, unicode)):
        paths = [paths]
    for path in paths:
        path = os.path.abspath(path)
        if path not in sys.path:
            if verbose:
                print 'Adding %s to path' % path
            sys.path.append(path)

if __name__ == '__main__':
    the_runner.run(sys.argv)
