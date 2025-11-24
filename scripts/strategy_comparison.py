#!/usr/bin/env python3
"""
多Strategy回测for比模块
支持并行回测多组Parameter，for比not同Strategy表现
"""

import sys
import os
import json
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import concurrent.futures

sys.path.append(os.path.dirname(__file__))

try:
 import ccxt
 import pandas as pd
 import numpy as np
except ImportError:
 print("Please: pip install ccxt pandas numpy")
 sys.exit(1)


class StrategyConfig:
 """StrategyConfig"""
 
 def __init__(self, name: str, params: Dict):
 self.name = name
 self.params = params
 
 def __repr__(self):
 return f"StrategyConfig(name='{self.name}', params={self.params})"


class BacktestResult:
 """回测result"""
 
 def __init__(self, config: StrategyConfig):
 self.config = config
 self.trades: List[Dict] = []
 self.equity_curve: List[float] = []
 self.timestamps: List[str] = []
 
 # 统计指标
 self.total_trades = 0
 self.winning_trades = 0
 self.losing_trades = 0
 self.win_rate = 0.0
 self.total_return = 0.0
 self.total_return_pct = 0.0
 self.sharpe_ratio = 0.0
 self.max_drawdown = 0.0
 self.max_drawdown_pct = 0.0
 self.profit_factor = 0.0
 self.avg_win = 0.0
 self.avg_loss = 0.0
 
 def calculate_metrics(self, initial_capital: float):
 """Calculate统计指标"""
 if not self.trades:
 return
 
 # 基本统计
 self.total_trades = len(self.trades)
 self.winning_trades = sum(1 for t in self.trades if t['pnl'] > 0)
 self.losing_trades = sum(1 for t in self.trades if t['pnl'] < 0)
 
 if self.total_trades > 0:
 self.win_rate = self.winning_trades / self.total_trades
 
 # 总Profit
 self.total_return = sum(t['pnl'] for t in self.trades)
 self.total_return_pct = (self.total_return / initial_capital) * 100
 
 # PnL比
 wins = [t['pnl'] for t in self.trades if t['pnl'] > 0]
 losses = [abs(t['pnl']) for t in self.trades if t['pnl'] < 0]
 
 if wins:
 self.avg_win = sum(wins) / len(wins)
 if losses:
 self.avg_loss = sum(losses) / len(losses)
 
 # 盈利因子
 total_wins = sum(wins) if wins else 0
 total_losses = sum(losses) if losses else 1
 self.profit_factor = total_wins / total_losses if total_losses > 0 else 0
 
 # 夏普ratio
 if len(self.equity_curve) > 1:
 returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
 if len(returns) > 0 and np.std(returns) > 0:
 self.sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
 
 # MaxDrawdown
 if self.equity_curve:
 peak = self.equity_curve[0]
 max_dd = 0
 
 for equity in self.equity_curve:
 if equity > peak:
 peak = equity
 dd = peak - equity
 if dd > max_dd:
 max_dd = dd
 
 self.max_drawdown = max_dd
 self.max_drawdown_pct = (max_dd / peak) * 100 if peak > 0 else 0
 
 def to_dict(self) -> Dict:
 """转换as字典"""
 return {
 'config': {
 'name': self.config.name,
 'params': self.config.params
 },
 'metrics': {
 'total_trades': self.total_trades,
 'winning_trades': self.winning_trades,
 'losing_trades': self.losing_trades,
 'win_rate': round(self.win_rate * 100, 2),
 'total_return': round(self.total_return, 2),
 'total_return_pct': round(self.total_return_pct, 2),
 'sharpe_ratio': round(self.sharpe_ratio, 2),
 'max_drawdown': round(self.max_drawdown, 2),
 'max_drawdown_pct': round(self.max_drawdown_pct, 2),
 'profit_factor': round(self.profit_factor, 2),
 'avg_win': round(self.avg_win, 2),
 'avg_loss': round(self.avg_loss, 2)
 },
 'trades': self.trades,
 'equity_curve': self.equity_curve,
 'timestamps': self.timestamps
 }


