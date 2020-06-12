@echo off
rem    vnv, the little shortcut for virtualenv.
rem    Wrapper script for cmd.exe.

set VNV_FINISH=%USERPROFILE%\.vnv\finish.bat
vnv.cli batch %* && if exist "%VNV_FINISH%" (
    call %VNV_FINISH%
    del %VNV_FINISH%
)
