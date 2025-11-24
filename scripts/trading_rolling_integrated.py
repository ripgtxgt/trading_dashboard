#!/usr/bin/env python3
"""
完整的10U战神滚仓策略 - 集成版本
整合了数据库同步和Telegram通知功能

使用方法：
1. 配置环境变量：DATABASE_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
2. 运行：python3 trading_rolling_integrated.py
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

# 配置日志
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
    """10U战神滚仓策略"""
    
    def __init__(self):
        self.symbol = "XBTUSDTM"
        self.initial_balance = 10.0  # 初始资金10U
        self.current_balance = self.initial_balance
        self.position = None  # 当前持仓
        self.trades_history = []  # 交易历史
        
        # 策略参数
        self.short_ma_period = 5
        self.long_ma_period = 20
        self.timeframe = "1h"
        self.leverage = 10
        
        # 集成模块
        self.db = DatabaseSync()
        self.telegram = TelegramNotifier()
        
        # 初始化数据库状态
        self._init_db_state()
        
    def _init_db_state(self):
        """初始化数据库状态"""
        try:
            # 更新机器人状态
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
            
            logger.info("数据库状态初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
    
    def get_klines(self, limit=100) -> List[Dict]:
        """
        获取K线数据
        
        实际使用时，这里应该调用KuCoin API获取真实数据
        示例代码保留模拟数据用于测试
        """
        # TODO: 替换为真实的KuCoin API调用
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
        """计算移动平均线"""
        if len(klines) < period:
            return 0.0
        
        closes = [k['close'] for k in klines[-period:]]
        return sum(closes) / len(closes)
    
    def generate_signal(self, klines: List[Dict]) -> Optional[str]:
        """
        生成交易信号
        
        返回：
        - 'long': 做多信号
        - 'short': 做空信号
        - None: 无信号
        """
        if len(klines) < self.long_ma_period:
            return None
        
        current_price = klines[-1]['close']
        ma_short = self.calculate_ma(klines, self.short_ma_period)
        ma_long = self.calculate_ma(klines, self.long_ma_period)
        prev_ma_short = self.calculate_ma(klines[:-1], self.short_ma_period)
        
        # 做多条件
        if (ma_short > ma_long and 
            current_price > ma_short and 
            ma_short > prev_ma_short):
            return 'long'
        
        # 做空条件
        if (ma_short < ma_long and 
            current_price < ma_short and 
            ma_short < prev_ma_short):
            return 'short'
        
        return None
    
    def open_position(self, signal: str, price: float):
        """开仓"""
        if self.position is not None:
            logger.warning("已有持仓，无法开仓")
            return
        
        # 计算仓位
        margin = self.current_balance * 0.9  # 使用90%资金
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
        
        logger.info(f"开仓成功: {signal} @ {price}, 数量: {quantity:.4f}")
        
        # 同步到数据库
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
            logger.info(f"持仓已同步到数据库，ID: {position_id}")
        except Exception as e:
            logger.error(f"持仓同步失败: {e}")
        
        # 发送Telegram通知
        try:
            self.telegram.send_trade_opened(
                symbol=self.symbol,
                side=signal,
                price=price,
                quantity=quantity,
                margin=margin
            )
        except Exception as e:
            logger.error(f"Telegram通知发送失败: {e}")
    
    def close_position(self, price: float, reason: str = "止盈/止损"):
        """平仓"""
        if self.position is None:
            logger.warning("无持仓，无法平仓")
            return
        
        entry_price = self.position['entry_price']
        quantity = self.position['quantity']
        side = self.position['side']
        margin = self.position['margin']
        
        # 计算盈亏
        if side == 'long':
            pnl = (price - entry_price) * quantity
        else:  # short
            pnl = (entry_price - price) * quantity
        
        pnl_percent = (pnl / margin) * 100
        
        # 更新余额
        self.current_balance += pnl
        
        # 记录交易
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
        
        logger.info(f"平仓成功: {side} @ {price}, 盈亏: {pnl:.2f} ({pnl_percent:.2f}%)")
        
        # 同步到数据库
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
            logger.info(f"交易已同步到数据库，ID: {trade_id}")
            
            # 更新机器人状态
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
            logger.error(f"交易同步失败: {e}")
        
        # 发送Telegram通知
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
            logger.error(f"Telegram通知发送失败: {e}")
        
        # 清空持仓
        self.position = None
    
    def check_stop_loss(self, current_price: float) -> bool:
        """检查止损"""
        if self.position is None:
            return False
        
        entry_price = self.position['entry_price']
        side = self.position['side']
        
        # 止损比例：10%
        stop_loss_percent = 0.10
        
        if side == 'long':
            stop_price = entry_price * (1 - stop_loss_percent)
            if current_price <= stop_price:
                logger.warning(f"触发止损: {current_price} <= {stop_price}")
                self.close_position(current_price, "止损")
                return True
        else:  # short
            stop_price = entry_price * (1 + stop_loss_percent)
            if current_price >= stop_price:
                logger.warning(f"触发止损: {current_price} >= {stop_price}")
                self.close_position(current_price, "止损")
                return True
        
        return False
    
    def check_take_profit(self, current_price: float) -> bool:
        """检查止盈"""
        if self.position is None:
            return False
        
        entry_price = self.position['entry_price']
        side = self.position['side']
        
        # 止盈比例：20%
        take_profit_percent = 0.20
        
        if side == 'long':
            take_price = entry_price * (1 + take_profit_percent)
            if current_price >= take_price:
                logger.info(f"触发止盈: {current_price} >= {take_price}")
                self.close_position(current_price, "止盈")
                return True
        else:  # short
            take_price = entry_price * (1 - take_profit_percent)
            if current_price <= take_price:
                logger.info(f"触发止盈: {current_price} <= {take_price}")
                self.close_position(current_price, "止盈")
                return True
        
        return False
    
    def run_cycle(self, cycle_num: int):
        """运行一个交易周期"""
        logger.info(f"\n{'='*50}")
        logger.info(f"周期 #{cycle_num} 开始")
        logger.info(f"当前余额: {self.current_balance:.2f} USDT")
        
        # 获取K线数据
        klines = self.get_klines(limit=100)
        current_price = klines[-1]['close']
        
        logger.info(f"当前价格: {current_price:.2f}")
        
        # 检查止损止盈
        if self.position:
            if self.check_stop_loss(current_price):
                return
            if self.check_take_profit(current_price):
                return
        
        # 生成交易信号
        signal = self.generate_signal(klines)
        
        if signal and self.position is None:
            logger.info(f"检测到信号: {signal}")
            self.open_position(signal, current_price)
        elif signal is None and self.position is None:
            logger.info("无交易信号")
        elif self.position:
            logger.info(f"持仓中: {self.position['side']} @ {self.position['entry_price']:.2f}")
    
    def run(self, max_cycles: Optional[int] = None):
        """
        运行策略主循环
        
        参数：
        - max_cycles: 最大运行周期数，None表示无限运行
        """
        logger.info("="*60)
        logger.info("10U战神滚仓策略 - 启动")
        logger.info("="*60)
        logger.info(f"交易对: {self.symbol}")
        logger.info(f"初始资金: {self.initial_balance} USDT")
        logger.info(f"杠杆倍数: {self.leverage}x")
        logger.info(f"MA参数: {self.short_ma_period}/{self.long_ma_period}")
        logger.info(f"时间框架: {self.timeframe}")
        logger.info("="*60)
        
        # 发送启动通知
        try:
            self.telegram.send_bot_status(
                status="启动",
                balance=self.current_balance,
                total_trades=0,
                win_rate=0.0
            )
        except Exception as e:
            logger.error(f"Telegram通知发送失败: {e}")
        
        cycle_num = 0
        
        try:
            while True:
                cycle_num += 1
                
                # 运行一个周期
                self.run_cycle(cycle_num)
                
                # 检查是否达到最大周期数
                if max_cycles and cycle_num >= max_cycles:
                    logger.info(f"达到最大周期数 {max_cycles}，停止运行")
                    break
                
                # 等待下一个周期（1小时）
                # 实际使用时根据timeframe调整
                sleep_seconds = 3600  # 1小时
                logger.info(f"等待 {sleep_seconds} 秒...")
                time.sleep(sleep_seconds)
                
        except KeyboardInterrupt:
            logger.info("\n收到停止信号，正在退出...")
        except Exception as e:
            logger.error(f"运行出错: {e}", exc_info=True)
            # 发送错误通知
            try:
                self.telegram.send_risk_alert(
                    level="严重",
                    message="策略运行出错",
                    details=str(e)
                )
            except:
                pass
        finally:
            self.shutdown()
    
    def shutdown(self):
        """关闭策略"""
        logger.info("="*60)
        logger.info("策略停止")
        logger.info("="*60)
        
        # 如果有持仓，平仓
        if self.position:
            klines = self.get_klines(limit=10)
            current_price = klines[-1]['close']
            logger.info("检测到持仓，执行平仓...")
            self.close_position(current_price, "策略停止")
        
        # 打印统计信息
        total_trades = len(self.trades_history)
        if total_trades > 0:
            win_trades = sum(1 for t in self.trades_history if t['pnl'] > 0)
            win_rate = (win_trades / total_trades) * 100
            total_profit = sum(t['pnl'] for t in self.trades_history)
            
            logger.info(f"总交易次数: {total_trades}")
            logger.info(f"盈利次数: {win_trades}")
            logger.info(f"胜率: {win_rate:.2f}%")
            logger.info(f"总盈亏: {total_profit:.2f} USDT")
            logger.info(f"最终余额: {self.current_balance:.2f} USDT")
            logger.info(f"收益率: {((self.current_balance - self.initial_balance) / self.initial_balance * 100):.2f}%")
            
            # 发送每日统计
            try:
                self.telegram.send_daily_summary(
                    total_trades=total_trades,
                    win_trades=win_trades,
                    win_rate=win_rate,
                    total_pnl=total_profit,
                    current_balance=self.current_balance
                )
            except Exception as e:
                logger.error(f"Telegram通知发送失败: {e}")
        
        # 更新数据库状态
        try:
            self.db.update_bot_state(
                status='stopped',
                current_balance=self.current_balance,
                total_trades=total_trades,
                win_trades=win_trades if total_trades > 0 else 0,
                total_profit=total_profit if total_trades > 0 else 0.0
            )
        except Exception as e:
            logger.error(f"数据库更新失败: {e}")
        
        logger.info("="*60)


def main():
    """主函数"""
    # 检查环境变量
    required_vars = ['DATABASE_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"缺少必需的环境变量: {', '.join(missing_vars)}")
        logger.error("请设置以下环境变量：")
        logger.error("  DATABASE_URL - MySQL数据库连接字符串")
        logger.error("  TELEGRAM_BOT_TOKEN - Telegram Bot Token（可选）")
        logger.error("  TELEGRAM_CHAT_ID - Telegram Chat ID（可选）")
        sys.exit(1)
    
    # 创建策略实例
    strategy = TradingStrategy()
    
    # 运行策略
    # 参数：max_cycles=None 表示无限运行
    # 测试时可以设置为较小的数字，例如 max_cycles=10
    strategy.run(max_cycles=None)


if __name__ == "__main__":
    main()
