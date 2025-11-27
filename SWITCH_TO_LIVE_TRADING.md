# 🚀 切换到正式交易环境指南

## 📊 当前环境状态

### ✅ 当前配置：测试模式（Paper Trading）

您的系统目前运行在**测试模式**，特点：

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| TRADING_MODE | `"paper"` | 模拟交易模式 |
| sandbox | `False` | 已连接KuCoin正式API |
| 资金 | 虚拟资金 | 不会使用真实USDT |
| 交易 | 模拟下单 | 不会在KuCoin产生真实订单 |
| 数据 | 真实行情 | 使用KuCoin真实市场数据 |

**测试模式的好处：**
- ✅ 安全：不会损失真实资金
- ✅ 完整功能：所有功能都可以测试
- ✅ 真实数据：使用真实市场K线数据
- ✅ 风险验证：可以测试风险管理机制
- ✅ 策略优化：可以调整参数观察效果

---

## 🔄 如何切换到正式环境

### ⚠️ 重要警告

**切换到正式交易前，请确保：**

1. ✅ 已在测试模式下运行至少**7天**
2. ✅ 策略参数已经过充分测试和优化
3. ✅ 风险管理机制运行正常
4. ✅ Telegram通知功能正常
5. ✅ 理解并接受交易风险
6. ✅ KuCoin账户有足够余额（建议至少20 USDT）

**⚠️ 正式交易会使用真实资金，可能造成实际损失！**

---

## 📝 切换步骤（3步）

### 步骤1：修改环境配置

编辑 `.env` 文件：

```cmd
cd C:\trading_dashboard_fixed
notepad .env
```

找到这一行：
```env
TRADING_MODE="paper"
```

改为：
```env
TRADING_MODE="live"
```

保存并关闭文件。

---

### 步骤2：验证KuCoin API权限

确保您的KuCoin API密钥有以下权限：

**必需权限：**
- ✅ **General** - 通用权限
- ✅ **Trade** - 交易权限（下单、撤单）
- ✅ **Futures** - 合约交易权限

**如何检查：**
1. 登录 KuCoin 网站
2. 进入 **API Management**
3. 查看您的API密钥权限
4. 如果缺少权限，需要重新创建API密钥

**当前API配置：**
```
API Key: 6902f625f9a9a300014c3976
API Secret: d71e4e3d-4369-4e77-94f8-fd456c5e0387
API Passphrase: x5gU7dnL6bvrvbV!
```

---

### 步骤3：重启交易机器人

```cmd
# 停止trading-bot
pm2 stop trading-bot

# 清空旧日志（可选）
pm2 flush trading-bot

# 重启trading-bot
pm2 restart trading-bot

# 查看日志确认
pm2 logs trading-bot --lines 30
```

**预期日志输出：**
```
[Trading Bot] Mode: LIVE TRADING
[Trading Bot] Connected to KuCoin (Production)
[Trading Bot] Initial Balance: 10.00 USDT
[Trading Bot] Strategy: 10U Rolling Position
[Trading Bot] Leverage: 100x
[Trading Bot] Waiting for signal...
```

---

## 🎯 正式环境特性

### 真实交易流程

1. **信号检测**
   - 每60秒检查一次K线数据
   - 使用MA5和MA20均线判断趋势
   - 符合条件时生成交易信号

2. **下单执行**
   - 根据当前资金计算仓位
   - 在KuCoin下真实市场订单
   - 设置止盈止损价格

3. **持仓管理**
   - 实时监控持仓盈亏
   - 触及止盈/止损自动平仓
   - 记录到数据库

4. **风险控制**
   - 单日亏损超5%自动停止
   - 单笔亏损超20%强制平仓
   - 连续亏损3次暂停交易
   - 账户余额低于5 USDT停止

5. **通知推送**
   - 开仓/平仓通知到Telegram
   - 风险警告推送
   - 每日交易报告

---

## 📊 数据接入说明

### 当前数据源

您的系统已经接入了**真实数据**：

