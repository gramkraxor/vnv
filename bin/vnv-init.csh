# vnv, the little shortcut for virtualenv.
# Startup script for csh.
# Rcfile: source `which vnv-init.csh`

alias vnv 'vnv.cli cshell \!* && if ( -f ~/.vnv-finish.csh ) then \
    source ~/.vnv-finish.csh \
    rm ~/.vnv-finish.csh \
endif'
