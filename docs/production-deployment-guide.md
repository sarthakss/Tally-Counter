# Production Deployment Guide
## TallyPrime Multi-Company Sync System

This guide covers deploying the TallyPrime sync system on a fresh Windows machine for production use with automated scheduling.

## Prerequisites

### System Requirements
- **Windows 10/11** or **Windows Server 2019/2022**
- **Minimum 4GB RAM**, 8GB recommended
- **50GB free disk space**
- **Stable internet connection**
- **Administrator privileges** for installation

### Software Requirements
- **Python 3.8 or higher** (3.11 recommended)
- **TallyPrime** (latest version)
- **Microsoft Visual C++ Redistributable** (for ODBC drivers)

## Step-by-Step Installation

### 1. Install Python

**Download and Install:**
1. Go to https://www.python.org/downloads/
2. Download **Python 3.11.x** (latest stable)
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Choose "Install for all users"
5. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

### 2. Install Git (Optional but Recommended)

1. Download from https://git-scm.com/download/win
2. Install with default settings
3. Verify: `git --version`

### 3. Download the Application

**Option A: Using Git (Recommended)**
```cmd
cd C:\
git clone https://github.com/sarthakss/Tally-Counter.git
cd Tally-Counter\python-sync
```

**Option B: Manual Download**
1. Download ZIP from GitHub repository
2. Extract to `C:\Tally-Counter\python-sync\`

### 4. Set Up Python Environment

```cmd
cd C:\Tally-Counter\python-sync

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 5. Install TallyPrime ODBC Driver

**Download ODBC Driver:**
1. Go to TallyPrime website or contact Tally support
2. Download **TallyPrime ODBC Driver** (64-bit)
3. Install with administrator privileges

**Verify Installation:**
1. Open **ODBC Data Source Administrator (64-bit)**
2. Go to **Drivers** tab
3. Look for **TallyPrime ODBC Driver**

### 6. Configure TallyPrime Companies

**For Each Company:**

1. **Open TallyPrime** with company database
2. **Gateway of Tally → F11 (Features) → Company Features → Data Configuration**
3. Set **ODBC Server = Yes**
4. Set **ODBC Port**:
   - Company 1: `9000`
   - Company 2: `9001`
5. **Save and restart TallyPrime**

**Keep TallyPrime Running:**
- TallyPrime must be running with both companies for sync to work
- Consider setting up TallyPrime as a Windows service for automatic startup

### 7. Create ODBC Data Sources

**Open ODBC Data Source Administrator (64-bit):**

**For Company 1:**
1. **System DSN** tab → **Add**
2. Select **TallyPrime ODBC Driver**
3. **Data Source Name:** `TallyODBC64_9000`
4. **Server:** `localhost`
5. **Port:** `9000`
6. **Test Connection** → Should succeed

**For Company 2:**
1. Repeat above with:
   - **Data Source Name:** `TallyODBC64_9001`
   - **Port:** `9001`

### 8. Configure Application Settings

**Create Configuration File:**
```cmd
cd C:\Tally-Counter\python-sync
copy config.json config_production.json
```

**Edit `config_production.json`:**
```json
{
  "supabase": {
    "url": "YOUR_SUPABASE_URL",
    "key": "YOUR_SERVICE_ROLE_KEY"
  },
  "tally": {
    "multi_company": true,
    "companies": [
      {
        "company_name": "Company 1 Name",
        "dsn_name": "TallyODBC64_9000",
        "timeout": 30
      },
      {
        "company_name": "Company 2 Name",
        "dsn_name": "TallyODBC64_9001",
        "timeout": 30
      }
    ]
  },
  "sync": {
    "physical_baseline_file": "physical_baseline.csv",
    "movement_days_back": 30,
    "batch_size": 50
  },
  "logging": {
    "level": "INFO",
    "file": "C:\\Logs\\tally_sync.log"
  }
}
```

**Create Physical Baseline File:**
```csv
item_code,item_name,physical_count,baseline_date,notes
BRAKE001,Brake Pad Set,50,2024-01-01,Combined count from both companies
FILTER002,Air Filter,30,2024-01-01,Total physical inventory
```

### 9. Create Logs Directory

```cmd
mkdir C:\Logs
```

### 10. Test the Installation

**Test Multi-Company Connections:**
```cmd
cd C:\Tally-Counter\python-sync
venv\Scripts\activate
python test_multi_company.py
```

**Test Full Sync:**
```cmd
python tally_sync.py
```

## Windows Task Scheduler Setup

### 1. Create Batch Script

**Create `C:\Tally-Counter\python-sync\run_production_sync.bat`:**
```batch
@echo off
cd /d "C:\Tally-Counter\python-sync"
call venv\Scripts\activate.bat
python tally_sync.py
if %ERRORLEVEL% NEQ 0 (
    echo Sync failed with error level %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
echo Sync completed successfully
```

### 2. Configure Task Scheduler

**Open Task Scheduler:**
1. **Start Menu** → **Task Scheduler**
2. **Action** → **Create Basic Task**

**Basic Task Wizard:**
1. **Name:** `TallyPrime Multi-Company Sync`
2. **Description:** `Automated sync of inventory data from TallyPrime to Supabase`
3. **Trigger:** `Daily`
4. **Start Time:** `02:00 AM` (or preferred time)
5. **Recur every:** `1 days`
6. **Action:** `Start a program`
7. **Program/script:** `C:\Tally-Counter\python-sync\run_production_sync.bat`
8. **Start in:** `C:\Tally-Counter\python-sync`