| 数据类型 | 来源 | 说明 |
|----------|------|------|
| K线数据 | KuCoin API | 实时BTC/USDT永续合约1小时K线 |
| 账户余额 | KuCoin API | 实时查询合约账户余额 |
| 持仓信息 | KuCoin API | 实时查询当前持仓 |
| 订单状态 | KuCoin API | 实时查询订单执行情况 |
| 市场深度 | KuCoin API | 实时买卖盘数据 |

### 数据更新频率

```python
# 配置文件: scripts/live_trading_config.py
RUN_CONFIG = {
    'check_interval': 60,  # 每60秒检查一次
}
```

**数据流程：**
```
KuCoin API → trading-bot → 数据库 → Dashboard
                ↓
           WebSocket推送
                ↓
           实时图表更新
```

---

## 🔍 如何验证正式交易已启动

### 1. 检查日志
```cmd
pm2 logs trading-bot --lines 50
```

**关键日志标记：**
```
[Trading Bot] Mode: LIVE TRADING          # 正式模式
[Trading Bot] Connected to KuCoin (Production)  # 生产环境
[KuCoin API] Fetching real balance...     # 查询真实余额
[KuCoin API] Current balance: XX.XX USDT  # 显示真实余额
```

### 2. 检查数据库
```cmd
mysql -u trading -ptrading123 trading_dashboard
```

```sql
-- 查看bot状态
SELECT * FROM bot_state;

-- 应该看到：
-- trading_mode: 'live'
-- is_active: 1
-- current_balance: (真实余额)
```

### 3. 查看Dashboard
访问 http://localhost:3000

**正式模式标识：**
- 顶部显示：**LIVE TRADING** 或 **实盘交易**
- 余额显示真实KuCoin账户余额
- 交易记录来自真实订单

### 4. Telegram通知
启动后应收到：
```
[Bot] Trading Bot started in LIVE mode
Current Balance: XX.XX USDT
Strategy: 10U Rolling Position
Leverage: 100x
```

---

## 📈 正式交易后的数据

### 数据库记录

**bot_state表：**
```sql
SELECT * FROM bot_state;
```
- `current_balance` - 实时账户余额
- `total_profit` - 累计盈亏
- `total_trades` - 总交易次数
- `win_rate` - 胜率

**positions表：**
```sql
SELECT * FROM positions WHERE status = 'open';
```
- 当前持仓信息
- 开仓价格、数量
- 止盈止损价格
- 未实现盈亏

**trades表：**
```sql
SELECT * FROM trades ORDER BY created_at DESC LIMIT 10;
```
- 所有交易历史
- 开仓/平仓时间
- 盈亏金额
- 手续费

**balance_snapshots表：**
```sql
SELECT * FROM balance_snapshots ORDER BY timestamp DESC LIMIT 20;
```
- 余额快照（每小时）
- 用于绘制资金曲线

---

## 🛡️ 风险管理机制

正式交易启动后，以下风险控制自动生效：

### 1. 单日亏损保护
```python
max_daily_loss_pct: 0.05  # 5%
```
- 当日亏损超过总资金5%
- 自动停止所有交易
- 发送Telegram警告
- 次日自动恢复

### 2. 单笔止损保护
```python
emergency_stop_loss: 0.20  # 20%
```
- 单笔持仓亏损超20%
- 立即强制平仓
- 防止单笔巨额亏损

### 3. 连续亏损保护
- 连续3笔交易亏损
- 自动暂停30分钟
- 等待市场稳定

### 4. 最小余额保护
```python
min_balance: 5  # USDT
```
- 账户余额低于5 USDT
- 停止开新仓
- 保留平仓功能

---

## 📱 实时监控

### Dashboard监控
访问：http://localhost:3000

**实时数据：**
- 当前余额和盈亏
- 持仓信息（方向、数量、盈亏）
- K线图表（MA5/MA20指标）
- 交易历史列表
- 资金曲线图
- 风险指标

### Telegram监控
发送命令查询：

```
/status   - 查看当前状态
/config   - 查看策略配置
/stop     - 紧急停止交易
/resume   - 恢复交易
```

**自动通知：**
- 开仓通知（价格、数量、方向）
- 平仓通知（盈亏金额、收益率）
- 风险警告（亏损、回撤）
- 每日报告（UTC 16:00，北京时间00:00）

---

## 🔧 常见问题

