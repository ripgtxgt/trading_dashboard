#!/usr/bin/env python3
"""
Parameter优化器 - auto寻找最优Parameter组合
"""
import sys
import json
from backtest import Backtester
from typing import List, Dict, Tuple

class ParamOptimizer:
 def __init__(self):
 self.backtester = Backtester()
 
 def optimize(
 self,
 symbol: str,
 timeframe: str,
 optimization_target: str = "winRate" # winRate, totalPnl, sharpeRatio
) -> Dict:
 """
 优化Parameter
 
 Args:
 symbol: Tradefor
 timeframe: Time框架
 optimization_target: 优化目标 (winRate, totalPnl, sharpeRatio)
 
 Returns:
 最优Parameterandresult
 """
 # 定义Parameter搜索空间
 short_ma_range = [3, 5, 7, 10]
 long_ma_range = [15, 20, 25, 30]
 sensitivity_options = ["loose", "standard", "strict"]
 
 best_result = None
 best_params = None
 best_score = float('-inf')
 
 all_results = []
 
 # 遍历所HasParameter组合
 for short_ma in short_ma_range:
 for long_ma in long_ma_range:
 if long_ma <= short_ma:
 continue
 
 for sensitivity in sensitivity_options:
 # 回测
 result = self.backtester.backtest_strategy(
 symbol, timeframe, short_ma, long_ma, sensitivity
)
 
 if "error" in result:
 continue
 
 # Calculate得分
 if optimization_target == "winRate":
 score = result["winRate"]
 elif optimization_target == "totalPnl":
 score = result["totalPnlPct"]
 elif optimization_target == "sharpeRatio":
 score = result["sharpeRatio"]
 else:
 # 综合得分：Win rate * 总Profit * 夏普ratio
 score = (
 result["winRate"] / 100 * 
 (1 + result["totalPnlPct"] / 100) * 
 max(0, result["sharpeRatio"])
)
 
 # 只考虑Has足够Tradecountresult
 if result["totalTrades"] >= 3:
 all_results.append({
 "shortMa": short_ma,
 "longMa": long_ma,
 "sensitivity": sensitivity,
 "score": round(score, 2),
 "winRate": result["winRate"],
 "totalPnlPct": result["totalPnlPct"],
 "totalTrades": result["totalTrades"],
 "sharpeRatio": result["sharpeRatio"]
 })
 
 if score > best_score:
 best_score = score
 best_result = result
 best_params = {
 "shortMaPeriod": short_ma,
 "longMaPeriod": long_ma,
 "sensitivity": sensitivity,
 "timeframe": timeframe
 }
 
 # 按得分排序
 all_results.sort(key=lambda x: x["score"], reverse=True)
 
 if not best_params:
 return {
 "error": "No valid parameter combination found",
 "recommendations": []
 }
 
 return {
 "recommended": best_params,
 "performance": {
 "winRate": best_result["winRate"],
 "totalPnlPct": best_result["totalPnlPct"],
 "totalTrades": best_result["totalTrades"],
 "sharpeRatio": best_result["sharpeRatio"],
 "maxDrawdown": best_result["maxDrawdown"]
 },
 "allResults": all_results[:10], # 返回前10最佳result
 "optimizationTarget": optimization_target
 }

def main():
 """
 主函数
 
 用法:
 python optimize_params.py <symbol> <timeframe> [optimization_target]
 """
 if len(sys.argv) < 3:
 print(json.dumps({
 "error": "Usage: optimize_params.py <symbol> <timeframe> [optimization_target]"
 }))
 sys.exit(1)
 
 symbol = sys.argv[1]
 timeframe = sys.argv[2]
 optimization_target = sys.argv[3] if len(sys.argv) > 3 else "composite"
 
 optimizer = ParamOptimizer()
 result = optimizer.optimize(symbol, timeframe, optimization_target)
 
 print(json.dumps(result))

if __name__ == "__main__":
 main()
