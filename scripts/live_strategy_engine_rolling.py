#!/usr/bin/env python3
"""
10U战神滚仓Strategy - 完整版实盘Execute引擎
版本: 3.0 Rolling Edition
集成滚仓管理器，实现真正滚仓Strategy
"""

import pandas as pd
import numpy as np
import json
import time
import logging
from datetime import datetime
from kucoin_trader import KuCoinTrader
from live_trading_config import STRATEGY_CONFIG, SIGNAL_CONFIG, SAFETY_CONFIG
from rolling_manager import RollingManager, Position


class LiveStrategyEngineRolling:
 """实盘StrategyExecute引擎 - 滚仓版"""
 
 def __init__(self, trader, initial_capital=None):
 """
 InitializeStrategy引擎
 
 Args:
 trader: KuCoinTrader实例
 initial_capital: 初始资金（如果None则fromaccount读取）
 """
 self.logger = logging.getLogger('StrategyEngine')
 self.trader = trader
 self.symbol = 'XBTUSDTM' # Tradefor
 
 # Get初始资金
 if initial_capital is None:
 balance = self.trader.get_balance()
 if isinstance(balance, dict):
 self.initial_capital = balance.get('total', 0)
 elif isinstance(balance, (int, float)):
 self.initial_capital = float(balance)
 else:
 self.initial_capital = 0
 else:
 self.initial_capital = initial_capital
 
 self.capital = self.initial_capital
 
 # 创建滚仓管理器
 self.rolling_manager = RollingManager(leverage=self.trader.leverage)
 self.rolling_manager.balance = self.capital
 
 # tryLoad之前Status
 try:
 self.rolling_manager.load_state()
 except:
 self.logger.info("NottoStatusStatus")
 
 # StrategyStatus
 self.is_running = False
 self.emergency_stopped = False
 self.last_check_time = 0
 self.check_interval = 60 # 检查间隔（second）
 
 # 统计Info
 self.daily_trades = 0
 self.daily_pnl = 0
 self.last_reset_date = datetime.now().date()
 
 # SignalAnalysis数据
 self.last_signal_analysis = None
 
 self.logger.info(f"StrategyInitializeComplete: ={self.capital:.2f}U")
 self.logger.info(f"Current: {self.rolling_manager.get_current_stage(self.capital).name}")
 
 def update_capital(self):
 """Update资金（fromaccountBalance）"""
 try:
 balance = self.trader.get_balance()
 if balance:
 if isinstance(balance, dict):
 self.capital = balance.get('total', 0)
 elif isinstance(balance, (int, float)):
 self.capital = float(balance)
 
 # 同步to滚仓管理器
 self.rolling_manager.balance = self.capital
 
 self.logger.debug(f"Update: {self.capital:.2f}U")
 return True
 return False
 except Exception as e:
 self.logger.error(f"UpdateFailed: {e}")
 return False
 
 def check_safety_limits(self):
 """检查safelimit"""
 # 检查Date
 today = datetime.now().date()
 if today!= self.last_reset_date:
 self.daily_trades = 0
 self.daily_pnl = 0
 self.last_reset_date = today
 self.logger.info("")
 
 # 检查滚仓管理器PauseStatus
 if self.rolling_manager.is_paused:
 self.logger.warning("[WARNING] AlreadyPauseconsecutiveLoss")
 return False
 
 # 检查dailyMaxTradecount
 if self.daily_trades >= SAFETY_CONFIG['max_daily_trades']:
 self.logger.warning(f"[WARNING] AlreadydailyMaxTradecount: {self.daily_trades}")
 return False
 
 # 检查dailyMaxLoss
 if self.daily_pnl <= -SAFETY_CONFIG['max_daily_loss']:
 self.logger.warning(f"[WARNING] AlreadydailyMaxLoss: {self.daily_pnl:.2f}U")
 return False
 
 # 检查MinBalance
 if self.capital < SAFETY_CONFIG['min_balance']:
 self.logger.warning(f"[WARNING] belowMinBalance: {self.capital:.2f}U")
 return False
 
 # 检查紧急Stop loss
 total_loss_pct = (self.capital - self.initial_capital) / self.initial_capital
 if total_loss_pct <= -SAFETY_CONFIG['emergency_stop_loss']:
 self.logger.error(f"[WARNING] triggerStop loss! Loss: {total_loss_pct*100:.2f}%")
 self.emergency_stopped = True
 return False
 
 return True
 
 def generate_signal(self, ohlcv_data):
 """
 生成TradeSignal
 
 Args:
 ohlcv_data: K线数据列表
 
 Returns:
 dict: {
 'signal': 'long'/'short'/None,
 'analysis': {详细Analysis数据}
 }
 """
 if not ohlcv_data or len(ohlcv_data) < SIGNAL_CONFIG['long_ma_period']:
 return None
 
 df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
 
 short_period = SIGNAL_CONFIG['short_ma_period']
 long_period = SIGNAL_CONFIG['long_ma_period']
 
 short_ma = df['close'].tail(short_period).mean()
 long_ma = df['close'].tail(long_period).mean()
 current_price = df['close'].iloc[-1]
 prev_short_ma = df['close'].tail(short_period + 1).head(short_period).mean()
 
 # 详细SignalAnalysis日志
 self.logger.info(f"[DATA] SignalAnalysis:")
 self.logger.info(f" CurrentPrice: {current_price:.2f}")
 self.logger.info(f" MA({short_period}): {short_ma:.2f}")
 self.logger.info(f" MA({long_period}): {long_ma:.2f}")
 self.logger.info(f" MA({short_period}): {prev_short_ma:.2f}")
 
 # 做多Signal检查
 long_cond1 = short_ma > long_ma
 long_cond2 = current_price > short_ma
 long_cond3 = short_ma > prev_short_ma
 self.logger.info(f" : MA={long_cond1}, Price>{short_period}MA={long_cond2}, MA={long_cond3}")
 
 if long_cond1 and long_cond2 and long_cond3:
 self.logger.info(f" Signal: MA={short_ma:.2f} > MA={long_ma:.2f}")
 return 'long'
 
 # 做空Signal检查
 short_cond1 = short_ma < long_ma
 short_cond2 = current_price < short_ma
 short_cond3 = short_ma < prev_short_ma
 self.logger.info(f" : MA={short_cond1}, Price<{short_period}MA={short_cond2}, MA={short_cond3}")
 
 if short_cond1 and short_cond2 and short_cond3:
 self.logger.info(f" Signal: MA={short_ma:.2f} < MA={long_ma:.2f}")
 return 'short'
 
 self.logger.info(f" : NoSignal")
 
 # 构建详细SignalAnalysis数据
 signal_type = None
 reason = ""
 
 if long_cond1 and long_cond2 and long_cond3:
 signal_type = 'long'
 reason = "所Has做多件满足，开仓做多"
 elif short_cond1 and short_cond2 and short_cond3:
 signal_type = 'short'
 reason = "所Has做空件满足，开仓做空"
 else:
 # Analysisas什么没HasSignal
 if not long_cond1 and not short_cond1:
 reason = "WaitMA交叉：MA5andMA20距离过近"
 elif long_cond1:
 if not long_cond2:
 reason = "WaitPrice突破：Price需要突破MA5"
 elif not long_cond3:
 reason = "WaittrendConfirm：MA5需要持续上升"
 elif short_cond1:
 if not short_cond2:
 reason = "WaitPrice突破：Price需要跌破MA5"
 elif not short_cond3:
 reason = "WaittrendConfirm：MA5需要持续下降"
 
 analysis = {
 'timestamp': int(time.time()),
 'price_data': {
 'current_price': float(current_price),
 'ma5': float(short_ma),
 'ma20': float(long_ma),
 'prev_ma5': float(prev_short_ma)
 },
 'long_conditions': {
 'ma_cross': bool(long_cond1),
 'price_confirm': bool(long_cond2),
 'trend_confirm': bool(long_cond3)
 },
 'short_conditions': {
 'ma_cross': bool(short_cond1),
 'price_confirm': bool(short_cond2),
 'trend_confirm': bool(short_cond3)
 },
 'decision': {
 'signal_type': signal_type if signal_type else 'none',
 'reason': reason
 }
 }
 
 return {
 'signal': signal_type,
 'analysis': analysis
 }
 
 def open_position(self, direction):
 """
 开仓（滚仓版）
 
 Args:
 direction: 'long' or 'short'
 """
 try:
 # ProcessdirectionParameter
 if isinstance(direction, dict):
 direction = direction.get('direction', direction)
 
 # 检查safelimit
 if not self.check_safety_limits():
 self.logger.warning("NotsafeCancel")
 return False
 
 # 检查is否AlreadyHasPosition
 if self.rolling_manager.current_position:
 self.logger.warning("AlreadyHasPositionnot")
 return False
 
 # Update资金
 self.update_capital()
 
 # 使用滚仓管理器CalculatePosition
 margin, size = self.rolling_manager.calculate_position_size(
 self.capital,
 self.trader.get_current_price()
)
 
 if margin <= 0 or size <= 0:
 self.logger.warning("PositionCalculateas0Cancel")
 return False
 
 # GetCurrentPrice
 entry_price = self.trader.get_current_price()
 if not entry_price:
 return False
 
 # Execute开仓
 if direction == 'long':
 order = self.trader.open_long(margin)
 else:
 order = self.trader.open_short(margin)
 
 if not order:
 return False
 
 # at滚仓管理器in创建PositionRecord
 position = self.rolling_manager.create_position(
 entry_price=entry_price,
 size=size,
 side=direction,
 margin=margin,
 balance=self.capital
)
 
 self.daily_trades += 1
 
 self.logger.info(f"[OK] Success: {direction.upper()} {size} @ {entry_price:.1f}, "
 f"保证金={margin:.2f}U, 阶段={position.stage}")
 
 # SaveStatus
 self.rolling_manager.save_state()
 
 return True
 
 except Exception as e:
 self.logger.error(f"Failed: {e}", exc_info=True)
 return False
 
 def check_add_position(self):
 """
 检查并Execute加仓
 """
 try:
 if not self.rolling_manager.current_position:
 return False
 
 # Update资金
 self.update_capital()
 
 # GetCurrentPrice并UpdatePnL
 current_price = self.trader.get_current_price()
 self.rolling_manager.update_position_pnl(current_price)
 
 # 检查is否should该加仓
 should_add, add_margin, reason = self.rolling_manager.should_add_position(self.capital)
 
 if not should_add:
 self.logger.debug(f"not: {reason}")
 return False
 
 self.logger.info(f" : {reason}")
 
 # Calculate加仓Amount
 add_size = int(add_margin * self.trader.leverage)
 
 if add_size <= 0:
 self.logger.warning("Amountas0Cancel")
 return False
 
 # Execute加仓
 pos = self.rolling_manager.current_position
 if pos.side == 'long':
 order = self.trader.open_long(add_margin)
 else:
 order = self.trader.open_short(add_margin)
 
 if not order:
 return False
 
 # Update滚仓管理器inPosition
 self.rolling_manager.add_position(current_price, add_size, add_margin)
 
 self.logger.info(f"[OK] Success: {add_size} @ {current_price:.1f}, "
 f"加仓保证金={add_margin:.2f}U")
 
 # SaveStatus
 self.rolling_manager.save_state()
 
 return True
 
 except Exception as e:
 self.logger.error(f"Failed: {e}", exc_info=True)
 return False
 
 def check_partial_close(self):
 """
 检查并Execute分批Close position
 """
 try:
 if not self.rolling_manager.current_position:
 return False
 
 # GetCurrentPrice并UpdatePnL
 current_price = self.trader.get_current_price()
 self.rolling_manager.update_position_pnl(current_price)
 
 # 检查is否should该分批Close position
 should_close, close_ratio, reason = self.rolling_manager.should_partial_close()
 
 if not should_close:
 return False
 
 self.logger.info(f"[DATA] Close position: {reason}")
 
 # Get实际Position
 positions = self.trader.get_positions()
 if not positions:
 self.logger.warning("APIQueryNoPosition")
 return False
 
 # CalculateClose positionAmount
 pos = self.rolling_manager.current_position
 close_size = int(pos.size * close_ratio)
 
 # Execute部分Close position
 for api_pos in positions:
 # Calculate要平Amount
 current_size = abs(api_pos.get('currentQty', 0))
 partial_size = int(current_size * close_ratio)
 
 if partial_size > 0:
 order = self.trader.close_position(api_pos, size=partial_size)
 if not order:
 return False
 
 # Update滚仓管理器
 record = self.rolling_manager.close_position(current_price, close_ratio)
 
 if record:
 self.daily_pnl += record['pnl']
 self.logger.info(f"[OK] Close positionSuccess: Close position{close_ratio*100:.0f}%, "
 f"PnL={record['pnl']:.2f}U ({record['pnl_ratio']*100:.1f}%)")
 
 # Update资金
 self.update_capital()
 
 # SaveStatus
 self.rolling_manager.save_state()
 
 return True
 
 return False
 
 except Exception as e:
 self.logger.error(f"Close positionFailed: {e}", exc_info=True)
 return False
 
 def check_stop_conditions(self):
 """
 检查Stop lossTake profit件
 
 Returns:
 (is否trigger, reason)
 """
 if not self.rolling_manager.current_position:
 return False, "NoPosition"
 
 try:
 # GetCurrentPrice
 current_price = self.trader.get_current_price()
 
 # UpdatePnL
 self.rolling_manager.update_position_pnl(current_price)
 
 # Update移动Stop loss
 self.rolling_manager.update_trailing_stop(current_price)
 
 # 检查Stop lossTake profit
 triggered, reason = self.rolling_manager.check_stop_conditions(current_price)
 
 return triggered, reason
 
 except Exception as e:
 self.logger.error(f"Stop lossTake profitFailed: {e}")
 return False, f"检查Failed: {e}"
 
 def close_position(self, reason='normal'):
 """
 Close position（滚仓版）
 
 Args:
 reason: Close positionreason
 """
 try:
 if not self.rolling_manager.current_position:
 self.logger.warning("HasPositionNoClose position")
 return False
 
 # Get实际Position
 positions = self.trader.get_positions()
 if not positions:
 self.logger.warning("APIQueryNoPositionRecord")
 self.rolling_manager.current_position = None
 return False
 
 # Close position所HasPosition
 for pos in positions:
 order = self.trader.close_position(pos)
 if not order:
 return False
 
 # GetClose positionPrice
 close_price = self.trader.get_current_price()
 
 # at滚仓管理器inRecordClose position
 record = self.rolling_manager.close_position(close_price, 1.0)
 
 if record:
 self.daily_pnl += record['pnl']
 self.daily_trades += 1
 
 self.logger.info(f"[OK] Close positionSuccess: {reason}, "
 f"PnL={record['pnl']:.2f}U ({record['pnl_ratio']*100:.1f}%), "
 f"持续Time={record['duration']/60:.1f}minute")
 
 # Update资金
 self.update_capital()
 
 # SaveStatus
 self.rolling_manager.save_state()
 
 return True
 
 return False
 
 except Exception as e:
 self.logger.error(f"Close positionFailed: {e}", exc_info=True)
 return False
 
 def run_cycle(self):
 """
 Running一Tradecycle
 
 Returns:
 Status字典
 """
 try:
 # Update资金
 self.update_capital()
 
 # 检查safelimit
 if not self.check_safety_limits():
 return {
 'status': 'paused',
 'reason': 'safelimit',
 'balance': self.capital
 }
 
 # 如果HasPosition，检查各种件
 if self.rolling_manager.current_position:
 # 1. 检查Stop lossTake profit
 triggered, reason = self.check_stop_conditions()
 if triggered:
 self.logger.info(f"triggerClose position: {reason}")
 self.close_position(reason)
 return {
 'status': 'closed',
 'reason': reason,
 'balance': self.capital
 }
 
 # 2. 检查分批Close position
 if self.check_partial_close():
 return {
 'status': 'partial_closed',
 'balance': self.capital
 }
 
 # 3. 检查加仓
 if self.check_add_position():
 return {
 'status': 'added',
 'balance': self.capital
 }
 
 return {
 'status': 'holding',
 'balance': self.capital,
 'position': self.rolling_manager.current_position.to_dict()
 }
 
 # 如果没HasPosition，检查开仓Signal
 else:
 # GetK线数据
 ohlcv = self.trader.get_klines(symbol=self.symbol, limit=30)
 if not ohlcv:
 return {
 'status': 'waiting',
 'reason': 'NoK线数据',
 'balance': self.capital
 }
 
 # 生成Signal
 signal_result = self.generate_signal(ohlcv)
 
 # SaveSignalAnalysis数据
 if signal_result and isinstance(signal_result, dict):
 signal = signal_result.get('signal')
 self.last_signal_analysis = signal_result.get('analysis')
 else:
 signal = signal_result
 self.last_signal_analysis = None
 
 if signal:
 self.logger.info(f"DetectedSignal: {signal}")
 if self.open_position(signal):
 return {
 'status': 'opened',
 'direction': signal,
 'balance': self.capital,
 'signal_analysis': self.last_signal_analysis
 }
 
 return {
 'status': 'waiting',
 'reason': 'NoSignal',
 'balance': self.capital,
 'signal_analysis': self.last_signal_analysis
 }
 
 except Exception as e:
 self.logger.error(f"RunningcycleFailed: {e}", exc_info=True)
 return {
 'status': 'error',
 'reason': str(e),
 'balance': self.capital
 }
 
 def get_status(self):
 """
 GetStrategyStatus
 
 Returns:
 Status字典
 """
 status = {
 'is_running': self.is_running,
 'emergency_stopped': self.emergency_stopped,
 'capital': self.capital,
 'initial_capital': self.initial_capital,
 'total_profit': self.capital - self.initial_capital,
 'total_profit_pct': (self.capital - self.initial_capital) / self.initial_capital * 100,
 'daily_trades': self.daily_trades,
 'daily_pnl': self.daily_pnl,
 'rolling_status': self.rolling_manager.get_status(),
 'current_stage': self.rolling_manager.get_current_stage(self.capital).name,
 'timestamp': datetime.now().isoformat()
 }
 
 return status
 
 def reset_emergency_stop(self):
 """重置紧急StopStatus"""
 self.emergency_stopped = False
 self.rolling_manager.reset_pause()
 self.logger.info("StopStatus")


if __name__ == '__main__':
 """测试代码"""
 print("=" * 60)
 print("10UStrategy - ")
 print("=" * 60)
 
 # 这里需要实际traderfor象才能测试
 print("KuCoinTraderforRunning")
 print("Pleaseatin")
