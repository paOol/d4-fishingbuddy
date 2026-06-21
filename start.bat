@echo off
REM Launch the bot. Right-click -> "Run as administrator" if your key presses
REM don't reach D4 (Battle.net often runs elevated).
cd /d "%~dp0"
py fishingbuddy.py
pause
