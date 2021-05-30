"""The main component of vnv."""

import itertools
import os
from pathlib import Path
import re
import shutil
import sys
import textwrap

from . import __version__
from .lists import BetterList, ChainList
from .meta import (PathManager, arg_is_name, internal_dir, path_file,
                   vnv_cache, vnv_home)
from .shell_compat import shells


def badcommand(msg):
    """(Parsing error) print to stderr and quit."""
    fatalerror(msg, label='usage', code=2)

class doing:
    """`with` wrapper for messages like "Doing X... Done.\""""

    done = ' Done.'

    def __init__(self, msg):
        self.msg = msg

    def __enter__(self):
        echo(self.msg + '...', width=72 - len(self.done), end='', flush=True)

    def __exit__(self, exc_type, exc_value, traceback):
        echo(self.done)


def echo(text, width=72, **kwargs):
    """`print()`, but wraps long lines, preserving the initial indent."""
    for line in str(text).splitlines():
        if len(line) > width:
            indent = re.match('\\s*', line)[0]
            line = textwrap.fill(line, width=width, replace_whitespace=False,
                                 subsequent_indent=indent)
        print(line, **kwargs)


def envnotfound(env):
    """`'Env "my-venv" not found. Did you mean "./my-venv"?'`"""
    msg = f'Env "{env}" not found.'
    if arg_is_name(env) and Path(env).exists():
        msg += f'\nDid you mean "./{env}"?'
    return msg


def expectedgot(expected, got):
    """A common error message."""
    return f'Expected {expected} arguments, got {got}.'


def failcheck(msg):
    """(Failed check) print to stderr and quit."""
    fatalerror(msg, label='failed', code=1)


def fatalerror(msg, label='error', code=1):
    """Print to stderr and quit."""
    id_msg = ': '.join(('vnv', label, msg))  # Identify vnv.
    echo(id_msg, file=sys.stderr)
    sys.exit(code)


def main(args=None):
    """Run the CLI."""
    CLI(args)


def selectnpop(dic, lis, i=0):
    """If `dic[lis[i]]` exists, return it after popping `lis[i]`.

    Falls back on `dic[None]`.
    """
    try:
        selection = dic[lis[i]]
    except (IndexError, KeyError):
        return dic[None]
    lis.pop(i)
    return selection


def tilde(path):
    """Inverse of `Path.expanduser()`. For display purposes."""
    try:
        rel = path.relative_to(Path.home())
    except ValueError:
        pass
    else:
        path = '~' / rel
    return path.as_posix()


def write_path_file(new_vnv_path):
    """Overwrite path.txt."""
    path_file.write_text('\n'.join(new_vnv_path))


class CLI:
    """Instance of CLI execution. Holds the args, vnv path, etc."""

    def __init__(self, args=None):
        args = sys.argv[1:] if args is None else list(args)
        # vnv needs to know which shell it's outputting for, so the
        # first argument is the name of the shell/shell family, passed
        # to vnv.cli under the hood.
        shellmap = {sh.name: sh for sh in shells}
        self.shell = shellmap.get(args.pop(0)) if args else None
        if self.shell is None:
            badcommand('vnv.cli should not be used directly.\nTry "vnv".')
        self.raw_args = tuple(args)  # Used for forwarding
        # Instantiate each Command subclass with a reference to the CLI.
        cmds = (Class(self) for Class in Command.__subclasses__())
        self.commands = {cmd.name: cmd for cmd in cmds}
        # If -- is an argument, split the args on it.
        # Options/subcommands can only be on the left side.
        dd_index = args.index('--') if '--' in args else len(args)
        self.mixedargs, ddargs = map(BetterList,
                                     (args[:dd_index], args[dd_index + 1:]))
        self.allargs = ChainList(self.mixedargs, ddargs)
        help_flag = self.mixedargs.eject('--help')
        cmd = selectnpop(self.commands, self.mixedargs)
        if help_flag:
            echo(cmd.long_help)
        else:
            self.pathm = PathManager(self.shell)
            cmd()
        sys.exit(0)


class Command:
    """Holds a subcommand's execution method and some metadata."""

    def __init__(self, cli):
        self.help = self.__doc__
        self.cli = cli


