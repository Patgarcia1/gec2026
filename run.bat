@echo off
setlocal
cd /d "%~dp0"

rem Use the project's Python directly; activation and PATH are not required.
"venv\Scripts\python.exe" -c "import pip" >nul 2>&1
if not errorlevel 1 goto check_dependencies

echo Setting up the Python environment...
for /d %%D in ("%LocalAppData%\Python\pythoncore-*") do if exist "%%~D\python.exe" (
    "%%~D\python.exe" -m venv venv
    if not errorlevel 1 goto check_dependencies
)
py -3 -m venv venv
if not errorlevel 1 goto check_dependencies
python -m venv venv
if not errorlevel 1 goto check_dependencies
echo Could not create the environment. Install Python 3.10 or later and try again.
goto failed

:check_dependencies
"venv\Scripts\python.exe" -c "import streamlit, pandas, plotly, openpyxl" >nul 2>&1
if not errorlevel 1 goto launch
echo Installing dashboard dependencies...
"venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed

:launch
"venv\Scripts\python.exe" -m streamlit run app.py %*
if errorlevel 1 goto failed
exit /b 0

:failed
echo.
echo The dashboard could not start. Review the error above.
pause
exit /b 1
