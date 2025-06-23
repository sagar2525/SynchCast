@if not "%EnableCmdEcho%" == "1" echo off

setlocal

set Cbl=%~1
set Side=%~2
set Type=%~3

if "%~3" == "" (

  echo Usage: %~n0 ^<Cbl^> c^|r ^<Hide^>
  exit /b 1

)

if "%Cbl%" == "*" (

  echo %~n0: Cable number must be present
  pause
  exit /b 1

)

if /i not "%Side%" == "c" if /i not "%Side%" == "r" (

  echo %~n0: Cable side must be "c" or "r"
  pause
  exit /b 1

)

if /i "%Side%" == "c" (

  set SideName=capture

) else (

  set SideName=render

)

if defined Hide if not "%Hide%" == "*" (

  call "%~dp0setregdword" "%Cbl%" "Hide %SideName% device" "%Hide%" 0 1
  if errorlevel 1 exit /b 1

)
