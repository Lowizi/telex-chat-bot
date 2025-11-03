@echo off
REM Activate virtual environment and clear any conflicting Django environment variables
REM This prevents conflicts with other Django projects

REM Clear the DJANGO_SETTINGS_MODULE if it exists
set DJANGO_SETTINGS_MODULE=

REM Activate the virtual environment
call .\venv\Scripts\activate.bat

echo Virtual environment activated and Django settings cleared!
echo You can now run Django commands safely.
