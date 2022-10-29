"""Things used between cli.py and python.py, mostly to do with "~/.vnv"."""

import os
from pathlib import Path, PurePath

envs_home = Path.home() / '.vnv' / 'envs'
path_var = 'VNV_PATH'


def arg_is_name(arg):
    """Is `arg` a simple name?."""
    return arg != '..' and PurePath(arg).name == arg


class Searcher:
    """Search path and env resolver."""

    def __init__(self, shell):
        self.shell = shell
        env_path = os.getenv(path_var)
        if env_path is None:
            self.path = (envs_home,)
        else:
            pathstrs = env_path.split(os.pathsep)
            self.path = (*map(Path, pathstrs),)

    def get_actfile(self, path):
        """Get a supposed env's activate file."""
        # If there is a bin/activate or Scripts/activate.bat, etc.,
        # assume `path` is a real env.
        for scripts_dir in ('bin', 'local/bin', 'Scripts'):
            # Check both platforms' scripts folders.
            actfile = path / scripts_dir / self.shell.actfile
            try:
                is_file = actfile.is_file()
            except OSError:
                is_file = False
            if is_file:
                return actfile.absolute()
        return None

    def get_envs(self, path_entry):
        """Yield all the envs in a vnv search path directory."""
        try:
            for path in path_entry.iterdir():
                if self.get_actfile(path) is not None:
                    yield path
        except OSError:  # path_entry is not a readable dir
            pass

    def lookup(self, env):
        """Get the activate file for `env`."""
        if arg_is_name(env):
            # If there is an exact match by name, return it.
            for path_entry in self.path:
                actfile = self.get_actfile(path_entry / env)
                if actfile is not None:
                    return actfile
            # Otherwise, return the first env `env` is short for.
            env = os.path.normcase(env)
            for path_entry in self.path:
                for possible_match in self.get_envs(path_entry):
                    possible_name = os.path.normcase(possible_match.name)
                    if possible_name.startswith(env):
                        return self.get_actfile(possible_match)
            return None
        return self.get_actfile(Path(env))  # Can be None
