"""The main component of vnv."""

import os
from pathlib import Path
import re
import shutil
import sys
import textwrap

from . import __version__
from .lists import ChainList
from .search import Searcher, arg_is_name, envs_home, path_var
from .shell_compat import shells

cache_var = 'VNV_CACHED'
finish_file_stem = Path.home() / '.vnv-finish'


def badcommand(msg):
    """(Parsing error) print to stderr and quit."""
    fatalerror(msg, label='usage', code=2)


class doing:
    """`with` wrapper for messages like "Doing X... Done.\""""

    done = ' Done.'

    def __init__(self, msg):
        self.msg = msg

    def __enter__(self):
        width = 72 - len(self.done)
        echo(self.msg + '...', width=width, end='', flush=True)

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


def eject(ls, item):
    """Try to find and remove the item, returning whether it was found."""
    try:
        ls.remove(item)
    except ValueError:
        return False
    return True


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


class CLI:
    """Instance of CLI execution. Holds the args, search path, etc."""

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
        try:
            dd_index = args.index('--')
        except ValueError:
            dd_index = len(args)
        self.mixedargs, ddargs = args[:dd_index], args[dd_index + 1:]
        self.allargs = ChainList(self.mixedargs, ddargs)
        help_flag = eject(self.mixedargs, '--help')
        cmd = selectnpop(self.commands, self.mixedargs)
        self.search = Searcher(self.shell)
        if help_flag:
            echo(cmd.long_help)
        else:
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
        subcmds = list(self.cli.commands.values())
        names = tuple(subcmd.name or '(none)' for subcmd in subcmds)
        maxwidth = max(map(len, names))
        subcmd_list = (f'  {name.ljust(maxwidth)}  {subcmd.help}'
                       for name, subcmd in zip(names, subcmds))
        subcmd_table = '\n'.join(subcmd_list)
        return f"""\
Usage:
  vnv [ENV]
  vnv SUBCOMMAND [ARGS]

vnv {__version__}, the little shortcut for virtualenv.

Run "vnv ENV" to activate and cache an env, then just "vnv" to toggle \
it afterwards.

Available subcommands:
{subcmd_table}

Use --help to get more help with subcommands.
"""

    def __call__(self):
        if len(self.cli.allargs) > 1:
            badcommand(expectedgot('0 or 1', len(self.cli.allargs)))
        if self.cli.allargs:
            # Env specified, so activate that.
            actfile = self.cli.search.lookup(self.cli.allargs[0])
            if actfile is None:
                fatalerror(envnotfound(self.cli.allargs[0]))
            self.activate(actfile, True)
        elif os.getenv('VIRTUAL_ENV'):
            # No args, active, so deactivate.
            self.deactivate()
        else:
            # No args, inactive, so try to activate from cache.
            cached = os.getenv(cache_var)
            if not cached:  # Could be None or ''
                fatalerror('No env cached.'
                           '\nTry "vnv --help" for more information.')
            actfile = self.cli.search.get_actfile(Path(cached))
            if actfile is None:
                fatalerror(f'Cached env "{cached}" is not really an env.')
            self.activate(actfile)

    def activate(self, actfile, set_cache=False):
        lines = [self.cli.shell.source % actfile]
        if set_cache:
            lines.append(self.cli.shell.export
                         % (cache_var, actfile.parents[1]))
        self.finish(lines)

    def deactivate(self):
        self.finish([self.cli.shell.deactivate])

    def finish(self, lines):
        finish_file = finish_file_stem.with_suffix(self.cli.shell.ext)
        finish_file.write_text('\n'.join(lines))


