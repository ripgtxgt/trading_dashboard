# Trading Bot 手动修复指南

由于自动修复脚本无法匹配文件格式，请按照以下步骤手动修复 `start_trading_system.py` 文件。

## 📋 需要修复的错误

根据日志，有3个错误需要修复：

1. **notify_bot_status()** 参数错误（第261-266行）
2. **update_bot_state()** 参数错误（第272-278行）
3. **update_bot_state()** 参数错误（第218-224行）
4. **update_bot_state()** 参数错误（第379-385行）

---

## 🔧 修复步骤

### 1. 打开文件进行编辑

```cmd
notepad C:\trading_dashboard\scripts\start_trading_system.py
```

或使用您喜欢的文本编辑器（如 VSCode、Notepad++）

---

### 2. 修复 notify_bot_status() 调用（约第261-266行）

**查找这段代码：**

```python
            self.telegram.notify_bot_status(
                status="启动",
                balance=self.engine.capital,
                total_trades=0,
                win_rate=0.0
            )
```

**替换为：**

```python
            self.telegram.notify_bot_status(
                is_running=True,
                reason="Bot started"
            )
```

**说明：** `notify_bot_status()` 方法只接受 `is_running` 和 `reason` 两个参数。

---

### 3. 修复 update_bot_state() 调用 #1（约第272-278行）

**查找这段代码：**

```python
            self.db.update_bot_state(
                status='running',
                current_balance=self.engine.capital,
                total_trades=0,
                win_trades=0,
                total_profit=0.0
            )
```

**替换为：**

```python
            self.db.update_bot_state(
                is_running=1,
                capital=self.engine.capital,
                initial_capital=self.engine.initial_capital,
                current_stage=self.engine.rolling_manager.get_current_stage(self.engine.capital).name,
                total_profit=0.0,
                total_trades=0,
                win_trades=0,
                emergency_stopped=0
            )
```

---

### 4. 修复 update_bot_state() 调用 #2（约第218-224行）

**查找这段代码：**

```python
                    self.db.update_bot_state(
                        status='running',
                        current_balance=self.engine.capital,
                        total_trades=len(self.engine.rolling_manager.trade_history),
                        win_trades=sum(1 for t in self.engine.rolling_manager.trade_history if t.get('pnl', 0) > 0),
                        total_profit=self.engine.capital - self.engine.initial_capital
                    )
```

**替换为：**

```python
                    self.db.update_bot_state(
                        is_running=1,
                        capital=self.engine.capital,
                        initial_capital=self.engine.initial_capital,
                        current_stage=self.engine.rolling_manager.get_current_stage(self.engine.capital).name,
                        total_profit=self.engine.capital - self.engine.initial_capital,
                        total_trades=len(self.engine.rolling_manager.trade_history),
                        win_trades=sum(1 for t in self.engine.rolling_manager.trade_history if t.get('pnl', 0) > 0),
                        emergency_stopped=0
                    )
```

---

### 5. 修复 update_bot_state() 调用 #3（约第379-385行）

**查找这段代码：**

```python
            self.db.update_bot_state(
                status='stopped',
                current_balance=self.engine.capital,
                total_trades=total_trades,
                win_trades=win_trades if total_trades > 0 else 0,
                total_profit=total_profit if total_trades > 0 else 0.0
            )
```

**替换为：**

```python
            self.db.update_bot_state(
                is_running=0,
                capital=self.engine.capital,
                initial_capital=self.engine.initial_capital,
                current_stage=self.engine.rolling_manager.get_current_stage(self.engine.capital).name,
                total_profit=total_profit if total_trades > 0 else 0.0,
                total_trades=total_trades,
                win_trades=win_trades if total_trades > 0 else 0,
                emergency_stopped=0
            )
```

---

## 📝 参数说明

### notify_bot_status() 正确签名

```python
def notify_bot_status(self, is_running, reason=None):
    """
    is_running: bool - True表示启动，False表示停止
    reason: str - 可选的原因说明
    """
```

### update_bot_state() 正确签名

```python
def update_bot_state(self, is_running, capital, initial_capital, current_stage, 
                     total_profit, total_trades, win_trades, emergency_stopped=0):
    """
    is_running: int - 1表示运行中，0表示已停止
    capital: float - 当前资金
    initial_capital: float - 初始资金
    current_stage: str - 当前阶段名称
    total_profit: float - 总盈亏
    total_trades: int - 总交易次数
    win_trades: int - 盈利交易次数
    emergency_stopped: int - 是否紧急停止（0或1）
    """
```

---

## ✅ 验证修复

修改完成后：

1. **保存文件**（Ctrl+S）

2. **验证Python语法**：
   ```cmd
   python -m py_compile C:\trading_dashboard\scripts\start_trading_system.py
   ```
   
   如果没有输出任何错误，说明语法正确。

3. **重启trading-bot**：
   ```cmd
   pm2 restart trading-bot
   ```

4. **查看日志**：
   ```cmd
   pm2 logs trading-bot --lines 50
   ```

5. **检查是否还有错误**：
   - 不应该再有 `got an unexpected keyword argument 'status'` 错误
   - 不应该再有 `object has no attribute 'current_stage'` 错误

---

## 🔍 使用 Ctrl+F 快速定位

在文本编辑器中使用 **Ctrl+F** 搜索以下关键字快速定位需要修改的位置：

1. 搜索 `status="启动"` → 找到 notify_bot_status() 调用
2. 搜索 `status='running'` → 找到 update_bot_state() 调用（2处）
3. 搜索 `status='stopped'` → 找到 update_bot_state() 调用（1处）

---

## ⚠️ 注意事项

1. **保持缩进一致**：Python对缩进非常敏感，确保修改后的代码缩进与周围代码一致
2. **不要改动其他代码**：只修改上述4处调用，不要改动其他部分
3. **备份文件**：修改前建议备份原文件
   ```cmd
   copy C:\trading_dashboard\scripts\start_trading_system.py C:\trading_dashboard\scripts\start_trading_system.py.backup
   ```

---

## 📞 遇到问题？

如果修改后仍有错误，请提供：
1. 修改后的代码截图
2. 完整的错误日志
3. Python语法检查结果
