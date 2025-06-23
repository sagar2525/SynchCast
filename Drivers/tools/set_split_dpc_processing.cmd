@if not "%EnableCmdEcho%" == "1" echo off

setlocal

set Val=%~1

if "%1" == "" (

  echo Usage: %~n0 ^<Split DPC proc param^>
  exit /b 1

)

call "%~dp0setregdword" * "Split DPC processing among CPUs" %Val% 0 1
