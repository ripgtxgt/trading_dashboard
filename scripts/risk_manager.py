#!/usr/bin/env python3
"""
Risk管理模块
实现市场VolatilityMonitor、Loss保护、consecutiveLoss保护、MaxDrawdown控制and紧急熔断机制
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os


class RiskManager:
 """Risk管理器"""
 
 def __init__(self, config: Dict = None):
 """
 InitializeRisk管理器
 
 Args:
 config: Risk管理Config
 """
 self.config = config or self._default_config()
 
 # Status变量
 self.is_trading_allowed = True
 self.pause_reason = None
 self.pause_until = None
 
 # 统计数据
 self.daily_pnl = 0.0
 self.total_pnl = 0.0
 self.peak_capital = 0.0
 self.current_capital = 0.0
 self.consecutive_losses = 0
 self.trade_history: List[Dict] = []
 
 # 市场数据
 self.price_history: List[float] = []
 self.volatility = 0.0
 
 # Risk事件日志
 self.risk_events: List[Dict] = []
 
 # Load持久化数据
 self._load_state()
 
 def _default_config(self) -> Dict:
 """defaultRisk管理Config"""
 return {
 # 市场Volatility控制
 'max_volatility': 0.05, # MaxVolatility率5%
 'volatility_window': 20, # Volatility率Calculate窗口
 
 # Loss保护
 'max_daily_loss_pct': 0.10, # dailyMaxLoss10%
 'max_total_loss_pct': 0.30, # cumulativeMaxLoss30%
 
 # consecutiveLoss保护
 'max_consecutive_losses': 3, # 最多consecutive3Loss
 'consecutive_loss_pause_hours': 1, # Pause1hour
 
 # MaxDrawdown控制
 'max_drawdown_pct': 0.20, # MaxDrawdown20%
 
 # Time窗口limit
 'trading_hours': {
 'enabled': False,
 'start_hour': 0, # BeginTime（UTC）
 'end_hour': 24, # EndTime（UTC）
 },
 
 # 紧急熔断
 'circuit_breaker': {
 'enabled': True,
 'price_change_pct': 0.10, # Price变动10%trigger
 'time_window_minutes': 5, # 5minute内
 },
 
 # Resume机制
 'auto_resume': {
 'enabled': True,
 'check_interval_minutes': 30, # 每30minute检查一times
 }
 }
 
 def check_risk(self, current_price: float, current_capital: float) -> Tuple[bool, Optional[str]]:
 """
 检查RiskStatus
 
 Args:
 current_price: CurrentPrice
 current_capital: Current资金
 
 Returns:
 (is否允许Trade, Pausereason)
 """
 self.current_capital = current_capital
 
 # Update峰值资金
 if current_capital > self.peak_capital:
 self.peak_capital = current_capital
 
 # UpdatePriceHistory
 self._update_price_history(current_price)
 
 # 检查is否atPause期
 if not self._check_pause_status():
 return False, self.pause_reason
 
 # 检查TradeTime窗口
 if not self._check_trading_hours():
 return False, "非TradeTime段"
 
 # 检查市场Volatility率
 if not self._check_volatility():
 self._trigger_pause("市场Volatility过大", hours=1)
 return False, self.pause_reason
 
 # 检查dailyLoss
 if not self._check_daily_loss():
 self._trigger_pause("dailyLoss超限", hours=24)
 return False, self.pause_reason
 
 # 检查cumulativeLoss
 if not self._check_total_loss():
 self._trigger_pause("cumulativeLoss超限", hours=None) # 需要manualResume
 return False, self.pause_reason
 
 # 检查MaxDrawdown
 if not self._check_drawdown():
 self._trigger_pause("Drawdown超限", hours=None)
 return False, self.pause_reason
 
 # 检查consecutiveLoss
 if not self._check_consecutive_losses():
 pause_hours = self.config['consecutive_loss_pause_hours']
 self._trigger_pause(f"consecutive{self.consecutive_losses}Loss", hours=pause_hours)
 return False, self.pause_reason
 
 # 检查紧急熔断
 if not self._check_circuit_breaker():
 self._trigger_pause("trigger紧急熔断", hours=1)
 return False, self.pause_reason
 
 return True, None
 
 def record_trade(self, pnl: float, is_win: bool):
 """
 RecordTraderesult
 
 Args:
 pnl: PnL金额
 is_win: is否盈利
 """
 trade = {
 'timestamp': datetime.now().isoformat(),
 'pnl': pnl,
 'is_win': is_win,
 }
 self.trade_history.append(trade)
 
 # Update统计
 self.daily_pnl += pnl
 self.total_pnl += pnl
 
 # UpdateconsecutiveLoss计数
 if is_win:
 self.consecutive_losses = 0
 else:
 self.consecutive_losses += 1
 
 # SaveStatus
 self._save_state()
 
 def reset_daily_stats(self):
 """重置每日统计"""
 self.daily_pnl = 0.0
 self._save_state()
 
 def manual_resume(self):
 """manualResumeTrade"""
 self.is_trading_allowed = True
 self.pause_reason = None
 self.pause_until = None
 
 self._log_risk_event("manual_resume", "manualResumeTrade")
 self._save_state()
 
 def manual_pause(self, reason: str, hours: Optional[int] = None):
 """manualPauseTrade"""
 self._trigger_pause(reason, hours)
 
 def get_risk_status(self) -> Dict:
 """GetRiskStatus摘要"""
 return {
 'is_trading_allowed': self.is_trading_allowed,
 'pause_reason': self.pause_reason,
 'pause_until': self.pause_until.isoformat() if self.pause_until else None,
 'daily_pnl': self.daily_pnl,
 'total_pnl': self.total_pnl,
 'current_drawdown_pct': self._calculate_drawdown(),
 'consecutive_losses': self.consecutive_losses,
 'volatility': self.volatility,
 'recent_events': self.risk_events[-10:], # 最近10事件
 }
 
 # ========== 私Has方法 ==========
 
 def _update_price_history(self, price: float):
 """UpdatePriceHistory"""
 self.price_history.append(price)
 
 # 只保留需要窗口大小
 max_window = max(
 self.config['volatility_window'],
 self.config['circuit_breaker']['time_window_minutes']
)
 if len(self.price_history) > max_window:
 self.price_history = self.price_history[-max_window:]
 
 # CalculateVolatility率
 self._calculate_volatility()
 
 def _calculate_volatility(self):
 """Calculate市场Volatility率"""
 window = self.config['volatility_window']
 if len(self.price_history) < window:
 self.volatility = 0.0
 return
 
 prices = self.price_history[-window:]
 returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
 
 # Calculate标准差作asVolatility率
 if len(returns) > 0:
 mean_return = sum(returns) / len(returns)
 variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
 self.volatility = variance ** 0.5
 else:
 self.volatility = 0.0
 
 def _calculate_drawdown(self) -> float:
 """CalculateCurrentDrawdown百分比"""
 if self.peak_capital == 0:
 return 0.0
 return (self.peak_capital - self.current_capital) / self.peak_capital
 
 def _check_pause_status(self) -> bool:
 """检查is否atPause期"""
 if not self.is_trading_allowed:
 if self.pause_until:
 if datetime.now() >= self.pause_until:
 # Pause期End，autoResume
 if self.config['auto_resume']['enabled']:
 self.manual_resume()
 return True
 return False
 else:
 # 需要manualResume
 return False
 return True
 
 def _check_trading_hours(self) -> bool:
 """检查TradeTime窗口"""
 if not self.config['trading_hours']['enabled']:
 return True
 
 current_hour = datetime.utcnow().hour
 start_hour = self.config['trading_hours']['start_hour']
 end_hour = self.config['trading_hours']['end_hour']
 
 if start_hour <= end_hour:
 return start_hour <= current_hour < end_hour
 else:
 # 跨日情况
 return current_hour >= start_hour or current_hour < end_hour
 
 def _check_volatility(self) -> bool:
 """检查市场Volatility率"""
 max_vol = self.config['max_volatility']
 return self.volatility <= max_vol
 
 def _check_daily_loss(self) -> bool:
 """检查dailyLoss"""
 if self.peak_capital == 0:
 return True
 
 max_loss_pct = self.config['max_daily_loss_pct']
 daily_loss_pct = abs(self.daily_pnl) / self.peak_capital
 
 return self.daily_pnl >= 0 or daily_loss_pct <= max_loss_pct
 
 def _check_total_loss(self) -> bool:
 """检查cumulativeLoss"""
 if self.peak_capital == 0:
 return True
 
 max_loss_pct = self.config['max_total_loss_pct']
 total_loss_pct = abs(self.total_pnl) / self.peak_capital
 
 return self.total_pnl >= 0 or total_loss_pct <= max_loss_pct
 
 def _check_drawdown(self) -> bool:
 """检查MaxDrawdown"""
 max_dd = self.config['max_drawdown_pct']
 current_dd = self._calculate_drawdown()
 
 return current_dd <= max_dd
 
 def _check_consecutive_losses(self) -> bool:
 """检查consecutiveLoss"""
 max_losses = self.config['max_consecutive_losses']
 return self.consecutive_losses < max_losses
 
 def _check_circuit_breaker(self) -> bool:
 """检查紧急熔断"""
 if not self.config['circuit_breaker']['enabled']:
 return True
 
 window_minutes = self.config['circuit_breaker']['time_window_minutes']
 if len(self.price_history) < 2:
 return True
 
 # 检查最近NminutePrice变动
 recent_prices = self.price_history[-window_minutes:]
 if len(recent_prices) < 2:
 return True
 
 price_change_pct = abs(recent_prices[-1] - recent_prices[0]) / recent_prices[0]
 max_change = self.config['circuit_breaker']['price_change_pct']
 
 return price_change_pct <= max_change
 
 def _trigger_pause(self, reason: str, hours: Optional[int]):
 """triggerTradePause"""
 self.is_trading_allowed = False
 self.pause_reason = reason
 
 if hours is not None:
 self.pause_until = datetime.now() + timedelta(hours=hours)
 else:
 self.pause_until = None
 
 self._log_risk_event("pause", reason)
 self._save_state()
 
 def _log_risk_event(self, event_type: str, description: str):
 """RecordRisk事件"""
 event = {
 'timestamp': datetime.now().isoformat(),
 'type': event_type,
 'description': description,
 }
 self.risk_events.append(event)
 
 # 只保留最近100
 if len(self.risk_events) > 100:
 self.risk_events = self.risk_events[-100:]
 
 def _save_state(self):
 """SaveStatusto文件"""
 state = {
 'is_trading_allowed': self.is_trading_allowed,
 'pause_reason': self.pause_reason,
 'pause_until': self.pause_until.isoformat() if self.pause_until else None,
 'daily_pnl': self.daily_pnl,
 'total_pnl': self.total_pnl,
 'peak_capital': self.peak_capital,
 'consecutive_losses': self.consecutive_losses,
 'trade_history': self.trade_history[-100:], # 只保留最近100
 'risk_events': self.risk_events,
 }
 
 state_file = os.path.join(os.path.dirname(__file__), 'risk_manager_state.json')
 with open(state_file, 'w') as f:
 json.dump(state, f, indent=2)
 
 def _load_state(self):
 """from文件LoadStatus"""
 state_file = os.path.join(os.path.dirname(__file__), 'risk_manager_state.json')
 if not os.path.exists(state_file):
 return
 
 try:
 with open(state_file, 'r') as f:
 state = json.load(f)
 
 self.is_trading_allowed = state.get('is_trading_allowed', True)
 self.pause_reason = state.get('pause_reason')
 
 pause_until_str = state.get('pause_until')
 if pause_until_str:
 self.pause_until = datetime.fromisoformat(pause_until_str)
 
 self.daily_pnl = state.get('daily_pnl', 0.0)
 self.total_pnl = state.get('total_pnl', 0.0)
 self.peak_capital = state.get('peak_capital', 0.0)
 self.consecutive_losses = state.get('consecutive_losses', 0)
 self.trade_history = state.get('trade_history', [])
 self.risk_events = state.get('risk_events', [])
 except Exception as e:
 print(f"[Warning] LoadRiskStatusFailed: {e}")


if __name__ == "__main__":
 # 测试代码
 print("========================================")
 print("Risk")
 print("========================================")
 
 # 创建Risk管理器
 risk_manager = RiskManager()
 
 # 模拟Trade场景
 initial_capital = 100.0
 current_capital = initial_capital
 current_price = 100.0
 
 print(f"\n: {current_capital} USDT")
 print(f"Price: {current_price}")
 
 # 测试1: 正常Trade
 print("\n[1] Trade...")
 allowed, reason = risk_manager.check_risk(current_price, current_capital)
 print(f"Trade: {allowed}, reason: {reason}")
 
 # 测试2: Record盈利Trade
 print("\n[2] RecordTrade...")
 risk_manager.record_trade(pnl=5.0, is_win=True)
 current_capital += 5.0
 print(f"Current: {current_capital} USDT")
 print(f"PnL: {risk_manager.daily_pnl} USDT")
 
 # 测试3: consecutiveLoss
 print("\n[3] consecutiveLoss...")
 for i in range(3):
 risk_manager.record_trade(pnl=-3.0, is_win=False)
 current_capital -= 3.0
 print(f"{i+1}Loss, Current: {current_capital} USDT")
 
 allowed, reason = risk_manager.check_risk(current_price, current_capital)
 print(f"Trade: {allowed}, reason: {reason}")
 
 # 测试4: 市场Volatility
 print("\n[4] Volatility...")
 for i in range(20):
 current_price *= (1 + 0.01 * (1 if i % 2 == 0 else -1))
 risk_manager.check_risk(current_price, current_capital)
 
 print(f"CurrentVolatility: {risk_manager.volatility:.4f}")
 
 # 测试5: GetRiskStatus
 print("\n[5] RiskStatus...")
 status = risk_manager.get_risk_status()
 print(json.dumps(status, indent=2, ensure_ascii=False))
 
 print("\n========================================")
 print("Complete")
 print("========================================")
