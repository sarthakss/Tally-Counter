# Multi-Company TallyPrime Setup Guide

## Overview

The TallyPrime Clean Slate System now supports **multi-company mode** by default, allowing you to sync inventory data from multiple TallyPrime company databases into a single unified inventory view.

## Architecture

```
TallyPrime Company 1 → ODBC DSN 1 →
                                   ↘ Aggregated Clean Slate → Supabase → Mobile App
TallyPrime Company 2 → ODBC DSN 2 →
```

## Setup Steps

### 1. TallyPrime Configuration

**For each company:**
1. Open TallyPrime with the company database
2. Go to **Gateway of Tally → F11 (Features) → Company Features → Data Configuration**
3. Enable **ODBC Server** = Yes
4. Set **ODBC Port** (use different ports for each company):
   - Company 1: Port 9000
   - Company 2: Port 9001
5. **Save and restart TallyPrime** for each company

### 2. ODBC DSN Setup

**Create separate DSNs for each company:**

1. Open **ODBC Data Source Administrator** (64-bit)
2. Go to **System DSN** tab
3. Click **Add** → Select **TallyPrime ODBC Driver**

**For Company 1:**
- Data Source Name: `TallyODBC64_9000`
- Server: `localhost`
- Port: `9000`
- Test Connection

**For Company 2:**
- Data Source Name: `TallyODBC64_9001` 
- Server: `localhost`
- Port: `9001`
- Test Connection

### 3. Configuration File

Update `config.json`:

```json
{
  "supabase": {
    "url": "your-supabase-url",
    "key": "your-service-role-key"
  },
  "tally": {
    "multi_company": true,
    "companies": [
      {
        "company_name": "SP Test 1",
        "dsn_name": "TallyODBC64_9000",
        "timeout": 30
      },
      {
        "company_name": "SP Test 2", 
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
    "file": "sync.log"
  }
}
```

### 4. Physical Baseline CSV

Create **one** `physical_baseline.csv` file for all companies:

```csv
item_code,item_name,physical_count,baseline_date,notes
BRAKE001,Brake Pad Set,50,2024-01-01,Combined count across all locations
FILTER002,Air Filter,30,2024-01-01,Total physical inventory
```

**Important:** The physical count should be the **total across all companies**.

### 5. Database Schema

**No schema changes required!** The existing Supabase schema works with multi-company data:

- `items` table: Stores aggregated item master data
- `stock_levels` table: Stores combined clean slate calculations
- `sync_logs` table: Tracks sync operations

## Testing

### Test Multi-Company Connections

```bash
python test_multi_company.py
```

This will:
- Test connections to all companies
- Show aggregated stock items
- Display combined movements
- Export test data

### Run Full Sync

```bash
python tally_sync.py
```

## Data Flow

### Stock Items Aggregation

**Company 1:** BRAKE001 = 25 units
**Company 2:** BRAKE001 = 20 units
**Result:** BRAKE001 = 45 units (combined)

### Clean Slate Calculation

```
Physical Baseline: 50 units (from CSV)
Company 1 Delta: -5 units (closing - opening)
Company 2 Delta: +2 units (closing - opening)
Combined Delta: -3 units
Clean Slate Stock: 50 + (-3) = 47 units
```

### Mobile App Display

The mobile app will show:
- **Current Stock:** 47 units (clean slate total)
- **Source:** Combined from all companies

## Single Company Mode

To use single company mode, update `config.json`:

```json
{
  "tally": {
    "multi_company": false,
    "odbc_dsn": "TallyODBC64_9000",
    "connection_timeout": 30
  }
}
```

## Troubleshooting

### Connection Issues

1. **Check TallyPrime is running** for both companies
2. **Verify ODBC DSNs** are configured correctly
3. **Test individual connections** using ODBC Data Source Administrator
4. **Check firewall** isn't blocking ODBC ports

### Data Issues

1. **Verify item codes match** across companies
2. **Check physical baseline CSV** has correct totals
3. **Review sync logs** for detailed error messages
4. **Use test script** to debug aggregation

### Common Errors

**"DSN not found"**
- Recreate ODBC DSN with correct name
- Ensure 64-bit ODBC driver is used

**"Connection timeout"**
- Increase timeout in config
- Check TallyPrime ODBC server is enabled

**"No stock items found"**
- Verify companies have inventory data
- Check TallyPrime ODBC permissions

## Benefits

✅ **Unified Inventory View** - Single stock count across all locations
✅ **Company Traceability** - Track which company contributed what
✅ **Simplified Management** - One physical baseline for all companies
✅ **Scalable Architecture** - Easy to add more companies
✅ **Backward Compatible** - Works with existing single company setups

## Advanced Configuration

### Adding More Companies

Simply add to the `companies` array in `config.json`:

```json
{
  "company_name": "SP Test 3",
  "dsn_name": "TallyODBC64_9002", 
  "timeout": 30
}
```

### Company-Specific Timeouts

```json
{
  "company_name": "Remote Company",
  "dsn_name": "TallyODBC64_Remote",
  "timeout": 60
}
```

### Debugging Mode

Set logging level to DEBUG for detailed information:

```json
{
  "logging": {
    "level": "DEBUG",
    "file": "sync.log"
  }
}
```
