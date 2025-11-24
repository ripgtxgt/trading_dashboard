#!/usr/bin/env python3
"""
多策略回测对比模块
支持并行回测多组参数，对比不同策略的表现
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
    print("请安装依赖: pip install ccxt pandas numpy")
    sys.exit(1)


class StrategyConfig:
    """策略配置"""
    
    def __init__(self, name: str, params: Dict):
        self.name = name
        self.params = params
    
    def __repr__(self):
        return f"StrategyConfig(name='{self.name}', params={self.params})"


class BacktestResult:
    """回测结果"""
    
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
        """计算统计指标"""
        if not self.trades:
            return
        
        # 基本统计
        self.total_trades = len(self.trades)
        self.winning_trades = sum(1 for t in self.trades if t['pnl'] > 0)
        self.losing_trades = sum(1 for t in self.trades if t['pnl'] < 0)
        
        if self.total_trades > 0:
            self.win_rate = self.winning_trades / self.total_trades
        
        # 总收益
        self.total_return = sum(t['pnl'] for t in self.trades)
        self.total_return_pct = (self.total_return / initial_capital) * 100
        
        # 盈亏比
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
        
        # 夏普比率
        if len(self.equity_curve) > 1:
            returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
            if len(returns) > 0 and np.std(returns) > 0:
                self.sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
        
        # 最大回撤
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
        """转换为字典"""
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
    """策略回测器"""
    
    def __init__(self, symbol: str = 'BTC/USDT', initial_capital: float = 100.0):
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.exchange = None
    
    def _init_exchange(self):
        """初始化交易所"""
        if not self.exchange:
            self.exchange = ccxt.kucoin({
                'enableRateLimit': True,
            })
    
    def fetch_historical_data(self, timeframe: str = '1h', days: int = 30) -> pd.DataFrame:
        """获取历史数据"""
        self._init_exchange()
        
        # 计算时间范围
        since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        print(f"正在获取 {self.symbol} {timeframe} 数据，最近 {days} 天...")
        
        # 获取K线数据
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe, since=since, limit=1000)
        
        # 转换为DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        print(f"✅ 获取到 {len(df)} 根K线")
        
        return df
    
    def calculate_indicators(self, df: pd.DataFrame, ma_short: int = 5, ma_long: int = 20) -> pd.DataFrame:
        """计算技术指标"""
        df = df.copy()
        
        # 计算移动平均线
        df[f'ma{ma_short}'] = df['close'].rolling(window=ma_short).mean()
        df[f'ma{ma_long}'] = df['close'].rolling(window=ma_long).mean()
        
        # 计算前一个MA值（用于趋势判断）
        df[f'ma{ma_short}_prev'] = df[f'ma{ma_short}'].shift(1)
        
        return df
    
    def generate_signals(self, df: pd.DataFrame, ma_short: int = 5, ma_long: int = 20) -> pd.DataFrame:
        """生成交易信号"""
        df = df.copy()
        
        # 做多条件
        long_condition = (
            (df[f'ma{ma_short}'] > df[f'ma{ma_long}']) &  # MA交叉
            (df['close'] > df[f'ma{ma_short}']) &  # 价格确认
            (df[f'ma{ma_short}'] > df[f'ma{ma_short}_prev'])  # 趋势确认
        )
        
        # 做空条件
        short_condition = (
            (df[f'ma{ma_short}'] < df[f'ma{ma_long}']) &  # MA交叉
            (df['close'] < df[f'ma{ma_short}']) &  # 价格确认
            (df[f'ma{ma_short}'] < df[f'ma{ma_short}_prev'])  # 趋势确认
        )
        
        df['signal'] = 0
        df.loc[long_condition, 'signal'] = 1  # 做多
        df.loc[short_condition, 'signal'] = -1  # 做空
        
        return df
    
    def backtest_strategy(self, config: StrategyConfig, df: pd.DataFrame) -> BacktestResult:
        """回测单个策略"""
        print(f"\n回测策略: {config.name}")
        print(f"参数: {config.params}")
        
        result = BacktestResult(config)
        
        # 获取参数
        ma_short = config.params.get('ma_short', 5)
        ma_long = config.params.get('ma_long', 20)
        position_size = config.params.get('position_size', 0.1)  # 每次交易占用资金比例
        
        # 计算指标和信号
        df = self.calculate_indicators(df, ma_short, ma_long)
        df = self.generate_signals(df, ma_short, ma_long)
        
        # 模拟交易
        capital = self.initial_capital
        position = None  # 当前持仓
        
        result.equity_curve.append(capital)
        result.timestamps.append(df.iloc[0]['timestamp'].isoformat())
        
        for i in range(len(df)):
            row = df.iloc[i]
            
            # 跳过无效数据
            if pd.isna(row['signal']):
                continue
            
            # 开仓信号
            if position is None and row['signal'] != 0:
                # 计算开仓数量
                size = (capital * position_size) / row['close']
                
                position = {
                    'side': 'long' if row['signal'] == 1 else 'short',
                    'entry_price': row['close'],
                    'size': size,
                    'entry_time': row['timestamp']
                }
                
                print(f"  开仓: {position['side']} @ {position['entry_price']:.2f}")
            
            # 平仓信号（反向信号或止损）
            elif position is not None:
                should_close = False
                
                # 反向信号
                if (position['side'] == 'long' and row['signal'] == -1) or \
                   (position['side'] == 'short' and row['signal'] == 1):
                    should_close = True
                
                if should_close:
                    # 计算盈亏
                    if position['side'] == 'long':
                        pnl = (row['close'] - position['entry_price']) * position['size']
                    else:
                        pnl = (position['entry_price'] - row['close']) * position['size']
                    
                    # 更新资金
                    capital += pnl
                    
                    # 记录交易
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
                    
                    print(f"  平仓: {position['side']} @ {row['close']:.2f}, 盈亏: {pnl:.2f}")
                    
                    position = None
            
            # 记录资金曲线
            result.equity_curve.append(capital)
            result.timestamps.append(row['timestamp'].isoformat())
        
        # 计算指标
        result.calculate_metrics(self.initial_capital)
        
        print(f"✅ 回测完成:")
        print(f"   总交易: {result.total_trades}")
        print(f"   胜率: {result.win_rate*100:.2f}%")
        print(f"   总收益: {result.total_return:.2f} ({result.total_return_pct:.2f}%)")
        print(f"   夏普比率: {result.sharpe_ratio:.2f}")
        print(f"   最大回撤: {result.max_drawdown:.2f} ({result.max_drawdown_pct:.2f}%)")
        
        return result
    
    def compare_strategies(self, configs: List[StrategyConfig], 
                          timeframe: str = '1h', days: int = 30) -> List[BacktestResult]:
        """对比多个策略"""
        print(f"\n{'='*60}")
        print(f"策略对比回测")
        print(f"{'='*60}")
        print(f"交易对: {self.symbol}")
        print(f"时间框架: {timeframe}")
        print(f"回测天数: {days}")
        print(f"初始资金: {self.initial_capital} USDT")
        print(f"策略数量: {len(configs)}")
        
        # 获取历史数据
        df = self.fetch_historical_data(timeframe, days)
        
        # 并行回测
        results = []
        
        # 使用线程池并行回测（注意：ccxt可能有API限制）
        # 为了安全，这里使用顺序执行
        for config in configs:
            result = self.backtest_strategy(config, df)
            results.append(result)
        
        # 排序（按总收益）
        results.sort(key=lambda r: r.total_return, reverse=True)
        
        print(f"\n{'='*60}")
        print(f"回测结果排名")
        print(f"{'='*60}")
        
        for i, result in enumerate(results, 1):
            print(f"\n第 {i} 名: {result.config.name}")
            print(f"  参数: {result.config.params}")
            print(f"  总收益: {result.total_return:.2f} USDT ({result.total_return_pct:.2f}%)")
            print(f"  胜率: {result.win_rate*100:.2f}%")
            print(f"  夏普比率: {result.sharpe_ratio:.2f}")
            print(f"  最大回撤: {result.max_drawdown_pct:.2f}%")
        
        return results
    
    def save_results(self, results: List[BacktestResult], filename: str = 'strategy_comparison.json'):
        """保存结果"""
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'symbol': self.symbol,
            'initial_capital': self.initial_capital,
            'results': [r.to_dict() for r in results]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✅ 结果已保存到: {filepath}")


def create_default_strategies() -> List[StrategyConfig]:
    """创建默认策略配置"""
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
        StrategyConfig('长周期 MA(20,50)', {
            'ma_short': 20,
            'ma_long': 50,
            'position_size': 0.1
        }),
        StrategyConfig('短周期 MA(5,10)', {
            'ma_short': 5,
            'ma_long': 10,
            'position_size': 0.15
        })
    ]
    
    return strategies


if __name__ == '__main__':
    # 创建回测器
    backtester = StrategyBacktester(symbol='BTC/USDT', initial_capital=100.0)
    
    # 创建策略配置
    strategies = create_default_strategies()
    
    # 对比回测
    results = backtester.compare_strategies(strategies, timeframe='1h', days=30)
    
    # 保存结果
    backtester.save_results(results)
    
    print("\n✅ 策略对比完成！")
