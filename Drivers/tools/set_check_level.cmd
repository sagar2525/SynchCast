@if not "%EnableCmdEcho%" == "1" echo off

setlocal

set Level=%~1

if not defined Level (

  echo Usage: %~n0 {^<Debug check level ^(0..9^)^> ^| - ^(delete value^)}
  exit /b 1

)

call "%~dp0setregdword" Debug GlobalCheckLevel %Level% 0 9
