#!/usr/bin/env python3
"""
Test script for Multi-Company TallyPrime sync functionality

This script tests the multi-company ODBC connections and data aggregation
without performing the full sync to Supabase.
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from tally_sync import MultiCompanyTallyODBCAPI

def setup_logging():
    """Setup basic logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def load_config(config_file: str = 'config.json'):
    """Load multi-company configuration"""
    try:
        with open(config_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        sys.exit(1)

def test_multi_company_connections():
    """Test connections to all configured TallyPrime companies"""
    logging.info("=== Multi-Company TallyPrime Connection Test ===")
    
    config = load_config()
    
    # Initialize multi-company API
    multi_api = MultiCompanyTallyODBCAPI(config['tally']['companies'])
    
    # Test all connections
    logging.info("Testing connections to all companies...")
    connection_results = multi_api.test_all_connections()
    
    # Report results
    all_connected = True
    for company_name, success in connection_results.items():
        if success:
            logging.info(f"✅ {company_name}: Connection successful")
        else:
            logging.error(f"❌ {company_name}: Connection failed")
            all_connected = False
    
    if not all_connected:
        logging.error("Some companies failed to connect. Please check:")
        logging.error("1. TallyPrime instances are running")
        logging.error("2. ODBC DSN configurations are correct")
        logging.error("3. Company databases are accessible")
        return False
    
    return True

def test_aggregated_stock_items():
    """Test aggregated stock items retrieval"""
    logging.info("=== Testing Aggregated Stock Items ===")
    
    config = load_config()
    multi_api = MultiCompanyTallyODBCAPI(config['tally']['companies'])
    
    try:
        # Get aggregated stock items
        aggregated_items = multi_api.get_aggregated_stock_items()
        
        logging.info(f"Retrieved {len(aggregated_items)} unique aggregated items")
        
        # Show sample data
        if aggregated_items:
            sample_item = aggregated_items[0]
            logging.info("Sample aggregated item:")
            logging.info(f"  Item Name: {sample_item['item_name']}")
            logging.info(f"  Total Balance: {sample_item['current_balance']}")
            logging.info(f"  Companies: {list(sample_item['companies'].keys())}")
            
            # Show company breakdown
            for company, data in sample_item['companies'].items():
                logging.info(f"    {company}: {data['current_balance']} units (Code: {data['item_code']})")
        
        return aggregated_items
        
    except Exception as e:
        logging.error(f"Failed to retrieve aggregated stock items: {e}")
        return []

def test_aggregated_movements():
    """Test aggregated stock movements retrieval"""
    logging.info("=== Testing Aggregated Stock Movements ===")
    
    config = load_config()
    multi_api = MultiCompanyTallyODBCAPI(config['tally']['companies'])
    
    try:
        # Get movements from last 30 days
        from_date = datetime.now() - timedelta(days=30)
        aggregated_movements = multi_api.get_aggregated_stock_movements(from_date)
        
        logging.info(f"Retrieved {len(aggregated_movements)} unique aggregated movements")
        
        # Show sample data
        if aggregated_movements:
            sample_movement = aggregated_movements[0]
            logging.info("Sample aggregated movement:")
            logging.info(f"  Item Name: {sample_movement['item_name']}")
            logging.info(f"  Total Change: {sample_movement['quantity_change']}")
            logging.info(f"  Companies: {list(sample_movement['companies'].keys())}")
            
            # Show company breakdown
            for company, data in sample_movement['companies'].items():
                logging.info(f"    {company}: {data['quantity_change']} units (Code: {data['original_item_code']})")
        
        return aggregated_movements
        
    except Exception as e:
        logging.error(f"Failed to retrieve aggregated movements: {e}")
        return []

def export_test_data():
    """Export multi-company test data to JSON file"""
    logging.info("=== Exporting Multi-Company Test Data ===")
    
    config = load_config()
    multi_api = MultiCompanyTallyODBCAPI(config['tally']['companies'])
    
    try:
        success = multi_api.export_multi_company_data('test_multi_company_export.json')
        if success:
            logging.info("✅ Test data exported successfully to test_multi_company_export.json")
        else:
            logging.error("❌ Failed to export test data")
        
        return success
        
    except Exception as e:
        logging.error(f"Error during export: {e}")
        return False

def main():
    """Run all multi-company tests"""
    setup_logging()
    
    logging.info("Starting Multi-Company TallyPrime Tests...")
    
    # Test 1: Connection testing
    if not test_multi_company_connections():
        logging.error("Connection test failed. Stopping tests.")
        return False
    
    # Test 2: Aggregated stock items
    items = test_aggregated_stock_items()
    if not items:
        logging.warning("No stock items retrieved")
    
    # Test 3: Aggregated movements
    movements = test_aggregated_movements()
    if not movements:
        logging.warning("No stock movements retrieved")
    
    # Test 4: Export test data
    export_test_data()
    
    logging.info("=== Multi-Company Tests Complete ===")
    logging.info("If all tests passed, you can now run the full sync with:")
    logging.info("python tally_sync.py")
    
    return True

if __name__ == "__main__":
    main()
