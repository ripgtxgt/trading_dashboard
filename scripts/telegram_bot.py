#!/usr/bin/env python3
"""
Telegram Bot控制模块
支持通过Telegram消息远程控制和查询交易系统
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
        初始化Telegram Bot
        
        Args:
            bot_token: Bot Token(从环境变量TELEGRAM_BOT_TOKEN读取)
            chat_id: 聊天ID(从环境变量TELEGRAM_CHAT_ID读取)
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
        发送风险警报
        
        Args:
            risk_level: 风险等级 (low/medium/high/extreme)
            volatility: 波动率
            message: 警报消息
        
        Returns:
            是否发送成功
        """
        emoji_map = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'extreme': '🔴'
        }
        
        emoji = emoji_map.get(risk_level, '⚪')
        
        alert_text = f"{emoji} 风险警报\n\n"
        alert_text += f"风险等级: {risk_level.upper()}\n"
        alert_text += f"波动率: {volatility*100:.2f}%\n\n"
        alert_text += f"{message}"
        
        return self.send_message(alert_text)
    
    def send_pause_alert(self, reason: str, volatility: float) -> bool:
        """
        发送交易暂停警报
        
        Args:
            reason: 暂停原因
            volatility: 当前波动率
        
        Returns:
            是否发送成功
        """
        alert_text = "[WARNING] 交易自动暂停\n\n"
        alert_text += f"原因: {reason}\n"
        alert_text += f"波动率: {volatility*100:.2f}%\n\n"
        alert_text += "系统将在波动率降低后自动恢复交易"
        
        return self.send_message(alert_text)
    
    def send_resume_alert(self, reason: str, pause_duration: float) -> bool:
        """
        发送交易恢复警报
        
        Args:
            reason: 恢复原因
            pause_duration: 暂停时长(秒)
        
        Returns:
            是否发送成功
        """
        alert_text = "[OK] 交易已恢复\n\n"
        alert_text += f"原因: {reason}\n"
        alert_text += f"暂停时长: {pause_duration/60:.1f}分钟\n\n"
        alert_text += "系统已恢复正常交易"
        
        return self.send_message(alert_text)
    
    def send_position_adjustment_alert(self, old_position: float, new_position: float, reason: str) -> bool:
        """
        发送仓位调整警报
        
        Args:
            old_position: 原仓位
            new_position: 新仓位
            reason: 调整原因
        
        Returns:
            是否发送成功
        """
        change_pct = ((new_position - old_position) / old_position * 100) if old_position > 0 else 0
        direction = "增加" if change_pct > 0 else "减少"
        
        alert_text = "[CHART] 仓位调整通知\n\n"
        alert_text += f"原仓位: {old_position:.4f}\n"
        alert_text += f"新仓位: {new_position:.4f}\n"
        alert_text += f"变化: {direction} {abs(change_pct):.1f}%\n\n"
        alert_text += f"原因: {reason}"
        
        return self.send_message(alert_text)
    
    def send_message(self, text: str) -> bool:
        """
        发送消息到Telegram
        
        Args:
            text: 消息文本
        
        Returns:
            是否发送成功
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
        获取新消息
        
        Returns:
            消息列表
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
        处理命令
        
        Args:
            command: 命令名称
            args: 命令参数
        
        Returns:
            响应消息
        """
        # /status - 查询状态
        if command == "status":
            return self._handle_status()
        
        # /config - 查看配置
        elif command == "config":
            return self._handle_config()
        
        # /set <param> <value> - 修改参数
        elif command == "set":
            if len(args) < 2:
                return "[ERROR] 用法: /set <参数名> <值>\n例如: /set roll_multiplier 2.5"
            return self._handle_set(args[0], args[1])
        
        # /enable - 启用策略
        elif command == "enable":
            return self._handle_enable(True)
        
        # /disable - 禁用策略
        elif command == "disable":
            return self._handle_enable(False)
        
        # /stop - 紧急停止
        elif command == "stop":
            return self._handle_emergency_stop()
        
        # /resume - 恢复交易
        elif command == "resume":
            return self._handle_resume()
        
        # /help - 帮助
        elif command == "help":
            return self._handle_help()
        
        else:
            return f"[ERROR] 未知命令: /{command}\n发送 /help 查看可用命令"
    
    def _handle_status(self) -> str:
        """处理状态查询"""
        try:
            # 这里需要从数据库读取实际状态
            # 简化版本, 返回配置状态
            config = self.config_loader.load_config(force_reload=True)
            if not config:
                return "[ERROR] 无法读取配置"
            
            status_text = "[CHART] *交易系统状态*\n\n"
            status_text += f"交易对: `{config['symbol']}`\n"
            status_text += f"策略状态: {'🟢 启用' if config['is_active'] else '🔴 禁用'}\n"
            status_text += f"杠杆: `{config['leverage']}x`\n"
            status_text += f"仓位大小: `{config['position_size']}`\n"
            status_text += f"\n滚仓倍数: `{config['roll_multiplier']}`\n"
            status_text += f"止盈: `{config['take_profit_pct']}%`\n"
            status_text += f"止损: `{config['stop_loss_pct']}%`\n"
            
            return status_text
            
        except Exception as e:
            return f"[ERROR] 查询失败: {str(e)}"
    
    def _handle_config(self) -> str:
        """处理配置查看"""
        try:
            config = self.config_loader.load_config(force_reload=True)
            if not config:
                return "[ERROR] 无法读取配置"
            
            config_text = "⚙️ *策略配置*\n\n"
            config_text += f"*基础配置*\n"
            config_text += f"交易对: `{config['symbol']}`\n"
            config_text += f"滚仓倍数: `{config['roll_multiplier']}`\n"
            config_text += f"\n*止盈止损*\n"
            config_text += f"止盈: `{config['take_profit_pct']}%`\n"
            config_text += f"止损: `{config['stop_loss_pct']}%`\n"
            config_text += f"\n*风险控制*\n"
            config_text += f"单日最大亏损: `{config['max_daily_loss']}%`\n"
            config_text += f"最大回撤: `{config['max_drawdown']}%`\n"
            config_text += f"连续亏损限制: `{config['consecutive_loss_limit']}`\n"
            config_text += f"\n*交易参数*\n"
            config_text += f"杠杆: `{config['leverage']}x`\n"
            config_text += f"仓位大小: `{config['position_size']}`\n"
            config_text += f"\n策略状态: {'🟢 启用' if config['is_active'] else '🔴 禁用'}\n"
            
            return config_text
            
        except Exception as e:
            return f"[ERROR] 查询失败: {str(e)}"
    
    def _handle_set(self, param: str, value: str) -> str:
        """处理参数修改"""
        # 这里需要调用API修改配置
        # 简化版本, 只返回提示
        return f"[WARNING] 参数修改功能需要通过Web Dashboard操作\n\n" \
               f"请访问Dashboard的策略配置面板修改参数: \n" \
               f"参数: `{param}`\n" \
               f"值: `{value}`"
    
    def _handle_enable(self, enable: bool) -> str:
        """处理启用/禁用策略"""
        # 这里需要调用API修改配置
        # 简化版本, 只返回提示
        action = "启用" if enable else "禁用"
        return f"[WARNING] 策略{action}需要通过Web Dashboard操作\n\n" \
               f"请访问Dashboard的策略配置面板进行操作"
    
    def _handle_emergency_stop(self) -> str:
        """处理紧急停止命令"""
        try:
            # 更新数据库状态
            self.db.update_bot_status(
                status='stopped',
                emergency_stopped=True
            )
            
            return "[WARNING] *紧急停止已激活*\n\n" \
                   "[OK] 所有交易活动已暂停\n" \
                   "[OK] 开仓位将被关闭\n\n" \
                   "使用 /resume 命令恢复交易"
        except Exception as e:
            return f"[ERROR] 紧急停止失败: {str(e)}"
    
    def _handle_resume(self) -> str:
        """处理恢复交易命令"""
        try:
            # 更新数据库状态
            self.db.update_bot_status(
                status='running',
                emergency_stopped=False
            )
            
            return "[OK] *交易已恢复*\n\n" \
                   "[OK] Bot已重新启动\n" \
                   "[OK] 正在监控市场\n\n" \
                   "使用 /status 查看当前状态"
        except Exception as e:
            return f"[ERROR] 恢复失败: {str(e)}"
    
    def _handle_help(self) -> str:
        """处理帮助命令"""
        help_text = "🤖 *Telegram Bot 命令帮助*\n\n"
        help_text += "*查询命令*\n"
        help_text += "/status - 查询交易系统状态\n"
        help_text += "/config - 查看策略配置\n"
        help_text += "\n*控制命令*\n"
        help_text += "/stop - 紧急停止所有交易\n"
        help_text += "/resume - 恢复交易活动\n"
        help_text += "/enable - 启用策略\n"
        help_text += "/disable - 禁用策略\n"
        help_text += "/set <参数> <值> - 修改参数\n"
        help_text += "\n*其他命令*\n"
        help_text += "/help - 显示此帮助信息\n"
        help_text += "\n💡 提示: 大部分操作建议通过Web Dashboard进行"
        
        return help_text
    
    def run(self):
        """运行Bot(轮询模式)"""
        print("[TG Bot] Starting bot...")
        self.send_message("🤖 Telegram Bot已启动\n发送 /help 查看可用命令")
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    if "message" in update:
                        message = update["message"]
                        chat_id = str(message["chat"]["id"])
                        text = message.get("text", "")
                        
                        # 只处理来自指定chat_id的消息
                        if chat_id != self.chat_id:
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
                self.send_message("🤖 Telegram Bot已停止")
                break
            except Exception as e:
                print(f"[TG Bot] Error in main loop: {e}")
                time.sleep(5)
    
    def close(self):
        """关闭Bot"""
        if self.db:
            self.db.close()


# 使用示例
if __name__ == "__main__":
    bot = TelegramBot()
    
    # 测试发送消息
    bot.send_message("🧪 测试消息")
    
    # 运行Bot(轮询模式)
    # bot.run()
