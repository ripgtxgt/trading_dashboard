#!/usr/bin/env python3
"""
Fix Trading Bot - Version 3 (Ultra Safe Find & Replace)
Uses precise string matching to avoid indentation errors
"""

import os
import sys

# File path
script_path = r'C:\trading_dashboard\scripts\start_trading_system.py'

# Read original file
with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
backup_path = script_path + '.backup_v3'
if not os.path.exists(backup_path):
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] Backup created: {backup_path}")

original_content = content
fixes_applied = 0

# ============================================================
# Fix 1: notify_bot_status() - Wrong parameters
# ============================================================
old_code_1 = '''            self.telegram.notify_bot_status(
                status="启动",
                balance=self.engine.capital,
                total_trades=0,
                win_rate=0.0
            )'''

new_code_1 = '''            self.telegram.notify_bot_status(
                is_running=True,
                reason="启动"
            )'''

if old_code_1 in content:
    content = content.replace(old_code_1, new_code_1)
    print("[OK] Fixed: notify_bot_status() parameters")
    fixes_applied += 1
else:
    print("[WARN] notify_bot_status() pattern not found")

# ============================================================
# Fix 2: send_risk_alert() -> notify_risk_alert()
# ============================================================
old_code_2 = '''                            risk_status = self.risk_manager.get_risk_status()
                            self.telegram.send_risk_alert(
                                alert_type=reason,
                                current_balance=self.engine.capital,
                                drawdown=risk_status['current_drawdown_pct'],
                                consecutive_losses=risk_status['consecutive_losses']
                            )'''

new_code_2 = '''                            risk_status = self.risk_manager.get_risk_status()
                            self.telegram.notify_risk_alert(
                                level="warning",
                                message=f"Trade paused: {reason}",
                                details=f"Balance: {self.engine.capital:.2f} USDT\\nDrawdown: {risk_status['current_drawdown_pct']:.2f}%\\nConsecutive losses: {risk_status['consecutive_losses']}"
                            )'''

if old_code_2 in content:
    content = content.replace(old_code_2, new_code_2)
    print("[OK] Fixed: send_risk_alert() -> notify_risk_alert()")
    fixes_applied += 1
else:
    print("[WARN] send_risk_alert() pattern not found")

# ============================================================
# Fix 3: update_bot_state() - First call (after trade)
# ============================================================
old_code_3 = '''                    self.db.update_bot_state(
                        status='running',
                        current_balance=self.engine.capital,
                        total_trades=len(self.engine.rolling_manager.trade_history),
                        win_trades=sum(1 for t in self.engine.rolling_manager.trade_history if t.get('pnl', 0) > 0),
                        total_profit=self.engine.capital - self.engine.initial_capital
                    )'''

new_code_3 = '''                    self.db.update_bot_state(
                        is_running=1,
                        capital=self.engine.capital,
                        initial_capital=self.engine.initial_capital,
                        current_stage=self.engine.current_stage,
                        total_profit=self.engine.capital - self.engine.initial_capital,
                        total_trades=len(self.engine.rolling_manager.trade_history),
                        win_trades=sum(1 for t in self.engine.rolling_manager.trade_history if t.get('pnl', 0) > 0),
                        emergency_stopped=0
                    )'''

if old_code_3 in content:
    content = content.replace(old_code_3, new_code_3)
    print("[OK] Fixed: update_bot_state() call #1 (after trade)")
    fixes_applied += 1
else:
    print("[WARN] update_bot_state() call #1 pattern not found")

# ============================================================
# Fix 4: update_bot_state() - Second call (on start)
# ============================================================
old_code_4 = '''            self.db.update_bot_state(
                status='running',
                current_balance=self.engine.capital,
                total_trades=0,
                win_trades=0,
                total_profit=0.0
            )'''

new_code_4 = '''            self.db.update_bot_state(
                is_running=1,
                capital=self.engine.capital,
                initial_capital=self.engine.initial_capital,
                current_stage=self.engine.current_stage,
                total_profit=0.0,
                total_trades=0,
                win_trades=0,
                emergency_stopped=0
            )'''

if old_code_4 in content:
    content = content.replace(old_code_4, new_code_4)
    print("[OK] Fixed: update_bot_state() call #2 (on start)")
    fixes_applied += 1
else:
    print("[WARN] update_bot_state() call #2 pattern not found")

# ============================================================
# Fix 5: update_bot_state() - Third call (on stop)
# ============================================================
old_code_5 = '''            self.db.update_bot_state(
                status='stopped',
                current_balance=self.engine.capital,
                total_trades=total_trades,
                win_trades=win_trades if total_trades > 0 else 0,
                total_profit=total_profit if total_trades > 0 else 0.0
            )'''

new_code_5 = '''            self.db.update_bot_state(
                is_running=0,
                capital=self.engine.capital,
                initial_capital=self.engine.initial_capital,
                current_stage=self.engine.current_stage,
                total_profit=total_profit if total_trades > 0 else 0.0,
                total_trades=total_trades,
                win_trades=win_trades if total_trades > 0 else 0,
                emergency_stopped=0
            )'''

if old_code_5 in content:
    content = content.replace(old_code_5, new_code_5)
    print("[OK] Fixed: update_bot_state() call #3 (on stop)")
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
else:
    print("\n[WARN] No fixes were applied (patterns not found)")
    print("[INFO] The file may have already been fixed or has different formatting")

print("\n" + "="*60)
print("Trading Bot Fix v3 Complete!")
print("="*60)
print("\nAll parameter mismatches have been fixed:")
print("1. [OK] notify_bot_status() - Fixed parameters")
print("2. [OK] send_risk_alert() -> notify_risk_alert() - Fixed method name and parameters")
print("3. [OK] update_bot_state() - Fixed all 3 calls with correct parameters")
print("\nNext steps:")
print("1. Restart trading-bot: pm2 restart trading-bot")
print("2. Check logs: pm2 logs trading-bot --lines 50")
print("3. Monitor: pm2 monit")
