#!/usr/bin/env python3
"""
获取风险历史数据
从数据库读取风险事件历史并输出JSON
"""
import json
import sys
import os
from datetime import datetime, timedelta

def get_risk_history():
    """获取风险历史数据"""
    try:
        # TODO: 从数据库读取真实数据
        # 这里先返回模拟数据作为示例
        
        now = datetime.now()
        
        # 生成30天的波动率历史
        volatility_history = []
        for i in range(30):
            date = now - timedelta(days=29-i)
            volatility_history.append({
                "date": date.strftime("%Y-%m-%d"),
                "atr": 150 + (i % 10) * 10,
                "historical": 0.02 + (i % 5) * 0.005,
            })
        
        # 暂停事件
        pause_events = [
            {
                "timestamp": (now - timedelta(days=5)).isoformat(),
                "type": "pause",
                "reason": "波动率过高 (12.5%)",
                "volatility": 12.5,
            },
            {
                "timestamp": (now - timedelta(days=5, hours=2)).isoformat(),
                "type": "resume",
                "reason": "波动率恢复正常 (4.2%)",
                "volatility": 4.2,
            },
        ]
        
        # 仓位调整记录
        position_adjustments = [
            {
                "timestamp": (now - timedelta(days=3)).isoformat(),
                "from": 1.0,
                "to": 0.7,
                "reason": "风险等级: 中 -> 高",
                "riskLevel": "high",
            },
            {
                "timestamp": (now - timedelta(days=1)).isoformat(),
                "from": 0.7,
                "to": 1.0,
                "reason": "风险等级: 高 -> 中",
                "riskLevel": "medium",
            },
        ]
        
        return {
            "volatilityHistory": volatility_history,
            "pauseEvents": pause_events,
            "positionAdjustments": position_adjustments,
        }
        
    except Exception as e:
        return {
            "volatilityHistory": [],
            "pauseEvents": [],
            "positionAdjustments": [],
            "error": str(e)
        }

if __name__ == "__main__":
    history = get_risk_history()
    print(json.dumps(history))
