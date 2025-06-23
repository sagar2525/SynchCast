@if not "%EnableCmdEcho%" == "1" echo off

setlocal EnableDelayedExpansion

rem set TestEcho=echo

call "%~dp0setvars"

if errorlevel 1 (

  echo No SetVars command file
  exit /b 1

)

set CableNum=%~1
set ValueName=%~2
set ValueData=%~3
set DataMin=%~4
set DataMax=%~5

if "%~3" == "" (

  echo Usage: %~n0 {^<Cable num^>^|*^|Debug^} ^<Value name^> {^<Value^>^|?^|-} [^<min^> ^<max^>]
  echo.
  echo Instead of cable number, specify "*" to set a driver parameter,
  echo or "Debug" to set a debug parameter ^(debug builds only^).
  echo Instead of the value, specify "?" to show the current value,
  echo or "-" to delete the value.
  echo.
  pause
  exit /b 1

)

if not "%CableNum%" == "*" if /i not "%CableNum%" == "debug" (

  call :CheckNumber "Cable number" "%CableNum%" 1 256
  if errorlevel 1 exit /b 1

)

if not "%ValueData%" == "-" if not "%ValueData%" == "?" (

  call :CheckNumber "%ValueName%" "%ValueData%" "%DataMin%" "%DataMax%"
  if errorlevel 1 exit /b 1

)

%TestEcho% reg query "%AppRegKey%" > nul

if errorlevel 1 (

  echo %~n0: Key "%AppRegKey%" not found
  pause
  exit /b 1

)

%TestEcho% reg query "%DrvRegBase%" > nul

if errorlevel 1 (

  echo %~n0: Key "%DrvRegBase%" not found
  pause
  exit /b 1

)

set MsgPfx=

if /i "%CableNum%" == "debug" (

  set AppRegKey=%AppRegKey%\Debug
  set DrvRegKey=%DrvRegKey%\Debug

) else if not "%CableNum%" == "*" (

  set AppRegKey=%AppRegKey%\Cable %CableNum%
  set DrvRegKey=%DrvRegKey%\Cable %CableNum%
  set MsgPfx=Cable %CableNum%: 

)

if "%ValueData%" == "?" (

  %TestEcho% reg query "%AppRegKey%" /v "%ValueName%"
  %TestEcho% reg query "%DrvRegKey%" /v "%ValueName%"

) else if "%ValueData%" == "-" (

  echo %MsgPfx%Deleting "%ValueName%"

  %TestEcho% reg delete "%AppRegKey%" /v "%ValueName%" /f
  if errorlevel 1 exit /b 1

  %TestEcho% reg delete "%DrvRegKey%" /v "%ValueName%" /f
  if errorlevel 1 exit /b 1

) else (

  echo %MsgPfx%Setting "%ValueName%" to %ValueData%

  %TestEcho% reg add "%AppRegKey%" /v "%ValueName%" /t REG_DWORD /d %ValueData% /f
  if errorlevel 1 exit /b 1

  %TestEcho% reg add "%DrvRegKey%" /v "%ValueName%" /t REG_DWORD /d %ValueData% /f
  if errorlevel 1 exit /b 1

)

exit /b 0




:CheckNumber

setlocal EnableDelayedExpansion

set Name=%~1
set Val=%~2
set Min=%~3
set Max=%~4

set /a Num=%Val%

if errorlevel 1 exit /b 1

set Valid=1

if %Num% == 0 if not "%Val%" == "0" if /i not "%Val%" == "0x0" set Valid=0

if %Valid% NEQ 1 (

  echo %~n0: "%Name%" - invalid number "%Val%"
  pause
  exit /b 1

)

if defined Min (

  set Valid=0

  if %Num% GEQ %Min% if %Num% LEQ %Max% set Valid=1

  if !Valid! NEQ 1 (

    echo %~n0: "%Name%" must be within %Min%..%Max%
    pause
    exit /b 1

  )

)

exit /b 0
