# Standin for a function, since csh doesn't have functions.

if ( -f ~/.vnv-finish.csh ) then
    source ~/.vnv-finish.csh
    rm ~/.vnv-finish.csh
endif
