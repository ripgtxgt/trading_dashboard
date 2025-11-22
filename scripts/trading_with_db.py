#!/usr/bin/env python3
"""
集成数据库的交易脚本示例
展示如何在交易过程中实时写入数据到数据库
"""

import sys
import time
from datetime import datetime
from db_integration import DatabaseIntegration


class TradingBotWithDB:
    """集成数据库的交易机器人"""
    
    def __init__(self, symbol="XBTUSDTM", initial_balance=10.0):
        """
        初始化交易机器人
        
        Args:
            symbol: 交易对
            initial_balance: 初始资金
        """
        self.symbol = symbol
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.position = None  # {"direction": "long/short", "entry_price": float, "quantity": float}
        
        # 初始化数据库集成
        self.db = DatabaseIntegration()
        
        # 初始化账户状态
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
            direction: long 或 short
            price: 入场价格
            quantity: 数量
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
        
        # 更新数据库持仓
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
        平仓
        
        Args:
            price: 出场价格
        """
        if not self.position:
            print("[Trading] No position to close")
            return
        
        # 计算盈亏
        direction = self.position["direction"]
        entry_price = self.position["entry_price"]
        quantity = self.position["quantity"]
        
        if direction == "long":
            pnl = (price - entry_price) * quantity
        else:  # short
            pnl = (entry_price - price) * quantity
        
        pnl_pct = (pnl / self.balance) * 100
        fee = abs(pnl) * 0.001  # 假设手续费0.1%
        net_pnl = pnl - fee
        
        # 更新余额
        self.balance += net_pnl
        profit_rate = ((self.balance - self.initial_balance) / self.initial_balance) * 100
        
        # 保存交易记录到数据库
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
        
        # 更新持仓为空
        self.db.update_position(
            symbol=self.symbol,
            direction=None,
            entry_price=None,
            quantity=None,
        )
        
        # 更新账户状态
        self.db.update_account_state(
            balance=self.balance,
            profit_rate=profit_rate,
            stage="stage1",
            symbol=self.symbol,
        )
        
        print(f"[Trading] Closed {direction} position at {price}")
        print(f"[Trading] PnL: {net_pnl:.2f} USDT ({pnl_pct:.2f}%), Fee: {fee:.2f} USDT")
        print(f"[Trading] Balance: {self.balance:.2f} USDT, Total Profit: {profit_rate:.2f}%")
        
        # 清空持仓
        self.position = None
    
    def update_position_price(self, current_price: float):
        """
        更新持仓当前价格
        
        Args:
            current_price: 当前价格
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
        """运行演示交易"""
        print("=" * 50)
        print("Trading Bot with Database Integration Demo")
        print("=" * 50)
        
        # 模拟交易序列
        print("\n[Demo] Starting trading simulation...")
        
        # 第一笔交易：做多
        print("\n--- Trade 1: Long ---")
        self.open_position("long", 50000.0, 0.01)
        time.sleep(1)
        self.update_position_price(50500.0)
        time.sleep(1)
        self.close_position(51000.0)
        
        time.sleep(2)
        
        # 第二笔交易：做空
        print("\n--- Trade 2: Short ---")
        self.open_position("short", 51000.0, 0.01)
        time.sleep(1)
        self.update_position_price(50800.0)
        time.sleep(1)
        self.close_position(50500.0)
        
        time.sleep(2)
        
        # 第三笔交易：做多亏损
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
        
        # 关闭数据库连接
        self.db.close()


if __name__ == "__main__":
    # 运行演示
    bot = TradingBotWithDB(symbol="XBTUSDTM", initial_balance=10.0)
    bot.run_demo()
