"""Shortcut for activate_this.py."""

from .meta import PathMaster
from .shell_compat import PYTHON


def activate(env):
    """Find ``env`` and use activate_this.py."""
    # pylint: disable=exec-used
    actfile = PathMaster(PYTHON).lookup(env)
    if actfile is None:
        raise RuntimeError(f'env {env!r} not found')
    exec(actfile.read_bytes(), {'__file__': str(actfile)})
