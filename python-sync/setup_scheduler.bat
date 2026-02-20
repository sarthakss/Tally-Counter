@echo off
echo ========================================
echo Windows Task Scheduler Setup
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
echo Creating scheduled task for TallyPrime Multi-Company Sync...
echo.

REM Create the scheduled task
schtasks /create /tn "TallyPrime Multi-Company Sync" /tr "C:\TallySync\run_production_sync.bat" /sc daily /st 02:00 /ru SYSTEM /rl HIGHEST /f

if %errorLevel% == 0 (
    echo ✅ Scheduled task created successfully!
    echo.
    echo Task Details:
    echo - Name: TallyPrime Multi-Company Sync
    echo - Schedule: Daily at 2:00 AM
    echo - Run as: SYSTEM account
    echo - Privileges: Highest
    echo.
    echo To modify the schedule:
    echo 1. Open Task Scheduler
    echo 2. Find "TallyPrime Multi-Company Sync"
    echo 3. Right-click ^> Properties
    echo.
    echo To test the task:
    echo 1. Right-click the task ^> Run
    echo 2. Check C:\Logs\tally_sync.log for results
) else (
    echo ❌ Failed to create scheduled task
    echo Please create manually using Task Scheduler
)

echo.
echo You can also run the sync manually anytime:
echo cd C:\TallySync
echo run_production_sync.bat
echo.
pause
