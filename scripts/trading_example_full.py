#!/usr/bin/env python3
"""
完整Trade机器人示例 - 集成Database同步
这is一完整可Running示例，展示如何willdb_sync模块集成to你Trade脚本in
"""

import os
import sys
import time
import requests
from datetime import datetime
from db_sync import DatabaseSync

# TradeConfig
SYMBOL = "XBTUSDTM"
INITIAL_CAPITAL = 10.0 # 初始资金 10 USDT
LEVERAGE = 10 # 杠杆倍数
SHORT_MA = 5 # 短期均线
LONG_MA = 20 # 长期均线
TIMEFRAME = "1hour" # Time框架

# KuCoin APIConfig
KUCOIN_API_BASE = "https://api-futures.kucoin.com"

class TradingBot:
 def __init__(self):
 self.db = DatabaseSync()
 self.db.connect()
 
 self.capital = INITIAL_CAPITAL
 self.initial_capital = INITIAL_CAPITAL
 self.current_stage = "stage1"
 self.position = None
 self.trades_count = 0
 self.win_count = 0
 
 print(f"[{datetime.now()}] TradeInitializeComplete")
 print(f": {INITIAL_CAPITAL} USDT")
 print(f": {LEVERAGE}x")
 print(f"Strategy: MA{SHORT_MA}/MA{LONG_MA}")
 
 def get_klines(self, limit=100):
 """GetK线数据"""
 try:
 end_time = int(time.time())
 start_time = end_time - 24 * 60 * 60 # 最近24hour
 
 url = f"{KUCOIN_API_BASE}/api/v1/kline/query"
 params = {
 "symbol": SYMBOL,
 "granularity": 60, # 1minute
 "from": start_time * 1000,
 "to": end_time * 1000
 }
 
 response = requests.get(url, params=params, timeout=10)
 if response.status_code == 200:
 data = response.json()
 if data.get("code") == "200000":
 return data.get("data", [])
 
 print(f"[Warning] GetKFailed")
 return self._generate_mock_klines(limit)
 
 except Exception as e:
 print(f"[Error] GetK: {e}")
 return self._generate_mock_klines(limit)
 
 def _generate_mock_klines(self, limit=100):
 """生成模拟K线数据"""
 import random
 base_price = 50000
 klines = []
 
 for i in range(limit):
 timestamp = int(time.time()) - (limit - i) * 60
 price = base_price + random.uniform(-1000, 1000)
 klines.append({
 "time": timestamp * 1000,
 "open": price,
 "high": price + random.uniform(0, 100),
 "low": price - random.uniform(0, 100),
 "close": price + random.uniform(-50, 50),
 "volume": random.uniform(1000, 10000)
 })
 
 return klines
 
 def calculate_ma(self, klines, period):
 """Calculate移动平均线"""
 if len(klines) < period:
 return None
 
 closes = []
 for k in klines[-period:]:
 if isinstance(k, dict):
 closes.append(float(k.get("close", 0)))
 else:
 closes.append(float(k[2])) # [time, open, close, high, low, volume]
 
 return sum(closes) / period
 
 def check_signal(self, klines):
 """检查TradeSignal"""
 if len(klines) < LONG_MA:
 return None
 
 ma_short = self.calculate_ma(klines, SHORT_MA)
 ma_long = self.calculate_ma(klines, LONG_MA)
 
 if ma_short is None or ma_long is None:
 return None
 
 # 金叉：短期均线上穿长期均线 -> BuySignal
 if ma_short > ma_long:
 prev_ma_short = self.calculate_ma(klines[:-1], SHORT_MA)
 prev_ma_long = self.calculate_ma(klines[:-1], LONG_MA)
 
 if prev_ma_short and prev_ma_long and prev_ma_short <= prev_ma_long:
 return "long"
 
 # 死叉：短期均线下穿长期均线 -> SellSignal
 if ma_short < ma_long:
 prev_ma_short = self.calculate_ma(klines[:-1], SHORT_MA)
 prev_ma_long = self.calculate_ma(klines[:-1], LONG_MA)
 
 if prev_ma_short and prev_ma_long and prev_ma_short >= prev_ma_long:
 return "short"
 
 return None
 
 def open_position(self, side, price):
 """开仓"""
 try:
 # CalculatePosition大小
 margin = self.capital * 0.1 # 使用10%资金作as保证金
 quantity = (margin * LEVERAGE) / price
 
 # 创建TradeRecord
 trade_id = self.db.create_trade(
 symbol=SYMBOL,
 side=side,
 entry_price=price,
 quantity=quantity,
 leverage=LEVERAGE,
 stage=self.current_stage
)
 
 self.position = {
 "trade_id": trade_id,
 "side": side,
 "entry_price": price,
 "quantity": quantity,
 "margin": margin
 }
 
 print(f"[{datetime.now()}] Success")
 print(f" : {side}")
 print(f" Price: {price:.2f}")
 print(f" Amount: {quantity:.6f}")
 print(f" : {margin:.2f} USDT")
 
 return True
 
 except Exception as e:
 print(f"[Error] Failed: {e}")
 return False
 
 def close_position(self, price):
 """Close position"""
 if not self.position:
 return False
 
 try:
 side = self.position["side"]
 entry_price = self.position["entry_price"]
 quantity = self.position["quantity"]
 margin = self.position["margin"]
 
 # CalculatePnL
 if side == "long":
 pnl = (price - entry_price) * quantity
 else:
 pnl = (entry_price - price) * quantity
 
 pnl_pct = pnl / margin
 
 # Update资金
 self.capital += pnl
 self.trades_count += 1
 
 if pnl > 0:
 self.win_count += 1
 
 # closeTradeRecord
 self.db.close_trade(
 trade_id=self.position["trade_id"],
 exit_price=price,
 pnl=pnl,
 pnl_pct=pnl_pct
)
 
 print(f"[{datetime.now()}] Close positionSuccess")
 print(f" : {side}")
 print(f" : {entry_price:.2f}")
 print(f" : {price:.2f}")
 print(f" PnL: {pnl:.2f} USDT ({pnl_pct*100:.2f}%)")
 print(f" Current: {self.capital:.2f} USDT")
 
 self.position = None
 return True
 
 except Exception as e:
 print(f"[Error] Close positionFailed: {e}")
 return False
 
 def update_state(self):
 """Update机器人StatustoDatabase"""
 try:
 self.db.update_bot_state(
 is_running=1,
 capital=self.capital,
 initial_capital=self.initial_capital,
 current_stage=self.current_stage,
 total_profit=self.capital - self.initial_capital,
 total_trades=self.trades_count,
 win_trades=self.win_count
)
 
 # SaveBalanceHistory
 self.db.save_balance_snapshot(self.capital)
 
 except Exception as e:
 print(f"[Error] UpdateStatusFailed: {e}")
 
 def run(self):
 """RunningTrade循环"""
 print(f"\n[{datetime.now()}] BeginRunningTrade...")
 print("=" * 60)
 
 cycle = 0
 
 try:
 while True:
 cycle += 1
 print(f"\n[cycle {cycle}] {datetime.now()}")
 
 # GetK线数据
 klines = self.get_klines(100)
 
 if not klines:
 print(" NoGetKcycle")
 time.sleep(60)
 continue
 
 # K线数据可能islistordict格式
 last_kline = klines[-1]
 if isinstance(last_kline, dict):
 current_price = float(last_kline.get("close", 0))
 else:
 current_price = float(last_kline[2]) # [time, open, close, high, low, volume]
 print(f" CurrentPrice: {current_price:.2f}")
 print(f" Current: {self.capital:.2f} USDT")
 
 # 检查is否HasPosition
 if self.position:
 print(f" Positionin: {self.position['side']} @ {self.position['entry_price']:.2f}")
 
 # 检查Close positionSignal
 signal = self.check_signal(klines)
 
 # 如果SignalandPosition方向相反，Close position
 if signal and signal!= self.position["side"]:
 print(f" DetectedSignal: {signal}")
 self.close_position(current_price)
 else:
 print(" NoClose positionSignalPosition")
 
 else:
 # 检查开仓Signal
 signal = self.check_signal(klines)
 
 if signal:
 print(f" DetectedSignal: {signal}")
 self.open_position(signal, current_price)
 else:
 print(" NoSignal")
 
 # UpdateStatustoDatabase
 self.update_state()
 
 # 每10cycle输出一times统计
 if cycle % 10 == 0:
 win_rate = (self.win_count / self.trades_count * 100) if self.trades_count > 0 else 0
 profit_rate = ((self.capital - self.initial_capital) / self.initial_capital * 100)
 
 print("\n" + "=" * 60)
 print(f"Info (cycle {cycle})")
 print(f" Tradecount: {self.trades_count}")
 print(f" count: {self.win_count}")
 print(f" Win rate: {win_rate:.2f}%")
 print(f" : {self.capital - self.initial_capital:.2f} USDT")
 print(f" return rate: {profit_rate:.2f}%")
 print("=" * 60)
 
 # Wait下一cycle（1minute）
 time.sleep(60)
 
 except KeyboardInterrupt:
 print(f"\n[{datetime.now()}] receivedstop signalprocessingclose...")
 
 # 如果HasPosition，先Close position
 if self.position:
 klines = self.get_klines(100)
 if klines:
 # K线数据可能islistordict格式
 last_kline = klines[-1]
 if isinstance(last_kline, dict):
 current_price = float(last_kline.get("close", 0))
 else:
 current_price = float(last_kline[2]) # [time, open, close, high, low, volume]
 self.close_position(current_price)
 
 # UpdateStatusasStop
 self.db.update_bot_state(
 is_running=0,
 capital=self.capital,
 initial_capital=self.initial_capital,
 current_stage=self.current_stage,
 total_profit=self.capital - self.initial_capital,
 total_trades=self.trades_count,
 win_trades=self.win_count
)
 
 print(f"[{datetime.now()}] AlreadyStop")
 
 finally:
 if hasattr(self.db, 'close'):
 self.db.close()

if __name__ == "__main__":
 # 检查env var
 if not os.getenv("DATABASE_URL"):
 print("Error: NotSet DATABASE_URL env var")
 print("PleaseSet: export DATABASE_URL='mysql://user:pass@host:port/dbname'")
 sys.exit(1)
 
 # 创建并Running机器人
 bot = TradingBot()
 bot.run()
