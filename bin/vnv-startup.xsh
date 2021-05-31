# vnv, the little shortcut for virtualenv.
# Startup script for xonsh.
# Rcfile: source vnv-startup.xsh

def vnv_xonsh(args):
    vnv_cli = ![vnv.cli xonsh @(args)]
    if not vnv_cli:
        return vnv_cli
    from pathlib import Path
    vnv_finish = Path.home() / '.vnv-finish.xsh'
    if vnv_finish.is_file():
        source @(str(vnv_finish))
        vnv_finish.unlink()

aliases['vnv'] = vnv_xonsh
