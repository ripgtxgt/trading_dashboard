# v28.0 高级功能指南

## 📋 版本概述

v28.0 实现了三个高级功能，将交易系统提升到生产级别：

1. **WebSocket实时推送** - Python脚本实时推送数据到Dashboard
2. **策略参数在线调整** - Dashboard配置面板+实时同步
3. **Telegram机器人控制** - 移动端远程控制

---

## 🔄 WebSocket实时推送

### 功能说明

Python交易脚本在执行交易时，自动通过WebSocket推送数据到Dashboard，实现真正的实时更新，无需刷新页面。

### 使用方法

#### 1. 在Python脚本中集成

```python
from db_integration import DatabaseIntegration

# 初始化数据库集成（自动启用WebSocket）
db = DatabaseIntegration(enable_websocket=True)

# 保存交易记录时自动推送
db.save_trade(
    symbol="XBTUSDTM",
    direction="long",
    entry_price=50000,
    exit_price=51000,
    quantity=0.01,
    pnl=10.0,
    pnl_pct=2.0,
    fee=0.5
)

# 更新持仓时自动推送
db.update_position(
    symbol="XBTUSDTM",
    direction="long",
    entry_price=50000,
    quantity=0.01,
    current_price=50500
)

# 更新账户状态时自动推送
db.update_account_state(
    balance=110.0,
    profit_rate=10.0,
    stage=2,
    symbol="XBTUSDTM"
)

# 关闭连接
db.close()
```

#### 2. 前端自动接收

Dashboard已集成`RealtimeDataContext`，会自动接收WebSocket推送并更新UI：

- 交易发生时，交易历史自动更新
- 持仓变化时，持仓信息自动更新
- 余额变化时，账户状态自动更新
- 风险事件时，风险警告自动显示

#### 3. 连接状态监控

Dashboard顶部的`ConnectionStatus`组件显示WebSocket连接状态：

- 🟢 绿色：已连接
- 🟡 黄色：连接中
- 🔴 红色：已断开

### 技术细节

- **重连机制**：自动重连，最多重试5次
- **心跳检测**：每30秒发送心跳包
- **错误处理**：推送失败不影响数据库写入
- **缓存机制**：配置缓存5秒，避免频繁查询

---

## ⚙️ 策略参数在线调整

### 功能说明

通过Dashboard的策略配置面板，在线修改滚仓倍数、止盈止损、风险控制等参数，Python脚本自动从数据库读取最新配置。

### 使用方法

#### 1. 访问配置面板

在Dashboard主页找到"策略配置"卡片，点击进入配置面板。

#### 2. 修改参数

配置面板包含以下参数：

**基础配置**
- 交易对：XBTUSDTM
- 滚仓倍数：2.0

**止盈止损**
- 止盈百分比：5.0%
- 止损百分比：2.0%

**风险控制**
- 单日最大亏损：10.0%
- 最大回撤：20.0%
- 连续亏损限制：3次

**交易参数**
- 杠杆倍数：10x
- 仓位大小：0.01

**状态控制**
- 启用策略：开关

#### 3. 保存配置

点击"保存配置"按钮，配置立即写入数据库。

#### 4. Python脚本读取配置

```python
from config_loader import get_config_loader

# 获取配置加载器
loader = get_config_loader()

# 加载完整配置
config = loader.load_config()
if config:
    roll_multiplier = config['roll_multiplier']
    take_profit_pct = config['take_profit_pct']
    stop_loss_pct = config['stop_loss_pct']
    # ... 使用配置

# 或者获取单个参数
roll_multiplier = loader.get_param('roll_multiplier', 2.0)

# 检查策略是否启用
if loader.is_active():
    # 执行交易逻辑
    pass
else:
    print("策略已禁用")
```

#### 5. 配置生效时间

- 配置保存后立即写入数据库
- Python脚本每5秒自动重新加载配置（可通过`force_reload=True`强制重新加载）
- 建议在交易循环开始时检查配置

### 最佳实践

1. **测试模式**：先在测试模式下验证参数效果
2. **小步调整**：每次只调整一个参数，观察效果
3. **记录变更**：记录每次参数调整和结果
4. **风险控制**：不要过度放宽风险控制参数

---

## 📱 Telegram机器人控制

### 功能说明

通过Telegram消息远程查询交易系统状态和配置，实现移动端管理。

### 快速开始

#### 1. 创建Bot