class MainCommand(Command):
    """Toggle an env"""

    name = None

    @property
    def long_help(self):
        start = f"""\
Usage:
  vnv [ENV]
  vnv SUBCOMMAND [ARGS]

vnv {__version__}, the little shortcut for virtualenv.

Run "vnv ENV" to activate and cache an env, then just "vnv" to toggle it
afterwards.

Available subcommands:"""
        subcmds = list(self.cli.commands.values())
        names = tuple(subcmd.name or '(none)' for subcmd in subcmds)
        maxwidth = max(map(len, names))
        subcmd_list = (f'  {name.ljust(maxwidth)}  {subcmd.help}'
                       for name, subcmd in zip(names, subcmds))
        end = '\nUse --help to get more help with subcommands.'
        return '\n'.join(itertools.chain((start,), subcmd_list, (end,)))

    def __call__(self):
        if len(self.cli.allargs) > 1:
            badcommand(expectedgot('0 or 1', len(self.cli.allargs)))
        if self.cli.allargs:
            # Env specified, so activate that.
            actfile = self.cli.pathm.lookup(self.cli.allargs[0])
            if actfile is None:
                fatalerror(envnotfound(self.cli.allargs[0]))
            self.activate(actfile, True)
        elif os.getenv('VIRTUAL_ENV'):
            # No args, active, so deactivate.
            self.deactivate()
        else:
            # No args, inactive, so try to activate from cache.
            cached = os.getenv(vnv_cache)
            if not cached:  # Could be None or ''
                fatalerror('No env cached.'
                           '\nTry "vnv --help" for more information.')
            actfile = self.cli.pathm.get_actfile(Path(cached))
            if actfile is None:
                fatalerror(f'Cached env "{cached}" is not really an env.')
            self.activate(actfile)

    def activate(self, actfile, set_cache=False):
        lines = [self.cli.shell.source % actfile]
        if set_cache:
            lines.append(self.cli.shell.export
                         % (vnv_cache, actfile.parents[1]))
        self.finish(lines)

    def deactivate(self):
        self.finish([self.cli.shell.deactivate])

    def finish(self, lines):
        finish_file = vnv_home / ('finish' + self.cli.shell.ext)
        finish_file.write_text('\n'.join(lines))


class NewCommand(Command):
    """Create an env"""

    name = 'new'
    long_help = """\
Usage:
    vnv new ENV [VIRTUALENV_OPTIONS]

Create an env with virtualenv, forwarding VIRTUALENV_OPTIONS.
See "virtualenv --help".

If ENV is a name, it will be created as an internal env.
To create "my-venv" in the current directory, make sure to use:
    vnv new ./my-venv"""

    def __call__(self):
        if not self.cli.allargs:
            badcommand(expectedgot('1 or more', 0))
        env = self.cli.allargs[0]
        if arg_is_name(env):
            env = str(internal_dir / env)
        try:
            import virtualenv
        except ImportError:
            fatalerror('Cannot access virtualenv. Is it installed?')
        # Account for the possiblility of a -- coming before ENV.
        subsequent_args = self.cli.raw_args[2 if self.cli.mixedargs else 3:]
        with doing(f'Creating virtualenv at "{env}"'):
            virtualenv.cli_run([env, *subsequent_args])


class DelCommand(Command):
    """Destroy an env"""

    name = 'del'
    long_help = """\
Usage:
    vnv del ENV...

Destroy ENV.
In other words, delete the folder ENV refers to.
Use "vnv which ENV" to confirm which folder that is."""

    def __call__(self):
        if not self.cli.allargs:
            badcommand(expectedgot('1 or more', 0))
        for env in self.cli.allargs:
            actfile = self.cli.pathm.lookup(env)
            if actfile is not None:
                env_folder = actfile.parents[1]
                with doing(f'Deleting env "{env_folder}"'):
                    shutil.rmtree(env_folder)
            else:
                fatalerror(envnotfound(env))


class ListCommand(Command):
    """List installed envs"""

    name = 'list'
    long_help = """\
Usage:
    vnv list [-n | -p]

List all envs on the vnv path. See "vnv path --help" for more
information.

If -n is given, only print env names, each on its own line. If -p is
given, do the same with env paths."""

    def __call__(self):
        paths_only = self.cli.mixedargs.eject('-p')
        names_only = not paths_only and self.cli.mixedargs.eject('-n')
        if self.cli.allargs:
            badcommand(expectedgot(0, len(self.cli.allargs)))
        for path_entry in self.cli.pathm.path:
            envs = tuple(self.cli.pathm.get_envs(path_entry))
            if names_only or paths_only:
                for env in envs:
                    print(env.name if names_only else env)
            # Print titles and indented env names, but skip the title if
            # there's nothing to put under it.
            elif envs:
                echo('(internal):' if path_entry is internal_dir
                     else f'{path_entry}:')
                for env in envs:
                    echo(' ' * 4 + env.name)


