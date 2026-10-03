@echo off
setlocal
cd /d "%~dp0"

set "C_COMPILER=gcc"
where gcc >nul 2>&1
if not errorlevel 1 goto compile
if exist "C:\mingw64\bin\gcc.exe" (
    set "C_COMPILER=C:\mingw64\bin\gcc.exe"
    set "PATH=C:\mingw64\bin;%PATH%"
    goto compile
)
echo GCC was not found. Install MinGW-w64 or add gcc to PATH.
exit /b 1

:compile
echo Compiling the C parser...
"%C_COMPILER%" parse.c -o parse.exe
if errorlevel 1 exit /b 1

rem The current C parser accepts its selection through standard input.
echo Parsing the datasets with C...
echo all| .\parse.exe
exit /b %errorlevel%
