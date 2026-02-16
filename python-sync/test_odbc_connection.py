#!/usr/bin/env python3
"""
Test script to verify TallyPrime ODBC connection and data retrieval.
Run this script to test your ODBC setup before running the full sync.
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from tally_sync import TallyODBCAPI

def test_odbc_connection():
    """Test ODBC connection and basic data retrieval"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("TallyPrime ODBC Connection Test")
    print("=" * 60)
    
    # Initialize ODBC API
    tally_api = TallyODBCAPI(dsn_name="TallyPrime", timeout=30)
    
    try:
        # Test 1: Basic connection
        print("\n1. Testing ODBC connection...")
        if tally_api.test_connection():
            print("✅ ODBC connection successful!")
        else:
            print("❌ ODBC connection failed!")
            print("   Check your DSN configuration and ensure TallyPrime is running.")
            return False
        
        # Test 2: Fetch stock items
        print("\n2. Testing stock items retrieval...")
        stock_items = tally_api.get_stock_items()
        
        if stock_items:
            print(f"✅ Retrieved {len(stock_items)} stock items")
            
            # Show first few items as sample
            print("\nSample stock items:")
            for i, item in enumerate(stock_items[:3]):
                print(f"  {i+1}. {item['item_name']} - Stock: {item['current_balance']} {item['unit']}")
            
            if len(stock_items) > 3:
                print(f"  ... and {len(stock_items) - 3} more items")
        else:
            print("❌ No stock items retrieved!")
            print("   Check if your TallyPrime company has stock items.")
            return False
        
        # Test 3: Fetch stock movements
        print("\n3. Testing stock movements retrieval...")
        from_date = datetime.now() - timedelta(days=30)  # Last 30 days
        movements = tally_api.get_stock_movements(from_date)
        
        if movements:
            print(f"✅ Retrieved {len(movements)} stock movements (last 30 days)")
            
            # Show first few movements as sample
            print("\nSample stock movements:")
            for i, movement in enumerate(movements[:3]):
                print(f"  {i+1}. {movement['item_name']} - Qty: {movement['quantity_change']} on {movement['date'][:10]}")
            
            if len(movements) > 3:
                print(f"  ... and {len(movements) - 3} more movements")
        else:
            print("⚠️  No stock movements found in the last 30 days")
            print("   This might be normal if there haven't been recent transactions.")
        
        # Test 4: Export to JSON
        print("\n4. Testing JSON export...")
        export_file = "test_tally_export.json"
        if tally_api.export_to_json_file(export_file):
            print(f"✅ Data exported to {export_file}")
            
            # Show file size
            import os
            file_size = os.path.getsize(export_file)
            print(f"   File size: {file_size:,} bytes")
        else:
            print("❌ JSON export failed!")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed! Your ODBC setup is working correctly.")
        print("=" * 60)
        
        # Show summary
        print(f"\nSummary:")
        print(f"  • Stock Items: {len(stock_items)}")
        print(f"  • Recent Movements: {len(movements)}")
        print(f"  • Export File: {export_file}")
        print(f"\nYou can now run the full sync with: python tally_sync_odbc.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.error(f"ODBC test failed: {e}")
        return False
        
    finally:
        # Always close connection
        tally_api.close_connection()

def show_sample_data():
    """Show sample data structure for debugging"""
    print("\n" + "=" * 60)
    print("Sample Data Structure")
    print("=" * 60)
    
    sample_item = {
        "item_code": "BRAKE001",
        "item_name": "Brake Pads Front",
        "category": "Brakes",
        "unit": "Set",
        "current_balance": 25.0,
        "closing_value": 2500.0,
        "rate": 100.0
    }
    
    sample_movement = {
        "item_code": "BRAKE001",
        "item_name": "Brake Pads Front",
        "date": "2024-02-14T10:30:00",
        "quantity_change": -2.0,
        "billed_qty": 2.0,
        "amount": 200.0,
        "voucher_type": "Sales",
        "voucher_number": "S001"
    }
    
    print("Stock Item JSON structure:")
    print(json.dumps(sample_item, indent=2))
    
    print("\nStock Movement JSON structure:")
    print(json.dumps(sample_movement, indent=2))

if __name__ == "__main__":
    success = test_odbc_connection()
    
    if not success:
        print("\n" + "=" * 60)
        print("Troubleshooting Tips:")
        print("=" * 60)
        print("1. Ensure TallyPrime is running")
        print("2. Check ODBC is enabled in TallyPrime:")
        print("   Gateway → F12 → Data Configuration → ODBC → Allow ODBC: Yes")
        print("3. Verify DSN 'TallyPrime' is configured in ODBC Data Source Administrator")
        print("4. Check if pyodbc is installed: pip install pyodbc")
        print("5. Try running as Administrator if permission issues occur")
        
        show_sample_data()
        sys.exit(1)
    
    sys.exit(0)
