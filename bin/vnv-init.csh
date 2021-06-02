# vnv, the little shortcut for virtualenv.
# Startup script for csh.
# Rcfile: source `which vnv-init.csh`

alias vnv 'vnv.cli cshell \!* && source `which vnv-do-finish.csh`'
