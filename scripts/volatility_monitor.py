#!/usr/bin/env python3
"""
Volatility率Monitor模块
RealtimeMonitor市场Volatility率，assessmentRisklevel，并提供Positionsuggest
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta


class VolatilityMonitor:
 """Volatility率Monitor器"""
 
 def __init__(self):
 """InitializeVolatility率Monitor器"""
 self.price_history: List[float] = []
 self.high_history: List[float] = []
 self.low_history: List[float] = []
 self.close_history: List[float] = []
 
 # Volatility率阈值Config
 self.volatility_thresholds = {
 'low': 0.02, # 低Volatility：< 2%
 'medium': 0.05, # inVolatility：2-5%
 'high': 0.10, # 高Volatility：5-10%
 'extreme': 0.10 # 极端Volatility：> 10%
 }
 
 # Positionadjustmultiplier
 self.position_multipliers = {
 'low': 1.0, # 低Volatility：正常Position
 'medium': 0.7, # inVolatility：70%Position
 'high': 0.4, # 高Volatility：40%Position
 'extreme': 0.0 # 极端Volatility：StopTrade
 }
 
 def add_price_data(
 self,
 high: float,
 low: float,
 close: float,
 max_history: int = 100
):
 """
 添加Price数据
 
 Args:
 high: 最高价
 low: 最低价
 close: 收盘价
 max_history: MaxHistory数据量
 """
 self.high_history.append(high)
 self.low_history.append(low)
 self.close_history.append(close)
 
 # limitHistory数据量
 if len(self.close_history) > max_history:
 self.high_history = self.high_history[-max_history:]
 self.low_history = self.low_history[-max_history:]
 self.close_history = self.close_history[-max_history:]
 
 def calculate_atr(self, period: int = 14) -> Optional[float]:
 """
 CalculateATR（平均真实波幅）
 
 Args:
 period: ATRcycle
 
 Returns:
 ATR值，如果数据not足返回None
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
 
 # CalculateATR（简单移动平均）
 if len(true_ranges) >= period:
 atr = np.mean(true_ranges[-period:])
 return atr
 
 return None
 
 def calculate_historical_volatility(self, period: int = 20) -> Optional[float]:
 """
 CalculateHistoryVolatility率（标准差）
 
 Args:
 period: Calculatecycle
 
 Returns:
 Volatility率（百分比），如果数据not足返回None
 """
 if len(self.close_history) < period + 1:
 return None
 
 # Calculatereturn rate
 returns = []
 for i in range(1, len(self.close_history)):
 ret = (self.close_history[i] - self.close_history[i-1]) / self.close_history[i-1]
 returns.append(ret)
 
 # Calculate标准差
 if len(returns) >= period:
 volatility = np.std(returns[-period:])
 return volatility
 
 return None
 
 def calculate_volatility_trend(self, short_period: int = 5, long_period: int = 20) -> Optional[str]:
 """
 CalculateVolatility率trend
 
 Args:
 short_period: 短期cycle
 long_period: 长期cycle
 
 Returns:
 'increasing' | 'decreasing' | 'stable' | None
 """
 short_vol = self.calculate_historical_volatility(short_period)
 long_vol = self.calculate_historical_volatility(long_period)
 
 if short_vol is None or long_vol is None:
 return None
 
 # Volatility率变化exceed20%认asistrend
 change_ratio = (short_vol - long_vol) / long_vol
 
 if change_ratio > 0.2:
 return 'increasing'
 elif change_ratio < -0.2:
 return 'decreasing'
 else:
 return 'stable'
 
 def assess_risk_level(self) -> Dict:
 """
 assessmentRisklevel
 
 Returns:
 Riskassessmentresult字典
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
 'message': '数据not足，No法assessmentRisk'
 }
 
 # 确定Risklevel
 if volatility < self.volatility_thresholds['low']:
 level = 'low'
 message = '市场Volatility较小，Risk较低'
 elif volatility < self.volatility_thresholds['medium']:
 level = 'medium'
 message = '市场Volatility正常，Risk适in'
 elif volatility < self.volatility_thresholds['high']:
 level = 'high'
 message = '市场Volatility较大，Risk较高'
 else:
 level = 'extreme'
 message = '市场剧烈Volatility，Risk极高'
 
 # GetPositionadjustmultiplier
 position_multiplier = self.position_multipliers[level]
 
 # is否should该PauseTrade
 should_pause = (level == 'extreme')
 
 # 如果Volatility率trend上升，降低Position
 if trend == 'increasing' and level in ['medium', 'high']:
 position_multiplier *= 0.8
 message += '，Volatility率上升trend'
 
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
 CalculatesafePosition大小
 
 Args:
 base_position: basePosition大小
 current_price: CurrentPrice
 account_balance: accountBalance
 
 Returns:
 Positionsuggest字典
 """
 risk_assessment = self.assess_risk_level()
 
 # 根据RiskleveladjustPosition
 multiplier = risk_assessment['position_multiplier']
 safe_position = base_position * multiplier
 
 # CalculatePositionvalue占accountBalance比例
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
 判断is否should该PauseTrade
 
 Returns:
 (is否Pause, reason)
 """
 risk_assessment = self.assess_risk_level()
 
 if risk_assessment['should_pause']:
 return True, risk_assessment['message']
 
 return False, '市场状况正常'
 
 def get_status_report(self) -> Dict:
 """
 GetVolatility率MonitorStatus报告
 
 Returns:
 Status报告字典
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
 
 # 模拟添加Price数据
 base_price = 50000
 for i in range(30):
 # 模拟PriceVolatility
 volatility = 0.02 + (i / 30) * 0.08 # Volatility率from2%逐渐增加to10%
 high = base_price * (1 + volatility * np.random.random())
 low = base_price * (1 - volatility * np.random.random())
 close = base_price * (1 + volatility * (np.random.random() - 0.5))
 
 monitor.add_price_data(high, low, close)
 base_price = close
 
 # GetRiskassessment
 risk = monitor.assess_risk_level()
 print(f"\nRiskassessment:")
 print(f" level: {risk['level']}")
 print(f" Volatility: {risk['volatility']:.4f} ({risk['volatility']*100:.2f}%)")
 print(f" ATR: {risk['atr']:.2f}")
 print(f" trend: {risk['trend']}")
 print(f" Positionmultiplier: {risk['position_multiplier']:.2f}")
 print(f" shouldPause: {risk['should_pause']}")
 print(f" description: {risk['message']}")
 
 # GetPositionsuggest
 position_advice = monitor.get_safe_position_size(
 base_position=0.1,
 current_price=base_price,
 account_balance=10000
)
 print(f"\nPositionsuggest:")
 print(f" basePosition: {position_advice['base_position']}")
 print(f" safePosition: {position_advice['safe_position']:.4f}")
 print(f" adjustmultiplier: {position_advice['multiplier']:.2f}")
 print(f" Positionvalue: ${position_advice['position_value']:.2f}")
 print(f" ratio: {position_advice['position_ratio']*100:.2f}%")
 
 # 判断is否Pause
 should_pause, reason = monitor.should_pause_trading()
 print(f"\nTradeStatus:")
 print(f" shouldPause: {should_pause}")
 print(f" reason: {reason}")
