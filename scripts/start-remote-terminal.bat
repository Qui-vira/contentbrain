@echo off
:: Remote Terminal Auto-Start (Windows)
:: Place a shortcut to this file in: shell:startup
:: Or run manually to start the web terminal

set PORT=7681
set USERNAME=quiv
set PASSWORD=contentbrain2026

echo Starting ttyd web terminal on port %PORT%...
cd /d "%USERPROFILE%\onedrive\desktop\contentbrain"

set TTYD="%USERPROFILE%\AppData\Local\Microsoft\WinGet\Packages\tsl0922.ttyd_Microsoft.Winget.Source_8wekyb3d8bbwe\ttyd.exe"
%TTYD% --port %PORT% --credential %USERNAME%:%PASSWORD% --writable bash
