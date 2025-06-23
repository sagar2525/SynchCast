@if not "%EnableCmdEcho%" == "1" echo off

setlocal

set Cbl=%~1
set Mask=%~2

if "%~2" == "" (

  echo Usage: %~n0 ^<Cbl^> ^<Mask^>
  exit /b 1

)

if "%Cbl%" == "*" (

  echo %~n0: Cable number must be present
  pause
  exit /b 1

)

if defined Mask if not "%Mask%" == "*" (

  call "%~dp0setregdword" "%Cbl%" "Source line types mask" "%Mask%" 1 7
  if errorlevel 1 exit /b 1

)