**Advanced Settings:**
1. **General** tab:
   - Check **Run whether user is logged on or not**
   - Check **Run with highest privileges**
   - **Configure for:** Windows 10/Windows Server 2019

2. **Conditions** tab:
   - Uncheck **Start the task only if the computer is on AC power**
   - Check **Wake the computer to run this task**

3. **Settings** tab:
   - Check **Allow task to be run on demand**
   - Check **Run task as soon as possible after a scheduled start is missed**
   - **If the task fails, restart every:** `15 minutes`
   - **Attempt to restart up to:** `3 times`

### 3. Test Scheduled Task

**Manual Test:**
1. Right-click task → **Run**
2. Check **History** tab for results
3. Verify log file: `C:\Logs\tally_sync.log`

## Security Configuration

### 1. Create Service Account (Recommended)

**Create Dedicated User:**
1. **Computer Management** → **Local Users and Groups** → **Users**
2. **New User:** `TallySync`
3. **Password never expires:** Yes
4. **User cannot change password:** Yes
5. Add to **Log on as a service** policy

**Configure Task to Use Service Account:**
1. Task Properties → **General** tab
2. **Change User or Group** → Select `TallySync`
3. Enter password

### 2. File Permissions

**Set Folder Permissions:**
```cmd
# Grant TallySync user full control to application folder
icacls "C:\Tally-Counter" /grant TallySync:F /T
icacls "C:\Logs" /grant TallySync:F /T
```

## Monitoring and Maintenance

### 1. Log Monitoring

**Log Locations:**
- **Application Logs:** `C:\Logs\tally_sync.log`
- **Task Scheduler Logs:** Event Viewer → Windows Logs → System
- **Python Error Logs:** Check console output in batch script

**Log Rotation:**
Create `rotate_logs.bat`:
```batch
@echo off
cd C:\Logs
if exist tally_sync.log.old del tally_sync.log.old
if exist tally_sync.log ren tally_sync.log tally_sync.log.old
```

### 2. Health Checks

**Create Health Check Script `health_check.py`:**
```python
import json
import logging
from datetime import datetime, timedelta
from tally_sync import MultiCompanyTallyODBCAPI
from supabase import create_client

def health_check():
    """Perform system health check"""
    try:
        # Load config
        with open('config_production.json', 'r') as f:
            config = json.load(f)
        
        # Test TallyPrime connections
        multi_api = MultiCompanyTallyODBCAPI(config['tally']['companies'])
        connections = multi_api.test_all_connections()
        
        # Test Supabase connection
        supabase = create_client(config['supabase']['url'], config['supabase']['key'])
        supabase.table('items').select('id').limit(1).execute()
        
        print("✅ All systems healthy")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    health_check()
```

### 3. Backup Strategy

**Backup Configuration:**
```batch
@echo off
set BACKUP_DIR=C:\Backups\TallySync\%date:~-4,4%-%date:~-10,2%-%date:~-7,2%
mkdir "%BACKUP_DIR%"
copy "C:\Tally-Counter\python-sync\config_production.json" "%BACKUP_DIR%\"
copy "C:\Tally-Counter\python-sync\physical_baseline.csv" "%BACKUP_DIR%\"
copy "C:\Logs\tally_sync.log" "%BACKUP_DIR%\"
```

## Troubleshooting

### Common Issues

**1. Python Not Found**
```cmd
# Add Python to PATH manually
set PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\
set PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts\
```

**2. ODBC Connection Failed**
- Verify TallyPrime is running
- Check ODBC DSN configuration
- Ensure correct ports (9000, 9001)
- Restart TallyPrime ODBC service

**3. Permission Denied**
- Run as Administrator
- Check file permissions
- Verify service account has correct rights

**4. Supabase Connection Failed**
- Verify internet connection
- Check Supabase URL and key
- Ensure service role key (not anon key)

**5. Task Scheduler Not Running**
- Check Task Scheduler service is running
- Verify user account has "Log on as a service" right
- Check task history for detailed errors

### Emergency Recovery

**Manual Sync:**
```cmd
cd C:\Tally-Counter\python-sync
venv\Scripts\activate
python tally_sync.py
```

**Reset Environment:**
```cmd
cd C:\Tally-Counter\python-sync
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Production Checklist

- [ ] Python 3.8+ installed with PATH
- [ ] TallyPrime ODBC driver installed
- [ ] Application downloaded and configured
- [ ] Virtual environment created and activated
- [ ] Dependencies installed via requirements.txt
- [ ] TallyPrime companies configured with ODBC
- [ ] ODBC DSNs created and tested
- [ ] Configuration file updated with production settings
- [ ] Physical baseline CSV created
- [ ] Logs directory created
- [ ] Test connections successful
- [ ] Test full sync successful
- [ ] Batch script created
- [ ] Task Scheduler configured
- [ ] Task tested manually
- [ ] Service account created (optional)
- [ ] File permissions set
- [ ] Monitoring configured
- [ ] Backup strategy implemented

## Support

For issues during deployment:
1. Check logs in `C:\Logs\tally_sync.log`
2. Run health check script
3. Verify all prerequisites are met
4. Test individual components (ODBC, Supabase, Python)
5. Contact system administrator if needed
