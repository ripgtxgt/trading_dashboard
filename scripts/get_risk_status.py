#!/usr/bin/env python3
"""
获取当前风险状态
从风险管理模块读取实时数据并输出JSON
"""
import json
import sys
import os
from datetime import datetime

# 添加scripts目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from volatility_monitor import VolatilityMonitor
    from dynamic_position_manager import DynamicPositionManager
    from auto_pause_manager import AutoPauseManager
except ImportError:
    # 如果导入失败，返回默认数据
    print(json.dumps({
        "volatility": {
            "atr": 0,
            "historical": 0,
            "trend": "stable"
        },
        "riskLevel": "low",
        "positionMultiplier": 1.0,
        "isPaused": false,
        "lastUpdate": datetime.now().isoformat()
    }))
    sys.exit(0)

def get_risk_status():
    """获取当前风险状态"""
    try:
        # 初始化风险管理模块
        vol_monitor = VolatilityMonitor()
        pos_manager = DynamicPositionManager()
        pause_manager = AutoPauseManager()
        
        # 获取模拟K线数据（实际使用时应该从交易所获取）
        # 这里使用最近的数据
        klines = []  # 实际应该从API获取
        
        # 如果没有数据，返回默认值
        if not klines:
            return {
                "volatility": {
                    "atr": 0,
                    "historical": 0,
                    "trend": "stable"
                },
                "riskLevel": "low",
                "positionMultiplier": 1.0,
                "isPaused": False,
                "lastUpdate": datetime.now().isoformat()
            }
        
        # 计算波动率
        vol_data = vol_monitor.calculate_volatility(klines)
        
        # 评估风险等级
        risk_level = vol_monitor.assess_risk_level(vol_data)
        
        # 计算仓位倍数
        position_mult = pos_manager.calculate_position_multiplier(risk_level)
        
        # 检查是否暂停
        is_paused = pause_manager.should_pause(vol_data)
        
        return {
            "volatility": {
                "atr": vol_data.get("atr", 0),
                "historical": vol_data.get("historical_volatility", 0),
                "trend": vol_data.get("trend", "stable")
            },
            "riskLevel": risk_level,
            "positionMultiplier": position_mult,
            "isPaused": is_paused,
            "lastUpdate": datetime.now().isoformat()
        }
        
    except Exception as e:
        # 发生错误时返回默认数据
        return {
            "volatility": {
                "atr": 0,
                "historical": 0,
                "trend": "stable"
            },
            "riskLevel": "low",
            "positionMultiplier": 1.0,
            "isPaused": False,
            "lastUpdate": datetime.now().isoformat(),
            "error": str(e)
        }

if __name__ == "__main__":
    status = get_risk_status()
    print(json.dumps(status))
