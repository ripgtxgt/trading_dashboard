#!/usr/bin/env python3
"""
动态仓位管理器
根据市场波动率自动调整仓位大小, 降低风险
"""

from volatility_monitor import VolatilityMonitor
from typing import Dict, Optional
from datetime import datetime
import json


class DynamicPositionManager:
    """动态仓位管理器"""
    
    def __init__(
        self,
        base_position_size: float = 0.01,
        max_position_size: float = 0.1,
        min_position_size: float = 0.001,
        account_balance: float = 100.0
    ):
        """
        初始化动态仓位管理器
        
        Args:
            base_position_size: 基础仓位大小
            max_position_size: 最大仓位大小
            min_position_size: 最小仓位大小
            account_balance: 账户余额
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
        更新市场数据
        
        Args:
            high: 最高价
            low: 最低价
            close: 收盘价
        """
        self.volatility_monitor.add_price_data(high, low, close)
    
    def calculate_optimal_position(self, current_price: float) -> Dict:
        """
        计算最优仓位
        
        Args:
            current_price: 当前价格
        
        Returns:
            仓位计算结果
        """
        # 获取风险评估
        risk_assessment = self.volatility_monitor.assess_risk_level()
        
        # 根据风险等级调整仓位
        multiplier = risk_assessment['position_multiplier']
        optimal_position = self.base_position_size * multiplier
        
        # 限制在最小和最大仓位之间
        optimal_position = max(self.min_position_size, min(optimal_position, self.max_position_size))
        
        # 如果应该暂停交易, 仓位设为0
        if risk_assessment['should_pause']:
            optimal_position = 0.0
        
        # 计算仓位价值
        position_value = optimal_position * current_price
        position_ratio = position_value / self.account_balance if self.account_balance > 0 else 0
        
        # 计算与当前仓位的变化
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
        调整仓位
        
        Args:
            current_price: 当前价格
            force: 是否强制调整(忽略最小变化阈值)
        
        Returns:
            调整结果
        """
        calculation = self.calculate_optimal_position(current_price)
        
        # 只有当变化超过5%或强制调整时才执行
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
            
            # 记录调整历史
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
                'message': f"仓位已调整: {old_position:.4f} -> {new_position:.4f} ({calculation['change_ratio']:+.2f}%)"
            }
        else:
            return {
                'adjusted': False,
                'current_position': self.current_position_size,
                'optimal_position': calculation['optimal_position'],
                'change_ratio': calculation['change_ratio'],
                'message': f"仓位变化较小 ({calculation['change_ratio']:+.2f}%), 无需调整"
            }
    
    def get_position_recommendation(self, current_price: float) -> Dict:
        """
        获取仓位建议(不实际调整)
        
        Args:
            current_price: 当前价格
        
        Returns:
            仓位建议
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
        获取仓位调整历史
        
        Args:
            limit: 返回的最大记录数
        
        Returns:
            调整历史列表
        """
        return self.position_history[-limit:]
    
    def reset_position(self):
        """重置仓位到基础值"""
        self.current_position_size = self.base_position_size
        self.position_history.append({
            'timestamp': datetime.now().isoformat(),
            'old_position': self.current_position_size,
            'new_position': self.base_position_size,
            'change': 0,
            'change_ratio': 0,
            'risk_level': 'unknown',
            'reason': '手动重置'
        })
    
    def get_status(self) -> Dict:
        """
        获取管理器状态
        
        Returns:
            状态字典
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
    
    print("===  ===\n")
    
    # 初始化管理器
    manager = DynamicPositionManager(
        base_position_size=0.01,
        max_position_size=0.1,
        min_position_size=0.001,
        account_balance=100.0
    )
    
    # 模拟市场数据
    base_price = 50000
    print("...\n")
    
    for i in range(30):
        # 模拟不同波动率场景
        if i < 10:
            # 低波动期
            volatility = 0.01
            scenario = "低波动期"
        elif i < 20:
            # 中波动期
            volatility = 0.04
            scenario = "中波动期"
        else:
            # 高波动期
            volatility = 0.12
            scenario = "高波动期"
        
        high = base_price * (1 + volatility * np.random.random())
        low = base_price * (1 - volatility * np.random.random())
        close = base_price * (1 + volatility * (np.random.random() - 0.5))
        
        manager.update_market_data(high, low, close)
        base_price = close
        
        # 每5个周期检查一次仓位
        if (i + 1) % 5 == 0:
            print(f"--- Period {i+1} ({scenario}) ---")
            
            # 获取仓位建议
            recommendation = manager.get_position_recommendation(close)
            print(f"CurrentPrice: ${close:.2f}")
            print(f"Risk: {recommendation['risk_level']}")
            vol_display = f"{recommendation['volatility']*100:.2f}%" if recommendation['volatility'] is not None else "N/A"
            print(f": {vol_display}")
            print(f"Current: {recommendation['current_position']:.4f}")
            print(f": {recommendation['recommended_position']:.4f}")
            print(f": {recommendation['change_ratio']:+.2f}%")
            print(f": {recommendation['message']}")
            
            # 执行仓位调整
            adjustment = manager.adjust_position(close)
            if adjustment['adjusted']:
                print(f"[OK] {adjustment['message']}")
            else:
                print(f"o {adjustment['message']}")
            
            print()
    
    # 显示调整历史
    print("\n=== History ===")
    history = manager.get_adjustment_history()
    for record in history:
        print(f"{record['timestamp']}: {record['old_position']:.4f} -> {record['new_position']:.4f} "
              f"({record['change_ratio']:+.2f}%) - {record['reason']}")
    
    # 显示最终状态
    print("\n===  ===")
    status = manager.get_status()
    print(f"Balance: ${status['account_balance']:.2f}")
    print(f": {status['base_position_size']:.4f}")
    print(f"Current: {status['current_position_size']:.4f}")
    print(f"Risk: {status['risk_assessment']['level']}")
    print(f": {status['total_adjustments']}")