class StrategyBacktester:
 """Strategy回测器"""
 
 def __init__(self, symbol: str = 'BTC/USDT', initial_capital: float = 100.0):
 self.symbol = symbol
 self.initial_capital = initial_capital
 self.exchange = None
 
 def _init_exchange(self):
 """InitializeTrade所"""
 if not self.exchange:
 self.exchange = ccxt.kucoin({
 'enableRateLimit': True,
 })
 
 def fetch_historical_data(self, timeframe: str = '1h', days: int = 30) -> pd.DataFrame:
 """GetHistory数据"""
 self._init_exchange()
 
 # CalculateTimerange
 since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
 
 print(f"processingGet {self.symbol} {timeframe}  {days} ...")
 
 # GetK线数据
 ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe, since=since, limit=1000)
 
 # 转换asDataFrame
 df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
 df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
 
 print(f"[OK] Getto {len(df)} K")
 
 return df
 
 def calculate_indicators(self, df: pd.DataFrame, ma_short: int = 5, ma_long: int = 20) -> pd.DataFrame:
 """Calculate技术指标"""
 df = df.copy()
 
 # Calculate移动平均线
 df[f'ma{ma_short}'] = df['close'].rolling(window=ma_short).mean()
 df[f'ma{ma_long}'] = df['close'].rolling(window=ma_long).mean()
 
 # Calculate前一MA值（用attrend判断）
 df[f'ma{ma_short}_prev'] = df[f'ma{ma_short}'].shift(1)
 
 return df
 
 def generate_signals(self, df: pd.DataFrame, ma_short: int = 5, ma_long: int = 20) -> pd.DataFrame:
 """生成TradeSignal"""
 df = df.copy()
 
 # 做多件
 long_condition = (
 (df[f'ma{ma_short}'] > df[f'ma{ma_long}']) & # MA交叉
 (df['close'] > df[f'ma{ma_short}']) & # PriceConfirm
 (df[f'ma{ma_short}'] > df[f'ma{ma_short}_prev']) # trendConfirm
)
 
 # 做空件
 short_condition = (
 (df[f'ma{ma_short}'] < df[f'ma{ma_long}']) & # MA交叉
 (df['close'] < df[f'ma{ma_short}']) & # PriceConfirm
 (df[f'ma{ma_short}'] < df[f'ma{ma_short}_prev']) # trendConfirm
)
 
 df['signal'] = 0
 df.loc[long_condition, 'signal'] = 1 # 做多
 df.loc[short_condition, 'signal'] = -1 # 做空
 
 return df
 
 def backtest_strategy(self, config: StrategyConfig, df: pd.DataFrame) -> BacktestResult:
 """回测单Strategy"""
 print(f"\nStrategy: {config.name}")
 print(f"Parameter: {config.params}")
 
 result = BacktestResult(config)
 
 # GetParameter
 ma_short = config.params.get('ma_short', 5)
 ma_long = config.params.get('ma_long', 20)
 position_size = config.params.get('position_size', 0.1) # 每timesTrade占用资金比例
 
 # Calculate指标andSignal
 df = self.calculate_indicators(df, ma_short, ma_long)
 df = self.generate_signals(df, ma_short, ma_long)
 
 # 模拟Trade
 capital = self.initial_capital
 position = None # CurrentPosition
 
 result.equity_curve.append(capital)
 result.timestamps.append(df.iloc[0]['timestamp'].isoformat())
 
 for i in range(len(df)):
 row = df.iloc[i]
 
 # 跳过No效数据
 if pd.isna(row['signal']):
 continue
 
 # 开仓Signal
 if position is None and row['signal']!= 0:
 # Calculate开仓Amount
 size = (capital * position_size) / row['close']
 
 position = {
 'side': 'long' if row['signal'] == 1 else 'short',
 'entry_price': row['close'],
 'size': size,
 'entry_time': row['timestamp']
 }
 
 print(f" : {position['side']} @ {position['entry_price']:.2f}")
 
 # Close positionSignal（反向SignalorStop loss）
 elif position is not None:
 should_close = False
 
 # 反向Signal
 if (position['side'] == 'long' and row['signal'] == -1) or \
 (position['side'] == 'short' and row['signal'] == 1):
 should_close = True
 
 if should_close:
 # CalculatePnL
 if position['side'] == 'long':
 pnl = (row['close'] - position['entry_price']) * position['size']
 else:
 pnl = (position['entry_price'] - row['close']) * position['size']
 
 # Update资金
 capital += pnl
 
 # RecordTrade
 trade = {
 'side': position['side'],
 'entry_price': position['entry_price'],
 'exit_price': row['close'],
 'size': position['size'],
 'pnl': pnl,
 'entry_time': position['entry_time'].isoformat(),
 'exit_time': row['timestamp'].isoformat()
 }
 result.trades.append(trade)
 
 print(f" Close position: {position['side']} @ {row['close']:.2f}, PnL: {pnl:.2f}")
 
 position = None
 
 # Record资金曲线
 result.equity_curve.append(capital)
 result.timestamps.append(row['timestamp'].isoformat())
 
 # Calculate指标
 result.calculate_metrics(self.initial_capital)
 
 print(f"[OK] Complete:")
 print(f" Trade: {result.total_trades}")
 print(f" Win rate: {result.win_rate*100:.2f}%")
 print(f" Profit: {result.total_return:.2f} ({result.total_return_pct:.2f}%)")
 print(f" ratio: {result.sharpe_ratio:.2f}")
 print(f" MaxDrawdown: {result.max_drawdown:.2f} ({result.max_drawdown_pct:.2f}%)")
 
 return result
 
 def compare_strategies(self, configs: List[StrategyConfig], 
 timeframe: str = '1h', days: int = 30) -> List[BacktestResult]:
 """for比多Strategy"""
 print(f"\n{'='*60}")
 print(f"Strategyfor")
 print(f"{'='*60}")
 print(f"Tradefor: {self.symbol}")
 print(f"Time: {timeframe}")
 print(f": {days}")
 print(f": {self.initial_capital} USDT")
 print(f"StrategyAmount: {len(configs)}")
 
 # GetHistory数据
 df = self.fetch_historical_data(timeframe, days)
 
 # 并行回测
 results = []
 
 # 使用线程池并行回测（注意：ccxt可能HasAPIlimit）
 # assafe，这里使用顺序Execute
 for config in configs:
 result = self.backtest_strategy(config, df)
 results.append(result)
 
 # 排序（按总Profit）
 results.sort(key=lambda r: r.total_return, reverse=True)
 
 print(f"\n{'='*60}")
 print(f"result")
 print(f"{'='*60}")
 
 for i, result in enumerate(results, 1):
 print(f"\n {i} : {result.config.name}")
 print(f" Parameter: {result.config.params}")
 print(f" Profit: {result.total_return:.2f} USDT ({result.total_return_pct:.2f}%)")
 print(f" Win rate: {result.win_rate*100:.2f}%")
 print(f" ratio: {result.sharpe_ratio:.2f}")
 print(f" MaxDrawdown: {result.max_drawdown_pct:.2f}%")
 
 return results
 
 def save_results(self, results: List[BacktestResult], filename: str = 'strategy_comparison.json'):
 """Saveresult"""
 filepath = os.path.join(os.path.dirname(__file__), filename)
 
 data = {
 'timestamp': datetime.now().isoformat(),
 'symbol': self.symbol,
 'initial_capital': self.initial_capital,
 'results': [r.to_dict() for r in results]
 }
 
 with open(filepath, 'w') as f:
 json.dump(data, f, indent=2)
 
 print(f"\n[OK] resultAlreadySaveto: {filepath}")


