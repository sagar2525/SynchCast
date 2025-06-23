@if not "%EnableCmdEcho%" == "1" echo off

setlocal

rem set TestEcho=echo

call "%~dp0setvars"

if errorlevel 1 (

  echo %~n0: No SetVars command file
  pause
  exit /b 1

)

echo.
echo Virtual Audio Cable driver service will be deleted.
echo This file should be used only as a last chance, if other ways failed.
echo All audio applications must be closed before proceeding, and
echo "Virtual Audio Cable" device must be uninstalled in Device Manager.
echo.

set /p Answer=Are you sure? [Y/N]

if errorlevel 1 exit /b

if /i not "%Answer%" == "y" exit /b 1

%TestEcho% sc delete "%Service%"

pause
