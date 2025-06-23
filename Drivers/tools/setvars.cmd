@if not "%EnableCmdEcho%" == "1" echo off

set SoftKey=Virtual Audio Cable
set Service=VirtualAudioCable_83ed7f0e-2028-4956-b0b4-39c76fdaef1d

set AppRegKey=HKLM\SOFTWARE\EuMus Design\%SoftKey%\4
set DrvRegBase=HKLM\SYSTEM\CurrentControlSet\Services\%Service%
set DrvRegKey=%DrvRegBase%\Parameters
