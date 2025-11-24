#!/usr/bin/env python3
"""
波动率监控模块
实时监控市场波动率，评估风险等级，并提供仓位建议
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta


class VolatilityMonitor:
    """波动率监控器"""
    
    def __init__(self):
        """初始化波动率监控器"""
        self.price_history: List[float] = []
        self.high_history: List[float] = []
        self.low_history: List[float] = []
        self.close_history: List[float] = []
        
        # 波动率阈值配置
        self.volatility_thresholds = {
            'low': 0.02,      # 低波动：< 2%
            'medium': 0.05,   # 中波动：2-5%
            'high': 0.10,     # 高波动：5-10%
            'extreme': 0.10   # 极端波动：> 10%
        }
        
        # 仓位调整系数
        self.position_multipliers = {
            'low': 1.0,       # 低波动：正常仓位
            'medium': 0.7,    # 中波动：70%仓位
            'high': 0.4,      # 高波动：40%仓位
            'extreme': 0.0    # 极端波动：停止交易
        }
    
    def add_price_data(
        self,
        high: float,
        low: float,
        close: float,
        max_history: int = 100
    ):
        """
        添加价格数据
        
        Args:
            high: 最高价
            low: 最低价
            close: 收盘价
            max_history: 最大历史数据量
        """
        self.high_history.append(high)
        self.low_history.append(low)
        self.close_history.append(close)
        
        # 限制历史数据量
        if len(self.close_history) > max_history:
            self.high_history = self.high_history[-max_history:]
            self.low_history = self.low_history[-max_history:]
            self.close_history = self.close_history[-max_history:]
    
    def calculate_atr(self, period: int = 14) -> Optional[float]:
        """
        计算ATR（平均真实波幅）
        
        Args:
            period: ATR周期
        
        Returns:
            ATR值，如果数据不足返回None
        """
        if len(self.close_history) < period + 1:
            return None
        
        true_ranges = []
        for i in range(1, len(self.close_history)):
            high = self.high_history[i]
            low = self.low_history[i]
            prev_close = self.close_history[i-1]
            
            # 真实波幅 = max(high-low, abs(high-prev_close), abs(low-prev_close))
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        # 计算ATR（简单移动平均）
        if len(true_ranges) >= period:
            atr = np.mean(true_ranges[-period:])
            return atr
        
        return None
    
    def calculate_historical_volatility(self, period: int = 20) -> Optional[float]:
        """
        计算历史波动率（标准差）
        
        Args:
            period: 计算周期
        
        Returns:
            波动率（百分比），如果数据不足返回None
        """
        if len(self.close_history) < period + 1:
            return None
        
        # 计算收益率
        returns = []
        for i in range(1, len(self.close_history)):
            ret = (self.close_history[i] - self.close_history[i-1]) / self.close_history[i-1]
            returns.append(ret)
        
        # 计算标准差
        if len(returns) >= period:
            volatility = np.std(returns[-period:])
            return volatility
        
        return None
    
    def calculate_volatility_trend(self, short_period: int = 5, long_period: int = 20) -> Optional[str]:
        """
        计算波动率趋势
        
        Args:
            short_period: 短期周期
            long_period: 长期周期
        
        Returns:
            'increasing' | 'decreasing' | 'stable' | None
        """
        short_vol = self.calculate_historical_volatility(short_period)
        long_vol = self.calculate_historical_volatility(long_period)
        
        if short_vol is None or long_vol is None:
            return None
        
        # 波动率变化超过20%认为是趋势
        change_ratio = (short_vol - long_vol) / long_vol
        
        if change_ratio > 0.2:
            return 'increasing'
        elif change_ratio < -0.2:
            return 'decreasing'
        else:
            return 'stable'
    
    def assess_risk_level(self) -> Dict:
        """
        评估风险等级
        
        Returns:
            风险评估结果字典
        """
        atr = self.calculate_atr()
        volatility = self.calculate_historical_volatility()
        trend = self.calculate_volatility_trend()
        
        if volatility is None:
            return {
                'level': 'unknown',
                'volatility': None,
                'atr': None,
                'trend': None,
                'position_multiplier': 0.5,
                'should_pause': False,
                'message': '数据不足，无法评估风险'
            }
        
        # 确定风险等级
        if volatility < self.volatility_thresholds['low']:
            level = 'low'
            message = '市场波动较小，风险较低'
        elif volatility < self.volatility_thresholds['medium']:
            level = 'medium'
            message = '市场波动正常，风险适中'
        elif volatility < self.volatility_thresholds['high']:
            level = 'high'
            message = '市场波动较大，风险较高'
        else:
            level = 'extreme'
            message = '市场剧烈波动，风险极高'
        
        # 获取仓位调整系数
        position_multiplier = self.position_multipliers[level]
        
        # 是否应该暂停交易
        should_pause = (level == 'extreme')
        
        # 如果波动率趋势上升，降低仓位
        if trend == 'increasing' and level in ['medium', 'high']:
            position_multiplier *= 0.8
            message += '，波动率上升趋势'
        
        return {
            'level': level,
            'volatility': volatility,
            'atr': atr,
            'trend': trend,
            'position_multiplier': position_multiplier,
            'should_pause': should_pause,
            'message': message
        }
    
    def get_safe_position_size(
        self,
        base_position: float,
        current_price: float,
        account_balance: float
    ) -> Dict:
        """
        计算安全仓位大小
        
        Args:
            base_position: 基础仓位大小
            current_price: 当前价格
            account_balance: 账户余额
        
        Returns:
            仓位建议字典
        """
        risk_assessment = self.assess_risk_level()
        
        # 根据风险等级调整仓位
        multiplier = risk_assessment['position_multiplier']
        safe_position = base_position * multiplier
        
        # 计算仓位价值占账户余额的比例
        position_value = safe_position * current_price
        position_ratio = position_value / account_balance if account_balance > 0 else 0
        
        return {
            'base_position': base_position,
            'safe_position': safe_position,
            'multiplier': multiplier,
            'position_value': position_value,
            'position_ratio': position_ratio,
            'risk_level': risk_assessment['level'],
            'should_pause': risk_assessment['should_pause'],
            'message': risk_assessment['message']
        }
    
    def should_pause_trading(self) -> Tuple[bool, str]:
        """
        判断是否应该暂停交易
        
        Returns:
            (是否暂停, 原因)
        """
        risk_assessment = self.assess_risk_level()
        
        if risk_assessment['should_pause']:
            return True, risk_assessment['message']
        
        return False, '市场状况正常'
    
    def get_status_report(self) -> Dict:
        """
        获取波动率监控状态报告
        
        Returns:
            状态报告字典
        """
        risk_assessment = self.assess_risk_level()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'data_points': len(self.close_history),
            'current_price': self.close_history[-1] if self.close_history else None,
            'risk_assessment': risk_assessment,
            'thresholds': self.volatility_thresholds,
            'position_multipliers': self.position_multipliers
        }


# 使用示例
if __name__ == "__main__":
    monitor = VolatilityMonitor()
    
    # 模拟添加价格数据
    base_price = 50000
    for i in range(30):
        # 模拟价格波动
        volatility = 0.02 + (i / 30) * 0.08  # 波动率从2%逐渐增加到10%
        high = base_price * (1 + volatility * np.random.random())
        low = base_price * (1 - volatility * np.random.random())
        close = base_price * (1 + volatility * (np.random.random() - 0.5))
        
        monitor.add_price_data(high, low, close)
        base_price = close
    
    # 获取风险评估
    risk = monitor.assess_risk_level()
    print(f"\n风险评估:")
    print(f"  等级: {risk['level']}")
    print(f"  波动率: {risk['volatility']:.4f} ({risk['volatility']*100:.2f}%)")
    print(f"  ATR: {risk['atr']:.2f}")
    print(f"  趋势: {risk['trend']}")
    print(f"  仓位系数: {risk['position_multiplier']:.2f}")
    print(f"  应暂停: {risk['should_pause']}")
    print(f"  说明: {risk['message']}")
    
    # 获取仓位建议
    position_advice = monitor.get_safe_position_size(
        base_position=0.1,
        current_price=base_price,
        account_balance=10000
    )
    print(f"\n仓位建议:")
    print(f"  基础仓位: {position_advice['base_position']}")
    print(f"  安全仓位: {position_advice['safe_position']:.4f}")
    print(f"  调整系数: {position_advice['multiplier']:.2f}")
    print(f"  仓位价值: ${position_advice['position_value']:.2f}")
    print(f"  占比: {position_advice['position_ratio']*100:.2f}%")
    
    # 判断是否暂停
    should_pause, reason = monitor.should_pause_trading()
    print(f"\n交易状态:")
    print(f"  应暂停: {should_pause}")
    print(f"  原因: {reason}")
