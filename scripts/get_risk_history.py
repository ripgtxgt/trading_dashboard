#!/usr/bin/env python3
"""
GetRiskHistory数据
fromDatabase读取Risk事件History并输出JSON
"""
import json
import sys
import os
from datetime import datetime, timedelta

def get_risk_history():
 """GetRiskHistory数据"""
 try:
 # TODO: fromDatabase读取真实数据
 # 这里先返回模拟数据作as示例
 
 now = datetime.now()
 
 # 生成30天Volatility率History
 volatility_history = []
 for i in range(30):
 date = now - timedelta(days=29-i)
 volatility_history.append({
 "date": date.strftime("%Y-%m-%d"),
 "atr": 150 + (i % 10) * 10,
 "historical": 0.02 + (i % 5) * 0.005,
 })
 
 # Pause事件
 pause_events = [
 {
 "timestamp": (now - timedelta(days=5)).isoformat(),
 "type": "pause",
 "reason": "Volatility率过高 (12.5%)",
 "volatility": 12.5,
 },
 {
 "timestamp": (now - timedelta(days=5, hours=2)).isoformat(),
 "type": "resume",
 "reason": "Volatility率Resume正常 (4.2%)",
 "volatility": 4.2,
 },
 ]
 
 # PositionadjustRecord
 position_adjustments = [
 {
 "timestamp": (now - timedelta(days=3)).isoformat(),
 "from": 1.0,
 "to": 0.7,
 "reason": "Risklevel: in → 高",
 "riskLevel": "high",
 },
 {
 "timestamp": (now - timedelta(days=1)).isoformat(),
 "from": 0.7,
 "to": 1.0,
 "reason": "Risklevel: 高 → in",
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
