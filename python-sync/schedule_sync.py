#!/usr/bin/env python3
"""
Scheduler script for TallyPrime Clean Slate sync operations.
This script can be used to run the sync at regular intervals.
"""

import schedule
import time
import logging
from tally_sync import TallySyncManager

def run_scheduled_sync():
    """Run the sync operation with error handling"""
    try:
        logging.info("Starting scheduled sync operation")
        sync_manager = TallySyncManager()
        success = sync_manager.run_sync()
        
        if success:
            logging.info("Scheduled sync completed successfully")
        else:
            logging.error("Scheduled sync failed")
            
    except Exception as e:
        logging.error(f"Scheduled sync error: {e}")

def main():
    """Main scheduler loop"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scheduler.log'),
            logging.StreamHandler()
        ]
    )
    
    # Schedule sync to run daily at 2 AM
    schedule.every().day.at("12:00").do(run_scheduled_sync)
    
    # Alternative: Run every 6 hours
    # schedule.every(6).hours.do(run_scheduled_sync)
    
    logging.info("TallyPrime sync scheduler started")
    logging.info("Next sync scheduled for: 12:00 daily")
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
