#!/usr/bin/env python3
"""
Telegram通知模块
用于从Python交易脚本SendTelegram通知
"""

import os
import requests
from datetime import datetime

class TelegramNotifier:
    """Telegram通知器"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
    
    def is_configured(self):
        """检查是否已配置"""
        return bool(self.bot_token and self.chat_id)
    
    def send_message(self, text, parse_mode="Markdown", disable_notification=False):
        """
        Send消息到Telegram
        
        Args:
            text: 消息文本
            parse_mode: 解析模式 ("Markdown" 或 "HTML")
            disable_notification: 是否静音通知
        """
        if not self.is_configured():
            print("[Telegram] NotConfig, Notify")
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
        """Send开仓通知"""
        emoji = "[CHART]" if side == "long" else "[DOWN]"
        direction = "做多" if side == "long" else "做空"
        
        text = f"""
{emoji} *开仓通知*

交易对: `{symbol}`
方向: *{direction}*
价格: ${price:.2f}
数量: {quantity:.6f}
保证金: {margin:.2f} USDT

_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
        """.strip()
        
        return self.send_message(text)
    
    def notify_close_position(self, symbol, side, entry_price, exit_price, pnl, pnl_pct):
        """Send平仓通知"""
        is_profit = pnl > 0
        emoji = "[OK]" if is_profit else "[ERROR]"
        direction = "做多" if side == "long" else "做空"
        
        text = f"""
{emoji} *平仓通知*

交易对: `{symbol}`
方向: *{direction}*
入场价: ${entry_price:.2f}
出场价: ${exit_price:.2f}
盈亏: {"+" if is_profit else ""}{pnl:.2f} USDT ({pnl_pct*100:.2f}%)

_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
        """.strip()
        
        return self.send_message(text, disable_notification=not is_profit)
    
    def notify_risk_alert(self, level, message, details=None):
        """
        Send风险警告
        
        Args:
            level: 警告级别 ("info", "warning", "error")
            message: Warning message
            details: 详细信息(可选)
        """
        emoji_map = {
            "info": "ℹ️",
            "warning": "[WARNING]",
            "error": "🚨"
        }
        
        level_text = {
            "info": "信息",
            "warning": "警告",
            "error": "严重警告"
        }
        
        emoji = emoji_map.get(level, "ℹ️")
        level_name = level_text.get(level, "信息")
        
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
[CHART] *每日统计*

总交易: {total_trades}笔
盈利交易: {win_trades}笔
胜率: {win_rate:.1f}%
总盈亏: {"+" if total_pnl > 0 else ""}{total_pnl:.2f} USDT
当前资金: {capital:.2f} USDT

_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
        """.strip()
        
        return self.send_message(text)
    
    def notify_bot_status(self, is_running, reason=None):
        """Send机器人状态变更通知"""
        emoji = "▶️" if is_running else "⏸️"
        status = "started" if is_running else "stopped"
        
        text = f"""
{emoji} *机器人状态*

状态: *{status}*
        """.strip()
        
        if reason:
            text += f"\nReason: {reason}"
        
        text += f"\n\n_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        
        return self.send_message(text)

# 使用示例
if __name__ == "__main__":
    notifier = TelegramNotifier()
    
    if not notifier.is_configured():
        print("Please:")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token'")
        print("export TELEGRAM_CHAT_ID='your_chat_id'")
        exit(1)
    
    # 测试开仓通知
    notifier.notify_open_position(
        symbol="XBTUSDTM",
        side="long",
        price=50000.0,
        quantity=0.001,
        margin=5.0
    )
    
    # 测试平仓通知
    notifier.notify_close_position(
        symbol="XBTUSDTM",
        side="long",
        entry_price=50000.0,
        exit_price=51000.0,
        pnl=10.0,
        pnl_pct=0.02
    )
    
    # 测试风险警告
    notifier.notify_risk_alert(
        level="warning",
        message="Position risk too high",
        details="当前仓位风险比例: 438.40%"
    )
    
    # 测试每日统计
    notifier.notify_daily_stats(
        total_trades=10,
        win_trades=6,
        win_rate=60.0,
        total_pnl=25.5,
        capital=35.5
    )
    
    # 测试机器人状态
    notifier.notify_bot_status(
        is_running=True,
        reason="Manual start"
    )
