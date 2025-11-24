#!/usr/bin/env python3
"""
10U战神滚仓Strategy - Web Dashboard集成版
完整集成Database同步andTelegramNotification功能
"""

import os
import sys
import time
import logging
from datetime import datetime

# 添加Current目录toPython路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from live_strategy_engine_rolling import LiveStrategyEngineRolling
from kucoin_trader import KuCoinTrader
from live_trading_config import STRATEGY_CONFIG
from db_sync import DatabaseSync
from telegram_notifier import TelegramNotifier
from risk_manager import RiskManager


# Config日志
logging.basicConfig(
 level=logging.INFO,
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
 handlers=[
 logging.FileHandler(f'trading_system_{datetime.now().strftime("%Y%m%d")}.log'),
 logging.StreamHandler()
 ]
)
logger = logging.getLogger('TradingSystem')


class IntegratedTradingSystem:
 """集成版Trade系统"""
 
 def __init__(self):
 """Initialize系统"""
 logger.info("="*60)
 logger.info("10UStrategy - Web Dashboard")
 logger.info("="*60)
 
 # 检查env var
 self.check_env_vars()
 
 # InitializeDatabaseConnection
 self.db = DatabaseSync()
 if not self.db.connect():
 logger.error("DatabaseConnectionFailed")
 sys.exit(1)
 
 # InitializeTelegramNotification
 self.telegram = TelegramNotifier()
 
 # InitializeRisk管理器
 self.risk_manager = RiskManager()
 logger.info("RiskAlreadyStart")
 
 # InitializeKuCoinTrade器
 api_key = os.getenv('KUCOIN_API_KEY')
 api_secret = os.getenv('KUCOIN_API_SECRET')
 api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')
 
 if not all([api_key, api_secret, api_passphrase]):
 logger.error("missingKuCoin APIConfig")
 logger.error("PleaseSetenv varKUCOIN_API_KEY, KUCOIN_API_SECRET, KUCOIN_API_PASSPHRASE")
 sys.exit(1)
 
 self.trader = KuCoinTrader(
 api_key=api_key,
 api_secret=api_secret,
 api_passphrase=api_passphrase,
 is_sandbox=os.getenv('KUCOIN_SANDBOX', 'false').lower() == 'true'
)
 
 # InitializeStrategy引擎
 self.engine = LiveStrategyEngineRolling(
 trader=self.trader,
 initial_capital=float(os.getenv('INITIAL_CAPITAL', '10.0'))
)
 
 # willDatabaseandTelegram集成to引擎
 self.engine.db = self.db
 self.telegram = self.telegram
 
 # 修改引擎开仓方法，添加Database同步
 self._patch_engine_methods()
 
 logger.info("InitializeComplete")
 logger.info(f": {self.engine.capital:.2f} USDT")
 logger.info(f"Current: {self.engine.rolling_manager.get_current_stage(self.engine.capital).name}")
 
 def check_env_vars(self):
 """检查requiredenv var"""
 required_vars = {
 'DATABASE_URL': 'DatabaseConnection字符串',
 'KUCOIN_API_KEY': 'KuCoin API Key',
 'KUCOIN_API_SECRET': 'KuCoin API Secret',
 'KUCOIN_API_PASSPHRASE': 'KuCoin API Passphrase'
 }
 
 missing_vars = []
 for var, desc in required_vars.items():
 if not os.getenv(var):
 missing_vars.append(f" {var} - {desc}")
 
 if missing_vars:
 logger.error("missingrequiredenv var")
 for var in missing_vars:
 logger.error(var)
 logger.error("\noptionalenv var")
 logger.error(" TELEGRAM_BOT_TOKEN - Telegram Bot Token")
 logger.error(" TELEGRAM_CHAT_ID - Telegram Chat ID")
 logger.error(" KUCOIN_SANDBOX - istrue/false")
 logger.error(" INITIAL_CAPITAL - default10.0")
 sys.exit(1)
 
 def _patch_engine_methods(self):
 """修改引擎方法，添加Database同步andTelegramNotification"""
 
 # Save原始方法
 original_open_position = self.engine.open_position
 original_close_position = self.engine.rolling_manager.close_position
 
 def patched_open_position(direction):
 """开仓（添加Database同步andNotification）"""
 result = original_open_position(direction)
 
 if result and self.engine.rolling_manager.current_position:
 pos = self.engine.rolling_manager.current_position
 
 # 同步toDatabase
 try:
 position_id = self.db.update_position(
 symbol='XBTUSDTM',
 side=pos.side,
 entry_price=pos.entry_price,
 quantity=pos.size,
 margin=pos.margin,
 leverage=self.trader.leverage
)
 logger.info(f"PositionAlreadytoDatabaseID: {position_id}")
 except Exception as e:
 logger.error(f"PositionFailed: {e}")
 
 # SendTelegramNotification
 try:
 self.telegram.send_trade_opened(
 symbol='XBTUSDTM',
 side=pos.side,
 price=pos.entry_price,
 quantity=pos.size,
 margin=pos.margin
)
 except Exception as e:
 logger.error(f"TelegramNotificationSendFailed: {e}")
 
 return result
 
 def patched_close_position(current_price, reason=""):
 """Close position（添加Database同步andNotification）"""
 pos = self.engine.rolling_manager.current_position
 if not pos:
 return None
 
 # SaveClose position前数据
 entry_price = pos.entry_price
 size = pos.size
 side = pos.side
 margin = pos.margin
 
 # ExecuteClose position
 result = original_close_position(current_price, reason)
 
 if result:
 # RecordtoRisk管理器
 self.risk_manager.record_trade(
 pnl=result['pnl'],
 is_win=result['pnl'] > 0
)
 
 # 同步toDatabase
 try:
 trade_id = self.db.add_trade(
 symbol='XBTUSDTM',
 side=side,
 entry_price=entry_price,
 exit_price=current_price,
 quantity=size,
 pnl=result['pnl'],
 pnl_percent=result['pnl_pct'],
 open_time=datetime.now(), # 简化Process
 close_time=datetime.now()
)
 logger.info(f"TradeAlreadytoDatabaseID: {trade_id}")
 
 # Update机器人Status
 self.db.update_bot_state(
 status='running',
 current_balance=self.engine.capital,
 total_trades=len(self.engine.rolling_manager.trade_history),
 win_trades=sum(1 for t in self.engine.rolling_manager.trade_history if t.get('pnl', 0) > 0),
 total_profit=self.engine.capital - self.engine.initial_capital
)
 
 # 添加资金快照
 self.db.add_balance_snapshot(
 balance=self.engine.capital,
 equity=self.engine.capital,
 margin_used=0.0
)
 
 except Exception as e:
 logger.error(f"TradeFailed: {e}")
 
 # SendTelegramNotification
 try:
 self.telegram.send_trade_closed(
 symbol='XBTUSDTM',
 side=side,
 entry_price=entry_price,
 exit_price=current_price,
 pnl=result['pnl'],
 pnl_percent=result['pnl_pct']
)
 except Exception as e:
 logger.error(f"TelegramNotificationSendFailed: {e}")
 
 return result
 
 # 替换方法
 self.engine.open_position = patched_open_position
 self.engine.rolling_manager.close_position = patched_close_position
 
 def run(self):
 """RunningTrade系统"""
 logger.info("TradeStart")
 
 # SendStartNotification
 try:
 self.telegram.send_bot_status(
 status="Start",
 balance=self.engine.capital,
 total_trades=0,
 win_rate=0.0
)
 except Exception as e:
 logger.error(f"TelegramNotificationSendFailed: {e}")
 
 # UpdateDatabaseStatus
 try:
 self.db.update_bot_state(
 status='running',
 current_balance=self.engine.capital,
 total_trades=0,
 win_trades=0,
 total_profit=0.0
)
 except Exception as e:
 logger.error(f"DatabaseUpdateFailed: {e}")
 
 try:
 # StartStrategy引擎
 self.engine.is_running = True
 
 while self.engine.is_running and not self.engine.emergency_stopped:
 try:
 # GetCurrentPrice
 current_price = self.trader.get_current_price()
 if not current_price:
 logger.warning("NoGetCurrentPrice")
 time.sleep(60)
 continue
 
 # Risk检查
 allowed, reason = self.risk_manager.check_risk(current_price, self.engine.capital)
 
 if not allowed:
 logger.warning(f"TradePause: {reason}")
 
 # SendRiskWarning
 try:
 risk_status = self.risk_manager.get_risk_status()
 self.telegram.send_risk_alert(
 alert_type=reason,
 current_balance=self.engine.capital,
 drawdown=risk_status['current_drawdown_pct'],
 consecutive_losses=risk_status['consecutive_losses']
)
 except Exception as e:
 logger.error(f"TelegramNotificationSendFailed: {e}")
 
 # 如果HasPosition，考虑Close position
 if self.engine.rolling_manager.current_position:
 logger.info("DetectedPositionExecuteClose position...")
 self.engine.rolling_manager.close_position(current_price, f"Risk控制: {reason}")
 
 # Wait一段Time再检查
 time.sleep(300) # 5minute
 continue
 
 # Execute一Tradecycle
 self.engine.run_cycle()
 
 # Wait下一cycle
 time.sleep(self.engine.check_interval)
 
 except KeyboardInterrupt:
 logger.info("\nreceivedstop signal...")
 break
 except Exception as e:
 logger.error(f"Tradecycleerror occurred: {e}", exc_info=True)
 time.sleep(60) # error occurred后Wait1minute再继续
 
 finally:
 self.shutdown()
 
 def shutdown(self):
 """close系统"""
 logger.info("="*60)
 logger.info("TradeStop")
 logger.info("="*60)
 
 # 如果HasPosition，Close position
 if self.engine.rolling_manager.current_position:
 logger.info("DetectedPositionExecuteClose position...")
 current_price = self.trader.get_current_price()
 if current_price:
 self.engine.rolling_manager.close_position(current_price, "系统Stop")
 
 # 打印统计Info
 total_trades = len(self.engine.rolling_manager.trade_history)
 if total_trades > 0:
 win_trades = sum(1 for t in self.engine.rolling_manager.trade_history if t.get('pnl', 0) > 0)
 win_rate = (win_trades / total_trades) * 100
 total_profit = self.engine.capital - self.engine.initial_capital
 
 logger.info(f"Tradecount: {total_trades}")
 logger.info(f"count: {win_trades}")
 logger.info(f"Win rate: {win_rate:.2f}%")
 logger.info(f"PnL: {total_profit:.2f} USDT")
 logger.info(f"finalBalance: {self.engine.capital:.2f} USDT")
 logger.info(f"return rate: {((self.engine.capital - self.engine.initial_capital) / self.engine.initial_capital * 100):.2f}%")
 
 # Send每日统计
 try:
 self.telegram.send_daily_summary(
 total_trades=total_trades,
 win_trades=win_trades,
 win_rate=win_rate,
 total_pnl=total_profit,
 current_balance=self.engine.capital
)
 except Exception as e:
 logger.error(f"TelegramNotificationSendFailed: {e}")
 
 # UpdateDatabaseStatus
 try:
 self.db.update_bot_state(
 status='stopped',
 current_balance=self.engine.capital,
 total_trades=total_trades,
 win_trades=win_trades if total_trades > 0 else 0,
 total_profit=total_profit if total_trades > 0 else 0.0
)
 except Exception as e:
 logger.error(f"DatabaseUpdateFailed: {e}")
 
 # disconnectDatabaseConnection
 self.db.disconnect()
 
 logger.info("="*60)


def main():
 """主函数"""
 system = IntegratedTradingSystem()
 system.run()


if __name__ == "__main__":
 main()
