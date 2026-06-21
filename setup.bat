@echo off
REM One-time setup: installs Python dependencies for D4 FishingBuddy.
echo Installing dependencies...
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo pip failed. Make sure Python 3.10+ is installed and on PATH ^(python.org^).
  pause
  exit /b 1
)
echo.
echo Done. Next:
echo   1^) run calibrate_roi.bat   ^(aim the scan box^)
echo   2^) run capture_template.bat ^(grab the fishing icon with F7^)
echo   3^) run start.bat            ^(F8 toggles fishing, F9 quits^)
pause
