"""``vnv``, the little shortcut for ``virtualenv``.

Mostly ``vnv.cli``, the main component of ``vnv``, which requires
wrapper scripts to source an env's activatiors.

Also includes an ``activate()`` function to activate envs within the
Python interpreter via ``activate_this.py``.

Written by Gramkraxor
Public Domain
"""

from .cli import main
from .meta import __version__
from .python import activate
