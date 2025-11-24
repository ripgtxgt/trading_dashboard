#!/usr/bin/env python3
"""
参数回测器 - 基于历史数据回测策略表现
"""
import sys
import json
from signal_simulator import SignalSimulator
from typing import List, Dict

class Backtester:
    def __init__(self):
        self.simulator = SignalSimulator("", "", "")
    
    def backtest_strategy(
        self,
        symbol: str,
        timeframe: str,
        short_ma: int,
        long_ma: int,
        sensitivity: str,
        initial_capital: float = 100.0,
        leverage: int = 100,
        position_size_pct: float = 0.5
    ) -> Dict:
        """
        回测策略
        
        Args:
            symbol: 交易对
            timeframe: 时间框架
            short_ma: 短期MA周期
            long_ma: 长期MA周期
            sensitivity: 灵敏度
            initial_capital: 初始资金
            leverage: 杠杆倍数
            position_size_pct: 仓位比例
        
        Returns:
            回测结果字典
        """
        # 获取K线数据
        klines = self.simulator.get_klines(symbol, timeframe, limit=200)
        
        if not klines:
            return {"error": "Failed to fetch klines"}
        
        # 生成信号
        total, long_count, short_count, signals = self.simulator.generate_signals(
            klines, short_ma, long_ma, sensitivity
        )
        
        if not signals:
            return {
                "totalTrades": 0,
                "winningTrades": 0,
                "winRate": 0,
                "totalPnl": 0,
                "totalPnlPct": 0,
                "avgPnl": 0,
                "maxDrawdown": 0,
                "sharpeRatio": 0,
                "signals": []
            }
        
        # 模拟交易
        capital = initial_capital
        trades = []
        current_position = None
        max_capital = initial_capital
        max_drawdown = 0
        
        for i, signal in enumerate(signals):
            signal_type = signal["type"]
            price = signal["price"]
            
            # 如果有持仓, 先平仓
            if current_position:
                exit_price = price
                entry_price = current_position["entry_price"]
                direction = current_position["direction"]
                margin = current_position["margin"]
                
                # 计算盈亏
                if direction == "long":
                    pnl_pct = (exit_price - entry_price) / entry_price
                else:
                    pnl_pct = (entry_price - exit_price) / entry_price
                
                pnl = margin * pnl_pct * leverage
                capital += pnl
                
                trades.append({
                    "direction": direction,
                    "entryPrice": entry_price,
                    "exitPrice": exit_price,
                    "margin": margin,
                    "pnl": pnl,
                    "pnlPct": pnl_pct * 100,
                    "capital": capital
                })
                
                # 更新最大资金和最大回撤
                if capital > max_capital:
                    max_capital = capital
                
                drawdown = (max_capital - capital) / max_capital * 100
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                
                current_position = None
            
            # 开新仓
            if capital > 0:
                margin = capital * position_size_pct
                current_position = {
                    "direction": signal_type,
                    "entry_price": price,
                    "margin": margin
                }
        
        # 计算统计数据
        if trades:
            winning_trades = [t for t in trades if t["pnl"] > 0]
            total_pnl = sum(t["pnl"] for t in trades)
            total_pnl_pct = (capital - initial_capital) / initial_capital * 100
            avg_pnl = total_pnl / len(trades)
            win_rate = len(winning_trades) / len(trades) * 100
            
            # 计算夏普比率(简化版)
            pnl_list = [t["pnl"] for t in trades]
            avg_return = sum(pnl_list) / len(pnl_list)
            std_dev = (sum((x - avg_return) ** 2 for x in pnl_list) / len(pnl_list)) ** 0.5
            sharpe_ratio = (avg_return / std_dev) if std_dev > 0 else 0
        else:
            winning_trades = []
            total_pnl = 0
            total_pnl_pct = 0
            avg_pnl = 0
            win_rate = 0
            sharpe_ratio = 0
        
        return {
            "totalTrades": len(trades),
            "winningTrades": len(winning_trades),
            "winRate": round(win_rate, 2),
            "totalPnl": round(total_pnl, 2),
            "totalPnlPct": round(total_pnl_pct, 2),
            "avgPnl": round(avg_pnl, 2),
            "maxDrawdown": round(max_drawdown, 2),
            "sharpeRatio": round(sharpe_ratio, 2),
            "finalCapital": round(capital, 2),
            "trades": trades[-10:]  # 最近10笔交易
        }

def main():
    """
    主函数
    
    用法:
        python backtest.py <symbol> <timeframe> <short_ma> <long_ma> <sensitivity>
    """
    if len(sys.argv) < 6:
        print(json.dumps({
            "error": "Usage: backtest.py <symbol> <timeframe> <short_ma> <long_ma> <sensitivity>"
        }))
        sys.exit(1)
    
    symbol = sys.argv[1]
    timeframe = sys.argv[2]
    short_ma = int(sys.argv[3])
    long_ma = int(sys.argv[4])
    sensitivity = sys.argv[5]
    
    backtester = Backtester()
    result = backtester.backtest_strategy(
        symbol, timeframe, short_ma, long_ma, sensitivity
    )
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
