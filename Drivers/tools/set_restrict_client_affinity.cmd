@if not "%EnableCmdEcho%" == "1" echo off

setlocal

set Num=%~1

if "%1" == "" (

  echo Usage: %~n0 ^<Minimum number of cables^>
  exit /b 1

)

call "%~dp0restrictaff" client %Num%
