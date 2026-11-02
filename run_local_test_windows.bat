@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo Revenue Guard AI - local Cloud.ru test
echo ======================================
where py >nul 2>&1
if errorlevel 1 (
  where python >nul 2>&1
  if errorlevel 1 goto missing
  set "PYCMD=python"
) else (
  set "PYCMD=py -3"
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  %PYCMD% -m venv .venv
  if errorlevel 1 goto fail
)
call ".venv\Scripts\activate.bat"
python -m pip install -q -r requirements.txt
if errorlevel 1 goto fail
echo.
echo Step 1 - free mock test, no external AI calls
python local_probe.py
if errorlevel 1 goto fail
echo.
echo Local simulation passed.
echo.
choice /C 12 /N /M "1=Finish free test, 2=Run REAL potentially billable Cloud.ru request: "
if errorlevel 2 (
  python local_probe.py --real
  if errorlevel 1 goto fail
)
echo.
echo Finished. No hosting payment required.
pause
exit /b 0
:missing
echo Python 3.11+ is required: https://www.python.org/downloads/
goto fail
:fail
echo Local test did not pass. Copy error message WITHOUT secrets.
pause
exit /b 1
