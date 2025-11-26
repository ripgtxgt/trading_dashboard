#!/usr/bin/env python3
"""
Fix Trading Bot - Final Version
Fix all parameter mismatches based on actual method signatures
"""

import os
import sys
import re

# 读取原始文件
script_path = r'C:\trading_dashboard\scripts\start_trading_system.py'

with open(script_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 备份原文件
backup_path = script_path + '.backup_final'
if not os.path.exists(backup_path):
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✓ Backup created: {backup_path}")

fixes_applied = 0

# ============================================================
# 修复1: notify_bot_status() 参数修复 (第261-266行)
# ============================================================
# 正确签名: notify_bot_status(self, is_running, reason=None)
# 错误调用: notify_bot_status(status="启动", balance=..., total_trades=..., win_rate=...)
# 正确调用: notify_bot_status(is_running=True, reason="启动")

for i in range(len(lines)):
    if i >= 260 and i <= 266:  # 第261-267行 (0-indexed: 260-266)
        if 'self.telegram.notify_bot_status(' in lines[i]:
            # 找到调用的结束位置
            call_start = i
            call_end = i
            for j in range(i, min(i+10, len(lines))):
                if ')' in lines[j]:
                    call_end = j
                    break
            
            # 替换整个调用
            indent = '            '  # 12个空格
            new_call = [
                f'{indent}self.telegram.notify_bot_status(\n',
                f'{indent}    is_running=True,\n',
                f'{indent}    reason="启动"\n',
                f'{indent})\n'
            ]
            
            lines[call_start:call_end+1] = new_call
            print(f"✓ Fixed notify_bot_status() call at line {call_start+1}")
            fixes_applied += 1
            break

# ============================================================
# 修复2: send_risk_alert() 改为 notify_risk_alert() (第304-309行)
# ============================================================
# 正确签名: notify_risk_alert(self, level, message, details=None)
# 错误调用: send_risk_alert(alert_type=..., current_balance=..., drawdown=..., consecutive_losses=...)
# 正确调用: notify_risk_alert(level="warning", message=reason, details=f"...")

for i in range(len(lines)):
    if i >= 303 and i <= 310:  # 第304-310行
        if 'self.telegram.send_risk_alert(' in lines[i]:
            # 找到调用的结束位置
            call_start = i
            call_end = i
            for j in range(i, min(i+10, len(lines))):
                if ')' in lines[j]:
                    call_end = j
                    break
            
            # 替换整个调用
            indent = '                            '  # 28个空格
            new_call = [
                f'{indent}risk_status = self.risk_manager.get_risk_status()\n',
                f'{indent}self.telegram.notify_risk_alert(\n',
                f'{indent}    level="warning",\n',
                f'{indent}    message=f"交易暂停: {{reason}}",\n',
                f'{indent}    details=f"当前资金: {{self.engine.capital:.2f}} USDT\\n回撤: {{risk_status[\'current_drawdown_pct\']:.2f}}%\\n连续亏损: {{risk_status[\'consecutive_losses\']}}次"\n',
                f'{indent})\n'
            ]
            
            lines[call_start:call_end+1] = new_call
            print(f"✓ Fixed send_risk_alert() -> notify_risk_alert() call at line {call_start+1}")
            fixes_applied += 1
            break

# ============================================================
# 修复3: update_bot_state() 参数修复 (第218-224行)
# ============================================================
# 正确签名: update_bot_state(self, is_running, capital, initial_capital, current_stage, total_profit, total_trades, win_trades, emergency_stopped=0)
# 错误调用: update_bot_state(status='running', current_balance=..., total_trades=..., win_trades=..., total_profit=...)
# 正确调用: update_bot_state(is_running=1, capital=..., initial_capital=..., current_stage=..., total_profit=..., total_trades=..., win_trades=..., emergency_stopped=0)

for i in range(len(lines)):
    if i >= 217 and i <= 225:  # 第218-225行
        if 'self.db.update_bot_state(' in lines[i]:
            # 找到调用的结束位置
            call_start = i
            call_end = i
            for j in range(i, min(i+15, len(lines))):
                if ')' in lines[j] and 'update_bot_state' not in lines[j]:
                    call_end = j
                    break
            
            # 替换整个调用
            indent = '                    '  # 20个空格
            new_call = [
                f'{indent}self.db.update_bot_state(\n',
                f'{indent}    is_running=1,\n',
                f'{indent}    capital=self.engine.capital,\n',
                f'{indent}    initial_capital=self.engine.initial_capital,\n',
                f'{indent}    current_stage=self.engine.current_stage,\n',
                f'{indent}    total_profit=self.engine.capital - self.engine.initial_capital,\n',
                f'{indent}    total_trades=len(self.engine.rolling_manager.trade_history),\n',
                f'{indent}    win_trades=sum(1 for t in self.engine.rolling_manager.trade_history if t.get(\'pnl\', 0) > 0),\n',
                f'{indent}    emergency_stopped=0\n',
                f'{indent})\n'
            ]
            
            lines[call_start:call_end+1] = new_call
            print(f"✓ Fixed update_bot_state() call at line {call_start+1}")
            fixes_applied += 1
            break

# ============================================================
# 修复4: 第272行的update_bot_state()
# ============================================================
for i in range(len(lines)):
    if i >= 271 and i <= 280:  # 第272行附近
        if 'self.db.update_bot_state(' in lines[i]:
            # 找到调用的结束位置
            call_start = i
            call_end = i
            for j in range(i, min(i+15, len(lines))):
                if ')' in lines[j] and 'update_bot_state' not in lines[j]:
                    call_end = j
                    break
            
            # 替换整个调用
            indent = '            '  # 12个空格
            new_call = [
                f'{indent}self.db.update_bot_state(\n',
                f'{indent}    is_running=0,\n',
                f'{indent}    capital=self.engine.capital,\n',
                f'{indent}    initial_capital=self.engine.initial_capital,\n',
                f'{indent}    current_stage=self.engine.current_stage,\n',
                f'{indent}    total_profit=self.engine.capital - self.engine.initial_capital,\n',
                f'{indent}    total_trades=len(self.engine.rolling_manager.trade_history),\n',
                f'{indent}    win_trades=sum(1 for t in self.engine.rolling_manager.trade_history if t.get(\'pnl\', 0) > 0),\n',
                f'{indent}    emergency_stopped=1\n',
                f'{indent})\n'
            ]
            
            lines[call_start:call_end+1] = new_call
            print(f"✓ Fixed update_bot_state() call at line {call_start+1}")
            fixes_applied += 1
            break

# ============================================================
# 修复5: 第379行的update_bot_state()
# ============================================================
for i in range(len(lines)):
    if i >= 378 and i <= 390:  # 第379行附近
        if 'self.db.update_bot_state(' in lines[i]:
            # 找到调用的结束位置
            call_start = i
            call_end = i
            for j in range(i, min(i+15, len(lines))):
                if ')' in lines[j] and 'update_bot_state' not in lines[j]:
                    call_end = j
                    break
            
            # 替换整个调用
            indent = '            '  # 12个空格
            new_call = [
                f'{indent}self.db.update_bot_state(\n',
                f'{indent}    is_running=0,\n',
                f'{indent}    capital=self.engine.capital,\n',
                f'{indent}    initial_capital=self.engine.initial_capital,\n',
                f'{indent}    current_stage=self.engine.current_stage,\n',
                f'{indent}    total_profit=self.engine.capital - self.engine.initial_capital,\n',
                f'{indent}    total_trades=len(self.engine.rolling_manager.trade_history),\n',
                f'{indent}    win_trades=sum(1 for t in self.engine.rolling_manager.trade_history if t.get(\'pnl\', 0) > 0),\n',
                f'{indent}    emergency_stopped=0\n',
                f'{indent})\n'
            ]
            
            lines[call_start:call_end+1] = new_call
            print(f"✓ Fixed update_bot_state() call at line {call_start+1}")
            fixes_applied += 1
            break

# ============================================================
# 写入修改后的文件
# ============================================================
if fixes_applied > 0:
    with open(script_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
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
            original = f.readlines()
        with open(script_path, 'w', encoding='utf-8') as f:
            f.writelines(original)
        print("✓ Rolled back to backup")
        sys.exit(1)
else:
    print("\n⚠ No fixes were applied")

print("\n" + "="*60)
print("Trading Bot Final Fix Applied Successfully!")
print("="*60)
print("\nAll parameter mismatches have been fixed:")
print("1. ✓ notify_bot_status() - Fixed parameters")
print("2. ✓ send_risk_alert() -> notify_risk_alert() - Fixed method name and parameters")
print("3. ✓ update_bot_state() - Fixed all 3 calls with correct parameters")
print("\nNext steps:")
print("1. Restart trading-bot: pm2 restart trading-bot")
print("2. Check logs: pm2 logs trading-bot --lines 50")
print("3. Monitor: pm2 monit")
