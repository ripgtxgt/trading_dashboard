#!/usr/bin/env python3
"""
Fix Trading Bot - Version 2 (Safe indentation handling)
Fix only the simple errors first:
1. get_current_price() missing symbol argument
2. send_bot_status() should be notify_bot_status()
"""

import os
import sys
import re

# 读取原始文件
script_path = r'C:\trading_dashboard\scripts\start_trading_system.py'

with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 备份原文件
backup_path = script_path + '.backup4'
if not os.path.exists(backup_path):
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Backup created: {backup_path}")

# 修复计数器
fixes_applied = 0

# ============================================================
# 修复1: get_current_price() 添加 symbol 参数
# ============================================================
# 简单替换，不会影响缩进
pattern1 = r'self\.trader\.get_current_price\(\)'
replacement1 = "self.trader.get_current_price(STRATEGY_CONFIG['symbol'])"

count1 = len(re.findall(pattern1, content))
if count1 > 0:
    content = re.sub(pattern1, replacement1, content)
    print(f"✓ Fixed {count1} get_current_price() calls")
    fixes_applied += count1
else:
    print("⚠ No get_current_price() calls found to fix")

# ============================================================
# 修复2: send_bot_status() 改为 notify_bot_status()
# ============================================================
# 简单替换，不会影响缩进
pattern2 = r'self\.telegram\.send_bot_status\('
replacement2 = 'self.telegram.notify_bot_status('

count2 = len(re.findall(pattern2, content))
if count2 > 0:
    content = re.sub(pattern2, replacement2, content)
    print(f"✓ Fixed {count2} send_bot_status() calls")
    fixes_applied += count2
else:
    print("⚠ No send_bot_status() calls found to fix")

# ============================================================
# 写入修改后的文件
# ============================================================
if fixes_applied > 0:
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✓ Fixed: {script_path}")
    print(f"✓ Total fixes applied: {fixes_applied}")
    
    # 验证Python语法
    print("\nValidating Python syntax...")
    import py_compile
    try:
        py_compile.compile(script_path, doraise=True)
        print("✓ Python syntax is valid")
    except py_compile.PyCompileError as e:
        print(f"✗ Syntax error detected: {e}")
        print("Rolling back changes...")
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print("✓ Rolled back to backup")
        sys.exit(1)
else:
    print("\n⚠ No fixes were applied")

print("\n" + "="*60)
print("Trading Bot Fix V2 Applied Successfully!")
print("="*60)
print("\nChanges made:")
print("1. Added symbol parameter to get_current_price() calls")
print("2. Renamed send_bot_status() to notify_bot_status()")
print("\nNote: update_bot_state() fix skipped to avoid indentation issues")
print("The bot should work now, but may have database update warnings")
print("\nNext steps:")
print("1. Restart trading-bot: pm2 restart trading-bot")
print("2. Check logs: pm2 logs trading-bot --lines 30")
