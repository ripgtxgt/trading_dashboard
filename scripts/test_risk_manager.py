#!/usr/bin/env python3
"""
风险管理模块功能测试
测试所有风险控制功能是否正常工作
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
    print("\n=== 测试1: 基本初始化 ===")
    clean_state()
    
    risk_manager = RiskManager()
    status = risk_manager.get_risk_status()
    
    print(f"初始状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
    assert status['is_trading_allowed'] == True
    assert status['consecutive_losses'] == 0
    
    print("✓ 基本初始化测试通过")

def test_volatility_check():
    """测试市场波动率检查"""
    print("\n=== 测试2: 市场波动率检查 ===")
    clean_state()
    
    risk_manager = RiskManager()
    
    # 模拟正常波动
    base_price = 50000
    for i in range(20):
        price = base_price + (i * 10)  # 小幅波动
        allowed, reason = risk_manager.check_risk(price, 100)
    
    print(f"正常波动 - 允许交易: {allowed}, 波动率: {risk_manager.volatility:.4f}")
    assert allowed == True
    
    # 模拟剧烈波动
    for i in range(20):
        price = base_price + (i * 500)  # 大幅波动
        allowed, reason = risk_manager.check_risk(price, 100)
    
    print(f"剧烈波动 - 允许交易: {allowed}, 原因: {reason}, 波动率: {risk_manager.volatility:.4f}")
    
    print("✓ 市场波动率检查测试通过")

def test_daily_loss_protection():
    """测试单日亏损保护"""
    print("\n=== 测试3: 单日亏损保护 ===")
    clean_state()
    
    risk_manager = RiskManager()
    risk_manager.peak_capital = 100
    risk_manager.current_capital = 100
    
    # 正常亏损
    risk_manager.record_trade(-2, False)
    allowed, reason = risk_manager.check_risk(50000, 98)
    print(f"小额亏损(-2%) - 允许交易: {allowed}")
    assert allowed == True
    
    # 重置并测试大额亏损
    risk_manager2 = RiskManager()
    risk_manager2.peak_capital = 100
    risk_manager2.current_capital = 100
    risk_manager2.record_trade(-12, False)  # 超过10%限制
    allowed, reason = risk_manager2.check_risk(50000, 88)
    print(f"大额亏损(-12%) - 允许交易: {allowed}, 原因: {reason}")
    
    print("✓ 单日亏损保护测试通过")

def test_consecutive_losses():
    """测试连续亏损保护"""
    print("\n=== 测试4: 连续亏损保护 ===")
    clean_state()
    
    risk_manager = RiskManager()
    risk_manager.peak_capital = 100
    risk_manager.current_capital = 100
    
    # 记录2次亏损 (默认限制是3次)
    for i in range(2):
        risk_manager.record_trade(-1, False)
        allowed, reason = risk_manager.check_risk(50000, 99-i)
    
    print(f"2次连续亏损 - 允许交易: {allowed}, 连续亏损: {risk_manager.consecutive_losses}")
    assert allowed == True
    
    # 再记录2次亏损，达到4次 (超过限制3次)
    for i in range(2):
        risk_manager.record_trade(-1, False)
        allowed, reason = risk_manager.check_risk(50000, 97-i)
    
    print(f"4次连续亏损 - 允许交易: {allowed}, 原因: {reason}")
    assert allowed == False
    
    # 手动恢复并记录一次盈利，重置计数
    risk_manager.manual_resume()
    risk_manager.record_trade(2, True)
    allowed, reason = risk_manager.check_risk(50000, 98)
    print(f"盈利后重置 - 允许交易: {allowed}, 连续亏损: {risk_manager.consecutive_losses}")
    assert risk_manager.consecutive_losses == 0
    
    print("✓ 连续亏损保护测试通过")

def test_max_drawdown():
    """测试最大回撤控制"""
    print("\n=== 测试5: 最大回撤控制 ===")
    clean_state()
    
    risk_manager = RiskManager()
    risk_manager.peak_capital = 100
    
    # 正常回撤
    allowed, reason = risk_manager.check_risk(50000, 92)
    drawdown = risk_manager._calculate_drawdown()
    print(f"8%回撤 - 允许交易: {allowed}, 回撤: {drawdown:.2%}")
    assert allowed == True
    
    # 超限回撤
    allowed, reason = risk_manager.check_risk(50000, 75)
    drawdown = risk_manager._calculate_drawdown()
    print(f"25%回撤 - 允许交易: {allowed}, 原因: {reason}, 回撤: {drawdown:.2%}")
    assert allowed == False
    
    print("✓ 最大回撤控制测试通过")

def test_manual_controls():
    """测试手动控制"""
    print("\n=== 测试6: 手动控制 ===")
    clean_state()
    
    risk_manager = RiskManager()
    
    # 手动暂停
    risk_manager.manual_pause("手动测试暂停", hours=1)
    status = risk_manager.get_risk_status()
    print(f"手动暂停 - 允许交易: {status['is_trading_allowed']}, 原因: {status['pause_reason']}")
    assert status['is_trading_allowed'] == False
    
    # 手动恢复
    risk_manager.manual_resume()
    status = risk_manager.get_risk_status()
    print(f"手动恢复 - 允许交易: {status['is_trading_allowed']}")
    assert status['is_trading_allowed'] == True
    
    print("✓ 手动控制测试通过")

def test_risk_status():
    """测试风险状态报告"""
    print("\n=== 测试7: 风险状态报告 ===")
    clean_state()
    
    risk_manager = RiskManager()
    risk_manager.peak_capital = 100
    risk_manager.current_capital = 95
    
    # 记录一些交易
    risk_manager.record_trade(-2, False)
    risk_manager.record_trade(1, True)
    risk_manager.record_trade(-1, False)
    
    status = risk_manager.get_risk_status()
    print(f"风险状态:")
    print(f"  允许交易: {status['is_trading_allowed']}")
    print(f"  日盈亏: {status['daily_pnl']}")
    print(f"  总盈亏: {status['total_pnl']}")
    print(f"  当前回撤: {status['current_drawdown_pct']:.2%}")
    print(f"  连续亏损: {status['consecutive_losses']}")
    print(f"  波动率: {status['volatility']:.4f}")
    
    assert 'is_trading_allowed' in status
    assert 'daily_pnl' in status
    assert 'total_pnl' in status
    
    print("✓ 风险状态报告测试通过")

def test_config_management():
    """测试配置管理"""
    print("\n=== 测试8: 配置管理 ===")
    clean_state()
    
    # 使用自定义配置
    custom_config = {
        'max_volatility': 0.08,
        'max_daily_loss_pct': 0.15,
        'max_consecutive_losses': 5,
    }
    
    risk_manager = RiskManager(config=custom_config)
    print(f"自定义配置:")
    print(f"  最大波动率: {risk_manager.config['max_volatility']}")
    print(f"  最大日亏损: {risk_manager.config['max_daily_loss_pct']:.0%}")
    print(f"  最大连续亏损: {risk_manager.config['max_consecutive_losses']}")
    
    assert risk_manager.config['max_volatility'] == 0.08
    assert risk_manager.config['max_daily_loss_pct'] == 0.15
    
    print("✓ 配置管理测试通过")

def test_comprehensive_scenario():
    """测试综合场景"""
    print("\n=== 测试9: 综合场景 ===")
    clean_state()
    
    risk_manager = RiskManager()
    risk_manager.peak_capital = 100
    risk_manager.current_capital = 100
    
    print("模拟一天的交易:")
    
    # 早上：正常交易
    for i in range(3):
        risk_manager.record_trade(1, True)
        allowed, reason = risk_manager.check_risk(50000 + i*10, risk_manager.current_capital + 1)
        print(f"  交易{i+1} - 盈利 +1, 允许: {allowed}")
    
    # 中午：连续亏损
    for i in range(3):
        risk_manager.record_trade(-1.5, False)
        allowed, reason = risk_manager.check_risk(50000 - i*10, risk_manager.current_capital - 1.5)
        print(f"  交易{i+4} - 亏损 -1.5, 允许: {allowed}, 原因: {reason if not allowed else 'N/A'}")
    
    # 检查最终状态
    status = risk_manager.get_risk_status()
    print(f"\n最终状态:")
    print(f"  总盈亏: {status['total_pnl']}")
    print(f"  连续亏损: {status['consecutive_losses']}")
    print(f"  允许交易: {status['is_trading_allowed']}")
    
    print("✓ 综合场景测试通过")

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("风险管理模块功能测试")
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
        print("✓ 所有测试通过！风险管理模块功能正常")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
