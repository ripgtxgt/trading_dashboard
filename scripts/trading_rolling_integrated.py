#!/usr/bin/env python3
"""
完整10U战神滚仓Strategy - 集成版本
整合Database同步andTelegramNotification功能

使用方法：
1. Configenv var：DATABASE_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
2. Running：python3 trading_rolling_integrated.py
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Optional, Dict, List

# 导入自定义模块
from db_sync import DatabaseSync
from telegram_notifier import TelegramNotifier

# Config日志
logging.basicConfig(
 level=logging.INFO,
 format='%(asctime)s - %(levelname)s - %(message)s',
 handlers=[
 logging.FileHandler(f'trading_rolling_{datetime.now().strftime("%Y%m%d")}.log'),
 logging.StreamHandler()
 ]
)
logger = logging.getLogger(__name__)


class TradingStrategy:
 """10U战神滚仓Strategy"""
 
 def __init__(self):
 self.symbol = "XBTUSDTM"
 self.initial_balance = 10.0 # 初始资金10U
 self.current_balance = self.initial_balance
 self.position = None # CurrentPosition
 self.trades_history = [] # TradeHistory
 
 # StrategyParameter
 self.short_ma_period = 5
 self.long_ma_period = 20
 self.timeframe = "1h"
 self.leverage = 10
 
 # 集成模块
 self.db = DatabaseSync()
 self.telegram = TelegramNotifier()
 
 # InitializeDatabaseStatus
 self._init_db_state()
 
 def _init_db_state(self):
 """InitializeDatabaseStatus"""
 try:
 # Update机器人Status
 self.db.update_bot_state(
 status='running',
 current_balance=self.current_balance,
 total_trades=0,
 win_trades=0,
 total_profit=0.0
)
 
 # 添加初始资金快照
 self.db.add_balance_snapshot(
 balance=self.current_balance,
 equity=self.current_balance,
 margin_used=0.0
)
 
 logger.info("DatabaseStatusInitializeSuccess")
 except Exception as e:
 logger.error(f"DatabaseInitializeFailed: {e}")
 
 def get_klines(self, limit=100) -> List[Dict]:
 """
 GetK线数据
 
 实际使用时，这里should该调用KuCoin APIGet真实数据
 示例代码保留模拟数据用at测试
 """
 # TODO: 替换as真实KuCoin API调用
 # 示例：使用ccxt库
 # import ccxt
 # exchange = ccxt.kucoin()
 # klines = exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
 
 # 模拟数据（测试用）
 base_price = 100000.0
 klines = []
 for i in range(limit):
 timestamp = int(time.time()) - (limit - i) * 3600
 price = base_price + (i * 100) + (i % 10 * 50)
 klines.append({
 'timestamp': timestamp,
 'open': price,
 'high': price + 100,
 'low': price - 100,
 'close': price + 50,
 'volume': 1000 + i * 10
 })
 
 return klines
 
 def calculate_ma(self, klines: List[Dict], period: int) -> float:
 """Calculate移动平均线"""
 if len(klines) < period:
 return 0.0
 
 closes = [k['close'] for k in klines[-period:]]
 return sum(closes) / len(closes)
 
 def generate_signal(self, klines: List[Dict]) -> Optional[str]:
 """
 生成TradeSignal
 
 返回：
 - 'long': 做多Signal
 - 'short': 做空Signal
 - None: NoSignal
 """
 if len(klines) < self.long_ma_period:
 return None
 
 current_price = klines[-1]['close']
 ma_short = self.calculate_ma(klines, self.short_ma_period)
 ma_long = self.calculate_ma(klines, self.long_ma_period)
 prev_ma_short = self.calculate_ma(klines[:-1], self.short_ma_period)
 
 # 做多件
 if (ma_short > ma_long and 
 current_price > ma_short and 
 ma_short > prev_ma_short):
 return 'long'
 
 # 做空件
 if (ma_short < ma_long and 
 current_price < ma_short and 
 ma_short < prev_ma_short):
 return 'short'
 
 return None
 
 def open_position(self, signal: str, price: float):
 """开仓"""
 if self.position is not None:
 logger.warning("AlreadyHasPositionNo")
 return
 
 # CalculatePosition
 margin = self.current_balance * 0.9 # 使用90%资金
 quantity = (margin * self.leverage) / price
 
 self.position = {
 'symbol': self.symbol,
 'side': signal,
 'entry_price': price,
 'quantity': quantity,
 'margin': margin,
 'leverage': self.leverage,
 'open_time': datetime.now()
 }
 
 logger.info(f"Success: {signal} @ {price}, Amount: {quantity:.4f}")
 
 # 同步toDatabase
 try:
 position_id = self.db.update_position(
 symbol=self.symbol,
 side=signal,
 entry_price=price,
 quantity=quantity,
 margin=margin,
 leverage=self.leverage
)
 self.position['db_id'] = position_id
 logger.info(f"PositionAlreadytoDatabaseID: {position_id}")
 except Exception as e:
 logger.error(f"PositionFailed: {e}")
 
 # SendTelegramNotification
 try:
 self.telegram.send_trade_opened(
 symbol=self.symbol,
 side=signal,
 price=price,
 quantity=quantity,
 margin=margin
)
 except Exception as e:
 logger.error(f"TelegramNotificationSendFailed: {e}")
 
 def close_position(self, price: float, reason: str = "Take profit/Stop loss"):
 """Close position"""
 if self.position is None:
 logger.warning("NoPositionNoClose position")
 return
 
 entry_price = self.position['entry_price']
 quantity = self.position['quantity']
 side = self.position['side']
 margin = self.position['margin']
 
 # CalculatePnL
 if side == 'long':
 pnl = (price - entry_price) * quantity
 else: # short
 pnl = (entry_price - price) * quantity
 
 pnl_percent = (pnl / margin) * 100
 
 # UpdateBalance
 self.current_balance += pnl
 
 # RecordTrade
 trade = {
 'symbol': self.symbol,
 'side': side,
 'entry_price': entry_price,
 'exit_price': price,
 'quantity': quantity,
 'pnl': pnl,
 'pnl_percent': pnl_percent,
 'open_time': self.position['open_time'],
 'close_time': datetime.now(),
 'reason': reason
 }
 self.trades_history.append(trade)
 
 logger.info(f"Close positionSuccess: {side} @ {price}, PnL: {pnl:.2f} ({pnl_percent:.2f}%)")
 
 # 同步toDatabase
 try:
 trade_id = self.db.add_trade(
 symbol=self.symbol,
 side=side,
 entry_price=entry_price,
 exit_price=price,
 quantity=quantity,
 pnl=pnl,
 pnl_percent=pnl_percent,
 open_time=self.position['open_time'],
 close_time=datetime.now()
)
 logger.info(f"TradeAlreadytoDatabaseID: {trade_id}")
 
 # Update机器人Status
 win_trades = sum(1 for t in self.trades_history if t['pnl'] > 0)
 total_profit = sum(t['pnl'] for t in self.trades_history)
 
 self.db.update_bot_state(
 status='running',
 current_balance=self.current_balance,
 total_trades=len(self.trades_history),
 win_trades=win_trades,
 total_profit=total_profit
)
 
 # 添加资金快照
 self.db.add_balance_snapshot(
 balance=self.current_balance,
 equity=self.current_balance,
 margin_used=0.0
)
 
 except Exception as e:
 logger.error(f"TradeFailed: {e}")
 
 # SendTelegramNotification
 try:
 self.telegram.send_trade_closed(
 symbol=self.symbol,
 side=side,
 entry_price=entry_price,
 exit_price=price,
 pnl=pnl,
 pnl_percent=pnl_percent
)
 except Exception as e:
 logger.error(f"TelegramNotificationSendFailed: {e}")
 
 # 清空Position
 self.position = None
 
 def check_stop_loss(self, current_price: float) -> bool:
 """检查Stop loss"""
 if self.position is None:
 return False
 
 entry_price = self.position['entry_price']
 side = self.position['side']
 
 # Stop loss比例：10%
 stop_loss_percent = 0.10
 
 if side == 'long':
 stop_price = entry_price * (1 - stop_loss_percent)
 if current_price <= stop_price:
 logger.warning(f"triggerStop loss: {current_price} <= {stop_price}")
 self.close_position(current_price, "Stop loss")
 return True
 else: # short
 stop_price = entry_price * (1 + stop_loss_percent)
 if current_price >= stop_price:
 logger.warning(f"triggerStop loss: {current_price} >= {stop_price}")
 self.close_position(current_price, "Stop loss")
 return True
 
 return False
 
 def check_take_profit(self, current_price: float) -> bool:
 """检查Take profit"""
 if self.position is None:
 return False
 
 entry_price = self.position['entry_price']
 side = self.position['side']
 
 # Take profit比例：20%
 take_profit_percent = 0.20
 
 if side == 'long':
 take_price = entry_price * (1 + take_profit_percent)
 if current_price >= take_price:
 logger.info(f"triggerTake profit: {current_price} >= {take_price}")
 self.close_position(current_price, "Take profit")
 return True
 else: # short
 take_price = entry_price * (1 - take_profit_percent)
 if current_price <= take_price:
 logger.info(f"triggerTake profit: {current_price} <= {take_price}")
 self.close_position(current_price, "Take profit")
 return True
 
 return False
 
 def run_cycle(self, cycle_num: int):
 """Running一Tradecycle"""
 logger.info(f"\n{'='*50}")
 logger.info(f"cycle #{cycle_num} Begin")
 logger.info(f"CurrentBalance: {self.current_balance:.2f} USDT")
 
 # GetK线数据
 klines = self.get_klines(limit=100)
 current_price = klines[-1]['close']
 
 logger.info(f"CurrentPrice: {current_price:.2f}")
 
 # 检查Stop lossTake profit
 if self.position:
 if self.check_stop_loss(current_price):
 return
 if self.check_take_profit(current_price):
 return
 
 # 生成TradeSignal
 signal = self.generate_signal(klines)
 
 if signal and self.position is None:
 logger.info(f"DetectedSignal: {signal}")
 self.open_position(signal, current_price)
 elif signal is None and self.position is None:
 logger.info("NoTradeSignal")
 elif self.position:
 logger.info(f"Positionin: {self.position['side']} @ {self.position['entry_price']:.2f}")
 
 def run(self, max_cycles: Optional[int] = None):
 """
 RunningStrategy主循环
 
 Parameter：
 - max_cycles: MaxRunningcycle数，None表示No限Running
 """
 logger.info("="*60)
 logger.info("10UStrategy - Start")
 logger.info("="*60)
 logger.info(f"Tradefor: {self.symbol}")
 logger.info(f": {self.initial_balance} USDT")
 logger.info(f": {self.leverage}x")
 logger.info(f"MAParameter: {self.short_ma_period}/{self.long_ma_period}")
 logger.info(f"Time: {self.timeframe}")
 logger.info("="*60)
 
 # SendStartNotification
 try:
 self.telegram.send_bot_status(
 status="Start",
 balance=self.current_balance,
 total_trades=0,
 win_rate=0.0
)
 except Exception as e:
 logger.error(f"TelegramNotificationSendFailed: {e}")
 
 cycle_num = 0
 
 try:
 while True:
 cycle_num += 1
 
 # Running一cycle
 self.run_cycle(cycle_num)
 
 # 检查is否reachMaxcycle数
 if max_cycles and cycle_num >= max_cycles:
 logger.info(f"reachMaxcycle {max_cycles}StopRunning")
 break
 
 # Wait下一cycle（1hour）
 # 实际使用时根据timeframeadjust
 sleep_seconds = 3600 # 1hour
 logger.info(f"Wait {sleep_seconds} second...")
 time.sleep(sleep_seconds)
 
 except KeyboardInterrupt:
 logger.info("\nreceivedstop signalprocessingExit...")
 except Exception as e:
 logger.error(f"Runningerror occurred: {e}", exc_info=True)
 # SendErrorNotification
 try:
 self.telegram.send_risk_alert(
 level="严重",
 message="StrategyRunningerror occurred",
 details=str(e)
)
 except:
 pass
 finally:
 self.shutdown()
 
 def shutdown(self):
 """closeStrategy"""
 logger.info("="*60)
 logger.info("StrategyStop")
 logger.info("="*60)
 
 # 如果HasPosition，Close position
 if self.position:
 klines = self.get_klines(limit=10)
 current_price = klines[-1]['close']
 logger.info("DetectedPositionExecuteClose position...")
 self.close_position(current_price, "StrategyStop")
 
 # 打印统计Info
 total_trades = len(self.trades_history)
 if total_trades > 0:
 win_trades = sum(1 for t in self.trades_history if t['pnl'] > 0)
 win_rate = (win_trades / total_trades) * 100
 total_profit = sum(t['pnl'] for t in self.trades_history)
 
 logger.info(f"Tradecount: {total_trades}")
 logger.info(f"count: {win_trades}")
 logger.info(f"Win rate: {win_rate:.2f}%")
 logger.info(f"PnL: {total_profit:.2f} USDT")
 logger.info(f"finalBalance: {self.current_balance:.2f} USDT")
 logger.info(f"return rate: {((self.current_balance - self.initial_balance) / self.initial_balance * 100):.2f}%")
 
 # Send每日统计
 try:
 self.telegram.send_daily_summary(
 total_trades=total_trades,
 win_trades=win_trades,
 win_rate=win_rate,
 total_pnl=total_profit,
 current_balance=self.current_balance
)
 except Exception as e:
 logger.error(f"TelegramNotificationSendFailed: {e}")
 
 # UpdateDatabaseStatus
 try:
 self.db.update_bot_state(
 status='stopped',
 current_balance=self.current_balance,
 total_trades=total_trades,
 win_trades=win_trades if total_trades > 0 else 0,
 total_profit=total_profit if total_trades > 0 else 0.0
)
 except Exception as e:
 logger.error(f"DatabaseUpdateFailed: {e}")
 
 logger.info("="*60)


def main():
 """主函数"""
 # 检查env var
 required_vars = ['DATABASE_URL']
 missing_vars = [var for var in required_vars if not os.getenv(var)]
 
 if missing_vars:
 logger.error(f"missingrequiredenv var: {', '.join(missing_vars)}")
 logger.error("PleaseSetfollowingenv var")
 logger.error(" DATABASE_URL - MySQLDatabaseConnection")
 logger.error(" TELEGRAM_BOT_TOKEN - Telegram Bot Tokenoptional")
 logger.error(" TELEGRAM_CHAT_ID - Telegram Chat IDoptional")
 sys.exit(1)
 
 # 创建Strategy实例
 strategy = TradingStrategy()
 
 # RunningStrategy
 # Parameter：max_cycles=None 表示No限Running
 # 测试时可以Setas较小数字，例如 max_cycles=10
 strategy.run(max_cycles=None)


if __name__ == "__main__":
 main()
