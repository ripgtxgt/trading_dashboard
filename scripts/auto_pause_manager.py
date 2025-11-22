#!/usr/bin/env python3
"""
自动暂停交易管理器
当市场剧烈波动时自动暂停交易，保护资金安全
"""

from volatility_monitor import VolatilityMonitor
from typing import Dict, Optional
from datetime import datetime, timedelta
import json


class AutoPauseManager:
    """自动暂停交易管理器"""
    
    def __init__(
        self,
        extreme_volatility_threshold: float = 0.10,  # 10%波动率触发暂停
        auto_resume_enabled: bool = True,
        resume_volatility_threshold: float = 0.05,   # 5%波动率自动恢复
        min_pause_duration: int = 300,  # 最小暂停时间（秒）
        max_pause_duration: int = 3600  # 最大暂停时间（秒）
    ):
        """
        初始化自动暂停管理器
        
        Args:
            extreme_volatility_threshold: 极端波动率阈值
            auto_resume_enabled: 是否启用自动恢复
            resume_volatility_threshold: 恢复交易的波动率阈值
            min_pause_duration: 最小暂停时间
            max_pause_duration: 最大暂停时间
        """
        self.extreme_volatility_threshold = extreme_volatility_threshold
        self.auto_resume_enabled = auto_resume_enabled
        self.resume_volatility_threshold = resume_volatility_threshold
        self.min_pause_duration = min_pause_duration
        self.max_pause_duration = max_pause_duration
        
        self.volatility_monitor = VolatilityMonitor()
        self.is_paused = False
        self.pause_start_time: Optional[datetime] = None
        self.pause_reason: str = ""
        self.pause_history = []
    
    def update_market_data(self, high: float, low: float, close: float):
        """
        更新市场数据
        
        Args:
            high: 最高价
            low: 最低价
            close: 收盘价
        """
        self.volatility_monitor.add_price_data(high, low, close)
    
    def check_should_pause(self) -> tuple[bool, str]:
        """
        检查是否应该暂停交易
        
        Returns:
            (是否应暂停, 原因)
        """
        risk_assessment = self.volatility_monitor.assess_risk_level()
        
        # 如果已经暂停，不需要重复检查
        if self.is_paused:
            return False, "已处于暂停状态"
        
        # 检查是否达到极端波动
        if risk_assessment['should_pause']:
            return True, risk_assessment['message']
        
        # 检查波动率是否超过阈值
        if risk_assessment['volatility'] is not None:
            if risk_assessment['volatility'] > self.extreme_volatility_threshold:
                return True, f"波动率 {risk_assessment['volatility']*100:.2f}% 超过阈值 {self.extreme_volatility_threshold*100:.2f}%"
        
        return False, "市场状况正常"
    
    def check_should_resume(self) -> tuple[bool, str]:
        """
        检查是否应该恢复交易
        
        Returns:
            (是否应恢复, 原因)
        """
        # 如果未暂停，不需要检查
        if not self.is_paused:
            return False, "未处于暂停状态"
        
        # 如果未启用自动恢复
        if not self.auto_resume_enabled:
            return False, "自动恢复未启用"
        
        # 检查是否达到最小暂停时间
        if self.pause_start_time:
            pause_duration = (datetime.now() - self.pause_start_time).total_seconds()
            if pause_duration < self.min_pause_duration:
                return False, f"暂停时间不足（{pause_duration:.0f}s < {self.min_pause_duration}s）"
        
        # 检查波动率是否降低
        risk_assessment = self.volatility_monitor.assess_risk_level()
        
        if risk_assessment['volatility'] is not None:
            if risk_assessment['volatility'] < self.resume_volatility_threshold:
                return True, f"波动率已降至 {risk_assessment['volatility']*100:.2f}%"
        
        # 检查是否超过最大暂停时间
        if self.pause_start_time:
            pause_duration = (datetime.now() - self.pause_start_time).total_seconds()
            if pause_duration > self.max_pause_duration:
                return True, f"已达到最大暂停时间（{pause_duration:.0f}s）"
        
        return False, "波动率仍然较高"
    
    def pause_trading(self, reason: str = ""):
        """
        暂停交易
        
        Args:
            reason: 暂停原因
        """
        if self.is_paused:
            return
        
        self.is_paused = True
        self.pause_start_time = datetime.now()
        self.pause_reason = reason or "市场波动过大"
        
        # 记录暂停事件
        pause_event = {
            'timestamp': self.pause_start_time.isoformat(),
            'action': 'pause',
            'reason': self.pause_reason,
            'volatility': self.volatility_monitor.calculate_historical_volatility()
        }
        self.pause_history.append(pause_event)
        
        print(f"⚠️  交易已暂停: {self.pause_reason}")
    
    def resume_trading(self, reason: str = ""):
        """
        恢复交易
        
        Args:
            reason: 恢复原因
        """
        if not self.is_paused:
            return
        
        pause_duration = (datetime.now() - self.pause_start_time).total_seconds() if self.pause_start_time else 0
        
        self.is_paused = False
        resume_reason = reason or "市场波动恢复正常"
        
        # 记录恢复事件
        resume_event = {
            'timestamp': datetime.now().isoformat(),
            'action': 'resume',
            'reason': resume_reason,
            'pause_duration': pause_duration,
            'volatility': self.volatility_monitor.calculate_historical_volatility()
        }
        self.pause_history.append(resume_event)
        
        self.pause_start_time = None
        self.pause_reason = ""
        
        print(f"✓ 交易已恢复: {resume_reason} (暂停时长: {pause_duration:.0f}秒)")
    
    def auto_check_and_act(self) -> Dict:
        """
        自动检查并执行暂停/恢复操作
        
        Returns:
            操作结果
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'action': 'none',
            'is_paused': self.is_paused,
            'message': ''
        }
        
        if not self.is_paused:
            # 检查是否需要暂停
            should_pause, reason = self.check_should_pause()
            if should_pause:
                self.pause_trading(reason)
                result['action'] = 'paused'
                result['is_paused'] = True
                result['message'] = reason
        else:
            # 检查是否可以恢复
            should_resume, reason = self.check_should_resume()
            if should_resume:
                self.resume_trading(reason)
                result['action'] = 'resumed'
                result['is_paused'] = False
                result['message'] = reason
            else:
                pause_duration = (datetime.now() - self.pause_start_time).total_seconds() if self.pause_start_time else 0
                result['message'] = f"继续暂停: {reason} (已暂停 {pause_duration:.0f}秒)"
        
        return result
    
    def get_status(self) -> Dict:
        """
        获取当前状态
        
        Returns:
            状态字典
        """
        risk_assessment = self.volatility_monitor.assess_risk_level()
        
        pause_duration = 0
        if self.is_paused and self.pause_start_time:
            pause_duration = (datetime.now() - self.pause_start_time).total_seconds()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'is_paused': self.is_paused,
            'pause_reason': self.pause_reason,
            'pause_duration': pause_duration,
            'pause_start_time': self.pause_start_time.isoformat() if self.pause_start_time else None,
            'risk_level': risk_assessment['level'],
            'volatility': risk_assessment['volatility'],
            'auto_resume_enabled': self.auto_resume_enabled,
            'thresholds': {
                'extreme_volatility': self.extreme_volatility_threshold,
                'resume_volatility': self.resume_volatility_threshold,
                'min_pause_duration': self.min_pause_duration,
                'max_pause_duration': self.max_pause_duration
            },
            'total_pause_events': len([e for e in self.pause_history if e['action'] == 'pause'])
        }
    
    def get_pause_history(self, limit: int = 10) -> list:
        """
        获取暂停历史
        
        Args:
            limit: 返回的最大记录数
        
        Returns:
            暂停历史列表
        """
        return self.pause_history[-limit:]
    
    def manual_pause(self):
        """手动暂停交易"""
        self.pause_trading("手动暂停")
    
    def manual_resume(self):
        """手动恢复交易"""
        self.resume_trading("手动恢复")


# 使用示例
if __name__ == "__main__":
    import numpy as np
    import time
    
    print("=== 自动暂停交易管理器测试 ===\n")
    
    # 初始化管理器
    manager = AutoPauseManager(
        extreme_volatility_threshold=0.08,
        auto_resume_enabled=True,
        resume_volatility_threshold=0.04,
        min_pause_duration=10,  # 测试用，设置为10秒
        max_pause_duration=60
    )
    
    # 模拟市场数据
    base_price = 50000
    print("模拟市场波动场景...\n")
    
    scenarios = [
        ("正常波动", 0.02, 5),
        ("波动增加", 0.05, 5),
        ("剧烈波动", 0.12, 5),
        ("波动降低", 0.06, 5),
        ("恢复正常", 0.03, 5)
    ]
    
    for scenario_name, volatility, periods in scenarios:
        print(f"--- {scenario_name} (波动率 {volatility*100:.0f}%) ---")
        
        for i in range(periods):
            high = base_price * (1 + volatility * np.random.random())
            low = base_price * (1 - volatility * np.random.random())
            close = base_price * (1 + volatility * (np.random.random() - 0.5))
            
            manager.update_market_data(high, low, close)
            base_price = close
            
            # 自动检查并执行操作
            result = manager.auto_check_and_act()
            
            if result['action'] != 'none':
                print(f"  {result['message']}")
            
            time.sleep(0.5)  # 模拟时间流逝
        
        # 显示当前状态
        status = manager.get_status()
        print(f"  当前状态: {'暂停' if status['is_paused'] else '运行'}")
        print(f"  风险等级: {status['risk_level']}")
        if status['volatility']:
            print(f"  波动率: {status['volatility']*100:.2f}%")
        print()
    
    # 显示暂停历史
    print("\n=== 暂停历史 ===")
    history = manager.get_pause_history()
    for event in history:
        action_text = "暂停" if event['action'] == 'pause' else "恢复"
        vol_text = f"{event['volatility']*100:.2f}%" if event['volatility'] else "N/A"
        duration_text = f" (时长: {event.get('pause_duration', 0):.0f}秒)" if event['action'] == 'resume' else ""
        print(f"{event['timestamp']}: {action_text} - {event['reason']} (波动率: {vol_text}){duration_text}")
    
    # 显示最终状态
    print("\n=== 最终状态 ===")
    final_status = manager.get_status()
    print(f"交易状态: {'暂停' if final_status['is_paused'] else '运行'}")
    print(f"总暂停次数: {final_status['total_pause_events']}")
