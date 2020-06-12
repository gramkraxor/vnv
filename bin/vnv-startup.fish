# vnv, the little shortcut for virtualenv.
# Startup script for fish.
# Rcfile: more (which vnv-startup.fish) | source

function vnv
    set -l vnv_finish ~/.vnv/finish.fish
    vnv.cli fish $argv; and if test -f $vnv_finish
        source $vnv_finish
        rm $vnv_finish
    end
end
