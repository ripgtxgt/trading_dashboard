#!/usr/bin/env python3
"""
Daily Report Scheduler
Runs daily report at specified time (00:00 Beijing Time = 16:00 UTC)
"""

import schedule
import time
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from daily_report import DailyReportGenerator


def run_daily_report():
    """Run daily report"""
    print(f"\n[Scheduler] Triggering daily report at {datetime.now()}")
    try:
        generator = DailyReportGenerator()
        generator.send_report()
        generator.close()
    except Exception as e:
        print(f"[Scheduler] Error running daily report: {e}")


def main():
    """Main scheduler loop"""
    print("=" * 60)
    print("Daily Report Scheduler Started")
    print("=" * 60)
    print("Schedule: Every day at 16:00 UTC (00:00 Beijing Time)")
    print("=" * 60)
    
    # Schedule daily report at 16:00 UTC (00:00 Beijing Time)
    schedule.every().day.at("16:00").do(run_daily_report)
    
    print(f"[Scheduler] Next run: {schedule.next_run()}")
    
    # Keep running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n[Scheduler] Stopping...")
            break
        except Exception as e:
            print(f"[Scheduler] Error: {e}")
            time.sleep(60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
