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
echo All Virtual Audio Cable settings will be deleted.
echo VAC Control Panel application must be closed before proceeding.
echo Driver restart will be required for changes to take effect.
echo.

set /p Answer=Are you sure? [Y/N]

if errorlevel 1 exit /b

if /i not "%Answer%" == "y" exit /b 1

%TestEcho% reg delete "%AppRegKey%" /f
%TestEcho% reg delete "%DrvRegKey%" /f

pause
