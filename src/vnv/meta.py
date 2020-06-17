"""Things used between cli.py and python.py, mostly to do with "~/.vnv"."""

import os
from pathlib import Path, PurePath

import pkg_resources

# Ask setuptools for version.
__version__ = pkg_resources.require('vnv')[0].version
vnv_home = Path.home() / '.vnv'
internal_dir = vnv_home / 'envs'
path_file = vnv_home / 'path.txt'
vnv_cache = 'VNV_CACHE'


def arg_is_name(arg):
    """Is ``arg`` a simple name?."""
    return arg != '..' and PurePath(arg).name == arg


def make_home():
    """Make sure ~/.vnv is present."""
    internal_dir.mkdir(parents=True, exist_ok=True)
    path_file.touch(exist_ok=True)


class PathMaster:
    """Path resolution manager."""

    def __init__(self, shell):
        self.shell = shell
        make_home()
        path_lines = path_file.read_text().splitlines()
        self.raw = tuple(filter(None, map(str.strip, path_lines)))
        self.path = (internal_dir, *map(Path, self.raw))

    def get_actfile(self, path):
        """Get a supposed env's activate file."""
        # If there is a bin/activate or Scripts/activate.bat, etc.,
        # assume `path` is a real env.
        for scripts_dir in ('bin', 'Scripts'):
            # Check both platforms' scripts folders.
            actfile = path / scripts_dir / self.shell.actfile
            if actfile.is_file():
                return actfile.absolute()
        return None

    def get_envs(self, path_entry):
        """Yield all the env folders in a vnv path folder."""
        try:
            for path in path_entry.iterdir():
                if self.get_actfile(path) is not None:
                    yield path
        except FileNotFoundError: # path_entry is not a dir
            pass

    def lookup(self, env):
        """Get the activate file for ``env``."""
        if arg_is_name(env):
            # If there is an exact match by name, return it.
            for path_entry in self.path:
                actfile = self.get_actfile(path_entry / env)
                if actfile is not None:
                    return actfile
            # Otherwise, return the first env ``env`` is short for.
            env = os.path.normcase(env)
            for path_entry in self.path:
                for possible_match in self.get_envs(path_entry):
                    possible_name = os.path.normcase(possible_match.name)
                    if possible_name.startswith(env):
                        return self.get_actfile(possible_match)
            return None
        return self.get_actfile(Path(env)) # Can be None
