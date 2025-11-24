#!/usr/bin/env python3
"""
动态Position管理器
根据市场Volatility率autoadjustPosition大小，降低Risk
"""

from volatility_monitor import VolatilityMonitor
from typing import Dict, Optional
from datetime import datetime
import json


class DynamicPositionManager:
 """动态Position管理器"""
 
 def __init__(
 self,
 base_position_size: float = 0.01,
 max_position_size: float = 0.1,
 min_position_size: float = 0.001,
 account_balance: float = 100.0
):
 """
 Initialize动态Position管理器
 
 Args:
 base_position_size: basePosition大小
 max_position_size: MaxPosition大小
 min_position_size: MinPosition大小
 account_balance: accountBalance
 """
 self.base_position_size = base_position_size
 self.max_position_size = max_position_size
 self.min_position_size = min_position_size
 self.account_balance = account_balance
 
 self.volatility_monitor = VolatilityMonitor()
 self.current_position_size = base_position_size
 self.position_history = []
 
 def update_market_data(self, high: float, low: float, close: float):
 """
 Update市场数据
 
 Args:
 high: 最高价
 low: 最低价
 close: 收盘价
 """
 self.volatility_monitor.add_price_data(high, low, close)
 
 def calculate_optimal_position(self, current_price: float) -> Dict:
 """
 Calculate最优Position
 
 Args:
 current_price: CurrentPrice
 
 Returns:
 PositionCalculateresult
 """
 # GetRiskassessment
 risk_assessment = self.volatility_monitor.assess_risk_level()
 
 # 根据RiskleveladjustPosition
 multiplier = risk_assessment['position_multiplier']
 optimal_position = self.base_position_size * multiplier
 
 # limitatMinandMaxPositionbetween
 optimal_position = max(self.min_position_size, min(optimal_position, self.max_position_size))
 
 # 如果should该PauseTrade，Position设as0
 if risk_assessment['should_pause']:
 optimal_position = 0.0
 
 # CalculatePositionvalue
 position_value = optimal_position * current_price
 position_ratio = position_value / self.account_balance if self.account_balance > 0 else 0
 
 # CalculateandCurrentPosition变化
 position_change = optimal_position - self.current_position_size
 change_ratio = (position_change / self.current_position_size * 100) if self.current_position_size > 0 else 0
 
 result = {
 'timestamp': datetime.now().isoformat(),
 'current_price': current_price,
 'current_position': self.current_position_size,
 'optimal_position': optimal_position,
 'position_change': position_change,
 'change_ratio': change_ratio,
 'position_value': position_value,
 'position_ratio': position_ratio,
 'risk_level': risk_assessment['level'],
 'volatility': risk_assessment['volatility'],
 'multiplier': multiplier,
 'should_pause': risk_assessment['should_pause'],
 'message': risk_assessment['message']
 }
 
 return result
 
 def adjust_position(self, current_price: float, force: bool = False) -> Dict:
 """
 adjustPosition
 
 Args:
 current_price: CurrentPrice
 force: is否强制adjust（忽略Min变化阈值）
 
 Returns:
 adjustresult
 """
 calculation = self.calculate_optimal_position(current_price)
 
 # 只Has当变化exceed5%or强制adjust时才Execute
 min_change_threshold = 0.05
 should_adjust = (
 force or
 abs(calculation['change_ratio']) > min_change_threshold * 100 or
 calculation['should_pause']
)
 
 if should_adjust:
 old_position = self.current_position_size
 new_position = calculation['optimal_position']
 
 self.current_position_size = new_position
 
 # RecordadjustHistory
 adjustment_record = {
 'timestamp': calculation['timestamp'],
 'old_position': old_position,
 'new_position': new_position,
 'change': calculation['position_change'],
 'change_ratio': calculation['change_ratio'],
 'risk_level': calculation['risk_level'],
 'reason': calculation['message']
 }
 self.position_history.append(adjustment_record)
 
 return {
 'adjusted': True,
 'old_position': old_position,
 'new_position': new_position,
 'change': calculation['position_change'],
 'change_ratio': calculation['change_ratio'],
 'risk_level': calculation['risk_level'],
 'message': f"PositionAlreadyadjust: {old_position:.4f} → {new_position:.4f} ({calculation['change_ratio']:+.2f}%)"
 }
 else:
 return {
 'adjusted': False,
 'current_position': self.current_position_size,
 'optimal_position': calculation['optimal_position'],
 'change_ratio': calculation['change_ratio'],
 'message': f"Position变化较小 ({calculation['change_ratio']:+.2f}%)，No需adjust"
 }
 
 def get_position_recommendation(self, current_price: float) -> Dict:
 """
 GetPositionsuggest（not实际adjust）
 
 Args:
 current_price: CurrentPrice
 
 Returns:
 Positionsuggest
 """
 calculation = self.calculate_optimal_position(current_price)
 
 return {
 'current_position': self.current_position_size,
 'recommended_position': calculation['optimal_position'],
 'change_needed': calculation['position_change'],
 'change_ratio': calculation['change_ratio'],
 'risk_level': calculation['risk_level'],
 'volatility': calculation['volatility'],
 'should_pause': calculation['should_pause'],
 'message': calculation['message'],
 'position_value': calculation['position_value'],
 'position_ratio': calculation['position_ratio']
 }
 
 def get_adjustment_history(self, limit: int = 10) -> list:
 """
 GetPositionadjustHistory
 
 Args:
 limit: 返回MaxRecord数
 
 Returns:
 adjustHistory列表
 """
 return self.position_history[-limit:]
 
 def reset_position(self):
 """重置Positiontobase值"""
 self.current_position_size = self.base_position_size
 self.position_history.append({
 'timestamp': datetime.now().isoformat(),
 'old_position': self.current_position_size,
 'new_position': self.base_position_size,
 'change': 0,
 'change_ratio': 0,
 'risk_level': 'unknown',
 'reason': 'manual重置'
 })
 
 def get_status(self) -> Dict:
 """
 Get管理器Status
 
 Returns:
 Status字典
 """
 risk_assessment = self.volatility_monitor.assess_risk_level()
 
 return {
 'timestamp': datetime.now().isoformat(),
 'account_balance': self.account_balance,
 'base_position_size': self.base_position_size,
 'current_position_size': self.current_position_size,
 'max_position_size': self.max_position_size,
 'min_position_size': self.min_position_size,
 'risk_assessment': risk_assessment,
 'total_adjustments': len(self.position_history)
 }


