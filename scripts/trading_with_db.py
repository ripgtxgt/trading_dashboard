#!/usr/bin/env python3
"""
集成DatabaseTrade脚本示例
展示如何atTrade过程inRealtime写入数据toDatabase
"""

import sys
import time
from datetime import datetime
from db_integration import DatabaseIntegration


class TradingBotWithDB:
 """集成DatabaseTrade机器人"""
 
 def __init__(self, symbol="XBTUSDTM", initial_balance=10.0):
 """
 InitializeTrade机器人
 
 Args:
 symbol: Tradefor
 initial_balance: 初始资金
 """
 self.symbol = symbol
 self.balance = initial_balance
 self.initial_balance = initial_balance
 self.position = None # {"direction": "long/short", "entry_price": float, "quantity": float}
 
 # InitializeDatabase集成
 self.db = DatabaseIntegration()
 
 # InitializeaccountStatus
 self.db.update_account_state(
 balance=self.balance,
 profit_rate=0.0,
 stage="stage1",
 symbol=self.symbol,
)
 
 def open_position(self, direction: str, price: float, quantity: float):
 """
 开仓
 
 Args:
 direction: long or short
 price: 入场Price
 quantity: Amount
 """
 if self.position:
 print(f"[Trading] Already in position: {self.position['direction']}")
 return
 
 self.position = {
 "direction": direction,
 "entry_price": price,
 "quantity": quantity,
 "entry_time": datetime.now(),
 }
 
 # UpdateDatabasePosition
 self.db.update_position(
 symbol=self.symbol,
 direction=direction,
 entry_price=price,
 quantity=quantity,
 current_price=price,
)
 
 print(f"[Trading] Opened {direction} position at {price}, quantity={quantity}")
 
 def close_position(self, price: float):
 """
 Close position
 
 Args:
 price: 出场Price
 """
 if not self.position:
 print("[Trading] No position to close")
 return
 
 # CalculatePnL
 direction = self.position["direction"]
 entry_price = self.position["entry_price"]
 quantity = self.position["quantity"]
 
 if direction == "long":
 pnl = (price - entry_price) * quantity
 else: # short
 pnl = (entry_price - price) * quantity
 
 pnl_pct = (pnl / self.balance) * 100
 fee = abs(pnl) * 0.001 # 假设Fee0.1%
 net_pnl = pnl - fee
 
 # UpdateBalance
 self.balance += net_pnl
 profit_rate = ((self.balance - self.initial_balance) / self.initial_balance) * 100
 
 # SaveTradeRecordtoDatabase
 self.db.save_trade(
 symbol=self.symbol,
 direction=direction,
 entry_price=entry_price,
 exit_price=price,
 quantity=quantity,
 pnl=net_pnl,
 pnl_pct=pnl_pct,
 fee=fee,
 entry_time=self.position["entry_time"],
 exit_time=datetime.now(),
)
 
 # UpdatePositionas空
 self.db.update_position(
 symbol=self.symbol,
 direction=None,
 entry_price=None,
 quantity=None,
)
 
 # UpdateaccountStatus
 self.db.update_account_state(
 balance=self.balance,
 profit_rate=profit_rate,
 stage="stage1",
 symbol=self.symbol,
)
 
 print(f"[Trading] Closed {direction} position at {price}")
 print(f"[Trading] PnL: {net_pnl:.2f} USDT ({pnl_pct:.2f}%), Fee: {fee:.2f} USDT")
 print(f"[Trading] Balance: {self.balance:.2f} USDT, Total Profit: {profit_rate:.2f}%")
 
 # 清空Position
 self.position = None
 
 def update_position_price(self, current_price: float):
 """
 UpdatePositionCurrentPrice
 
 Args:
 current_price: CurrentPrice
 """
 if self.position:
 self.db.update_position(
 symbol=self.symbol,
 direction=self.position["direction"],
 entry_price=self.position["entry_price"],
 quantity=self.position["quantity"],
 current_price=current_price,
)
 
 def run_demo(self):
 """Running演示Trade"""
 print("=" * 50)
 print("Trading Bot with Database Integration Demo")
 print("=" * 50)
 
 # 模拟Trade序列
 print("\n[Demo] Starting trading simulation...")
 
 # 第一Trade：做多
 print("\n--- Trade 1: Long ---")
 self.open_position("long", 50000.0, 0.01)
 time.sleep(1)
 self.update_position_price(50500.0)
 time.sleep(1)
 self.close_position(51000.0)
 
 time.sleep(2)
 
 # 第二Trade：做空
 print("\n--- Trade 2: Short ---")
 self.open_position("short", 51000.0, 0.01)
 time.sleep(1)
 self.update_position_price(50800.0)
 time.sleep(1)
 self.close_position(50500.0)
 
 time.sleep(2)
 
 # 第三Trade：做多Loss
 print("\n--- Trade 3: Long (Loss) ---")
 self.open_position("long", 50500.0, 0.01)
 time.sleep(1)
 self.update_position_price(50200.0)
 time.sleep(1)
 self.close_position(50000.0)
 
 print("\n" + "=" * 50)
 print(f"Demo completed!")
 print(f"Final Balance: {self.balance:.2f} USDT")
 print(f"Total Profit: {((self.balance - self.initial_balance) / self.initial_balance) * 100:.2f}%")
 print("=" * 50)
 
 # closeDatabaseConnection
 self.db.close()


if __name__ == "__main__":
 # Running演示
 bot = TradingBotWithDB(symbol="XBTUSDTM", initial_balance=10.0)
 bot.run_demo()
