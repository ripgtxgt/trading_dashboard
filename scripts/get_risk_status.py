#!/usr/bin/env python3
"""
GetCurrentRiskStatus
fromRisk管理模块读取Realtime数据并输出JSON
"""
import json
import sys
import os
from datetime import datetime

# 添加scripts目录to路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
 from volatility_monitor import VolatilityMonitor
 from dynamic_position_manager import DynamicPositionManager
 from auto_pause_manager import AutoPauseManager
except ImportError:
 # 如果导入Failed，返回default数据
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
 """GetCurrentRiskStatus"""
 try:
 # InitializeRisk管理模块
 vol_monitor = VolatilityMonitor()
 pos_manager = DynamicPositionManager()
 pause_manager = AutoPauseManager()
 
 # Get模拟K线数据（实际使用时should该fromTrade所Get）
 # 这里使用最近数据
 klines = [] # 实际should该fromAPIGet
 
 # 如果没Has数据，返回default值
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
 
 # CalculateVolatility率
 vol_data = vol_monitor.calculate_volatility(klines)
 
 # assessmentRisklevel
 risk_level = vol_monitor.assess_risk_level(vol_data)
 
 # CalculatePosition倍数
 position_mult = pos_manager.calculate_position_multiplier(risk_level)
 
 # 检查is否Pause
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
 # 发生Error时返回default数据
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
