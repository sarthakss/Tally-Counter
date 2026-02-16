# TallyPrime Clean Slate System - User Manual

## Overview

The TallyPrime Clean Slate Inventory System provides accurate, real-time inventory data for your auto parts business by combining physical stock counts with TallyPrime transaction data.

## System Components

### 1. Python Sync Engine
- Runs on your TallyPrime PC
- Connects to TallyPrime via ODBC interface
- Fetches stock items and transaction data as JSON
- Calculates clean slate stock levels using physical baselines
- Syncs data to Supabase cloud database every 24 hours

### 2. Mobile Inventory App
- Progressive Web App (PWA)
- Works offline when TallyPrime PC is off
- Real-time search and filtering
- Shows last sync timestamp

### 3. Supabase Cloud Database
- Stores clean slate inventory data
- Provides reliable access for mobile devices
- Maintains sync history and logs

## How It Works

### Clean Slate Logic
```
Current Stock = Physical Baseline + Tally Delta
```

- **Physical Baseline**: Manual stock count from physical verification
- **Tally Delta**: Net transactions in TallyPrime since baseline date
- **Current Stock**: Calculated truth combining both sources

### Data Flow
1. Physical stock count entered in `physical_baseline.csv` file
2. Python script connects to TallyPrime via ODBC
3. Fetches stock items and movements as JSON data
4. Calculates clean slate stock = Physical Baseline + Tally Delta
5. Data synced to Supabase cloud database
6. Mobile app displays current inventory from Supabase

## Technical Architecture

### ODBC Connection
The system uses TallyPrime's ODBC interface to extract data:
- **Connection**: Direct database connection via ODBC DSN
- **Data Format**: JSON for all data handling (no XML parsing)
- **Tables Accessed**: STOCKITEM, VOUCHER, VOUCHERITEM
- **Query Types**: Stock balances, stock movements, transaction history

### Data Processing
1. **Stock Items Query**: Fetches current balances, rates, and item details
2. **Stock Movements Query**: Gets transaction history since baseline date
3. **Clean Slate Calculation**: Combines physical counts with transaction deltas
4. **JSON Export**: All data handled as structured JSON for reliability

### Sync Process
- **Initial Sync**: `python tally_sync.py` (one-time setup)
- **Scheduled Sync**: `python schedule_sync.py` (daily automation)
- **Test Connection**: `python test_odbc_connection.py` (troubleshooting)

## Using the Mobile App

### Accessing the App
- Open web browser on mobile device
- Navigate to your deployed app URL
- Install as PWA for offline access

### Main Features

#### **Inventory List**
- View all items with current stock levels
- Color-coded stock status:
  - 🟢 Green: Good stock (>5 units)
  - 🟡 Yellow: Low stock (1-5 units)
  - 🔴 Red: Out of stock (0 units)

#### **Search & Filter**
- Search by item name or code
- Filter by category
- Real-time results as you type

#### **Stock Information**
For each item, you can see:
- Current stock level
- Physical baseline count
- Tally delta (transactions since baseline)
- Last sync timestamp
- Item category and unit

#### **Sync Status**
- Last sync timestamp displayed at top
- Refresh button to check for updates
- Offline indicator when no internet

### Offline Usage
- App works without internet connection
- Shows last synced data
- Install as PWA for app-like experience
- Data updates when connection restored

## Managing Physical Baselines

### When to Update Baselines
- Monthly physical stock verification
- After major stock movements
- When discrepancies are found
- Before busy seasons

### Updating Process
1. Conduct physical stock count
2. Update `physical_baseline.csv` file
3. Set new baseline date
4. Run sync to update system

### CSV Format
```csv
item_code,item_name,physical_count,baseline_date,notes
BRAKE001,Brake Pads Front,25,2024-01-01,Physical count verified
OIL001,Engine Oil 5W30,42,2024-01-01,Physical count verified
```

## Monitoring & Maintenance

### Daily Operations
- Check mobile app for current stock levels
- Monitor low stock alerts
- Use search to find specific items quickly

### Weekly Tasks
- Review sync logs for errors
- Check last sync timestamp
- Verify critical item stock levels

### Monthly Tasks
- Update physical baselines
- Review stock movement patterns
- Clean up old sync logs