1. 在Telegram搜索 `@BotFather`
2. 发送 `/newbot` 创建Bot
3. 保存Bot Token

#### 2. 获取Chat ID

1. 在Telegram搜索 `@userinfobot`
2. 发送任意消息获取Chat ID

#### 3. 配置环境变量

```bash
export TELEGRAM_BOT_TOKEN="你的Bot Token"
export TELEGRAM_CHAT_ID="你的Chat ID"
```

#### 4. 启动Bot

```bash
cd /home/ubuntu/trading_dashboard/scripts
python3 telegram_bot.py
```

### 可用命令

#### `/status` - 查询状态

显示交易系统当前状态：

```
📊 交易系统状态

交易对: XBTUSDTM
策略状态: 🟢 启用
杠杆: 10x
仓位大小: 0.01

滚仓倍数: 2.0
止盈: 5.0%
止损: 2.0%
```

#### `/config` - 查看配置

显示完整策略配置：

```
⚙️ 策略配置

基础配置
交易对: XBTUSDTM
滚仓倍数: 2.0

止盈止损
止盈: 5.0%
止损: 2.0%

风险控制
单日最大亏损: 10.0%
最大回撤: 20.0%
连续亏损限制: 3

交易参数
杠杆: 10x
仓位大小: 0.01

策略状态: 🟢 启用
```

#### `/enable` / `/disable` - 启用/禁用策略

控制策略运行状态。

#### `/help` - 帮助信息

显示所有可用命令。

### 集成到交易脚本

```python
from telegram_bot import TelegramBot

# 初始化Bot
bot = TelegramBot()

# 发送交易通知
bot.send_message(f"✅ 开仓成功\n方向: 做多\n价格: {price} USDT")

# 发送风险警告
bot.send_message(f"⚠️ 风险警告\n单日亏损已达 {loss_pct}%")

# 发送系统错误
bot.send_message(f"❌ 系统错误\n{error_message}")
```

### 安全建议

1. **保护Token**：不要泄露Bot Token
2. **验证Chat ID**：Bot只响应指定Chat ID
3. **私聊使用**：不要在群组中使用
4. **定期更换**：定期更换Bot Token

---

## 🔗 完整工作流

### 1. 启动系统

```bash
# 1. 启动Dashboard
cd /home/ubuntu/trading_dashboard
pnpm dev

# 2. 启动Telegram Bot（可选）
cd scripts
python3 telegram_bot.py &

# 3. 启动交易脚本
python3 trading_with_db.py
```

### 2. 监控交易

- **Dashboard**：实时查看交易状态、持仓、账户余额
- **Telegram**：移动端接收交易通知
- **WebSocket**：自动更新，无需刷新

### 3. 调整策略

- **Dashboard配置面板**：在线修改参数
- **Python脚本**：自动加载最新配置
- **Telegram**：查询配置是否生效

### 4. 风险控制

- **自动风险管理**：触发风险事件时自动暂停
- **实时推送**：风险警告立即显示在Dashboard
- **Telegram通知**：移动端接收风险警告

---

## 📝 注意事项

1. **WebSocket连接**：确保服务器WebSocket端口可访问
2. **数据库连接**：Python脚本需要正确的DATABASE_URL
3. **配置缓存**：配置变更可能有5秒延迟
4. **Telegram限制**：避免频繁发送消息（API限制）
5. **网络稳定性**：WebSocket和Telegram都需要稳定网络

---

## 🐛 故障排除

### WebSocket无法连接

1. 检查服务器是否启动
2. 检查防火墙设置
3. 查看浏览器控制台错误

### 配置不生效

1. 确认配置已保存到数据库
2. 等待5秒配置缓存过期
3. 或使用`force_reload=True`强制重新加载

### Telegram Bot无响应

1. 检查Bot Token和Chat ID
2. 确认Bot进程正在运行
3. 检查网络连接

---

## 📚 相关文档

- [DB_INTEGRATION_GUIDE.md](./DB_INTEGRATION_GUIDE.md) - 数据库集成指南
- [TELEGRAM_BOT_GUIDE.md](./TELEGRAM_BOT_GUIDE.md) - Telegram Bot详细指南
- [V24_FEATURES_GUIDE.md](./V24_FEATURES_GUIDE.md) - v24功能指南
- [V27_FEATURES_GUIDE.md](./V27_FEATURES_GUIDE.md) - v27功能指南
