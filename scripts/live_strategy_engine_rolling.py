#!/usr/bin/env python3
"""
10U战神滚仓策略 - 完整版实盘执行引擎
版本: 3.0 Rolling Edition
集成滚仓管理器，实现真正的滚仓策略
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
    """实盘策略执行引擎 - 滚仓版"""
    
    def __init__(self, trader, initial_capital=None):
        """
        初始化策略引擎
        
        Args:
            trader: KuCoinTrader实例
            initial_capital: 初始资金（如果None则从账户读取）
        """
        self.logger = logging.getLogger('StrategyEngine')
        self.trader = trader
        self.symbol = 'XBTUSDTM'  # 交易对
        
        # 获取初始资金
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
        
        # 尝试加载之前的状态
        try:
            self.rolling_manager.load_state()
        except:
            self.logger.info("未找到之前的状态文件，使用新状态")
        
        # 策略状态
        self.is_running = False
        self.emergency_stopped = False
        self.last_check_time = 0
        self.check_interval = 60  # 检查间隔（秒）
        
        # 统计信息
        self.daily_trades = 0
        self.daily_pnl = 0
        self.last_reset_date = datetime.now().date()
        
        # 信号分析数据
        self.last_signal_analysis = None
        
        self.logger.info(f"滚仓策略引擎初始化完成: 初始资金={self.capital:.2f}U")
        self.logger.info(f"当前阶段: {self.rolling_manager.get_current_stage(self.capital).name}")
    
    def update_capital(self):
        """更新资金（从账户余额）"""
        try:
            balance = self.trader.get_balance()
            if balance:
                if isinstance(balance, dict):
                    self.capital = balance.get('total', 0)
                elif isinstance(balance, (int, float)):
                    self.capital = float(balance)
                
                # 同步到滚仓管理器
                self.rolling_manager.balance = self.capital
                
                self.logger.debug(f"资金更新: {self.capital:.2f}U")
                return True
            return False
        except Exception as e:
            self.logger.error(f"更新资金失败: {e}")
            return False
    
    def check_safety_limits(self):
        """检查安全限制"""
        # 检查日期
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.daily_trades = 0
            self.daily_pnl = 0
            self.last_reset_date = today
            self.logger.info("新的一天，重置日计数器")
        
        # 检查滚仓管理器的暂停状态
        if self.rolling_manager.is_paused:
            self.logger.warning("⚠️  滚仓管理器已暂停（连续亏损）")
            return False
        
        # 检查单日最大交易次数
        if self.daily_trades >= SAFETY_CONFIG['max_daily_trades']:
            self.logger.warning(f"⚠️  已达单日最大交易次数: {self.daily_trades}")
            return False
        
        # 检查单日最大亏损
        if self.daily_pnl <= -SAFETY_CONFIG['max_daily_loss']:
            self.logger.warning(f"⚠️  已达单日最大亏损: {self.daily_pnl:.2f}U")
            return False
        
        # 检查最小余额
        if self.capital < SAFETY_CONFIG['min_balance']:
            self.logger.warning(f"⚠️  资金低于最小余额: {self.capital:.2f}U")
            return False
        
        # 检查紧急止损
        total_loss_pct = (self.capital - self.initial_capital) / self.initial_capital
        if total_loss_pct <= -SAFETY_CONFIG['emergency_stop_loss']:
            self.logger.error(f"⚠️  触发紧急止损! 总亏损: {total_loss_pct*100:.2f}%")
            self.emergency_stopped = True
            return False
        
        return True
    
    def generate_signal(self, ohlcv_data):
        """
        生成交易信号
        
        Args:
            ohlcv_data: K线数据列表
        
        Returns:
            dict: {
                'signal': 'long'/'short'/None,
                'analysis': {详细分析数据}
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
        
        # 详细的信号分析日志
        self.logger.info(f"📊 信号分析:")
        self.logger.info(f"  当前价格: {current_price:.2f}")
        self.logger.info(f"  短MA({short_period}): {short_ma:.2f}")
        self.logger.info(f"  长MA({long_period}): {long_ma:.2f}")
        self.logger.info(f"  前MA({short_period}): {prev_short_ma:.2f}")
        
        # 做多信号检查
        long_cond1 = short_ma > long_ma
        long_cond2 = current_price > short_ma
        long_cond3 = short_ma > prev_short_ma
        self.logger.info(f"  做多条件: MA交叉={long_cond1}, 价格>{short_period}MA={long_cond2}, MA上升={long_cond3}")
        
        if long_cond1 and long_cond2 and long_cond3:
            self.logger.info(f"📈 做多信号: 短MA={short_ma:.2f} > 长MA={long_ma:.2f}")
            return 'long'
        
        # 做空信号检查
        short_cond1 = short_ma < long_ma
        short_cond2 = current_price < short_ma
        short_cond3 = short_ma < prev_short_ma
        self.logger.info(f"  做空条件: MA交叉={short_cond1}, 价格<{short_period}MA={short_cond2}, MA下降={short_cond3}")
        
        if short_cond1 and short_cond2 and short_cond3:
            self.logger.info(f"📉 做空信号: 短MA={short_ma:.2f} < 长MA={long_ma:.2f}")
            return 'short'
        
        self.logger.info(f"  结论: 无信号")
        
        # 构建详细的信号分析数据
        signal_type = None
        reason = ""
        
        if long_cond1 and long_cond2 and long_cond3:
            signal_type = 'long'
            reason = "所有做多条件满足，开仓做多"
        elif short_cond1 and short_cond2 and short_cond3:
            signal_type = 'short'
            reason = "所有做空条件满足，开仓做空"
        else:
            # 分析为什么没有信号
            if not long_cond1 and not short_cond1:
                reason = "等待MA交叉：MA5与MA20距离过近"
            elif long_cond1:
                if not long_cond2:
                    reason = "等待价格突破：价格需要突破MA5"
                elif not long_cond3:
                    reason = "等待趋势确认：MA5需要持续上升"
            elif short_cond1:
                if not short_cond2:
                    reason = "等待价格突破：价格需要跌破MA5"
                elif not short_cond3:
                    reason = "等待趋势确认：MA5需要持续下降"
        
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
            direction: 'long' 或 'short'
        """
        try:
            # 处理direction参数
            if isinstance(direction, dict):
                direction = direction.get('direction', direction)
            
            # 检查安全限制
            if not self.check_safety_limits():
                self.logger.warning("未通过安全检查，取消开仓")
                return False
            
            # 检查是否已有持仓
            if self.rolling_manager.current_position:
                self.logger.warning("已有持仓，不能重复开仓")
                return False
            
            # 更新资金
            self.update_capital()
            
            # 使用滚仓管理器计算仓位
            margin, size = self.rolling_manager.calculate_position_size(
                self.capital,
                self.trader.get_current_price()
            )
            
            if margin <= 0 or size <= 0:
                self.logger.warning("仓位计算为0，取消开仓")
                return False
            
            # 获取当前价格
            entry_price = self.trader.get_current_price()
            if not entry_price:
                return False
            
            # 执行开仓
            if direction == 'long':
                order = self.trader.open_long(margin)
            else:
                order = self.trader.open_short(margin)
            
            if not order:
                return False
            
            # 在滚仓管理器中创建持仓记录
            position = self.rolling_manager.create_position(
                entry_price=entry_price,
                size=size,
                side=direction,
                margin=margin,
                balance=self.capital
            )
            
            self.daily_trades += 1
            
            self.logger.info(f"✓ 开仓成功: {direction.upper()} {size}张 @ {entry_price:.1f}, "
                           f"保证金={margin:.2f}U, 阶段={position.stage}")
            
            # 保存状态
            self.rolling_manager.save_state()
            
            return True
            
        except Exception as e:
            self.logger.error(f"开仓失败: {e}", exc_info=True)
            return False
    
    def check_add_position(self):
        """
        检查并执行加仓
        """
        try:
            if not self.rolling_manager.current_position:
                return False
            
            # 更新资金
            self.update_capital()
            
            # 获取当前价格并更新盈亏
            current_price = self.trader.get_current_price()
            self.rolling_manager.update_position_pnl(current_price)
            
            # 检查是否应该加仓
            should_add, add_margin, reason = self.rolling_manager.should_add_position(self.capital)
            
            if not should_add:
                self.logger.debug(f"暂不加仓: {reason}")
                return False
            
            self.logger.info(f"🔄 准备加仓: {reason}")
            
            # 计算加仓数量
            add_size = int(add_margin * self.trader.leverage)
            
            if add_size <= 0:
                self.logger.warning("加仓数量为0，取消加仓")
                return False
            
            # 执行加仓
            pos = self.rolling_manager.current_position
            if pos.side == 'long':
                order = self.trader.open_long(add_margin)
            else:
                order = self.trader.open_short(add_margin)
            
            if not order:
                return False
            
            # 更新滚仓管理器中的持仓
            self.rolling_manager.add_position(current_price, add_size, add_margin)
            
            self.logger.info(f"✓ 加仓成功: {add_size}张 @ {current_price:.1f}, "
                           f"加仓保证金={add_margin:.2f}U")
            
            # 保存状态
            self.rolling_manager.save_state()
            
            return True
            
        except Exception as e:
            self.logger.error(f"加仓失败: {e}", exc_info=True)
            return False
    
    def check_partial_close(self):
        """
        检查并执行分批平仓
        """
        try:
            if not self.rolling_manager.current_position:
                return False
            
            # 获取当前价格并更新盈亏
            current_price = self.trader.get_current_price()
            self.rolling_manager.update_position_pnl(current_price)
            
            # 检查是否应该分批平仓
            should_close, close_ratio, reason = self.rolling_manager.should_partial_close()
            
            if not should_close:
                return False
            
            self.logger.info(f"📊 准备分批平仓: {reason}")
            
            # 获取实际持仓
            positions = self.trader.get_positions()
            if not positions:
                self.logger.warning("API查询无持仓")
                return False
            
            # 计算平仓数量
            pos = self.rolling_manager.current_position
            close_size = int(pos.size * close_ratio)
            
            # 执行部分平仓
            for api_pos in positions:
                # 计算要平的数量
                current_size = abs(api_pos.get('currentQty', 0))
                partial_size = int(current_size * close_ratio)
                
                if partial_size > 0:
                    order = self.trader.close_position(api_pos, size=partial_size)
                    if not order:
                        return False
            
            # 更新滚仓管理器
            record = self.rolling_manager.close_position(current_price, close_ratio)
            
            if record:
                self.daily_pnl += record['pnl']
                self.logger.info(f"✓ 分批平仓成功: 平仓{close_ratio*100:.0f}%, "
                               f"盈亏={record['pnl']:.2f}U ({record['pnl_ratio']*100:.1f}%)")
                
                # 更新资金
                self.update_capital()
                
                # 保存状态
                self.rolling_manager.save_state()
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"分批平仓失败: {e}", exc_info=True)
            return False
    
    def check_stop_conditions(self):
        """
        检查止损止盈条件
        
        Returns:
            (是否触发, 原因)
        """
        if not self.rolling_manager.current_position:
            return False, "无持仓"
        
        try:
            # 获取当前价格
            current_price = self.trader.get_current_price()
            
            # 更新盈亏
            self.rolling_manager.update_position_pnl(current_price)
            
            # 更新移动止损
            self.rolling_manager.update_trailing_stop(current_price)
            
            # 检查止损止盈
            triggered, reason = self.rolling_manager.check_stop_conditions(current_price)
            
            return triggered, reason
            
        except Exception as e:
            self.logger.error(f"检查止损止盈失败: {e}")
            return False, f"检查失败: {e}"
    
    def close_position(self, reason='normal'):
        """
        平仓（滚仓版）
        
        Args:
            reason: 平仓原因
        """
        try:
            if not self.rolling_manager.current_position:
                self.logger.warning("没有持仓，无需平仓")
                return False
            
            # 获取实际持仓
            positions = self.trader.get_positions()
            if not positions:
                self.logger.warning("API查询无持仓，清除本地记录")
                self.rolling_manager.current_position = None
                return False
            
            # 平仓所有持仓
            for pos in positions:
                order = self.trader.close_position(pos)
                if not order:
                    return False
            
            # 获取平仓价格
            close_price = self.trader.get_current_price()
            
            # 在滚仓管理器中记录平仓
            record = self.rolling_manager.close_position(close_price, 1.0)
            
            if record:
                self.daily_pnl += record['pnl']
                self.daily_trades += 1
                
                self.logger.info(f"✓ 平仓成功: {reason}, "
                               f"盈亏={record['pnl']:.2f}U ({record['pnl_ratio']*100:.1f}%), "
                               f"持续时间={record['duration']/60:.1f}分钟")
                
                # 更新资金
                self.update_capital()
                
                # 保存状态
                self.rolling_manager.save_state()
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"平仓失败: {e}", exc_info=True)
            return False
    
    def run_cycle(self):
        """
        运行一个交易周期
        
        Returns:
            状态字典
        """
        try:
            # 更新资金
            self.update_capital()
            
            # 检查安全限制
            if not self.check_safety_limits():
                return {
                    'status': 'paused',
                    'reason': '安全限制',
                    'balance': self.capital
                }
            
            # 如果有持仓，检查各种条件
            if self.rolling_manager.current_position:
                # 1. 检查止损止盈
                triggered, reason = self.check_stop_conditions()
                if triggered:
                    self.logger.info(f"触发平仓: {reason}")
                    self.close_position(reason)
                    return {
                        'status': 'closed',
                        'reason': reason,
                        'balance': self.capital
                    }
                
                # 2. 检查分批平仓
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
            
            # 如果没有持仓，检查开仓信号
            else:
                # 获取K线数据
                ohlcv = self.trader.get_klines(symbol=self.symbol, limit=30)
                if not ohlcv:
                    return {
                        'status': 'waiting',
                        'reason': '无K线数据',
                        'balance': self.capital
                    }
                
                # 生成信号
                signal_result = self.generate_signal(ohlcv)
                
                # 保存信号分析数据
                if signal_result and isinstance(signal_result, dict):
                    signal = signal_result.get('signal')
                    self.last_signal_analysis = signal_result.get('analysis')
                else:
                    signal = signal_result
                    self.last_signal_analysis = None
                
                if signal:
                    self.logger.info(f"检测到信号: {signal}")
                    if self.open_position(signal):
                        return {
                            'status': 'opened',
                            'direction': signal,
                            'balance': self.capital,
                            'signal_analysis': self.last_signal_analysis
                        }
                
                return {
                    'status': 'waiting',
                    'reason': '无信号',
                    'balance': self.capital,
                    'signal_analysis': self.last_signal_analysis
                }
        
        except Exception as e:
            self.logger.error(f"运行周期失败: {e}", exc_info=True)
            return {
                'status': 'error',
                'reason': str(e),
                'balance': self.capital
            }
    
    def get_status(self):
        """
        获取策略状态
        
        Returns:
            状态字典
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
        """重置紧急停止状态"""
        self.emergency_stopped = False
        self.rolling_manager.reset_pause()
        self.logger.info("重置紧急停止状态")


if __name__ == '__main__':
    """测试代码"""
    print("=" * 60)
    print("10U战神滚仓策略引擎 - 测试")
    print("=" * 60)
    
    # 这里需要实际的trader对象才能测试
    print("需要实际的KuCoinTrader对象才能运行测试")
    print("请在主程序中使用此引擎")
