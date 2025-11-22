# 风险管理模块使用指南

## 📋 目录

1. [功能概述](#功能概述)
2. [风险控制机制](#风险控制机制)
3. [配置说明](#配置说明)
4. [使用方法](#使用方法)
5. [Web Dashboard操作](#web-dashboard操作)
6. [常见问题](#常见问题)

---

## 功能概述

风险管理模块是交易系统的核心安全组件，提供多层次的风险保护机制，确保在市场异常波动或连续亏损时自动暂停交易，保护账户资金安全。

### 主要功能

- **市场波动率监控** - 检测市场异常波动，避免在剧烈行情中交易
- **单日亏损保护** - 限制单日最大亏损比例
- **累计亏损保护** - 限制总体最大亏损比例
- **连续亏损保护** - 检测连续亏损次数，防止策略失效
- **最大回撤控制** - 监控账户回撤，及时止损
- **时间窗口限制** - 限制交易时间段和频率
- **紧急熔断机制** - 价格剧烈变动时立即停止交易
- **自动恢复机制** - 风险消除后自动恢复交易
- **Telegram实时警告** - 触发风险时立即推送通知

---

## 风险控制机制

### 1. 市场波动率监控

**触发条件：**
- 市场波动率超过设定阈值（默认5%）

**计算方法：**
- 使用最近20个价格点计算标准差
- 标准差 > 最大波动率阈值时触发

**暂停时长：** 1小时

**恢复条件：** 波动率降低到阈值以下

---

### 2. 单日亏损保护

**触发条件：**
- 当日累计亏损超过账户峰值资金的10%

**计算公式：**
```
单日亏损率 = |当日盈亏| / 峰值资金
```

**暂停时长：** 24小时（次日自动重置）

**恢复条件：** 
- 自动：24小时后自动恢复
- 手动：在Web Dashboard手动恢复

---

### 3. 累计亏损保护

**触发条件：**
- 总体亏损超过初始资金的30%

**计算公式：**
```
累计亏损率 = |总盈亏| / 初始资金
```

**暂停时长：** 永久（需要手动恢复）

**恢复条件：** 必须在Web Dashboard手动恢复

---

### 4. 连续亏损保护

**触发条件：**
- 连续3笔交易亏损

**计数规则：**
- 每次亏损交易 +1
- 任何一次盈利交易重置为0

**暂停时长：** 1小时

**恢复条件：** 
- 自动：1小时后自动恢复
- 手动：在Web Dashboard手动恢复

---

### 5. 最大回撤控制

**触发条件：**
- 当前资金相对峰值资金回撤超过20%

**计算公式：**
```
回撤率 = (峰值资金 - 当前资金) / 峰值资金
```

**暂停时长：** 永久（需要手动恢复）

**恢复条件：** 必须在Web Dashboard手动恢复

---

### 6. 时间窗口限制

**功能说明：**
- 限制交易时间段（默认关闭）
- 限制交易频率（防止过度交易）

**默认配置：**
- 交易时间：全天24小时（可配置）
- 交易频率：无限制（可配置）

---

### 7. 紧急熔断机制

**触发条件：**
- 5分钟内价格变动超过10%

**暂停时长：** 1小时

**恢复条件：** 
- 自动：1小时后自动恢复
- 手动：在Web Dashboard手动恢复

---

## 配置说明

### 默认配置

风险管理模块的默认配置如下：

```python
{
    # 市场波动控制
    'max_volatility': 0.05,              # 最大波动率5%
    'volatility_window': 20,             # 波动率计算窗口20个数据点
    
    # 亏损保护
    'max_daily_loss_pct': 0.10,          # 单日最大亏损10%
    'max_total_loss_pct': 0.30,          # 累计最大亏损30%
    
    # 连续亏损保护
    'max_consecutive_losses': 3,         # 最多连续3笔亏损
    'consecutive_loss_pause_hours': 1,   # 暂停1小时
    
    # 最大回撤控制
    'max_drawdown_pct': 0.20,            # 最大回撤20%
    
    # 时间窗口限制
    'trading_hours': {
        'enabled': False,                # 默认关闭
        'start_hour': 0,                 # 开始时间（UTC）
        'end_hour': 24,                  # 结束时间（UTC）
    },
    
    # 紧急熔断
    'circuit_breaker': {
        'enabled': True,                 # 默认开启
        'price_change_pct': 0.10,        # 价格变动10%触发
        'time_window_minutes': 5,        # 5分钟内
    },
    
    # 恢复机制
    'auto_resume': {
        'enabled': True,                 # 默认开启自动恢复
        'check_interval_minutes': 30,    # 每30分钟检查一次
    }
}
```

### 自定义配置

您可以通过以下方式修改配置：

#### 方法1：修改配置文件

编辑 `scripts/risk_manager.py` 中的 `_default_config()` 方法：

```python
def _default_config(self) -> Dict:
    return {
        'max_volatility': 0.08,          # 修改为8%
        'max_daily_loss_pct': 0.15,      # 修改为15%
        'max_consecutive_losses': 5,     # 修改为5次
        # ... 其他配置
    }
```

#### 方法2：通过Web Dashboard修改

1. 打开Web Dashboard
2. 进入"风险管理"面板
3. 点击"配置"按钮
4. 修改参数并保存

#### 方法3：代码中传入配置

```python
custom_config = {
    'max_volatility': 0.08,
    'max_daily_loss_pct': 0.15,
}

risk_manager = RiskManager(config=custom_config)
```

---

## 使用方法

### 在交易脚本中集成

风险管理模块已经集成到 `live_strategy_engine_rolling.py` 中，无需额外配置即可使用。

#### 基本使用

```python
from risk_manager import RiskManager

# 初始化风险管理器
risk_manager = RiskManager()

# 在每次交易前检查风险
current_price = get_current_price()
current_capital = get_account_balance()

allowed, reason = risk_manager.check_risk(current_price, current_capital)

if not allowed:
    print(f"交易被暂停: {reason}")
    send_telegram_alert(f"⚠️ 风险警告: {reason}")
    return

# 执行交易
execute_trade()

# 记录交易结果
pnl = calculate_pnl()
is_win = pnl > 0
risk_manager.record_trade(pnl, is_win)
```

#### 获取风险状态

```python
status = risk_manager.get_risk_status()

print(f"允许交易: {status['is_trading_allowed']}")
print(f"暂停原因: {status['pause_reason']}")
print(f"日盈亏: {status['daily_pnl']}")
print(f"总盈亏: {status['total_pnl']}")
print(f"当前回撤: {status['current_drawdown_pct']:.2%}")
print(f"连续亏损: {status['consecutive_losses']}")
print(f"波动率: {status['volatility']:.4f}")
```

#### 手动控制

```python
# 手动暂停交易
risk_manager.manual_pause("手动暂停进行系统维护", hours=2)

# 手动恢复交易
risk_manager.manual_resume()

# 重置每日统计（通常在每天开始时调用）
risk_manager.reset_daily_stats()
```

---

## Web Dashboard操作

### 查看风险状态

1. 打开Web Dashboard
2. 在主页面找到"风险控制"面板
3. 查看实时风险指标：
   - 当前回撤百分比
   - 连续亏损次数
   - 仓位风险比例
   - 市场波动率

### 风险警告显示

当触发风险控制时，Dashboard会显示：

```
⚠️ 风险警告
交易已暂停: 连续3笔亏损
暂停时间: 2025-11-22 12:00:00
预计恢复: 2025-11-22 13:00:00
```

### 手动控制操作

#### 手动暂停交易

1. 点击"暂停交易"按钮
2. 输入暂停原因
3. 选择暂停时长（或选择"需要手动恢复"）
4. 确认暂停

#### 手动恢复交易

1. 点击"恢复交易"按钮
2. 确认恢复操作
3. 系统会检查当前风险状态
4. 如果风险已消除，交易将恢复

### 查看风险事件日志

1. 在"风险管理"面板中点击"事件日志"
2. 查看历史风险事件：
   - 触发时间
   - 事件类型
   - 详细描述
   - 处理结果

---

## 常见问题

### Q1: 为什么交易被暂停了？

**A:** 检查以下几点：

1. 查看Dashboard的"风险控制"面板，确认暂停原因
2. 检查是否触发了以下任一条件：
   - 市场波动率过高
   - 单日亏损超限
   - 累计亏损超限
   - 连续亏损次数过多
   - 最大回撤超限
   - 紧急熔断触发

3. 查看Telegram通知，了解详细信息

### Q2: 如何恢复交易？

**A:** 根据暂停原因选择恢复方式：

**自动恢复（适用于以下情况）：**
- 市场波动率过高 → 等待1小时
- 连续亏损 → 等待1小时
- 单日亏损 → 等待24小时（次日自动重置）

**手动恢复（适用于以下情况）：**
- 累计亏损超限 → 必须在Dashboard手动恢复
- 最大回撤超限 → 必须在Dashboard手动恢复
- 手动暂停 → 必须在Dashboard手动恢复

### Q3: 风险参数如何调整？

**A:** 根据您的风险承受能力调整：

**保守型（低风险）：**
```python
{
    'max_volatility': 0.03,           # 3%
    'max_daily_loss_pct': 0.05,       # 5%
    'max_consecutive_losses': 2,      # 2次
    'max_drawdown_pct': 0.15,         # 15%
}
```

**平衡型（中风险，默认）：**
```python
{
    'max_volatility': 0.05,           # 5%
    'max_daily_loss_pct': 0.10,       # 10%
    'max_consecutive_losses': 3,      # 3次
    'max_drawdown_pct': 0.20,         # 20%
}
```

**激进型（高风险）：**
```python
{
    'max_volatility': 0.08,           # 8%
    'max_daily_loss_pct': 0.15,       # 15%
    'max_consecutive_losses': 5,      # 5次
    'max_drawdown_pct': 0.25,         # 25%
}
```

⚠️ **警告：** 激进型配置风险较高，可能导致更大的亏损，请谨慎使用！

### Q4: 为什么连续盈利后还是被暂停了？

**A:** 可能触发了其他风险控制：

- 虽然交易盈利，但市场波动率过高
- 虽然交易盈利，但当日累计亏损仍超限
- 虽然交易盈利，但回撤仍超过限制

风险控制是多维度的，任何一个维度超限都会触发暂停。

### Q5: 如何关闭某个风险控制？

**A:** 不建议完全关闭风险控制，但如果确实需要：

```python
# 示例：关闭波动率监控（不推荐）
custom_config = {
    'max_volatility': 1.0,  # 设置为100%，实际上不会触发
}

risk_manager = RiskManager(config=custom_config)
```

⚠️ **强烈建议：** 保持所有风险控制开启，这是保护您资金安全的最后一道防线！

### Q6: 风险状态数据保存在哪里？

**A:** 风险状态数据保存在：

- **本地文件：** `scripts/risk_manager_state.json`
- **数据库：** 通过 `db_sync.py` 同步到MySQL数据库

如果需要重置风险状态，删除 `risk_manager_state.json` 文件即可。

### Q7: Telegram通知没有收到？

**A:** 检查以下配置：

1. 确认 `.env` 文件中配置了正确的Telegram参数：
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

2. 测试Telegram连接：
   ```bash
   python scripts/telegram_notifier.py
   ```

3. 检查Bot是否被阻止或删除

### Q8: 如何测试风险管理功能？

**A:** 运行测试脚本：

```bash
cd /home/ubuntu/trading_dashboard
python3 scripts/test_risk_manager.py
```

测试脚本会验证所有风险控制机制是否正常工作。

---

## 最佳实践

### 1. 初始配置建议

**第一次使用时：**
- 使用默认配置（平衡型）
- 观察1-2周，了解策略表现
- 根据实际情况调整参数

### 2. 定期检查

**每日检查：**
- 查看Dashboard风险状态
- 确认当日盈亏情况
- 检查是否有风险警告

**每周检查：**
- 查看风险事件日志
- 分析触发风险的原因
- 优化风险参数配置

### 3. 紧急处理

**当触发风险控制时：**

1. **不要慌张** - 这是正常的保护机制
2. **查看原因** - 在Dashboard或Telegram查看详细信息
3. **分析情况** - 判断是市场原因还是策略问题
4. **决定行动** - 等待自动恢复或手动干预
5. **记录经验** - 总结经验，优化配置

### 4. 参数优化

**优化流程：**

1. **收集数据** - 记录每次触发风险的情况
2. **分析原因** - 是参数过严还是市场确实有风险
3. **小步调整** - 每次只调整一个参数
4. **观察效果** - 观察1-2周后再做下一步调整
5. **持续优化** - 根据市场变化不断调整

---

## 技术支持

如有问题，请参考：

1. **主文档：** `INTEGRATED_SYSTEM_GUIDE.md`
2. **部署教程：** `WINDOWS_部署教程.md`
3. **Python集成：** `PYTHON_INTEGRATION.md`
4. **测试脚本：** `scripts/test_risk_manager.py`

---

## 更新日志

### v23.0 (2025-11-22)

- ✅ 创建风险管理核心模块
- ✅ 实现市场波动率监控
- ✅ 实现单日亏损保护
- ✅ 实现累计亏损保护
- ✅ 实现连续亏损保护
- ✅ 实现最大回撤控制
- ✅ 实现时间窗口限制
- ✅ 实现紧急熔断机制
- ✅ 集成到交易系统
- ✅ 添加Web Dashboard控制面板
- ✅ 添加风险事件日志
- ✅ 添加Telegram风险警告
- ✅ 完成功能测试

---

**祝您交易顺利，风险可控！** 🎯
