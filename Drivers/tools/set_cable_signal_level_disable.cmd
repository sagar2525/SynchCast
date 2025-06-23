@if not "%EnableCmdEcho%" == "1" echo off

setlocal

set Cbl=%~1
set Disable=%~2

if "%~2" == "" (

  echo Usage: %~n0 ^<Cbl^> ^<Disable^>
  exit /b 1

)

if "%Cbl%" == "*" (

  echo %~n0: Cable number must be present
  pause
  exit /b 1

)

if defined Disable if not "%Disable%" == "*" (

  call "%~dp0setregdword" "%Cbl%" "Disable cable signal level" "%Disable%" 0 1
  if errorlevel 1 exit /b 1

)
