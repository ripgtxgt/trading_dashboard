#!/usr/bin/env python3
"""
完整的交易机器人示例 - 集成数据库同步
这是一个完整的可运行示例, 展示如何将db_sync模块集成到你的交易脚本中
"""

import os
import sys
import time
import requests
from datetime import datetime
from db_sync import DatabaseSync

# 交易配置
SYMBOL = "XBTUSDTM"
INITIAL_CAPITAL = 10.0  # 初始资金 10 USDT
LEVERAGE = 10  # 杠杆倍数
SHORT_MA = 5  # 短期均线
LONG_MA = 20  # 长期均线
TIMEFRAME = "1hour"  # 时间框架

# KuCoin API配置
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
        print(f"Capital: {INITIAL_CAPITAL} USDT")
        print(f": {LEVERAGE}x")
        print(f": MA{SHORT_MA}/MA{LONG_MA}")
        
    def get_klines(self, limit=100):
        """获取K线数据"""
        try:
            end_time = int(time.time())
            start_time = end_time - 24 * 60 * 60  # 最近24小时
            
            url = f"{KUCOIN_API_BASE}/api/v1/kline/query"
            params = {
                "symbol": SYMBOL,
                "granularity": 60,  # 1分钟
                "from": start_time * 1000,
                "to": end_time * 1000
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "200000":
                    return data.get("data", [])
            
            print(f"[Warning] GetKFailed, ")
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
        """计算移动平均线"""
        if len(klines) < period:
            return None
        
        closes = []
        for k in klines[-period:]:
            if isinstance(k, dict):
                closes.append(float(k.get("close", 0)))
            else:
                closes.append(float(k[2]))  # [time, open, close, high, low, volume]
        
        return sum(closes) / period
    
    def check_signal(self, klines):
        """检查交易信号"""
        if len(klines) < LONG_MA:
            return None
        
        ma_short = self.calculate_ma(klines, SHORT_MA)
        ma_long = self.calculate_ma(klines, LONG_MA)
        
        if ma_short is None or ma_long is None:
            return None
        
        # 金叉: 短期均线上穿长期均线 -> 买入信号
        if ma_short > ma_long:
            prev_ma_short = self.calculate_ma(klines[:-1], SHORT_MA)
            prev_ma_long = self.calculate_ma(klines[:-1], LONG_MA)
            
            if prev_ma_short and prev_ma_long and prev_ma_short <= prev_ma_long:
                return "long"
        
        # 死叉: 短期均线下穿长期均线 -> 卖出信号
        if ma_short < ma_long:
            prev_ma_short = self.calculate_ma(klines[:-1], SHORT_MA)
            prev_ma_long = self.calculate_ma(klines[:-1], LONG_MA)
            
            if prev_ma_short and prev_ma_long and prev_ma_short >= prev_ma_long:
                return "short"
        
        return None
    
    def open_position(self, side, price):
        """开仓"""
        try:
            # 计算仓位大小
            margin = self.capital * 0.1  # 使用10%资金作为保证金
            quantity = (margin * LEVERAGE) / price
            
            # 创建交易记录
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
            
            print(f"[{datetime.now()}] Open positionSuccess")
            print(f"  : {side}")
            print(f"  Price: {price:.2f}")
            print(f"  Amount: {quantity:.6f}")
            print(f"  : {margin:.2f} USDT")
            
            return True
            
        except Exception as e:
            print(f"[Error] Open positionFailed: {e}")
            return False
    
    def close_position(self, price):
        """平仓"""
        if not self.position:
            return False
        
        try:
            side = self.position["side"]
            entry_price = self.position["entry_price"]
            quantity = self.position["quantity"]
            margin = self.position["margin"]
            
            # 计算盈亏
            if side == "long":
                pnl = (price - entry_price) * quantity
            else:
                pnl = (entry_price - price) * quantity
            
            pnl_pct = pnl / margin
            
            # 更新资金
            self.capital += pnl
            self.trades_count += 1
            
            if pnl > 0:
                self.win_count += 1
            
            # 关闭交易记录
            self.db.close_trade(
                trade_id=self.position["trade_id"],
                exit_price=price,
                pnl=pnl,
                pnl_pct=pnl_pct
            )
            
            print(f"[{datetime.now()}] Close positionSuccess")
            print(f"  : {side}")
            print(f"  : {entry_price:.2f}")
            print(f"  : {price:.2f}")
            print(f"  : {pnl:.2f} USDT ({pnl_pct*100:.2f}%)")
            print(f"  CurrentCapital: {self.capital:.2f} USDT")
            
            self.position = None
            return True
            
        except Exception as e:
            print(f"[Error] Close positionFailed: {e}")
            return False
    
    def update_state(self):
        """更新机器人状态到数据库"""
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
            
            # 保存余额历史
            self.db.save_balance_snapshot(self.capital)
            
        except Exception as e:
            print(f"[Error] UpdateFailed: {e}")
    
    def run(self):
        """运行交易循环"""
        print(f"\n[{datetime.now()}] StartRunningTrade...")
        print("=" * 60)
        
        cycle = 0
        
        try:
            while True:
                cycle += 1
                print(f"\n[Period {cycle}] {datetime.now()}")
                
                # 获取K线数据
                klines = self.get_klines(100)
                
                if not klines:
                    print("  CannotGetK, Period")
                    time.sleep(60)
                    continue
                
                # K线数据可能是list或dict格式
                last_kline = klines[-1]
                if isinstance(last_kline, dict):
                    current_price = float(last_kline.get("close", 0))
                else:
                    current_price = float(last_kline[2])  # [time, open, close, high, low, volume]
                print(f"  CurrentPrice: {current_price:.2f}")
                print(f"  CurrentCapital: {self.capital:.2f} USDT")
                
                # 检查是否有持仓
                if self.position:
                    print(f"  Position: {self.position['side']} @ {self.position['entry_price']:.2f}")
                    
                    # 检查平仓信号
                    signal = self.check_signal(klines)
                    
                    # 如果信号与持仓方向相反, 平仓
                    if signal and signal != self.position["side"]:
                        print(f"  : {signal}")
                        self.close_position(current_price)
                    else:
                        print("  Close position, Position")
                
                else:
                    # 检查开仓信号
                    signal = self.check_signal(klines)
                    
                    if signal:
                        print(f"  Open position: {signal}")
                        self.open_position(signal, current_price)
                    else:
                        print("  ")
                
                # 更新状态到数据库
                self.update_state()
                
                # 每10个周期输出一次统计
                if cycle % 10 == 0:
                    win_rate = (self.win_count / self.trades_count * 100) if self.trades_count > 0 else 0
                    profit_rate = ((self.capital - self.initial_capital) / self.initial_capital * 100)
                    
                    print("\n" + "=" * 60)
                    print(f"Info (Period {cycle})")
                    print(f"  Trade: {self.trades_count}")
                    print(f"  Profit: {self.win_count}")
                    print(f"  : {win_rate:.2f}%")
                    print(f"  Profit: {self.capital - self.initial_capital:.2f} USDT")
                    print(f"  : {profit_rate:.2f}%")
                    print("=" * 60)
                
                # 等待下一个周期(1分钟)
                time.sleep(60)
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Stop, In progress...")
            
            # 如果有持仓, 先平仓
            if self.position:
                klines = self.get_klines(100)
                if klines:
                    # K线数据可能是list或dict格式
                    last_kline = klines[-1]
                    if isinstance(last_kline, dict):
                        current_price = float(last_kline.get("close", 0))
                    else:
                        current_price = float(last_kline[2])  # [time, open, close, high, low, volume]
                    self.close_position(current_price)
            
            # 更新状态为停止
            self.db.update_bot_state(
                is_running=0,
                capital=self.capital,
                initial_capital=self.initial_capital,
                current_stage=self.current_stage,
                total_profit=self.capital - self.initial_capital,
                total_trades=self.trades_count,
                win_trades=self.win_count
            )
            
            print(f"[{datetime.now()}] Stop")
            
        finally:
            if hasattr(self.db, 'close'):
                self.db.close()

if __name__ == "__main__":
    # 检查环境变量
    if not os.getenv("DATABASE_URL"):
        print("Error: Not DATABASE_URL ")
        print("Please: export DATABASE_URL='mysql://user:pass@host:port/dbname'")
        sys.exit(1)
    
    # 创建并运行机器人
    bot = TradingBot()
    bot.run()
