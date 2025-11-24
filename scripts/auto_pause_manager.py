#!/usr/bin/env python3
"""
autoPauseTrade管理器
当市场剧烈Volatility时autoPauseTrade，保护资金safe
"""

from volatility_monitor import VolatilityMonitor
from typing import Dict, Optional
from datetime import datetime, timedelta
import json


class AutoPauseManager:
 """autoPauseTrade管理器"""
 
 def __init__(
 self,
 extreme_volatility_threshold: float = 0.10, # 10%Volatility率triggerPause
 auto_resume_enabled: bool = True,
 resume_volatility_threshold: float = 0.05, # 5%Volatility率autoResume
 min_pause_duration: int = 300, # MinPauseTime（second）
 max_pause_duration: int = 3600 # MaxPauseTime（second）
):
 """
 InitializeautoPause管理器
 
 Args:
 extreme_volatility_threshold: 极端Volatility率阈值
 auto_resume_enabled: is否enableautoResume
 resume_volatility_threshold: ResumeTradeVolatility率阈值
 min_pause_duration: MinPauseTime
 max_pause_duration: MaxPauseTime
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
 Update市场数据
 
 Args:
 high: 最高价
 low: 最低价
 close: 收盘价
 """
 self.volatility_monitor.add_price_data(high, low, close)
 
 def check_should_pause(self) -> tuple[bool, str]:
 """
 检查is否should该PauseTrade
 
 Returns:
 (is否shouldPause, reason)
 """
 risk_assessment = self.volatility_monitor.assess_risk_level()
 
 # 如果alreadyPause，not需要重复检查
 if self.is_paused:
 return False, "Already处atPauseStatus"
 
 # 检查is否reach极端Volatility
 if risk_assessment['should_pause']:
 return True, risk_assessment['message']
 
 # 检查Volatility率is否exceed阈值
 if risk_assessment['volatility'] is not None:
 if risk_assessment['volatility'] > self.extreme_volatility_threshold:
 return True, f"Volatility率 {risk_assessment['volatility']*100:.2f}% exceed阈值 {self.extreme_volatility_threshold*100:.2f}%"
 
 return False, "市场状况正常"
 
 def check_should_resume(self) -> tuple[bool, str]:
 """
 检查is否should该ResumeTrade
 
 Returns:
 (is否shouldResume, reason)
 """
 # 如果NotPause，not需要检查
 if not self.is_paused:
 return False, "Not处atPauseStatus"
 
 # 如果NotenableautoResume
 if not self.auto_resume_enabled:
 return False, "autoResumeNotenable"
 
 # 检查is否reachMinPauseTime
 if self.pause_start_time:
 pause_duration = (datetime.now() - self.pause_start_time).total_seconds()
 if pause_duration < self.min_pause_duration:
 return False, f"PauseTimenot足（{pause_duration:.0f}s < {self.min_pause_duration}s）"
 
 # 检查Volatility率is否降低
 risk_assessment = self.volatility_monitor.assess_risk_level()
 
 if risk_assessment['volatility'] is not None:
 if risk_assessment['volatility'] < self.resume_volatility_threshold:
 return True, f"Volatility率Already降至 {risk_assessment['volatility']*100:.2f}%"
 
 # 检查is否exceedMaxPauseTime
 if self.pause_start_time:
 pause_duration = (datetime.now() - self.pause_start_time).total_seconds()
 if pause_duration > self.max_pause_duration:
 return True, f"AlreadyreachMaxPauseTime（{pause_duration:.0f}s）"
 
 return False, "Volatility率仍然较高"
 
 def pause_trading(self, reason: str = ""):
 """
 PauseTrade
 
 Args:
 reason: Pausereason
 """
 if self.is_paused:
 return
 
 self.is_paused = True
 self.pause_start_time = datetime.now()
 self.pause_reason = reason or "市场Volatility过大"
 
 # RecordPause事件
 pause_event = {
 'timestamp': self.pause_start_time.isoformat(),
 'action': 'pause',
 'reason': self.pause_reason,
 'volatility': self.volatility_monitor.calculate_historical_volatility()
 }
 self.pause_history.append(pause_event)
 
 print(f"[WARNING] TradeAlreadyPause: {self.pause_reason}")
 
 def resume_trading(self, reason: str = ""):
 """
 ResumeTrade
 
 Args:
 reason: Resumereason
 """
 if not self.is_paused:
 return
 
 pause_duration = (datetime.now() - self.pause_start_time).total_seconds() if self.pause_start_time else 0
 
 self.is_paused = False
 resume_reason = reason or "市场VolatilityResume正常"
 
 # RecordResume事件
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
 
 print(f"[OK] TradeAlreadyResume: {resume_reason} (Pause: {pause_duration:.0f}second)")
 
 def auto_check_and_act(self) -> Dict:
 """
 auto检查并ExecutePause/Resume操作
 
 Returns:
 操作result
 """
 result = {
 'timestamp': datetime.now().isoformat(),
 'action': 'none',
 'is_paused': self.is_paused,
 'message': ''
 }
 
 if not self.is_paused:
 # 检查is否需要Pause
 should_pause, reason = self.check_should_pause()
 if should_pause:
 self.pause_trading(reason)
 result['action'] = 'paused'
 result['is_paused'] = True
 result['message'] = reason
 else:
 # 检查is否可以Resume
 should_resume, reason = self.check_should_resume()
 if should_resume:
 self.resume_trading(reason)
 result['action'] = 'resumed'
 result['is_paused'] = False
 result['message'] = reason
 else:
 pause_duration = (datetime.now() - self.pause_start_time).total_seconds() if self.pause_start_time else 0
 result['message'] = f"继续Pause: {reason} (AlreadyPause {pause_duration:.0f}second)"
 
 return result
 
 def get_status(self) -> Dict:
 """
 GetCurrentStatus
 
 Returns:
 Status字典
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
 GetPauseHistory
 
 Args:
 limit: 返回MaxRecord数
 
 Returns:
 PauseHistory列表
 """
 return self.pause_history[-limit:]
 
 def manual_pause(self):
 """manualPauseTrade"""
 self.pause_trading("manualPause")
 
 def manual_resume(self):
 """manualResumeTrade"""
 self.resume_trading("manualResume")


