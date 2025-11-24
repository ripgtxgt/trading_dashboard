#!/usr/bin/env python3
"""
Daily Trading Report Generator
Generates and sends daily trading summary via Telegram
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Optional
import mysql.connector

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

try:
 from telegram_bot import TelegramBot
except ImportError:
 print("[Daily Report] Warning: telegram_bot not available")
 TelegramBot = None


class DailyReportGenerator:
 """Generate daily trading reports"""
 
 def __init__(self):
 """Initialize report generator"""
 self.db_url = os.getenv("DATABASE_URL", "")
 self.conn = None
 self.telegram_bot = None
 
 if self.db_url:
 self._connect_db()
 
 # Initialize Telegram bot if available
 if TelegramBot:
 try:
 self.telegram_bot = TelegramBot()
 print("[Daily Report] Telegram bot initialized")
 except Exception as e:
 print(f"[Daily Report] Failed to initialize Telegram: {e}")
 
 def _connect_db(self):
 """Connect to database"""
 try:
 if self.db_url.startswith("mysql://"):
 url = self.db_url.replace("mysql://", "")
 if "@" in url:
 auth, location = url.split("@")
 user, password = auth.split(":")
 host_port, database = location.split("/")
 
 if ":" in host_port:
 host, port = host_port.split(":")
 port = int(port)
 else:
 host = host_port
 port = 3306
 
 self.conn = mysql.connector.connect(
 host=host,
 port=port,
 user=user,
 password=password,
 database=database
)
 print("[Daily Report] Database connected")
 except Exception as e:
 print(f"[Daily Report] Failed to connect to database: {e}")
 self.conn = None
 
 def get_daily_stats(self) -> Optional[Dict]:
 """Get daily trading statistics"""
 if not self.conn:
 print("[Daily Report] No database connection")
 return None
 
 try:
 cursor = self.conn.cursor(dictionary=True)
 
 # Get today's date range (UTC)
 today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
 today_end = today_start + timedelta(days=1)
 
 # Get today's trades
 cursor.execute("""
 SELECT 
 COUNT(*) as total_trades,
 SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
 SUM(pnl) as total_pnl,
 MAX(pnl) as max_profit,
 MIN(pnl) as max_loss,
 AVG(pnl) as avg_pnl
 FROM trade_history
 WHERE exitTime >= %s AND exitTime < %s
 """, (today_start, today_end))
 
 trade_stats = cursor.fetchone()
 
 # Get current account status
 cursor.execute("""
 SELECT balance, profitRate, stage, updatedAt
 FROM account_status
 ORDER BY updatedAt DESC
 LIMIT 1
 """)
 
 account_stats = cursor.fetchone()
 
 # Get max drawdown today
 cursor.execute("""
 SELECT MIN(profitRate) as max_drawdown
 FROM account_status
 WHERE updatedAt >= %s AND updatedAt < %s
 """, (today_start, today_end))
 
 drawdown_stats = cursor.fetchone()
 
 cursor.close()
 
 # Calculate win rate
 total_trades = trade_stats['total_trades'] or 0
 winning_trades = trade_stats['winning_trades'] or 0
 win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
 
 return {
 'date': today_start.strftime('%Y-%m-%d'),
 'total_trades': total_trades,
 'winning_trades': winning_trades,
 'win_rate': win_rate,
 'total_pnl': trade_stats['total_pnl'] or 0,
 'max_profit': trade_stats['max_profit'] or 0,
 'max_loss': trade_stats['max_loss'] or 0,
 'avg_pnl': trade_stats['avg_pnl'] or 0,
 'current_balance': account_stats['balance'] if account_stats else 0,
 'profit_rate': account_stats['profitRate'] if account_stats else 0,
 'stage': account_stats['stage'] if account_stats else 'N/A',
 'max_drawdown': drawdown_stats['max_drawdown'] or 0
 }
 
 except Exception as e:
 print(f"[Daily Report] Error getting stats: {e}")
 return None
 
 def format_report(self, stats: Dict) -> str:
 """Format report message"""
 if not stats:
 return "No trading data available for today."
 
 report = f"""
[DATA] Daily Trading Report - {stats['date']}

[MONEY] Account Status:
• Current Balance: {stats['current_balance']:.2f} USDT
• Profit Rate: {stats['profit_rate']:.2f}%
• Current Stage: {stats['stage']}

📈 Trading Performance:
• Total Trades: {stats['total_trades']}
• Winning Trades: {stats['winning_trades']}
• Win Rate: {stats['win_rate']:.2f}%

💵 P&L Summary:
• Total P&L: {stats['total_pnl']:.2f} USDT
• Average P&L: {stats['avg_pnl']:.2f} USDT
• Max Profit: {stats['max_profit']:.2f} USDT
• Max Loss: {stats['max_loss']:.2f} USDT

[WARNING] Risk Metrics:
• Max Drawdown: {stats['max_drawdown']:.2f}%

---
Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
 return report.strip()
 
 def send_report(self):
 """Generate and send daily report"""
 print(f"[Daily Report] Generating report for {datetime.now().strftime('%Y-%m-%d')}")
 
 # Get statistics
 stats = self.get_daily_stats()
 if not stats:
 print("[Daily Report] Failed to get statistics")
 return False
 
 # Format report
 report = self.format_report(stats)
 print("[Daily Report] Report generated:")
 print(report)
 
 # Send via Telegram
 if self.telegram_bot:
 try:
 self.telegram_bot.send_message(report)
 print("[Daily Report] Report sent via Telegram")
 return True
 except Exception as e:
 print(f"[Daily Report] Failed to send Telegram message: {e}")
 return False
 else:
 print("[Daily Report] Telegram bot not available")
 return False
 
 def close(self):
 """Close database connection"""
 if self.conn:
 self.conn.close()
 print("[Daily Report] Database connection closed")


def main():
 """Main function"""
 print("=" * 60)
 print("Daily Trading Report Generator")
 print("=" * 60)
 
 generator = DailyReportGenerator()
 success = generator.send_report()
 generator.close()
 
 return 0 if success else 1


if __name__ == "__main__":
 sys.exit(main())
