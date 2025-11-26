# 修复前后代码对比

## 修复位置 #1: notify_bot_status() 调用

**位置：** 约第261-266行

### ❌ 修复前（错误）

```python
            self.telegram.notify_bot_status(
                status="启动",
                balance=self.engine.capital,
                total_trades=0,
                win_rate=0.0
            )
```

### ✅ 修复后（正确）

```python
            self.telegram.notify_bot_status(
                is_running=True,
                reason="Bot started"
            )
```

---

## 修复位置 #2: update_bot_state() 调用（启动时）

**位置：** 约第272-278行

### ❌ 修复前（错误）

```python
            self.db.update_bot_state(
                status='running',
                current_balance=self.engine.capital,
                total_trades=0,
                win_trades=0,
                total_profit=0.0
            )
```

### ✅ 修复后（正确）

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

## 修复位置 #3: update_bot_state() 调用（交易后）

**位置：** 约第218-224行

### ❌ 修复前（错误）

```python
                    self.db.update_bot_state(
                        status='running',
                        current_balance=self.engine.capital,
                        total_trades=len(self.engine.rolling_manager.trade_history),
                        win_trades=sum(1 for t in self.engine.rolling_manager.trade_history if t.get('pnl', 0) > 0),
                        total_profit=self.engine.capital - self.engine.initial_capital
                    )
```

### ✅ 修复后（正确）

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

## 修复位置 #4: update_bot_state() 调用（停止时）

**位置：** 约第379-385行

### ❌ 修复前（错误）

```python
            self.db.update_bot_state(
                status='stopped',
                current_balance=self.engine.capital,
                total_trades=total_trades,
                win_trades=win_trades if total_trades > 0 else 0,
                total_profit=total_profit if total_trades > 0 else 0.0
            )
```

### ✅ 修复后（正确）

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

## 关键变更总结

### notify_bot_status() 参数变更

| 错误参数 | 正确参数 |
|---------|---------|
| `status="启动"` | `is_running=True` |
| `balance=...` | ❌ 删除 |
| `total_trades=...` | ❌ 删除 |
| `win_rate=...` | ❌ 删除 |
| ❌ 缺失 | `reason="Bot started"` |

### update_bot_state() 参数变更

| 错误参数 | 正确参数 |
|---------|---------|
| `status='running'` 或 `'stopped'` | `is_running=1` 或 `0` |
| `current_balance=...` | `capital=...` |
| ❌ 缺失 | `initial_capital=...` |
| ❌ 缺失 | `current_stage=...` |
| `total_profit=...` | `total_profit=...` ✅ 保持 |
| `total_trades=...` | `total_trades=...` ✅ 保持 |
| `win_trades=...` | `win_trades=...` ✅ 保持 |
| ❌ 缺失 | `emergency_stopped=0` |

---

## 快速搜索关键字

使用文本编辑器的搜索功能（Ctrl+F）查找以下内容：

1. `status="启动"` → 定位到 notify_bot_status() 错误
2. `status='running'` → 定位到 update_bot_state() 错误（2处）
3. `status='stopped'` → 定位到 update_bot_state() 错误（1处）

共需要修改 **4个位置**。
