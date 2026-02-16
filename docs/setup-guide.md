# TallyPrime Clean Slate System - Setup Guide

## Prerequisites

- **TallyPrime** installed and running on Windows PC
- **Python 3.8+** installed
- **Node.js 16+** and npm installed
- **Supabase account** (free tier available)

## Step 1: Supabase Database Setup

1. **Create Supabase Project**:
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Note your project URL and anon key

2. **Run Database Schema**:
   - Go to Supabase SQL Editor
   - Copy and paste contents of `docs/supabase-schema.sql`
   - Execute the script

3. **Configure Row Level Security**:
   - The schema automatically sets up RLS policies
   - Verify policies are active in Authentication > Policies

## Step 2: TallyPrime ODBC Setup

1. **Enable ODBC in TallyPrime**:
   - Open TallyPrime
   - Go to Gateway of Tally → F12 (Configure)
   - Navigate to Data Configuration → ODBC
   - Set "Allow ODBC" to Yes
   - Create a Data Source Name (DSN): "TallyPrime"
   - Note the connection details

2. **Configure Windows ODBC Data Source**:
   - Open "ODBC Data Source Administrator" (64-bit)
   - Go to "System DSN" tab
   - Click "Add" and select "TallyPrime ODBC Driver"
   - Set DSN Name: "TallyPrime"
   - Configure connection to your TallyPrime installation

## Step 3: Python Sync Engine Setup

1. **Navigate to Python Directory**:
   ```bash
   cd python-sync
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Settings**:
   - Copy `config.json` and update:
     - `supabase.url`: Your Supabase project URL
     - `supabase.key`: Your Supabase service role key (not anon key)
     - `tally.odbc_dsn`: "TallyPrime" (or your DSN name)
     - `tally.company_name`: Your TallyPrime company name

4. **Update Physical Baseline**:
   - Edit `physical_baseline.csv` with your actual stock counts
   - Use format: `item_code,item_name,physical_count,baseline_date,notes`

5. **Test Connection**:
   ```bash
   python test_odbc_connection.py
   python tally_sync.py
   ```

## Step 4: Mobile App Setup

1. **Navigate to Mobile App Directory**:
   ```bash
   cd mobile-app
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Configure Environment**:
   - Copy `.env.example` to `.env`
   - Update with your Supabase credentials:
     ```
     REACT_APP_SUPABASE_URL=your_supabase_project_url
     REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
     ```

4. **Start Development Server**:
   ```bash
   npm start
   ```

5. **Build for Production**:
   ```bash
   npm run build
   ```

## Step 5: Deployment

### Python Script Scheduling

1. **Windows Task Scheduler**:
   - Open Task Scheduler
   - Create Basic Task
   - Set trigger: Daily at desired time
   - Action: Start program
   - Program: `python`
   - Arguments: `C:\path\to\tally_sync.py`
   - Start in: `C:\path\to\python-sync\`

### Mobile App Deployment

1. **Deploy to Netlify/Vercel**:
   ```bash
   # Build the app
   npm run build
   
   # Deploy build folder to your preferred hosting service
   ```

2. **Configure Environment Variables**:
   - Add Supabase credentials to hosting platform
   - Ensure PWA manifest is properly served

## Step 6: TallyPrime Configuration

1. **Enable ODBC (Already done in Step 2)**:
   - ODBC should already be configured from Step 2
   - Verify DSN "TallyPrime" is working

2. **Verify ODBC Access**:
   - Test connection using ODBC Data Source Administrator
   - Should connect successfully to TallyPrime database

## Verification Checklist

- [ ] Supabase database tables created successfully
- [ ] TallyPrime ODBC DSN "TallyPrime" configured and working
- [ ] Python script connects to TallyPrime via ODBC
- [ ] Python script connects to Supabase
- [ ] Physical baseline CSV is populated with real data
- [ ] Mobile app displays inventory items
- [ ] Sync timestamp updates after running Python script
- [ ] Mobile app works offline (test by disconnecting internet)
- [ ] Python script scheduled to run automatically

## Troubleshooting

### TallyPrime Connection Issues
- Ensure TallyPrime is running
- Check if ODBC is enabled (F12 > Configure > Data Configuration > ODBC)
- Verify DSN "TallyPrime" is configured correctly
- Test connection using ODBC Data Source Administrator
- Check Windows ODBC drivers are installed

### Supabase Connection Issues
- Verify URL and keys are correct
- Check RLS policies are properly configured
- Ensure service role key is used for Python script
- Use anon key for mobile app

### Mobile App Issues
- Clear browser cache and reload
- Check browser console for errors
- Verify environment variables are set
- Test with different devices/browsers

### Python Script Issues
- Check log file: `sync.log`
- Verify all dependencies are installed
- Test individual components (TallyPrime, Supabase) separately
- Check physical baseline CSV format

## Security Notes

- **Never commit** `.env` files or config files with real credentials
- Use **service role key** for Python script (server-side)
- Use **anon key** for mobile app (client-side)
- Keep TallyPrime PC on local network only
- Consider VPN for remote access to mobile app

## Performance Tips

- Run Python sync during off-hours (e.g., 2 AM)
- Monitor Supabase usage to stay within free tier limits
- Use batch operations for large inventories
- Cache mobile app data for offline use
- Optimize physical baseline frequency based on business needs
