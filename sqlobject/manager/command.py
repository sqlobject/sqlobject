#!/usr/bin/env python
import optparse
import fnmatch
import os
import sys

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
            self.invalid('No COMMAND given')
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
                    interactive=False):
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
        if self.options.connection_uri:
            return sqlobject.connectionForURI(self.options.connection_uri)
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
            print '  (use "%s help COMMAND" or "%s COMMAND -h" for more)' % (
                self.prog_name, self.prog_name)
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
                

if __name__ == '__main__':
    the_runner.run(sys.argv)
