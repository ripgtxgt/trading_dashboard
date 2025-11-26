#!/usr/bin/env python3
"""
Fix KuCoinTrader initialization call
"""

import os
import sys

# 读取原始文件
script_path = r'C:\trading_dashboard\scripts\start_trading_system.py'

with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找需要替换的代码块
old_code = '''        self.trader = KuCoinTrader(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
            is_sandbox=os.getenv('KUCOIN_SANDBOX', 'false').lower() == 'true'
        )'''

new_code = '''        # Create config dictionary for KuCoinTrader
        kucoin_config = {
            'api_key': api_key,
            'api_secret': api_secret,
            'api_passphrase': api_passphrase,
            'is_sandbox': os.getenv('KUCOIN_SANDBOX', 'false').lower() == 'true'
        }
        self.trader = KuCoinTrader(kucoin_config)'''

if old_code not in content:
    print("✗ Could not find the code to replace")
    print("The file may have already been fixed or has a different format")
    sys.exit(1)

# 替换代码
new_content = content.replace(old_code, new_code)

# 备份原文件（如果还没有备份）
backup_path = script_path + '.backup2'
if not os.path.exists(backup_path):
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Backup created: {backup_path}")

# 写入修改后的文件
with open(script_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print(f"✓ Fixed: {script_path}")

print("\n" + "="*60)
print("KuCoinTrader Call Fix Applied Successfully!")
print("="*60)
print("\nChanges made:")
print("1. Changed KuCoinTrader initialization to use config dict")
print("2. Fixed parameter passing to match KuCoinTrader.__init__()")
print("\nNext steps:")
print("1. Restart trading-bot: pm2 restart trading-bot")
print("2. Check logs: pm2 logs trading-bot --lines 30")
