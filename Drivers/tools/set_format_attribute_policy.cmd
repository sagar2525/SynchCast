@if not "%EnableCmdEcho%" == "1" echo off

setlocal

set Cbl=%~1
set Policy=%~2

if "%~2" == "" (

  echo Usage: %~n0 ^<Cbl^> ^<Format attribute support policy^>
  exit /b 1

)

if defined Policy if not "%Policy%" == "*" (

  call "%~dp0setregdword" "%Cbl%" "Format attribute support policy" "%Policy%" 0 2
  if errorlevel 1 exit /b 1

)
