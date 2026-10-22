@echo off
setlocal

cd /d "%~dp0"
python -m pytest -q %*
set "EXIT_CODE=%ERRORLEVEL%"

PAUSE

endlocal & exit /b %EXIT_CODE%

