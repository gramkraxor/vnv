"""Compatibility between the shells virtualenv supports.

bash/zsh vs cmd.exe vs csh vs fish vs PowerShell vs xonsh.
"""


class Shell: # pylint: disable=too-many-instance-attributes
    """Profile of a supported shell, including the Python interpreter."""

    def __init__(self, *, name, actfile, deactivate=None, export=None,
                 exported=None, ext=None, source=None, startup=None):
        self.name = name # Name virtualenv knows it by
        self.actfile = actfile # Name of activator file
        self.deactivate = deactivate # Deactivate command
        self.export = export # Export syntax
        self.exported = exported # Environment variable syntax
        self.ext = ext # Suffix to use for the finish script
        self.source = source # Source command syntax
        self.startup = startup # What should be in the rcfile

    def __repr__(self):
        return self.name.upper()


BASH = Shell( # Also zsh, and maybe ksh
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
    startup='less (which vnv-startup.fish) | source'
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
