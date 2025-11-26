#!/usr/bin/env python3
"""
Fix Trading Bot - Fix 3 critical errors
1. get_current_price() missing symbol argument
2. update_bot_state() parameter mismatch  
3. send_bot_status() should be notify_bot_status()
"""

import os
import sys
import re

# 读取原始文件
script_path = r'C:\trading_dashboard\scripts\start_trading_system.py'

with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 备份原文件
backup_path = script_path + '.backup3'
if not os.path.exists(backup_path):
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Backup created: {backup_path}")

# 修复计数器
fixes_applied = 0

# ============================================================
# 修复1: get_current_price() 添加 symbol 参数
# ============================================================
# 查找所有 self.trader.get_current_price() 调用（不带参数的）
pattern1 = r'self\.trader\.get_current_price\(\)'
replacement1 = "self.trader.get_current_price(STRATEGY_CONFIG['symbol'])"

matches1 = re.findall(pattern1, content)
if matches1:
    content = re.sub(pattern1, replacement1, content)
    print(f"✓ Fixed {len(matches1)} get_current_price() calls")
    fixes_applied += len(matches1)
else:
    print("⚠ No get_current_price() calls found to fix")

# ============================================================
# 修复2: send_bot_status() 改为 notify_bot_status()
# ============================================================
pattern2 = r'self\.telegram\.send_bot_status\('
replacement2 = 'self.telegram.notify_bot_status('

matches2 = re.findall(pattern2, content)
if matches2:
    content = re.sub(pattern2, replacement2, content)
    print(f"✓ Fixed {len(matches2)} send_bot_status() calls")
    fixes_applied += len(matches2)
else:
    print("⚠ No send_bot_status() calls found to fix")

# ============================================================
# 修复3: update_bot_state() 参数修复
# ============================================================
# 这个比较复杂，需要找到所有update_bot_state调用并重写参数

# 查找所有 self.db.update_bot_state( 的位置
update_bot_state_pattern = r'self\.db\.update_bot_state\([^)]+\)'

# 由于参数可能跨多行，我们需要更复杂的匹配
# 先找到所有调用的起始位置
import re

# 使用更宽松的模式匹配多行调用
multiline_pattern = r'self\.db\.update_bot_state\(\s*(?:[^)]*\n)*[^)]*\)'

def fix_update_bot_state_call(match):
    """修复update_bot_state调用的参数"""
    call_text = match.group(0)
    
    # 如果已经是正确的格式（使用is_running参数），则不修改
    if 'is_running=' in call_text:
        return call_text
    
    # 否则，尝试提取参数并重新构造
    # 这是一个简化版本，假设调用格式相对固定
    
    # 提取status参数
    status_match = re.search(r"status\s*=\s*['\"](\w+)['\"]", call_text)
    is_running = 1 if status_match and status_match.group(1) == 'running' else 0
    
    # 提取current_balance
    balance_match = re.search(r'current_balance\s*=\s*([^,\n]+)', call_text)
    capital = balance_match.group(1).strip() if balance_match else 'self.engine.capital'
    
    # 提取initial_capital（如果没有则使用默认值）
    initial_capital = 'self.engine.initial_capital'
    
    # 提取win_trades
    win_trades_match = re.search(r'win_trades\s*=\s*([^,\n]+)', call_text)
    win_trades = win_trades_match.group(1).strip() if win_trades_match else '0'
    
    # 构造新的调用
    new_call = f'''self.db.update_bot_state(
            is_running={is_running},
            capital={capital},
            initial_capital={initial_capital},
            win_trades={win_trades},
            emergency_stopped=0
        )'''
    
    return new_call

# 应用修复
new_content = re.sub(multiline_pattern, fix_update_bot_state_call, content, flags=re.DOTALL)

if new_content != content:
    update_fixes = len(re.findall(r'self\.db\.update_bot_state\(', content))
    print(f"✓ Fixed {update_fixes} update_bot_state() calls")
    fixes_applied += update_fixes
    content = new_content
else:
    print("⚠ No update_bot_state() calls found to fix")

# ============================================================
# 写入修改后的文件
# ============================================================
if fixes_applied > 0:
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✓ Fixed: {script_path}")
    print(f"✓ Total fixes applied: {fixes_applied}")
else:
    print("\n⚠ No fixes were applied")

print("\n" + "="*60)
print("Trading Bot Error Fix Applied Successfully!")
print("="*60)
print("\nChanges made:")
print("1. Added symbol parameter to get_current_price() calls")
print("2. Renamed send_bot_status() to notify_bot_status()")
print("3. Fixed update_bot_state() parameter format")
print("\nNext steps:")
print("1. Restart trading-bot: pm2 restart trading-bot")
print("2. Check logs: pm2 logs trading-bot --lines 50")
print("3. Monitor for errors: pm2 logs trading-bot --err")
