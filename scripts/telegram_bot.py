#!/usr/bin/env python3
"""
Telegram Bot控制模块
支持通过TelegramMessage远程控制andQueryTrade系统
"""

import os
import requests
from typing import Optional, Dict, Any
import time
from config_loader import get_config_loader
from db_integration import DatabaseIntegration


class TelegramBot:
 """Telegram Bot控制器"""
 
 def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
 """
 InitializeTelegram Bot
 
 Args:
 bot_token: Bot Token（fromenv varTELEGRAM_BOT_TOKEN读取）
 chat_id: 聊天ID（fromenv varTELEGRAM_CHAT_ID读取）
 """
 self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
 self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
 self.api_base = f"https://api.telegram.org/bot{self.bot_token}"
 self.last_update_id = 0
 self.config_loader = get_config_loader()
 self.db = DatabaseIntegration(enable_websocket=False)
 
 if not self.bot_token:
 print("[TG Bot] Warning: TELEGRAM_BOT_TOKEN not set")
 if not self.chat_id:
 print("[TG Bot] Warning: TELEGRAM_CHAT_ID not set")
 
 def send_risk_alert(self, risk_level: str, volatility: float, message: str) -> bool:
 """
 SendRisk警报
 
 Args:
 risk_level: Risklevel (low/medium/high/extreme)
 volatility: Volatility率
 message: 警报Message
 
 Returns:
 is否SendSuccess
 """
 emoji_map = {
 'low': '🟢',
 'medium': '🟡',
 'high': '🟠',
 'extreme': '🔴'
 }
 
 emoji = emoji_map.get(risk_level, '⚪')
 
 alert_text = f"{emoji} Risk警报\n\n"
 alert_text += f"Risklevel: {risk_level.upper()}\n"
 alert_text += f"Volatility率: {volatility*100:.2f}%\n\n"
 alert_text += f"{message}"
 
 return self.send_message(alert_text)
 
 def send_pause_alert(self, reason: str, volatility: float) -> bool:
 """
 SendTradePause警报
 
 Args:
 reason: Pausereason
 volatility: CurrentVolatility率
 
 Returns:
 is否SendSuccess
 """
 alert_text = "[WARNING] TradeautoPause\n\n"
 alert_text += f"reason: {reason}\n"
 alert_text += f"Volatility率: {volatility*100:.2f}%\n\n"
 alert_text += "系统willatVolatility率降低后autoResumeTrade"
 
 return self.send_message(alert_text)
 
 def send_resume_alert(self, reason: str, pause_duration: float) -> bool:
 """
 SendTradeResume警报
 
 Args:
 reason: Resumereason
 pause_duration: Pause时长（second）
 
 Returns:
 is否SendSuccess
 """
 alert_text = "[OK] TradeAlreadyResume\n\n"
 alert_text += f"reason: {reason}\n"
 alert_text += f"Pause时长: {pause_duration/60:.1f}minute\n\n"
 alert_text += "系统AlreadyResume正常Trade"
 
 return self.send_message(alert_text)
 
 def send_position_adjustment_alert(self, old_position: float, new_position: float, reason: str) -> bool:
 """
 SendPositionadjust警报
 
 Args:
 old_position: 原Position
 new_position: 新Position
 reason: adjustreason
 
 Returns:
 is否SendSuccess
 """
 change_pct = ((new_position - old_position) / old_position * 100) if old_position > 0 else 0
 direction = "增加" if change_pct > 0 else "减少"
 
 alert_text = "[DATA] PositionadjustNotification\n\n"
 alert_text += f"原Position: {old_position:.4f}\n"
 alert_text += f"新Position: {new_position:.4f}\n"
 alert_text += f"变化: {direction} {abs(change_pct):.1f}%\n\n"
 alert_text += f"reason: {reason}"
 
 return self.send_message(alert_text)
 
 def send_message(self, text: str) -> bool:
 """
 SendMessagetoTelegram
 
 Args:
 text: Message文本
 
 Returns:
 is否SendSuccess
 """
 if not self.bot_token or not self.chat_id:
 print(f"[TG Bot] Cannot send message (no token/chat_id): {text}")
 return False
 
 try:
 url = f"{self.api_base}/sendMessage"
 data = {
 "chat_id": self.chat_id,
 "text": text,
 "parse_mode": "Markdown",
 }
 
 response = requests.post(url, json=data, timeout=10)
 if response.status_code == 200:
 print(f"[TG Bot] Message sent: {text[:50]}...")
 return True
 else:
 print(f"[TG Bot] Failed to send message: {response.text}")
 return False
 
 except Exception as e:
 print(f"[TG Bot] Error sending message: {e}")
 return False
 
 def get_updates(self) -> list:
 """
 Get新Message
 
 Returns:
 Message列表
 """
 if not self.bot_token:
 return []
 
 try:
 url = f"{self.api_base}/getUpdates"
 params = {
 "offset": self.last_update_id + 1,
 "timeout": 30,
 }
 
 response = requests.get(url, params=params, timeout=35)
 if response.status_code == 200:
 data = response.json()
 if data.get("ok"):
 updates = data.get("result", [])
 if updates:
 self.last_update_id = updates[-1]["update_id"]
 return updates
 
 return []
 
 except Exception as e:
 print(f"[TG Bot] Error getting updates: {e}")
 return []
 
 def process_command(self, command: str, args: list) -> str:
 """
 Process命令
 
 Args:
 command: 命令名称
 args: 命令Parameter
 
 Returns:
 响shouldMessage
 """
 # /status - QueryStatus
 if command == "status":
 return self._handle_status()
 
 # /config - 查看Config
 elif command == "config":
 return self._handle_config()
 
 # /set <param> <value> - 修改Parameter
 elif command == "set":
 if len(args) < 2:
 return "[ERROR] 用法: /set <Parameter名> <值>\n例如: /set roll_multiplier 2.5"
 return self._handle_set(args[0], args[1])
 
 # /enable - enableStrategy
 elif command == "enable":
 return self._handle_enable(True)
 
 # /disable - disableStrategy
 elif command == "disable":
 return self._handle_enable(False)
 
 # /stop - 紧急Stop
 elif command == "stop":
 return self._handle_emergency_stop()
 
 # /resume - ResumeTrade
 elif command == "resume":
 return self._handle_resume()
 
 # /help - 帮助
 elif command == "help":
 return self._handle_help()
 
 else:
 return f"[ERROR] Not知命令: /{command}\nSend /help 查看可用命令"
 
 def _handle_status(self) -> str:
 """ProcessStatusQuery"""
 try:
 # 这里需要fromDatabase读取实际Status
 # 简化版本，返回ConfigStatus
 config = self.config_loader.load_config(force_reload=True)
 if not config:
 return "[ERROR] No法读取Config"
 
 status_text = "[DATA] *Trade系统Status*\n\n"
 status_text += f"Tradefor: `{config['symbol']}`\n"
 status_text += f"StrategyStatus: {'🟢 enable' if config['is_active'] else '🔴 disable'}\n"
 status_text += f"杠杆: `{config['leverage']}x`\n"
 status_text += f"Position大小: `{config['position_size']}`\n"
 status_text += f"\n滚仓倍数: `{config['roll_multiplier']}`\n"
 status_text += f"Take profit: `{config['take_profit_pct']}%`\n"
 status_text += f"Stop loss: `{config['stop_loss_pct']}%`\n"
 
 return status_text
 
 except Exception as e:
 return f"[ERROR] QueryFailed: {str(e)}"
 
 def _handle_config(self) -> str:
 """ProcessConfig查看"""
 try:
 config = self.config_loader.load_config(force_reload=True)
 if not config:
 return "[ERROR] No法读取Config"
 
 config_text = "⚙️ *StrategyConfig*\n\n"
 config_text += f"*baseConfig*\n"
 config_text += f"Tradefor: `{config['symbol']}`\n"
 config_text += f"滚仓倍数: `{config['roll_multiplier']}`\n"
 config_text += f"\n*Take profitStop loss*\n"
 config_text += f"Take profit: `{config['take_profit_pct']}%`\n"
 config_text += f"Stop loss: `{config['stop_loss_pct']}%`\n"
 config_text += f"\n*Risk控制*\n"
 config_text += f"dailyMaxLoss: `{config['max_daily_loss']}%`\n"
 config_text += f"MaxDrawdown: `{config['max_drawdown']}%`\n"
 config_text += f"consecutiveLosslimit: `{config['consecutive_loss_limit']}`\n"
 config_text += f"\n*TradeParameter*\n"
 config_text += f"杠杆: `{config['leverage']}x`\n"
 config_text += f"Position大小: `{config['position_size']}`\n"
 config_text += f"\nStrategyStatus: {'🟢 enable' if config['is_active'] else '🔴 disable'}\n"
 
 return config_text
 
 except Exception as e:
 return f"[ERROR] QueryFailed: {str(e)}"
 
 def _handle_set(self, param: str, value: str) -> str:
 """ProcessParameter修改"""
 # 这里需要调用API修改Config
 # 简化版本，只返回提示
 return f"[WARNING] Parameter修改功能需要通过Web Dashboard操作\n\n" \
 f"Please访问DashboardStrategyConfig面板修改Parameter：\n" \
 f"Parameter: `{param}`\n" \
 f"值: `{value}`"
 
 def _handle_enable(self, enable: bool) -> str:
 """Processenable/disableStrategy"""
 # 这里需要调用API修改Config
 # 简化版本，只返回提示
 action = "enable" if enable else "disable"
 return f"[WARNING] Strategy{action}需要通过Web Dashboard操作\n\n" \
 f"Please访问DashboardStrategyConfig面板进行操作"
 
 def _handle_emergency_stop(self) -> str:
 """Process紧急Stop命令"""
 try:
 # UpdateDatabaseStatus
 self.db.update_bot_status(
 status='stopped',
 emergency_stopped=True
)
 
 return "[WARNING] *紧急StopAlreadyactivate*\n\n" \
 "[OK] 所HasTrade活动AlreadyPause\n" \
 "[OK] 开Positionwill被close\n\n" \
 "使用 /resume 命令ResumeTrade"
 except Exception as e:
 return f"[ERROR] 紧急StopFailed: {str(e)}"
 
 def _handle_resume(self) -> str:
 """ProcessResumeTrade命令"""
 try:
 # UpdateDatabaseStatus
 self.db.update_bot_status(
 status='running',
 emergency_stopped=False
)
 
 return "[OK] *TradeAlreadyResume*\n\n" \
 "[OK] BotAlreadyre-Start\n" \
 "[OK] processingMonitor市场\n\n" \
 "使用 /status 查看CurrentStatus"
 except Exception as e:
 return f"[ERROR] ResumeFailed: {str(e)}"
 
 def _handle_help(self) -> str:
 """Process帮助命令"""
 help_text = "🤖 *Telegram Bot 命令帮助*\n\n"
 help_text += "*Query命令*\n"
 help_text += "/status - QueryTrade系统Status\n"
 help_text += "/config - 查看StrategyConfig\n"
 help_text += "\n*控制命令*\n"
 help_text += "/stop - 紧急Stop所HasTrade\n"
 help_text += "/resume - ResumeTrade活动\n"
 help_text += "/enable - enableStrategy\n"
 help_text += "/disable - disableStrategy\n"
 help_text += "/set <Parameter> <值> - 修改Parameter\n"
 help_text += "\n*其他命令*\n"
 help_text += "/help - 显示此帮助Info\n"
 help_text += "\n💡 提示：大部分操作suggest通过Web Dashboard进行"
 
 return help_text
 
 def run(self):
 """RunningBot（轮询模式）"""
 print("[TG Bot] Starting bot...")
 self.send_message("🤖 Telegram BotAlreadyStart\nSend /help 查看可用命令")
 
 while True:
 try:
 updates = self.get_updates()
 
 for update in updates:
 if "message" in update:
 message = update["message"]
 chat_id = str(message["chat"]["id"])
 text = message.get("text", "")
 
 # 只Process来自指定chat_idMessage
 if chat_id!= self.chat_id:
 print(f"[TG Bot] Ignoring message from {chat_id}")
 continue
 
 # 解析命令
 if text.startswith("/"):
 parts = text[1:].split()
 command = parts[0]
 args = parts[1:]
 
 print(f"[TG Bot] Command: /{command} {args}")
 response = self.process_command(command, args)
 self.send_message(response)
 
 time.sleep(1)
 
 except KeyboardInterrupt:
 print("\n[TG Bot] Stopping bot...")
 self.send_message("🤖 Telegram BotAlreadyStop")
 break
 except Exception as e:
 print(f"[TG Bot] Error in main loop: {e}")
 time.sleep(5)
 
 def close(self):
 """closeBot"""
 if self.db:
 self.db.close()


# 使用示例
if __name__ == "__main__":
 bot = TelegramBot()
 
 # 测试SendMessage
 bot.send_message("🧪 测试Message")
 
 # RunningBot（轮询模式）
 # bot.run()
