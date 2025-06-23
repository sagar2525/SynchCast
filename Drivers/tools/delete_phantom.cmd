@echo off

setlocal

set RegKey=HKLM\SYSTEM\CurrentControlSet\Enum\ROOT\{83ED7F0E-2028-4956-B0B4-39C76FDAEF1D}\0000
set RegVal=Phantom

echo Deleting value "%RegVal%" of key "%RegKey%"

reg delete "%RegKey%" /v "%RegVal%" /f

pause
