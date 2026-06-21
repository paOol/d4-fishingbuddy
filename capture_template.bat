@echo off
REM Run as administrator if D4 is elevated, so the F7 hotkey works in-game.
cd /d "%~dp0"
py capture_template.py
pause