# 使用示例
if __name__ == "__main__":
 import numpy as np
 import time
 
 print("=== autoPauseTrade ===\n")
 
 # Initialize管理器
 manager = AutoPauseManager(
 extreme_volatility_threshold=0.08,
 auto_resume_enabled=True,
 resume_volatility_threshold=0.04,
 min_pause_duration=10, # 测试用，Setas10second
 max_pause_duration=60
)
 
 # 模拟市场数据
 base_price = 50000
 print("Volatility...\n")
 
 scenarios = [
 ("正常Volatility", 0.02, 5),
 ("Volatility增加", 0.05, 5),
 ("剧烈Volatility", 0.12, 5),
 ("Volatility降低", 0.06, 5),
 ("Resume正常", 0.03, 5)
 ]
 
 for scenario_name, volatility, periods in scenarios:
 print(f"--- {scenario_name} (Volatility {volatility*100:.0f}%) ---")
 
 for i in range(periods):
 high = base_price * (1 + volatility * np.random.random())
 low = base_price * (1 - volatility * np.random.random())
 close = base_price * (1 + volatility * (np.random.random() - 0.5))
 
 manager.update_market_data(high, low, close)
 base_price = close
 
 # auto检查并Execute操作
 result = manager.auto_check_and_act()
 
 if result['action']!= 'none':
 print(f" {result['message']}")
 
 time.sleep(0.5) # 模拟Time流逝
 
 # 显示CurrentStatus
 status = manager.get_status()
 print(f" CurrentStatus: {'Pause' if status['is_paused'] else 'Running'}")
 print(f" Risklevel: {status['risk_level']}")
 if status['volatility']:
 print(f" Volatility: {status['volatility']*100:.2f}%")
 print()
 
 # 显示PauseHistory
 print("\n=== PauseHistory ===")
 history = manager.get_pause_history()
 for event in history:
 action_text = "Pause" if event['action'] == 'pause' else "Resume"
 vol_text = f"{event['volatility']*100:.2f}%" if event['volatility'] else "N/A"
 duration_text = f" (时长: {event.get('pause_duration', 0):.0f}second)" if event['action'] == 'resume' else ""
 print(f"{event['timestamp']}: {action_text} - {event['reason']} (Volatility: {vol_text}){duration_text}")
 
 # 显示finalStatus
 print("\n=== finalStatus ===")
 final_status = manager.get_status()
 print(f"TradeStatus: {'Pause' if final_status['is_paused'] else 'Running'}")
 print(f"Pausecount: {final_status['total_pause_events']}")
