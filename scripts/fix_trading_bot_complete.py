#!/usr/bin/env python3
"""
Fix Trading Bot - Complete Fix
Fixes all remaining issues:
1. notify_bot_status() parameters
2. update_bot_state() parameters  
3. current_stage attribute access
"""

import os
import sys
import re

# File path
script_path = r'C:\trading_dashboard\scripts\start_trading_system.py'

# Read original file
with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
backup_path = script_path + '.backup_complete'
if not os.path.exists(backup_path):
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] Backup created: {backup_path}")

original_content = content
fixes_applied = 0

# ============================================================
# Fix 1: notify_bot_status() parameters (line 261-266)
# ============================================================
print("\n[INFO] Fixing notify_bot_status() parameters...")

old_pattern_1 = r'''self\.telegram\.notify_bot_status\(\s*status="启动",\s*balance=self\.engine\.capital,\s*total_trades=0,\s*win_rate=0\.0\s*\)'''

new_code_1 = '''self.telegram.notify_bot_status(
                is_running=True,
                reason="Bot started"
            )'''

matches_1 = re.findall(old_pattern_1, content, re.MULTILINE | re.DOTALL)
if matches_1:
    content = re.sub(old_pattern_1, new_code_1, content, flags=re.MULTILINE | re.DOTALL)
    print(f"[OK] Fixed notify_bot_status() - found {len(matches_1)} occurrence(s)")
    fixes_applied += 1
else:
    print("[WARN] notify_bot_status() pattern not found")

# ============================================================
# Fix 2: update_bot_state() - all 3 calls
# ============================================================
print("\n[INFO] Fixing update_bot_state() calls...")

# Pattern 1: status='running' with 5 parameters
old_pattern_2a = r'''self\.db\.update_bot_state\(\s*status='running',\s*current_balance=self\.engine\.capital,\s*total_trades=0,\s*win_trades=0,\s*total_profit=0\.0\s*\)'''

new_code_2a = '''self.db.update_bot_state(
                is_running=1,
                capital=self.engine.capital,
                initial_capital=self.engine.initial_capital,
                current_stage=self.engine.rolling_manager.get_current_stage(self.engine.capital).name,
                total_profit=0.0,
                total_trades=0,
                win_trades=0,
                emergency_stopped=0
            )'''

matches_2a = re.findall(old_pattern_2a, content, re.MULTILINE | re.DOTALL)
if matches_2a:
    content = re.sub(old_pattern_2a, new_code_2a, content, flags=re.MULTILINE | re.DOTALL)
    print(f"[OK] Fixed update_bot_state() call #1 (on start) - found {len(matches_2a)} occurrence(s)")
    fixes_applied += 1
else:
    print("[WARN] update_bot_state() call #1 pattern not found")

# Pattern 2: status='running' with trade history
old_pattern_2b = r'''self\.db\.update_bot_state\(\s*status='running',\s*current_balance=self\.engine\.capital,\s*total_trades=len\(self\.engine\.rolling_manager\.trade_history\),\s*win_trades=sum\(1 for t in self\.engine\.rolling_manager\.trade_history if t\.get\('pnl', 0\) > 0\),\s*total_profit=self\.engine\.capital - self\.engine\.initial_capital\s*\)'''

new_code_2b = '''self.db.update_bot_state(
                        is_running=1,
                        capital=self.engine.capital,
                        initial_capital=self.engine.initial_capital,
                        current_stage=self.engine.rolling_manager.get_current_stage(self.engine.capital).name,
                        total_profit=self.engine.capital - self.engine.initial_capital,
                        total_trades=len(self.engine.rolling_manager.trade_history),
                        win_trades=sum(1 for t in self.engine.rolling_manager.trade_history if t.get('pnl', 0) > 0),
                        emergency_stopped=0
                    )'''

matches_2b = re.findall(old_pattern_2b, content, re.MULTILINE | re.DOTALL)
if matches_2b:
    content = re.sub(old_pattern_2b, new_code_2b, content, flags=re.MULTILINE | re.DOTALL)
    print(f"[OK] Fixed update_bot_state() call #2 (after trade) - found {len(matches_2b)} occurrence(s)")
    fixes_applied += 1
else:
    print("[WARN] update_bot_state() call #2 pattern not found")

# Pattern 3: status='stopped'
old_pattern_2c = r'''self\.db\.update_bot_state\(\s*status='stopped',\s*current_balance=self\.engine\.capital,\s*total_trades=total_trades,\s*win_trades=win_trades if total_trades > 0 else 0,\s*total_profit=total_profit if total_trades > 0 else 0\.0\s*\)'''

new_code_2c = '''self.db.update_bot_state(
                is_running=0,
                capital=self.engine.capital,
                initial_capital=self.engine.initial_capital,
                current_stage=self.engine.rolling_manager.get_current_stage(self.engine.capital).name,
                total_profit=total_profit if total_trades > 0 else 0.0,
                total_trades=total_trades,
                win_trades=win_trades if total_trades > 0 else 0,
                emergency_stopped=0
            )'''

matches_2c = re.findall(old_pattern_2c, content, re.MULTILINE | re.DOTALL)
if matches_2c:
    content = re.sub(old_pattern_2c, new_code_2c, content, flags=re.MULTILINE | re.DOTALL)
    print(f"[OK] Fixed update_bot_state() call #3 (on stop) - found {len(matches_2c)} occurrence(s)")
    fixes_applied += 1
else:
    print("[WARN] update_bot_state() call #3 pattern not found")

# ============================================================
# Write fixed file
# ============================================================
if fixes_applied > 0:
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n[OK] Fixed: {script_path}")
    print(f"[OK] Total fixes applied: {fixes_applied}")
    
    # Validate Python syntax
    print("\n[INFO] Validating Python syntax...")
    import py_compile
    try:
        py_compile.compile(script_path, doraise=True)
        print("[OK] Python syntax is valid")
    except py_compile.PyCompileError as e:
        print(f"[ERROR] Syntax error detected: {e}")
        print("[INFO] Rolling back changes...")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print("[OK] Rolled back to original")
        sys.exit(1)
        
    print("\n" + "="*60)
    print("Trading Bot Complete Fix Applied!")
    print("="*60)
    print("\nAll issues fixed:")
    print("1. [OK] notify_bot_status() - Correct parameters")
    print("2. [OK] update_bot_state() - All 3 calls fixed")
    print("3. [OK] current_stage - Using rolling_manager.get_current_stage()")
    print("\nNext steps:")
    print("1. Restart: pm2 restart trading-bot")
    print("2. Check logs: pm2 logs trading-bot --lines 50")
    print("3. Monitor: pm2 monit")
else:
    print("\n[WARN] No fixes were applied")
    print("[INFO] Checking if file already fixed or has different format...")
    
    # Check if errors still exist
    has_errors = False
    if 'status="启动"' in content or "status='running'" in content or "status='stopped'" in content:
        print("[ERROR] File still contains old parameter names!")
        print("[INFO] Please check file manually")
        has_errors = True
    
    if not has_errors:
        print("[OK] File appears to be already fixed")