### Q1: 切换到正式模式后没有交易？

**可能原因：**
1. 市场没有符合条件的信号
2. 风险控制限制了交易
3. 账户余额不足

**检查方法：**
```cmd
pm2 logs trading-bot --lines 50
```

查找日志：
```
[Signal] No signal (MA5 < MA20)  # 没有信号
[Risk] Daily loss limit reached  # 风险限制
[Error] Insufficient balance     # 余额不足
```

### Q2: 如何确认订单已在KuCoin执行？

**方法1：查看KuCoin网站**
1. 登录 KuCoin
2. 进入 **Futures** → **Orders**
3. 查看订单历史

**方法2：查看数据库**
```sql
SELECT * FROM trades WHERE order_id IS NOT NULL;
```

**方法3：查看日志**
```cmd
pm2 logs trading-bot | grep "Order"
```

### Q3: 如何紧急停止所有交易？

**方法1：Telegram命令**
```
/stop
```

**方法2：停止服务**
```cmd
pm2 stop trading-bot
```

**方法3：切换回测试模式**
编辑 `.env`：
```env
TRADING_MODE="paper"
```
然后重启：
```cmd
pm2 restart trading-bot
```

### Q4: 正式交易的手续费是多少？

**KuCoin合约手续费：**
- Maker（挂单）：0.02%
- Taker（吃单）：0.06%

**系统配置：**
```python
fee_rate: 0.0006  # 0.06% (Taker费率)
```

**示例：**
- 开仓10 USDT，100倍杠杆
- 仓位价值：1000 USDT
- 手续费：1000 × 0.0006 = 0.6 USDT

### Q5: 数据多久更新一次？

**更新频率：**
- K线检查：每60秒
- 持仓监控：每60秒
- 余额查询：每次交易后
- Dashboard显示：实时（WebSocket推送）
- 数据库记录：每次交易后

---

## 📋 切换前检查清单

在切换到正式交易前，请确认：

### 系统检查
- [ ] 所有5个服务都是 `online` 状态
- [ ] 测试模式已运行至少7天
- [ ] 策略参数已优化
- [ ] 风险管理机制测试通过
- [ ] Telegram通知功能正常

### KuCoin检查
- [ ] API密钥有Trade和Futures权限
- [ ] 合约账户有足够余额（建议≥20 USDT）
- [ ] 已开通BTC/USDT永续合约
- [ ] 已设置100倍杠杆
- [ ] 已设置逐仓模式

### 配置检查
- [ ] `.env` 文件中 `TRADING_MODE="live"`
- [ ] `live_trading_config.py` 参数已确认
- [ ] 数据库连接正常
- [ ] WebSocket服务运行中

### 风险确认
- [ ] 理解并接受交易风险
- [ ] 只使用可承受损失的资金
- [ ] 已设置合理的止损
- [ ] 已设置单日亏损限制
- [ ] 准备好应对市场波动

---

## 🎯 建议的启动流程

### 第一天：小资金测试
1. 准备20 USDT
2. 切换到正式模式
3. 观察1-2笔真实交易
4. 验证订单执行正常
5. 检查数据记录完整

### 第一周：监控运行
1. 每天查看交易日志
2. 检查Telegram通知
3. 观察资金曲线
4. 记录问题和优化点
5. 必要时调整参数

### 长期运行：
1. 定期查看Dashboard
2. 关注风险警告
3. 每周回顾交易记录
4. 根据市场调整策略
5. 定期备份数据库

---

## 📞 技术支持

如果在切换过程中遇到问题：

1. **查看日志**
   ```cmd
   pm2 logs trading-bot --lines 100
   ```

2. **检查数据库**
   ```cmd
   mysql -u trading -ptrading123 trading_dashboard
   SELECT * FROM bot_state;
   ```

3. **测试API连接**
   ```cmd
   cd C:\trading_dashboard_fixed\scripts
   python test_kucoin_connection.py
   ```

4. **紧急回退到测试模式**
   - 编辑 `.env`：`TRADING_MODE="paper"`
   - 重启：`pm2 restart trading-bot`

---

**祝您交易顺利！** 🚀

**⚠️ 再次提醒：正式交易有风险，请谨慎操作！**
