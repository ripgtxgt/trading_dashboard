#!/usr/bin/env python3
"""
TelegramNotification模块
用atfromPythonTrade脚本SendTelegramNotification
"""

import os
import requests
from datetime import datetime

class TelegramNotifier:
 """TelegramNotification器"""
 
 def __init__(self):
 self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
 self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
 self.api_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
 
 def is_configured(self):
 """检查is否AlreadyConfig"""
 return bool(self.bot_token and self.chat_id)
 
 def send_message(self, text, parse_mode="Markdown", disable_notification=False):
 """
 SendMessagetoTelegram
 
 Args:
 text: Message文本
 parse_mode: 解析模式 ("Markdown" or "HTML")
 disable_notification: is否静音Notification
 """
 if not self.is_configured():
 print("[Telegram] NotConfigNotification")
 return False
 
 try:
 response = requests.post(
 f"{self.api_url}/sendMessage",
 json={
 "chat_id": self.chat_id,
 "text": text,
 "parse_mode": parse_mode,
 "disable_notification": disable_notification
 },
 timeout=10
)
 
 if response.status_code == 200:
 print("[Telegram] MessageSendSuccess")
 return True
 else:
 print(f"[Telegram] SendFailed: {response.status_code}")
 return False
 
 except Exception as e:
 print(f"[Telegram] Send: {e}")
 return False
 
 def notify_open_position(self, symbol, side, price, quantity, margin):
 """Send开仓Notification"""
 emoji = "📈" if side == "long" else "📉"
 direction = "做多" if side == "long" else "做空"
 
 text = f"""
{emoji} *开仓Notification*

Tradefor: `{symbol}`
方向: *{direction}*
Price: ${price:.2f}
Amount: {quantity:.6f}
保证金: {margin:.2f} USDT

_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
 """.strip()
 
 return self.send_message(text)
 
 def notify_close_position(self, symbol, side, entry_price, exit_price, pnl, pnl_pct):
 """SendClose positionNotification"""
 is_profit = pnl > 0
 emoji = "[OK]" if is_profit else "[ERROR]"
 direction = "做多" if side == "long" else "做空"
 
 text = f"""
{emoji} *Close positionNotification*

Tradefor: `{symbol}`
方向: *{direction}*
入场价: ${entry_price:.2f}
出场价: ${exit_price:.2f}
PnL: {"+" if is_profit else ""}{pnl:.2f} USDT ({pnl_pct*100:.2f}%)

_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
 """.strip()
 
 return self.send_message(text, disable_notification=not is_profit)
 
 def notify_risk_alert(self, level, message, details=None):
 """
 SendRiskWarning
 
 Args:
 level: Warning级别 ("info", "warning", "error")
 message: WarningMessage
 details: 详细Info（optional）
 """
 emoji_map = {
 "info": "ℹ️",
 "warning": "[WARNING]",
 "error": "🚨"
 }
 
 level_text = {
 "info": "Info",
 "warning": "Warning",
 "error": "严重Warning"
 }
 
 emoji = emoji_map.get(level, "ℹ️")
 level_name = level_text.get(level, "Info")
 
 text = f"""
{emoji} *{level_name}*

{message}
 """.strip()
 
 if details:
 text += f"\n\n{details}"
 
 text += f"\n\n_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
 
 return self.send_message(text, disable_notification=(level == "info"))
 
 def notify_daily_stats(self, total_trades, win_trades, win_rate, total_pnl, capital):
 """Send每日统计"""
 text = f"""
[DATA] *每日统计*

总Trade: {total_trades}
盈利Trade: {win_trades}
Win rate: {win_rate:.1f}%
总PnL: {"+" if total_pnl > 0 else ""}{total_pnl:.2f} USDT
Current资金: {capital:.2f} USDT

_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
 """.strip()
 
 return self.send_message(text)
 
 def notify_bot_status(self, is_running, reason=None):
 """Send机器人Status变更Notification"""
 emoji = "▶️" if is_running else "⏸️"
 status = "AlreadyStart" if is_running else "AlreadyStop"
 
 text = f"""
{emoji} *机器人Status*

Status: *{status}*
 """.strip()
 
 if reason:
 text += f"\nreason: {reason}"
 
 text += f"\n\n_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
 
 return self.send_message(text)

# 使用示例
if __name__ == "__main__":
 notifier = TelegramNotifier()
 
 if not notifier.is_configured():
 print("PleaseSetenv var:")
 print("export TELEGRAM_BOT_TOKEN='your_bot_token'")
 print("export TELEGRAM_CHAT_ID='your_chat_id'")
 exit(1)
 
 # 测试开仓Notification
 notifier.notify_open_position(
 symbol="XBTUSDTM",
 side="long",
 price=50000.0,
 quantity=0.001,
 margin=5.0
)
 
 # 测试Close positionNotification
 notifier.notify_close_position(
 symbol="XBTUSDTM",
 side="long",
 entry_price=50000.0,
 exit_price=51000.0,
 pnl=10.0,
 pnl_pct=0.02
)
 
 # 测试RiskWarning
 notifier.notify_risk_alert(
 level="warning",
 message="PositionRisk过高",
 details="CurrentPositionRisk比例: 438.40%"
)
 
 # 测试每日统计
 notifier.notify_daily_stats(
 total_trades=10,
 win_trades=6,
 win_rate=60.0,
 total_pnl=25.5,
 capital=35.5
)
 
 # 测试机器人Status
 notifier.notify_bot_status(
 is_running=True,
 reason="manualStart"
)