# 使用示例
if __name__ == "__main__":
 import numpy as np
 
 print("=== Position ===\n")
 
 # Initialize管理器
 manager = DynamicPositionManager(
 base_position_size=0.01,
 max_position_size=0.1,
 min_position_size=0.001,
 account_balance=100.0
)
 
 # 模拟市场数据
 base_price = 50000
 print("Volatility...\n")
 
 for i in range(30):
 # 模拟not同Volatility率场景
 if i < 10:
 # 低Volatility期
 volatility = 0.01
 scenario = "低Volatility期"
 elif i < 20:
 # inVolatility期
 volatility = 0.04
 scenario = "inVolatility期"
 else:
 # 高Volatility期
 volatility = 0.12
 scenario = "高Volatility期"
 
 high = base_price * (1 + volatility * np.random.random())
 low = base_price * (1 - volatility * np.random.random())
 close = base_price * (1 + volatility * (np.random.random() - 0.5))
 
 manager.update_market_data(high, low, close)
 base_price = close
 
 # 每5cycle检查一timesPosition
 if (i + 1) % 5 == 0:
 print(f"--- cycle {i+1} ({scenario}) ---")
 
 # GetPositionsuggest
 recommendation = manager.get_position_recommendation(close)
 print(f"CurrentPrice: ${close:.2f}")
 print(f"Risklevel: {recommendation['risk_level']}")
 vol_display = f"{recommendation['volatility']*100:.2f}%" if recommendation['volatility'] is not None else "N/A"
 print(f"Volatility: {vol_display}")
 print(f"CurrentPosition: {recommendation['current_position']:.4f}")
 print(f"suggestPosition: {recommendation['recommended_position']:.4f}")
 print(f": {recommendation['change_ratio']:+.2f}%")
 print(f"description: {recommendation['message']}")
 
 # ExecutePositionadjust
 adjustment = manager.adjust_position(close)
 if adjustment['adjusted']:
 print(f"[OK] {adjustment['message']}")
 else:
 print(f" {adjustment['message']}")
 
 print()
 
 # 显示adjustHistory
 print("\n=== PositionadjustHistory ===")
 history = manager.get_adjustment_history()
 for record in history:
 print(f"{record['timestamp']}: {record['old_position']:.4f}  {record['new_position']:.4f} "
 f"({record['change_ratio']:+.2f}%) - {record['reason']}")
 
 # 显示finalStatus
 print("\n=== finalStatus ===")
 status = manager.get_status()
 print(f"accountBalance: ${status['account_balance']:.2f}")
 print(f"basePosition: {status['base_position_size']:.4f}")
 print(f"CurrentPosition: {status['current_position_size']:.4f}")
 print(f"Risklevel: {status['risk_assessment']['level']}")
 print(f"adjustcount: {status['total_adjustments']}")
