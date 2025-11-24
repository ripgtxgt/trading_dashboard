#!/usr/bin/env python3
"""
风险管理模块功能测试
测试所有Risk control功能是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from risk_manager import RiskManager
from datetime import datetime, timedelta
import json

def clean_state():
    """清理状态文件"""
    state_file = os.path.join(os.path.dirname(__file__), 'risk_manager_state.json')
    if os.path.exists(state_file):
        os.remove(state_file)

def test_basic_initialization():
    """测试基本初始化"""
    print("\n=== 1: Initialize ===")
    clean_state()
    
    risk_manager = RiskManager()
    status = risk_manager.get_risk_status()
    
    print(f": {json.dumps(status, indent=2, ensure_ascii=False)}")
    assert status['is_trading_allowed'] == True
    assert status['consecutive_losses'] == 0
    
    print("[OK] Initialize")

def test_volatility_check():
    """测试市场波动率检查"""
    print("\n=== 2: Check ===")
    clean_state()
    
    risk_manager = RiskManager()
    
    # 模拟正常波动
    base_price = 50000
    for i in range(20):
        price = base_price + (i * 10)  # 小幅波动
        allowed, reason = risk_manager.check_risk(price, 100)
    
    print(f" - Trade: {allowed}, : {risk_manager.volatility:.4f}")
    assert allowed == True
    
    # 模拟剧烈波动
    for i in range(20):
        price = base_price + (i * 500)  # 大幅波动
        allowed, reason = risk_manager.check_risk(price, 100)
    
    print(f" - Trade: {allowed}, : {reason}, : {risk_manager.volatility:.4f}")
    
    print("[OK] Check")

def test_daily_loss_protection():
    """测试单日亏损保护"""
    print("\n=== 3: Loss ===")
    clean_state()
    
    risk_manager = RiskManager()
    risk_manager.peak_capital = 100
    risk_manager.current_capital = 100
    
    # 正常亏损
    risk_manager.record_trade(-2, False)
    allowed, reason = risk_manager.check_risk(50000, 98)
    print(f"Loss(-2%) - Trade: {allowed}")
    assert allowed == True
    
    # 重置并测试大额亏损
    risk_manager2 = RiskManager()
    risk_manager2.peak_capital = 100
    risk_manager2.current_capital = 100
    risk_manager2.record_trade(-12, False)  # 超过10%限制
    allowed, reason = risk_manager2.check_risk(50000, 88)
    print(f"Loss(-12%) - Trade: {allowed}, : {reason}")
    
    print("[OK] Loss")

def test_consecutive_losses():
    """测试连续亏损保护"""
    print("\n=== 4: Loss ===")
    clean_state()
    
    risk_manager = RiskManager()
    risk_manager.peak_capital = 100
    risk_manager.current_capital = 100
    
    # 记录2次亏损 (默认限制是3次)
    for i in range(2):
        risk_manager.record_trade(-1, False)
        allowed, reason = risk_manager.check_risk(50000, 99-i)
    
    print(f"2Loss - Trade: {allowed}, Loss: {risk_manager.consecutive_losses}")
    assert allowed == True
    
    # 再记录2次亏损, 达到4次 (超过限制3次)
    for i in range(2):
        risk_manager.record_trade(-1, False)
        allowed, reason = risk_manager.check_risk(50000, 97-i)
    
    print(f"4Loss - Trade: {allowed}, : {reason}")
    assert allowed == False
    
    # 手动恢复并记录一次盈利, 重置计数
    risk_manager.manual_resume()
    risk_manager.record_trade(2, True)
    allowed, reason = risk_manager.check_risk(50000, 98)
    print(f"Profit - Trade: {allowed}, Loss: {risk_manager.consecutive_losses}")
    assert risk_manager.consecutive_losses == 0
    
    print("[OK] Loss")

def test_max_drawdown():
    """测试最大回撤控制"""
    print("\n=== 5: Control ===")
    clean_state()
    
    risk_manager = RiskManager()
    risk_manager.peak_capital = 100
    
    # 正常回撤
    allowed, reason = risk_manager.check_risk(50000, 92)
    drawdown = risk_manager._calculate_drawdown()
    print(f"8% - Trade: {allowed}, : {drawdown:.2%}")
    assert allowed == True
    
    # 超限回撤
    allowed, reason = risk_manager.check_risk(50000, 75)
    drawdown = risk_manager._calculate_drawdown()
    print(f"25% - Trade: {allowed}, : {reason}, : {drawdown:.2%}")
    assert allowed == False
    
    print("[OK] Control")

def test_manual_controls():
    """测试手动控制"""
    print("\n=== 6: Control ===")
    clean_state()
    
    risk_manager = RiskManager()
    
    # 手动暂停
    risk_manager.manual_pause("手动测试暂停", hours=1)
    status = risk_manager.get_risk_status()
    print(f"Paused - Trade: {status['is_trading_allowed']}, : {status['pause_reason']}")
    assert status['is_trading_allowed'] == False
    
    # 手动恢复
    risk_manager.manual_resume()
    status = risk_manager.get_risk_status()
    print(f" - Trade: {status['is_trading_allowed']}")
    assert status['is_trading_allowed'] == True
    
    print("[OK] Control")

def test_risk_status():
    """测试风险状态报告"""
    print("\n=== 7: Risk ===")
    clean_state()
    
    risk_manager = RiskManager()
    risk_manager.peak_capital = 100
    risk_manager.current_capital = 95
    
    # 记录一些交易
    risk_manager.record_trade(-2, False)
    risk_manager.record_trade(1, True)
    risk_manager.record_trade(-1, False)
    
    status = risk_manager.get_risk_status()
    print(f"Risk:")
    print(f"  Trade: {status['is_trading_allowed']}")
    print(f"  : {status['daily_pnl']}")
    print(f"  : {status['total_pnl']}")
    print(f"  Current: {status['current_drawdown_pct']:.2%}")
    print(f"  Loss: {status['consecutive_losses']}")
    print(f"  : {status['volatility']:.4f}")
    
    assert 'is_trading_allowed' in status
    assert 'daily_pnl' in status
    assert 'total_pnl' in status
    
    print("[OK] Risk")

def test_config_management():
    """测试配置管理"""
    print("\n=== 8: Config ===")
    clean_state()
    
    # 使用自定义配置
    custom_config = {
        'max_volatility': 0.08,
        'max_daily_loss_pct': 0.15,
        'max_consecutive_losses': 5,
    }
    
    risk_manager = RiskManager(config=custom_config)
    print(f"Config:")
    print(f"  : {risk_manager.config['max_volatility']}")
    print(f"  Loss: {risk_manager.config['max_daily_loss_pct']:.0%}")
    print(f"  Loss: {risk_manager.config['max_consecutive_losses']}")
    
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
    
    # 早上: 正常交易
    for i in range(3):
        risk_manager.record_trade(1, True)
        allowed, reason = risk_manager.check_risk(50000 + i*10, risk_manager.current_capital + 1)
        print(f"  Trade{i+1} - Profit +1, : {allowed}")
    
    # 中午: 连续亏损
    for i in range(3):
        risk_manager.record_trade(-1.5, False)
        allowed, reason = risk_manager.check_risk(50000 - i*10, risk_manager.current_capital - 1.5)
        print(f"  Trade{i+4} - Loss -1.5, : {allowed}, : {reason if not allowed else 'N/A'}")
    
    # 检查最终状态
    status = risk_manager.get_risk_status()
    print(f"\n:")
    print(f"  : {status['total_pnl']}")
    print(f"  Loss: {status['consecutive_losses']}")
    print(f"  Trade: {status['is_trading_allowed']}")
    
    print("[OK] ")

def run_all_tests():
    """运行所有测试"""
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
        print("[OK] !Risk")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] Failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n[FAIL] : {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
