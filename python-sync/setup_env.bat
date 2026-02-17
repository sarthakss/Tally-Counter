@echo off
echo Setting up TallyPrime Sync Environment...

REM Remove existing venv if it exists
if exist venv (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

REM Create new virtual environment
echo Creating new virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements with compatible versions
echo Installing requirements...
pip install -r requirements.txt

echo.
echo Setup complete! To activate the environment, run:
echo venv\Scripts\activate.bat
echo.
echo Then test with:
echo python tally_sync.py
pause