class WhichCommand(Command):
    """Which env is ...?"""

    name = 'which'

    @property
    def long_help(self):
        return f"""\
Usage:
    vnv which [ENV]

Print the location of ENV, if specified. If not, print the location of
the cached env.

Use this to see what ENV resolves to, or to check the cached env (also
stored in {self.cli.shell.exported % vnv_cache})."""

    def __call__(self):
        if len(self.cli.allargs) > 1:
            badcommand(expectedgot('0 or 1', len(self.cli.allargs)))
        env = self.cli.allargs.safepop(0)
        if env is not None:
            # Resolve and print env.
            actfile = self.cli.pathm.lookup(env)
            if actfile is not None:
                print(actfile.parents[1])
            else:
                failcheck(envnotfound(env))
        else:
            # Print $VNV_CACHE.
            cached = os.getenv(vnv_cache)
            if cached:  # Could be None or ''
                print(cached)
            else:
                failcheck('No env cached.')


class PathCommand(Command):
    """View/modify your vnv path"""

    name = 'path'
    long_help = f"""\
Usage:
    vnv path
    vnv path add [N] DIR
    vnv path pop N...
    vnv path order N...

Display or modify your vnv path.

If you keep your installed envs in a folder somewhere, the vnv path is
how to tell vnv about it. The vnv path includes the internal envs folder
and any newline-separated paths in "{tilde(path_file)}".

When given a name like "my-venv", vnv will only look for it on the vnv
path. To specify that "my-venv" is in the current directory, use the
path "./my-venv" instead.

vnv only finds envs that your shell can activate.

vnv path
    Displays your vnv path.

vnv path add [N] DIR
    Adds DIR to {path_file.name}, at position N (if specified). If DIR is not \
an absolute path, it will be relative to wherever vnv is run. Since \
{tilde(internal_dir)} is always #0, N must be 1 or more.

vnv path pop N...
    Removes dir(s) by number.

vnv path order N...
    Brings dir(s) to the start of {path_file.name} by number.

You can always just go edit {path_file.name} yourself."""

    def __call__(self):
        option_cmds = {None: self.print, 'add': self.add, 'pop': self.pop,
                       'order': self.order}
        selectnpop(option_cmds, self.cli.mixedargs)()

    def print(self):
        """$ vnv path"""
        if self.cli.allargs:
            badcommand(expectedgot(0, len(self.cli.allargs)))
        # Display all the searchable paths, numbered and aligned.
        path_entries = (internal_dir.as_posix(), *self.cli.pathm.raw)
        digits = len(str(len(path_entries) - 1))
        def num(n):
            return f'{n}.'.ljust(digits + 2)
        echo(f'{num(0)}{path_entries[0]}  (internal)')
        for n, path_entry in enumerate(path_entries[1:], start=1):
            echo(num(n) + path_entry)

    def add(self):
        """$ vnv path add [N] DIR"""
        if len(self.cli.allargs) not in (1, 2):
            badcommand(expectedgot('1 or 2', len(self.cli.allargs)))
        max_n = len(self.cli.pathm.path)
        if len(self.cli.allargs) == 2:
            # Get N.
            n_str = self.cli.allargs.pop(0)
            try:
                n = int(n_str)
                if not 1 <= n <= max_n:
                    raise ValueError()
            except ValueError:
                badcommand(f'N must be an integer between 1 and {max_n}.')
        else:
            n = max_n
        new_vnv_path = list(self.cli.pathm.raw)
        new_vnv_path.insert(n - 1, self.cli.allargs[0])
        write_path_file(new_vnv_path)

    def pop(self):
        """$ vnv path pop N..."""
        new_vnv_path = list(self.cli.pathm.raw)
        for n in self.parse_ns():
            entry = self.cli.pathm.raw[n - 1]
            new_vnv_path.remove(entry)
        write_path_file(new_vnv_path)

    def order(self):
        """$ vnv path order N..."""
        old_vnv_path = list(self.cli.pathm.raw)
        new_vnv_path = []
        for n in self.parse_ns():
            entry = self.cli.pathm.raw[n - 1]
            new_vnv_path.append(entry)
            old_vnv_path[n - 1] = None
        new_vnv_path.extend(i for i in old_vnv_path if i is not None)
        write_path_file(new_vnv_path)

    def parse_ns(self):
        """For path pop and path order, parse all those Ns."""
        if not self.cli.allargs:
            badcommand(expectedgot('1 or more', 0))
        ns = []
        valid_n = range(1, len(self.cli.pathm.path))
        for n_str in self.cli.allargs:
            try:
                n = int(n_str)
            except ValueError:
                badcommand(f'{n_str!r} is not an integer.')
            if n not in valid_n:
                fatalerror(f'Cannot modify path entry #{n}.')
            if n in ns:
                fatalerror(f'Got duplicate: {n}.')
            ns.append(n)
        return ns
