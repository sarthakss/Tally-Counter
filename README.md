# TallyPrime Clean Slate Inventory System

A "Push & Cache" architecture that provides reliable mobile inventory access by combining TallyPrime data with physical baselines.

## System Overview

- **Python Delta Engine**: Fetches TallyPrime data via ODBC, calculates clean slate stock, pushes to Supabase
- **Supabase Database**: Cloud PostgreSQL database for reliable data storage
- **React Mobile App**: Progressive Web App for offline inventory access

## Quick Start

1. **Setup Python Environment**:
   ```bash
   cd python-sync
   pip install -r requirements.txt
   ```

2. **Setup TallyPrime ODBC**:
   - Enable ODBC in TallyPrime (F12 → Data Configuration → ODBC)
   - Configure Windows ODBC DSN named "TallyPrime"

3. **Configure Supabase**:
   - Create Supabase project
   - Run SQL schema from `docs/supabase-schema.sql`
   - Update `python-sync/config.json` with your credentials

4. **Setup Mobile App**:
   ```bash
   cd mobile-app
   npm install
   npm start
   ```

5. **Schedule Python Sync**:
   - Configure Windows Task Scheduler to run `python-sync/tally_sync.py` daily

## Architecture

```
TallyPrime (ODBC) → Python Delta Engine → Supabase → React Mobile App
```

The system works even when the TallyPrime PC is powered off, as the mobile app reads cached data from Supabase.