class NewCommand(Command):
    """Create an env"""

    name = 'new'

    @property
    def long_help(self):
        return f"""\
Usage:
  vnv new ENV [VIRTUALENV_OPTIONS]

Create an env with virtualenv, forwarding VIRTUALENV_OPTIONS.
See "virtualenv --help".

If ENV is a name, it will be created in the first directory of the vnv \
search path ({tilde(self.cli.search.path[0])}). To always create \
"my-venv" in the current directory, use the explicit path "./my-venv".
"""

    def __call__(self):
        if not self.cli.allargs:
            badcommand(expectedgot('1 or more', 0))
        env = self.cli.allargs[0]
        try:
            import virtualenv
        except ImportError:
            fatalerror('Cannot access virtualenv. Is it installed?')
        if arg_is_name(env):
            first_dir = self.cli.search.path[0]
            env = str(first_dir / env)
        # If the env path starts with `-`, prefix it with `./`.
        if env.startswith('-'):
            env_arg = f'.{os.path.sep}{env}'
        else:
            env_arg = env
        # Account for the possiblility of a -- coming before ENV.
        subsequent_args = self.cli.raw_args[2 if self.cli.mixedargs else 3:]
        with doing(f'Creating virtualenv at "{env}"'):
            virtualenv.cli_run([env_arg, *subsequent_args])


class DelCommand(Command):
    """Destroy an env"""

    name = 'del'
    long_help = """\
Usage:
  vnv del ENV...

Destroy ENV.
In other words, delete the directory ENV refers to.
Use "vnv which ENV" to confirm which directory that is.
"""

    def __call__(self):
        if not self.cli.allargs:
            badcommand(expectedgot('1 or more', 0))
        for env in self.cli.allargs:
            actfile = self.cli.search.lookup(env)
            if actfile is not None:
                env_folder = actfile.parents[1]
                with doing(f'Deleting env "{env_folder}"'):
                    shutil.rmtree(env_folder)
            else:
                fatalerror(envnotfound(env))


class ListCommand(Command):
    """List known envs"""

    name = 'list'

    @property
    def long_help(self):
        exported_path_var = self.cli.shell.exported % path_var
        return f"""\
Usage:
  vnv list [-n | -p]

List all envs on the vnv search path.

If -n is given, only print env names, each on its own line.
If -p is given, do the same with env paths.

The vnv search path is taken from {exported_path_var}, if defined. \
It defaults to a single directory: {tilde(envs_home)}. Directories in \
{exported_path_var} should be separated by a {os.pathsep!r} on this \
platform.

vnv only finds envs that your shell can activate.
"""

    def __call__(self):
        paths_only = eject(self.cli.mixedargs, '-p')
        names_only = not paths_only and eject(self.cli.mixedargs, '-n')
        if self.cli.allargs:
            badcommand(expectedgot(0, len(self.cli.allargs)))
        for path_entry in self.cli.search.path:
            envs = tuple(self.cli.search.get_envs(path_entry))
            if names_only or paths_only:
                for env in envs:
                    print(env.name if names_only else env)
            elif envs:
                echo(f'{path_entry}:')
                for env in envs:
                    echo(f'  {env.name}')
            else:
                try:
                    is_dir = path_entry.is_dir()
                except OSError:
                    is_dir = False
                status = 'empty' if is_dir else 'nonexistent'
                echo(f'{path_entry} ({status})')


class WhichCommand(Command):
    """Test name resolution"""

    name = 'which'

    @property
    def long_help(self):
        return f"""\
Usage:
  vnv which [ENV]

Print the location of ENV, if specified. If not, print the location of
the cached env. Use this to see what ENV resolves to, or to check the
cached env (also stored in {self.cli.shell.exported % cache_var}).

When given a name like "my-venv", vnv will only look for it on the vnv
search path. To specify that "my-venv" is in the current directory, use
the explicit path "./my-venv" instead.
"""

    def __call__(self):
        if self.cli.allargs:
            if len(self.cli.allargs) > 1:
                badcommand(expectedgot('0 or 1', len(self.cli.allargs)))
            env = self.cli.allargs[0]
            # Resolve and print env.
            actfile = self.cli.search.lookup(env)
            if actfile is not None:
                print(actfile.parents[1])
            else:
                failcheck(envnotfound(env))
        else:
            # Print $VNV_CACHED.
            cached = os.getenv(cache_var)
            if cached:  # Could be None or ''
                print(cached)
            else:
                failcheck('No env cached.')
