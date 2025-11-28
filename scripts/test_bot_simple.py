#!/usr/bin/env python3
"""
简化的Trading Bot测试脚本
用于验证核心配置和导入
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*50)
print("Trading Bot Configuration Test")
print("="*50)

# 1. 测试配置文件
print("\n1. Testing config.py...")
try:
    from config import (
        KUCOIN_API_KEY,
        KUCOIN_API_SECRET, 
        KUCOIN_API_PASSPHRASE,
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHAT_ID
    )
    print(f"   ✓ KuCoin API Key: {KUCOIN_API_KEY[:10]}...")
    print(f"   ✓ Telegram Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"   ✓ Telegram Chat ID: {TELEGRAM_CHAT_ID}")
except Exception as e:
    print(f"   ✗ Config import failed: {e}")
    sys.exit(1)

# 2. 测试核心模块导入
print("\n2. Testing core module imports...")
modules_to_test = [
    'live_strategy_engine_rolling',
    'kucoin_trader',
    'live_trading_config',
    'rolling_manager',
    'risk_manager'
]

failed_modules = []
for module_name in modules_to_test:
    try:
        __import__(module_name)
        print(f"   ✓ {module_name}")
    except Exception as e:
        print(f"   ✗ {module_name}: {e}")
        failed_modules.append(module_name)

# 3. 测试数据库路径
print("\n3. Testing database setup...")
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'trading.db')
print(f"   Database path: {db_path}")
print(f"   Database exists: {os.path.exists(db_path)}")

# 4. 总结
print("\n" + "="*50)
if failed_modules:
    print(f"FAILED: {len(failed_modules)} modules failed to import")
    print(f"Failed modules: {', '.join(failed_modules)}")
    sys.exit(1)
else:
    print("SUCCESS: All core modules loaded successfully")
    print("Trading bot is ready to start!")
print("="*50)
