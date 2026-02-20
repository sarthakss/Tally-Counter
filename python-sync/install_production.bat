@echo off
echo ========================================
echo TallyPrime Multi-Company Sync Installer
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - Good!
) else (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo.
echo Step 1: Creating application directory...
if not exist "C:\TallySync" mkdir "C:\TallySync"
cd /d "C:\TallySync"

echo.
echo Step 2: Checking Python installation...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo Python found!
    python --version
) else (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.8+ and add to PATH
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Step 3: Creating virtual environment...
if exist venv rmdir /s /q venv
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo Step 4: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 5: Installing dependencies...
echo supabase==2.28.0 > requirements.txt
echo requests==2.31.0 >> requirements.txt
echo pandas==2.1.4 >> requirements.txt
echo schedule==1.2.0 >> requirements.txt
echo python-dotenv==1.0.0 >> requirements.txt
echo pyodbc==5.0.1 >> requirements.txt
echo websockets^>=11,^<16 >> requirements.txt
echo realtime^>=1.0.6,^<2.0.0 >> requirements.txt
echo postgrest^>=0.10.8,^<1.0.0 >> requirements.txt
echo storage3^>=0.5.4,^<1.0.0 >> requirements.txt
echo gotrue^>=1.0.4,^<2.0.0 >> requirements.txt
echo httpx^>=0.24.0,^<1.0.0 >> requirements.txt
echo python-dateutil^>=2.8.2 >> requirements.txt

pip install -r requirements.txt

echo.
echo Step 6: Creating logs directory...
if not exist "C:\Logs" mkdir "C:\Logs"

echo.
echo Step 7: Creating configuration template...
echo {> config_production.json
echo   "supabase": {>> config_production.json
echo     "url": "YOUR_SUPABASE_URL",>> config_production.json
echo     "key": "YOUR_SERVICE_ROLE_KEY">> config_production.json
echo   },>> config_production.json
echo   "tally": {>> config_production.json
echo     "multi_company": true,>> config_production.json
echo     "companies": [>> config_production.json
echo       {>> config_production.json
echo         "company_name": "Company 1 Name",>> config_production.json
echo         "dsn_name": "TallyODBC64_9000",>> config_production.json
echo         "timeout": 30>> config_production.json
echo       },>> config_production.json
echo       {>> config_production.json
echo         "company_name": "Company 2 Name",>> config_production.json
echo         "dsn_name": "TallyODBC64_9001",>> config_production.json
echo         "timeout": 30>> config_production.json
echo       }>> config_production.json
echo     ]>> config_production.json
echo   },>> config_production.json
echo   "sync": {>> config_production.json
echo     "physical_baseline_file": "physical_baseline.csv",>> config_production.json
echo     "movement_days_back": 30,>> config_production.json
echo     "batch_size": 50>> config_production.json
echo   },>> config_production.json
echo   "logging": {>> config_production.json
echo     "level": "INFO",>> config_production.json
echo     "file": "C:\\Logs\\tally_sync.log">> config_production.json
echo   }>> config_production.json
echo }>> config_production.json

echo.
echo Step 8: Creating physical baseline template...
echo item_code,item_name,physical_count,baseline_date,notes> physical_baseline.csv
echo BRAKE001,Brake Pad Set,50,2024-01-01,Combined count from both companies>> physical_baseline.csv
echo FILTER002,Air Filter,30,2024-01-01,Total physical inventory>> physical_baseline.csv

echo.
echo Step 9: Creating run script...
echo @echo off> run_production_sync.bat
echo cd /d "C:\TallySync">> run_production_sync.bat
echo call venv\Scripts\activate.bat>> run_production_sync.bat
echo python tally_sync.py>> run_production_sync.bat
echo if %%ERRORLEVEL%% NEQ 0 (>> run_production_sync.bat
echo     echo Sync failed with error level %%ERRORLEVEL%%>> run_production_sync.bat
echo     exit /b %%ERRORLEVEL%%>> run_production_sync.bat
echo )>> run_production_sync.bat
echo echo Sync completed successfully>> run_production_sync.bat

echo.
echo Step 10: Creating health check script...
echo import json> health_check.py
echo import sys>> health_check.py
echo from datetime import datetime>> health_check.py
echo try:>> health_check.py
echo     import pyodbc>> health_check.py
echo     from supabase import create_client>> health_check.py
echo     print("✅ All Python packages imported successfully")>> health_check.py
echo except ImportError as e:>> health_check.py
echo     print(f"❌ Import error: {e}")>> health_check.py
echo     sys.exit(1)>> health_check.py
echo print("✅ Health check completed")>> health_check.py

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Copy your Python sync files to C:\TallySync\
echo 2. Edit C:\TallySync\config_production.json with your settings
echo 3. Update C:\TallySync\physical_baseline.csv with your inventory
echo 4. Install TallyPrime ODBC driver
echo 5. Configure TallyPrime ODBC settings
echo 6. Create ODBC DSNs (TallyODBC64_9000, TallyODBC64_9001)
echo 7. Test with: cd C:\TallySync ^&^& venv\Scripts\activate ^&^& python health_check.py
echo 8. Set up Windows Task Scheduler
echo.
echo Installation directory: C:\TallySync\
echo Log directory: C:\Logs\
echo.
pause
