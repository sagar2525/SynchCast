@if not "%EnableCmdEcho%" == "1" echo off

setlocal

set Cbl=%~1
set Enable=%~2

if "%~2" == "" (

  echo Usage: %~n0 ^<Cbl^> ^<Enable^>
  exit /b 1

)

if "%Cbl%" == "*" (

  echo %~n0: Cable number must be present
  pause
  exit /b 1

)

if defined Enable if not "%Enable%" == "*" (

  call "%~dp0setregdword" "%Cbl%" "Use standard PortCls engine" "%Enable%" 0 1
  if errorlevel 1 exit /b 1

)
