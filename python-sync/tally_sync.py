#!/usr/bin/env python3
"""
TallyPrime Clean Slate Inventory Sync Engine - ODBC/JSON Version

This script fetches inventory data from TallyPrime via ODBC, calculates clean slate stock
levels using physical baselines and Tally deltas, then pushes the truth to Supabase.
Uses JSON for all data handling - much simpler than XML parsing.
"""

import json
import logging
import csv
import sys
import pyodbc
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from supabase import create_client, Client


class TallyODBCAPI:
    """ODBC-based interface for TallyPrime data extraction"""
    
    def __init__(self, dsn_name: str = "TallyODBC64_9000", timeout: int = 30, company_name: str = "Default"):
        self.dsn_name = dsn_name
        self.timeout = timeout
        self.company_name = company_name
        self.connection = None
    
    def test_connection(self) -> bool:
        """Test if TallyPrime ODBC connection is available"""
        try:
            conn_string = f"DSN={self.dsn_name};Timeout={self.timeout};"
            test_conn = pyodbc.connect(conn_string)
            test_conn.close()
            return True
        except pyodbc.Error as e:
            logging.error(f"ODBC connection test failed: {e}")
            return False
    
    def _get_connection(self):
        """Get or create ODBC connection"""
        if not self.connection:
            try:
                conn_string = f"DSN={self.dsn_name};Timeout={self.timeout};"
                self.connection = pyodbc.connect(conn_string)
                logging.info("Successfully connected to TallyPrime via ODBC")
            except pyodbc.Error as e:
                logging.error(f"Failed to connect to TallyPrime via ODBC: {e}")
                raise
        return self.connection
    
    def close_connection(self):
        """Close ODBC connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_stock_items(self) -> List[Dict]:
        """
        Fetch all stock items from TallyPrime and return as JSON-compatible list
        
        Returns:
            List of dictionaries containing stock item data
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Query to get stock items with current balances
            # Note: Column names may vary by TallyPrime version - adjust as needed
            query = """
                        SELECT 
                            $Name AS STOCKITEMNAME, 
                            $Parent AS PARENT, 
                            $BaseUnits AS BASEUNITS, 
                            $ClosingBalance AS CLOSINGBALANCE, 
                            $ClosingValue AS CLOSINGVALUE, 
                            $ClosingRate AS CLOSINGRATE
                        FROM STOCKITEM
                        """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            logging.info(f"Fetched {len(rows)} stock items from TallyPrime")
            # Convert to JSON-compatible format
            items = []
            for row in rows:
                # Handle potential None values and convert to appropriate types
                item_code = (row[0] or '').strip()
                if not item_code:  # Skip empty item codes
                    continue
                    
                item = {
                    'item_code': item_code,
                    'item_name': item_code,  # Using item code as name for consistency
                    'category': (row[1] or 'General').strip(),
                    'unit': (row[2] or 'Nos').strip(),
                    'current_balance': float(row[3] or 0),
                    'closing_value': float(row[4] or 0),
                    'rate': float(row[5] or 0)
                }
                items.append(item)
            
            cursor.close()
            logging.info(f"Retrieved {len(items)} stock items via ODBC")
            return items
            
        except pyodbc.Error as e:
            logging.error(f"Error fetching stock items from TallyPrime: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error fetching stock items: {e}")
            return []
    
    def get_stock_movements(self, from_date: datetime) -> List[Dict]:
        """
        Fetch stock movements using STOCKITEM balance differences
        
        Calculates net stock changes by comparing opening and closing balances.
        This approach works reliably with TallyPrime ODBC without complex joins.
        
        Args:
            from_date: Start date for movement query (not used in this approach)
            
        Returns:
            List of dictionaries containing stock movement data
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Query STOCKITEM for opening and closing balances
            query = """
            SELECT 
                $Name AS STOCKITEMNAME,
                $ClosingBalance AS CLOSINGBALANCE,
                $OpeningBalance AS OPENINGBALANCE
            FROM 
                STOCKITEM
            WHERE 
                $Name IS NOT NULL
            ORDER BY 
                $Name
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            logging.info(f"Retrieved {len(rows)} stock items for balance difference calculation")
            
            # Process balance differences into movement records
            movements = []
            for row in rows:
                item_code = (row[0] or '').strip()
                if not item_code:
                    continue
                    
                closing_balance = float(row[1] or 0)
                opening_balance = float(row[2] or 0)
                net_change = closing_balance - opening_balance
                
                if net_change != 0:  # Only include items with changes
                    movement = {
                        'item_code': item_code,
                        'item_name': item_code,
                        'date': datetime.now().isoformat(),
                        'quantity_change': net_change,
                        'billed_qty': abs(net_change),
                        'amount': 0,
                        'voucher_type': 'Balance Change',
                        'voucher_number': ''
                    }
                    movements.append(movement)
            
            cursor.close()
            logging.info(f"Calculated {len(movements)} stock movements from balance differences")
            return movements
            
        except pyodbc.Error as e:
            logging.error(f"Error fetching stock movements from TallyPrime: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error fetching stock movements: {e}")
            return []
    
    def export_to_json_file(self, filename: str = 'tally_export.json') -> bool:
        """
        Export all TallyPrime data to a JSON file for inspection/debugging
        
        Args:
            filename: Output JSON filename
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            # Get stock items
            stock_items = self.get_stock_items()
            
            # Get recent movements (last 365 days by default)
            from_date = datetime.now() - timedelta(days=365)
            movements = self.get_stock_movements(from_date)
            
            # Create comprehensive JSON structure
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'export_info': {
                    'dsn_name': self.dsn_name,
                    'export_date': datetime.now().strftime('%Y-%m-%d'),
                    'total_items': len(stock_items),
                    'total_movements': len(movements),
                    'movements_from_date': from_date.strftime('%Y-%m-%d')
                },
                'stock_items': stock_items,
                'stock_movements': movements
            }
            
            # Write to JSON file with proper formatting
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"TallyPrime data exported to {filename}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting TallyPrime data to JSON: {e}")
            return False


class MultiCompanyTallyODBCAPI:
    """Multi-company ODBC interface for aggregating data from multiple TallyPrime instances"""
    
    def __init__(self, companies_config: List[Dict]):
        """
        Initialize multi-company API
        
        Args:
            companies_config: List of company configurations with dsn_name, timeout, and company_name
        """
        self.companies = []
        for config in companies_config:
            company_api = TallyODBCAPI(
                dsn_name=config['dsn_name'],
                timeout=config.get('timeout', 30),
                company_name=config['company_name']
            )
            self.companies.append(company_api)
        
        logging.info(f"Initialized multi-company API for {len(self.companies)} companies")
    
    def test_all_connections(self) -> Dict[str, bool]:
        """Test connections to all companies"""
        results = {}
        for company_api in self.companies:
            try:
                result = company_api.test_connection()
                results[company_api.company_name] = result
                if result:
                    logging.info(f" {company_api.company_name} connection successful")
                else:
                    logging.error(f" {company_api.company_name} connection failed")
            except Exception as e:
                logging.error(f" {company_api.company_name} connection error: {e}")
                results[company_api.company_name] = False
        
        return results
    
    def get_aggregated_stock_items(self) -> List[Dict]:
        """
        Get stock items from all companies and aggregate by item_code
        
        Returns:
            List of dictionaries with combined stock data
        """
        all_items = {}
        
        for company_api in self.companies:
            try:
                logging.info(f"Fetching stock items from {company_api.company_name}...")
                company_items = company_api.get_stock_items()
                
                for item in company_items:
                    item_name = item['item_name']
                    
                    if item_name not in all_items:
                        # First time seeing this item - initialize with company data
                        all_items[item_name] = {
                            'item_code': item_name,  # Use item_name as the unified identifier
                            'item_name': item_name,
                            'category': item['category'],
                            'unit': item['unit'],
                            'current_balance': item['current_balance'],
                            'closing_value': item['closing_value'],
                            'rate': item['rate'],
                            'companies': {
                                company_api.company_name: {
                                    'item_code': item['item_code'],  # Store original company-specific code
                                    'current_balance': item['current_balance'],
                                    'closing_value': item['closing_value'],
                                    'rate': item['rate']
                                }
                            }
                        }
                    else:
                        # Item exists - aggregate the balances
                        all_items[item_name]['current_balance'] += item['current_balance']
                        all_items[item_name]['closing_value'] += item['closing_value']
                        # Use weighted average for rate
                        existing_qty = sum(comp['current_balance'] for comp in all_items[item_name]['companies'].values())
                        if existing_qty + item['current_balance'] > 0:
                            total_value = all_items[item_name]['closing_value'] + item['closing_value']
                            total_qty = existing_qty + item['current_balance']
                            all_items[item_name]['rate'] = total_value / total_qty if total_qty > 0 else 0
                        
                        # Track company-specific data
                        all_items[item_name]['companies'][company_api.company_name] = {
                            'item_code': item['item_code'],  # Store original company-specific code
                            'current_balance': item['current_balance'],
                            'closing_value': item['closing_value'],
                            'rate': item['rate']
                        }
                
                logging.info(f"Retrieved {len(company_items)} items from {company_api.company_name}")
                
            except Exception as e:
                logging.error(f"Failed to fetch stock items from {company_api.company_name}: {e}")
                continue
        
        # Convert to list format
        aggregated_items = list(all_items.values())
        logging.info(f"Aggregated {len(aggregated_items)} unique items from all companies")
        
        return aggregated_items
    
    def get_aggregated_stock_movements(self, from_date: datetime) -> List[Dict]:
        """
        Get stock movements from all companies and combine them
        
        Args:
            from_date: Start date for movement query
            
        Returns:
            List of combined movement dictionaries
        """
        all_movements = []
        
        for company_api in self.companies:
            try:
                logging.info(f"Fetching stock movements from {company_api.company_name}...")
                company_movements = company_api.get_stock_movements(from_date)
                
                # Add company identifier to each movement
                for movement in company_movements:
                    movement['company'] = company_api.company_name
                    all_movements.append(movement)
                
                logging.info(f"Retrieved {len(company_movements)} movements from {company_api.company_name}")
                
            except Exception as e:
                logging.error(f"Failed to fetch stock movements from {company_api.company_name}: {e}")
                continue
        
        # Aggregate movements by item_name
        aggregated_movements = {}
        for movement in all_movements:
            item_name = movement['item_name']
            
            if item_name not in aggregated_movements:
                # First movement for this item
                aggregated_movements[item_name] = {
                    'item_code': item_name,  # Use item_name as unified identifier
                    'item_name': item_name,
                    'date': movement['date'],
                    'quantity_change': movement['quantity_change'],
                    'billed_qty': movement['billed_qty'],
                    'amount': movement['amount'],
                    'voucher_type': 'Multi-Company Balance Change',
                    'voucher_number': '',
                    'companies': {
                        movement['company']: {
                            'original_item_code': movement['item_code'],  # Store original company-specific code
                            'quantity_change': movement['quantity_change'],
                            'amount': movement['amount']
                        }
                    }
                }
            else:
                # Aggregate with existing movement
                aggregated_movements[item_name]['quantity_change'] += movement['quantity_change']
                aggregated_movements[item_name]['billed_qty'] += movement['billed_qty']
                aggregated_movements[item_name]['amount'] += movement['amount']
                
                # Track company-specific changes
                aggregated_movements[item_name]['companies'][movement['company']] = {
                    'original_item_code': movement['item_code'],  # Store original company-specific code
                    'quantity_change': movement['quantity_change'],
                    'amount': movement['amount']
                }
        
        result = list(aggregated_movements.values())
        logging.info(f"Aggregated {len(result)} unique item movements from all companies")
        
        return result
    
    def close_all_connections(self):
        """Close all company connections"""
        for company_api in self.companies:
            try:
                company_api.close_connection()
                logging.info(f"Closed connection for {company_api.company_name}")
            except Exception as e:
                logging.warning(f"Error closing connection for {company_api.company_name}: {e}")
    
    def export_multi_company_data(self, filename: str = 'multi_company_tally_export.json') -> bool:
        """Export aggregated data from all companies to JSON file"""
        try:
            from_date = datetime.now() - timedelta(days=30)
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'companies': [api.company_name for api in self.companies],
                'aggregated_stock_items': self.get_aggregated_stock_items(),
                'aggregated_stock_movements': self.get_aggregated_stock_movements(from_date)
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            logging.info(f"Multi-company data exported to {filename}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to export multi-company data: {e}")
            return False


class CleanSlateEngine:
    """Calculates clean slate stock levels using JSON data"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.physical_baseline = self._load_physical_baseline()
    
    def _load_physical_baseline(self) -> Dict[str, Dict]:
        """Load physical baseline data from CSV"""
        baseline_file = self.config['sync']['physical_baseline_file']
        baseline_data = {}
        
        try:
            with open(baseline_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    item_name = row['item_name'].strip()
                    if item_name:
                        baseline_data[item_name] = {
                            'item_code': row.get('item_code', '').strip(),  # Keep original item_code for reference
                            'physical_count': float(row['physical_count']),
                            'baseline_date': datetime.strptime(row['baseline_date'], '%Y-%m-%d'),
                            'notes': row.get('notes', '').strip()
                        }
            
            logging.info(f"Loaded {len(baseline_data)} physical baseline records")
            
        except FileNotFoundError:
            logging.warning(f"Physical baseline file not found: {baseline_file}")
        except Exception as e:
            logging.error(f"Error loading physical baseline: {e}")
        
        return baseline_data
    
    def calculate_clean_slate_stock(self, tally_items: List[Dict], tally_movements: List[Dict]) -> List[Dict]:
        """
        Calculate clean slate stock levels using JSON data
        
        Args:
            tally_items: List of stock items from TallyPrime
            tally_movements: List of stock movements from TallyPrime
            
        Returns:
            List of dictionaries with clean slate calculations
        """
        clean_slate_items = []
        
        for tally_item in tally_items:
            item_name = tally_item['item_name']
            
            # Get physical baseline for this item (now using item_name)
            baseline = self.physical_baseline.get(item_name, {})
            physical_count = baseline.get('physical_count', 0)
            baseline_date = baseline.get('baseline_date', datetime.now() - timedelta(days=365))
            
            # Calculate Tally delta since baseline
            tally_delta = self._calculate_tally_delta(item_name, baseline_date, tally_movements)
            
            # Clean Slate = Physical Baseline + Tally Delta
            clean_slate_stock = physical_count + tally_delta
            
            clean_slate_item = {
                'item_code': item_name,  # Use item_name as unified identifier
                'item_name': item_name,
                'category': tally_item.get('category', 'General'),
                'unit': tally_item.get('unit', 'Nos'),
                'current_stock': clean_slate_stock,
                'physical_baseline': physical_count,
                'tally_delta': tally_delta,
                'tally_balance': tally_item.get('current_balance', 0),  # For comparison
                'last_sync': datetime.now(),
                'sync_source': 'tally_odbc_sync'
            }
            
            clean_slate_items.append(clean_slate_item)
        
        logging.info(f"Calculated clean slate for {len(clean_slate_items)} items")
        return clean_slate_items
    
    def _calculate_tally_delta(self, item_name: str, baseline_date: datetime, movements: List[Dict]) -> float:
        """
        Calculate net stock movement from Tally since baseline date
        
        Args:
            item_name: Item name to calculate delta for
            baseline_date: Date from which to calculate movements
            movements: List of stock movements
            
        Returns:
            Net quantity change since baseline date
        """
        delta = 0.0
        
        for movement in movements:
            if movement.get('item_name') == item_name:
                try:
                    movement_date = datetime.fromisoformat(movement.get('date', ''))
                    if movement_date >= baseline_date:
                        quantity_change = movement.get('quantity_change', 0)
                        delta += quantity_change
                except (ValueError, TypeError):
                    # Skip movements with invalid dates
                    continue
        
        return delta


class SupabaseSync:
    """Handles Supabase database operations for JSON data"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.client: Client = create_client(
            config['supabase']['url'],
            config['supabase']['key']
        )
    
    def test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            result = self.client.table('items').select('id').limit(1).execute()
            return True
        except Exception as e:
            logging.error(f"Supabase connection failed: {e}")
            return False
    
    def sync_items(self, items: List[Dict]) -> bool:
        """
        Sync clean slate items to Supabase
        
        Args:
            items: List of clean slate item dictionaries
            
        Returns:
            True if sync successful, False otherwise
        """
        try:
            batch_size = self.config['sync']['batch_size']
            synced_count = 0
            
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                
                for item in batch:
                    # Upsert the item master record
                    item_data = {
                        'item_code': item['item_code'],
                        'item_name': item['item_name'],
                        'category': item['category'],
                        'unit': item['unit'],
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    result = self.client.table('items').upsert(
                        item_data,
                        on_conflict='item_code'
                    ).execute()
                    
                    if result.data:
                        item_id = result.data[0]['id']
                        
                        # Upsert the stock level
                        stock_data = {
                            'item_id': item_id,
                            'current_stock': item['current_stock'],
                            'physical_baseline': item['physical_baseline'],
                            'tally_delta': item['tally_delta'],
                            'last_sync': item['last_sync'].isoformat(),
                            'sync_source': item['sync_source']
                        }
                        
                        self.client.table('stock_levels').upsert(
                            stock_data,
                            on_conflict='item_id'
                        ).execute()
                        
                        synced_count += 1
                
                logging.info(f"Synced batch {i//batch_size + 1}: {len(batch)} items")
            
            logging.info(f"Successfully synced {synced_count} items to Supabase")
            return True
            
        except Exception as e:
            logging.error(f"Failed to sync items to Supabase: {e}")
            return False
    
    def log_sync_status(self, items_processed: int, status: str, error_message: str = None):
        """Log sync operation status"""
        try:
            log_data = {
                'sync_timestamp': datetime.now().isoformat(),
                'items_processed': items_processed,
                'status': status,
                'error_message': error_message
            }
            
            self.client.table('sync_logs').insert(log_data).execute()
            
        except Exception as e:
            logging.error(f"Failed to log sync status: {e}")


class TallySyncManager:
    """Main sync manager orchestrating the ODBC/JSON-based sync process"""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config = self._load_config(config_file)
        self._setup_logging()
        
        # Check if multi-company mode is enabled
        if self.config['tally'].get('multi_company', True):
            self.tally_api = MultiCompanyTallyODBCAPI(self.config['tally']['companies'])
            self.multi_company_mode = True
            logging.info("Initialized in multi-company mode")
        else:
            self.tally_api = TallyODBCAPI(
                self.config['tally']['odbc_dsn'],
                self.config['tally']['connection_timeout']
            )
            self.multi_company_mode = False
            logging.info("Initialized in single-company mode")
        
        self.clean_slate_engine = CleanSlateEngine(self.config)
        self.supabase_sync = SupabaseSync(self.config)
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {config_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config['logging']['level'].upper())
        log_file = self.config['logging']['file']
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def run_sync(self) -> bool:
        """Execute the complete ODBC/JSON-based sync process"""
        logging.info("Starting TallyPrime Clean Slate sync process (ODBC/JSON)")
        
        try:
            # Test connections based on mode
            if self.multi_company_mode:
                connection_results = self.tally_api.test_all_connections()
                failed_companies = [name for name, success in connection_results.items() if not success]
                if failed_companies:
                    raise Exception(f"Cannot connect to TallyPrime companies: {', '.join(failed_companies)}. Check DSN configurations and ensure TallyPrime instances are running.")
            else:
                if not self.tally_api.test_connection():
                    raise Exception("Cannot connect to TallyPrime via ODBC. Check DSN configuration and ensure TallyPrime is running.")
            
            if not self.supabase_sync.test_connection():
                raise Exception("Cannot connect to Supabase. Check your configuration and internet connection.")
            
            logging.info("All connections verified successfully")
            
            # Fetch data from TallyPrime via ODBC
            if self.multi_company_mode:
                logging.info("Fetching aggregated stock items from all TallyPrime companies...")
                tally_items = self.tally_api.get_aggregated_stock_items()
            else:
                logging.info("Fetching stock items from TallyPrime via ODBC...")
                tally_items = self.tally_api.get_stock_items()
            
            if not tally_items:
                logging.warning("No stock items found in TallyPrime")
                return False
            
            logging.info(f"Retrieved {len(tally_items)} stock items from TallyPrime")
            
            # Fetch stock movements
            movement_days_back = self.config['sync']['movement_days_back']
            from_date = datetime.now() - timedelta(days=movement_days_back)
            
            if self.multi_company_mode:
                logging.info("Fetching aggregated stock movements from all TallyPrime companies...")
                tally_movements = self.tally_api.get_aggregated_stock_movements(from_date)
            else:
                logging.info("Fetching stock movements from TallyPrime...")
                tally_movements = self.tally_api.get_stock_movements(from_date)
            
            logging.info(f"Retrieved {len(tally_movements)} stock movements from TallyPrime")
            
            # Calculate clean slate stock levels
            logging.info("Calculating clean slate stock levels...")
            clean_slate_items = self.clean_slate_engine.calculate_clean_slate_stock(
                tally_items, 
                tally_movements
            )
            
            # Optional: Export to JSON file for debugging
            self.tally_api.export_to_json_file('debug_tally_export.json')
            
            # Sync to Supabase
            logging.info("Syncing data to Supabase...")
            success = self.supabase_sync.sync_items(clean_slate_items)
            
            if success:
                logging.info(f"Successfully synced {len(clean_slate_items)} items to Supabase")
                self.supabase_sync.log_sync_status(
                    len(clean_slate_items), 
                    'SUCCESS'
                )
                return True
            else:
                logging.error("Failed to sync data to Supabase")
                self.supabase_sync.log_sync_status(
                    len(clean_slate_items), 
                    'FAILED', 
                    'Supabase sync failed'
                )
                return False
                
        except Exception as e:
            error_msg = f"Sync process failed: {e}"
            logging.error(error_msg)
            self.supabase_sync.log_sync_status(0, 'ERROR', str(e))
            return False
        finally:
            # Always close the ODBC connection
            self.tally_api.close_connection()


def main():
    """Main entry point"""
    sync_manager = TallySyncManager()
    success = sync_manager.run_sync()
    
    if success:
        logging.info("ODBC/JSON sync completed successfully")
        sys.exit(0)
    else:
        logging.error("ODBC/JSON sync failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