def create_default_strategies() -> List[StrategyConfig]:
 """创建defaultStrategyConfig"""
 strategies = [
 StrategyConfig('保守型 MA(5,20)', {
 'ma_short': 5,
 'ma_long': 20,
 'position_size': 0.1
 }),
 StrategyConfig('平衡型 MA(10,30)', {
 'ma_short': 10,
 'ma_long': 30,
 'position_size': 0.15
 }),
 StrategyConfig('激进型 MA(3,15)', {
 'ma_short': 3,
 'ma_long': 15,
 'position_size': 0.2
 }),
 StrategyConfig('长cycle MA(20,50)', {
 'ma_short': 20,
 'ma_long': 50,
 'position_size': 0.1
 }),
 StrategyConfig('短cycle MA(5,10)', {
 'ma_short': 5,
 'ma_long': 10,
 'position_size': 0.15
 })
 ]
 
 return strategies


if __name__ == '__main__':
 # 创建回测器
 backtester = StrategyBacktester(symbol='BTC/USDT', initial_capital=100.0)
 
 # 创建StrategyConfig
 strategies = create_default_strategies()
 
 # for比回测
 results = backtester.compare_strategies(strategies, timeframe='1h', days=30)
 
 # Saveresult
 backtester.save_results(results)
 
 print("\n[OK] StrategyforComplete")