### Troubleshooting

#### **Mobile App Issues**

**App won't load:**
- Check internet connection
- Clear browser cache
- Try different browser
- Check if app URL is correct

**Data not updating:**
- Check last sync timestamp
- Verify TallyPrime PC is running
- Check Python sync logs
- Refresh app manually

**Search not working:**
- Clear search field and try again
- Check spelling of item names/codes
- Try different search terms

#### **Sync Issues**

**Python script errors:**
- Check `sync.log` file for details
- Verify TallyPrime is running
- Test internet connection
- Check Supabase credentials

**TallyPrime ODBC connection failed:**
- Ensure TallyPrime is running
- Check ODBC is enabled in TallyPrime (Gateway → F12 → Data Configuration → ODBC → Allow ODBC: Yes)
- Verify 'TallyPrime' DSN is configured in ODBC Data Source Administrator
- Check if pyodbc Python package is installed
- Try running Python script as Administrator

**Supabase connection failed:**
- Verify credentials in config.json
- Check internet connection
- Test Supabase dashboard access
- Review API usage limits

## Best Practices

### Stock Management
- Update physical baselines regularly
- Monitor low stock items daily
- Use categories for better organization
- Keep item codes consistent

### System Maintenance
- Run sync during off-hours (12:00 PM as currently configured)
- Monitor sync logs weekly (`sync.log` and `scheduler.log`)
- Keep TallyPrime PC powered during sync times
- Backup configuration files (`config.json`, `physical_baseline.csv`)
- Test ODBC connection periodically with `test_odbc_connection.py`

### Mobile Usage
- Install app as PWA for better performance
- Use search for quick item lookup
- Check sync timestamp before making decisions
- Report discrepancies immediately

### Security
- Don't share Supabase credentials
- Keep TallyPrime PC on local network
- Use strong passwords for all accounts
- Regular backup of important data

## Understanding Stock Levels

### Stock Status Colors
- **Green (>5 units)**: Good stock level
- **Yellow (1-5 units)**: Low stock, consider reordering
- **Red (0 units)**: Out of stock, immediate action needed

### Delta Interpretation
- **Positive Delta**: More items sold/used than received
- **Negative Delta**: More items received than sold/used
- **Zero Delta**: No net change since baseline

### Sync Frequency
- **Real-time**: Mobile app shows last synced data
- **Daily**: Python script runs automatically
- **Manual**: Can trigger sync manually if needed

## Support & Maintenance

### Log Files
- `sync.log`: Python sync operations
- `scheduler.log`: Scheduled task operations
- Browser console: Mobile app errors

### Configuration Files
- `config.json`: Python script settings (Supabase credentials, ODBC DSN, sync parameters)
- `.env`: Mobile app environment variables
- `physical_baseline.csv`: Stock baseline data with physical counts
- `requirements.txt`: Python dependencies (pyodbc, supabase, pandas, etc.)

### Backup Strategy
- Export Supabase data monthly
- Backup configuration files
- Keep physical baseline history
- Document any customizations

## FAQ

**Q: How often should I update physical baselines?**
A: Monthly is recommended, or whenever you notice significant discrepancies.

**Q: What happens if TallyPrime PC is off?**
A: Mobile app continues to work with last synced data. Sync resumes when PC is back online.

**Q: Can multiple people use the mobile app?**
A: Yes, the app supports multiple concurrent users viewing the same inventory data.

**Q: How do I add new items?**
A: Add items in TallyPrime first. They will appear in the next sync automatically. Update physical baseline CSV with initial count for accurate clean slate calculation.

**Q: What if ODBC connection fails?**
A: Check TallyPrime ODBC settings, verify DSN configuration, ensure TallyPrime is running, and try running the test script as Administrator.

**Q: How does the JSON system work?**
A: The system fetches data from TallyPrime via ODBC, converts it to JSON format for processing, calculates clean slate stock levels, and syncs to Supabase. No XML parsing is involved.

**Q: What if I find stock discrepancies?**
A: Update the physical baseline for affected items and investigate the cause.

**Q: Is my data secure?**
A: Yes, data is encrypted in transit and at rest. Follow security best practices for credentials.
