#!/usr/bin/env python3
"""
Risk管理模块功能测试
测试所HasRisk控制功能is否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from risk_manager import RiskManager
from datetime import datetime, timedelta
import json

def clean_state():
 """清理Status文件"""
 state_file = os.path.join(os.path.dirname(__file__), 'risk_manager_state.json')
 if os.path.exists(state_file):
 os.remove(state_file)

def test_basic_initialization():
 """测试基本Initialize"""
 print("\n=== 1: Initialize ===")
 clean_state()
 
 risk_manager = RiskManager()
 status = risk_manager.get_risk_status()
 
 print(f"Status: {json.dumps(status, indent=2, ensure_ascii=False)}")
 assert status['is_trading_allowed'] == True
 assert status['consecutive_losses'] == 0
 
 print("[OK] Initialize")

def test_volatility_check():
 """测试市场Volatility率检查"""
 print("\n=== 2: Volatility ===")
 clean_state()
 
 risk_manager = RiskManager()
 
 # 模拟正常Volatility
 base_price = 50000
 for i in range(20):
 price = base_price + (i * 10) # 小幅Volatility
 allowed, reason = risk_manager.check_risk(price, 100)
 
 print(f"Volatility - Trade: {allowed}, Volatility: {risk_manager.volatility:.4f}")
 assert allowed == True
 
 # 模拟剧烈Volatility
 for i in range(20):
 price = base_price + (i * 500) # 大幅Volatility
 allowed, reason = risk_manager.check_risk(price, 100)
 
 print(f"Volatility - Trade: {allowed}, reason: {reason}, Volatility: {risk_manager.volatility:.4f}")
 
 print("[OK] Volatility")

def test_daily_loss_protection():
 """测试dailyLoss保护"""
 print("\n=== 3: dailyLoss ===")
 clean_state()
 
 risk_manager = RiskManager()
 risk_manager.peak_capital = 100
 risk_manager.current_capital = 100
 
 # 正常Loss
 risk_manager.record_trade(-2, False)
 allowed, reason = risk_manager.check_risk(50000, 98)
 print(f"Loss(-2%) - Trade: {allowed}")
 assert allowed == True
 
 # 重置并测试大额Loss
 risk_manager2 = RiskManager()
 risk_manager2.peak_capital = 100
 risk_manager2.current_capital = 100
 risk_manager2.record_trade(-12, False) # exceed10%limit
 allowed, reason = risk_manager2.check_risk(50000, 88)
 print(f"Loss(-12%) - Trade: {allowed}, reason: {reason}")
 
 print("[OK] dailyLoss")

def test_consecutive_losses():
 """测试consecutiveLoss保护"""
 print("\n=== 4: consecutiveLoss ===")
 clean_state()
 
 risk_manager = RiskManager()
 risk_manager.peak_capital = 100
 risk_manager.current_capital = 100
 
 # Record2timesLoss (defaultlimitis3times)
 for i in range(2):
 risk_manager.record_trade(-1, False)
 allowed, reason = risk_manager.check_risk(50000, 99-i)
 
 print(f"2timesconsecutiveLoss - Trade: {allowed}, consecutiveLoss: {risk_manager.consecutive_losses}")
 assert allowed == True
 
 # 再Record2timesLoss，reach4times (exceedlimit3times)
 for i in range(2):
 risk_manager.record_trade(-1, False)
 allowed, reason = risk_manager.check_risk(50000, 97-i)
 
 print(f"4timesconsecutiveLoss - Trade: {allowed}, reason: {reason}")
 assert allowed == False
 
 # manualResume并Record一times盈利，重置计数
 risk_manager.manual_resume()
 risk_manager.record_trade(2, True)
 allowed, reason = risk_manager.check_risk(50000, 98)
 print(f" - Trade: {allowed}, consecutiveLoss: {risk_manager.consecutive_losses}")
 assert risk_manager.consecutive_losses == 0
 
 print("[OK] consecutiveLoss")

def test_max_drawdown():
 """测试MaxDrawdown控制"""
 print("\n=== 5: MaxDrawdown ===")
 clean_state()
 
 risk_manager = RiskManager()
 risk_manager.peak_capital = 100
 
 # 正常Drawdown
 allowed, reason = risk_manager.check_risk(50000, 92)
 drawdown = risk_manager._calculate_drawdown()
 print(f"8%Drawdown - Trade: {allowed}, Drawdown: {drawdown:.2%}")
 assert allowed == True
 
 # 超限Drawdown
 allowed, reason = risk_manager.check_risk(50000, 75)
 drawdown = risk_manager._calculate_drawdown()
 print(f"25%Drawdown - Trade: {allowed}, reason: {reason}, Drawdown: {drawdown:.2%}")
 assert allowed == False
 
 print("[OK] MaxDrawdown")

def test_manual_controls():
 """测试manual控制"""
 print("\n=== 6: manual ===")
 clean_state()
 
 risk_manager = RiskManager()
 
 # manualPause
 risk_manager.manual_pause("manual测试Pause", hours=1)
 status = risk_manager.get_risk_status()
 print(f"manualPause - Trade: {status['is_trading_allowed']}, reason: {status['pause_reason']}")
 assert status['is_trading_allowed'] == False
 
 # manualResume
 risk_manager.manual_resume()
 status = risk_manager.get_risk_status()
 print(f"manualResume - Trade: {status['is_trading_allowed']}")
 assert status['is_trading_allowed'] == True
 
 print("[OK] manual")

def test_risk_status():
 """测试RiskStatus报告"""
 print("\n=== 7: RiskStatus ===")
 clean_state()
 
 risk_manager = RiskManager()
 risk_manager.peak_capital = 100
 risk_manager.current_capital = 95
 
 # Record一些Trade
 risk_manager.record_trade(-2, False)
 risk_manager.record_trade(1, True)
 risk_manager.record_trade(-1, False)
 
 status = risk_manager.get_risk_status()
 print(f"RiskStatus:")
 print(f" Trade: {status['is_trading_allowed']}")
 print(f" PnL: {status['daily_pnl']}")
 print(f" PnL: {status['total_pnl']}")
 print(f" CurrentDrawdown: {status['current_drawdown_pct']:.2%}")
 print(f" consecutiveLoss: {status['consecutive_losses']}")
 print(f" Volatility: {status['volatility']:.4f}")
 
 assert 'is_trading_allowed' in status
 assert 'daily_pnl' in status
 assert 'total_pnl' in status
 
 print("[OK] RiskStatus")

def test_config_management():
 """测试Config管理"""
 print("\n=== 8: Config ===")
 clean_state()
 
 # 使用自定义Config
 custom_config = {
 'max_volatility': 0.08,
 'max_daily_loss_pct': 0.15,
 'max_consecutive_losses': 5,
 }
 
 risk_manager = RiskManager(config=custom_config)
 print(f"Config:")
 print(f" MaxVolatility: {risk_manager.config['max_volatility']}")
 print(f" MaxLoss: {risk_manager.config['max_daily_loss_pct']:.0%}")
 print(f" MaxconsecutiveLoss: {risk_manager.config['max_consecutive_losses']}")
 
 assert risk_manager.config['max_volatility'] == 0.08
 assert risk_manager.config['max_daily_loss_pct'] == 0.15
 
 print("[OK] Config")

def test_comprehensive_scenario():
 """测试综合场景"""
 print("\n=== 9:  ===")
 clean_state()
 
 risk_manager = RiskManager()
 risk_manager.peak_capital = 100
 risk_manager.current_capital = 100
 
 print("Trade:")
 
 # 早上：正常Trade
 for i in range(3):
 risk_manager.record_trade(1, True)
 allowed, reason = risk_manager.check_risk(50000 + i*10, risk_manager.current_capital + 1)
 print(f" Trade{i+1} -  +1, : {allowed}")
 
 # in午：consecutiveLoss
 for i in range(3):
 risk_manager.record_trade(-1.5, False)
 allowed, reason = risk_manager.check_risk(50000 - i*10, risk_manager.current_capital - 1.5)
 print(f" Trade{i+4} - Loss -1.5, : {allowed}, reason: {reason if not allowed else 'N/A'}")
 
 # 检查finalStatus
 status = risk_manager.get_risk_status()
 print(f"\nfinalStatus:")
 print(f" PnL: {status['total_pnl']}")
 print(f" consecutiveLoss: {status['consecutive_losses']}")
 print(f" Trade: {status['is_trading_allowed']}")
 
 print("[OK] ")

def run_all_tests():
 """Running所Has测试"""
 print("=" * 60)
 print("Risk")
 print("=" * 60)
 
 try:
 test_basic_initialization()
 test_volatility_check()
 test_daily_loss_protection()
 test_consecutive_losses()
 test_max_drawdown()
 test_manual_controls()
 test_risk_status()
 test_config_management()
 test_comprehensive_scenario()
 
 print("\n" + "=" * 60)
 print("[OK] HasRisk")
 print("=" * 60)
 return True
 
 except AssertionError as e:
 print(f"\n[FAIL] Failed: {e}")
 import traceback
 traceback.print_exc()
 return False
 except Exception as e:
 print(f"\n[FAIL] error occurred: {e}")
 import traceback
 traceback.print_exc()
 return False

if __name__ == '__main__':
 success = run_all_tests()
 sys.exit(0 if success else 1)
