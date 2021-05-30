"""Compatibility between the shells virtualenv supports.

bash/zsh vs cmd.exe vs csh vs fish vs PowerShell vs xonsh.
"""

from collections import namedtuple

shell_field_names = (
    'name',  # Name virtualenv knows it by
    'actfile',  # Name of activator file
    'deactivate',  # Deactivate command
    'export',  # Export syntax
    'exported',  # Environment variable syntax
    'ext',  # Suffix to use for the finish script
    'source',  # Source command syntax
    'startup',  # What should be in the rcfile
)
Shell = namedtuple('Shell', shell_field_names, defaults=(None,) * 6)

BASH = Shell(  # Also zsh, and maybe ksh
    name='bash',
    actfile='activate',
    deactivate='deactivate',
    export='export %s="%s"',
    exported='$%s',
    ext='.sh',
    source='. "%s"',
    startup='. vnv-startup',
)

BATCH = Shell(
    name='batch',
    actfile='activate.bat',
    deactivate='call deactivate',
    export='set "%s=%s"',
    exported='%%%s%%',
    ext='.bat',
    source='call "%s"',
    # No startup=
)

CSHELL = Shell(
    name='cshell',
    actfile='activate.csh',
    deactivate='deactivate',
    export='setenv %s "%s"',
    exported='$%s',
    ext='.csh',
    source='source "%s"',
    startup='source `which vnv-startup.csh`',
)

FISH = Shell(
    name='fish',
    actfile='activate.fish',
    deactivate='deactivate',
    export='set -gx %s "%s"',
    exported='$%s',
    ext='.fish',
    source='source "%s"',
    startup='source < (which vnv-startup.fish)'
)

POWERSHELL = Shell(
    name='powershell',
    actfile='activate.ps1',
    deactivate='deactivate',
    export='$env:%s = "%s"',
    exported='$env:%s',
    ext='.ps1',
    source='& "%s"',
    # No startup=
)

PYTHON = Shell(
    name='python',
    actfile='activate_this.py',
    # No finish script or startup line
)

XONSH = Shell(
    name='xonsh',
    actfile='activate.xsh',
    deactivate='deactivate',
    export='$%s = "%s"',
    exported='$%s',
    ext='.xsh',
    source='source "%s"',
    startup='source vnv-startup.xsh',
)

shells = (BASH, BATCH, CSHELL, FISH, POWERSHELL, PYTHON, XONSH)
