# Telegram Bot 使用指南

## 📱 功能概述

Telegram Bot允许您通过Telegram消息远程控制和查询交易系统，实现移动端管理。

## 🚀 快速开始

### 1. 创建Telegram Bot

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 创建新Bot
3. 按提示设置Bot名称和用户名
4. 保存BotFather返回的Bot Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2. 获取Chat ID

1. 在Telegram中搜索 `@userinfobot`
2. 发送任意消息
3. Bot会返回您的Chat ID（格式：`123456789`）

### 3. 配置环境变量

在`.env`文件中添加：

```bash
TELEGRAM_BOT_TOKEN=你的Bot Token
TELEGRAM_CHAT_ID=你的Chat ID
```

### 4. 启动Bot

```bash
cd /home/ubuntu/trading_dashboard/scripts
python3 telegram_bot.py
```

## 📋 可用命令

### 查询命令

#### `/status` - 查询交易系统状态
显示当前交易对、策略状态、杠杆、仓位大小、滚仓倍数、止盈止损等关键信息。

**示例**：
```
/status
```

**响应**：
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

#### `/config` - 查看策略配置
显示完整的策略配置，包括基础配置、止盈止损、风险控制和交易参数。

**示例**：
```
/config
```

**响应**：
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

### 控制命令

#### `/enable` - 启用策略
启用交易策略，允许系统执行交易。

**示例**：
```
/enable
```

#### `/disable` - 禁用策略
禁用交易策略，系统将停止执行新交易。

**示例**：
```
/disable
```

#### `/set <参数> <值>` - 修改参数
修改策略参数（建议通过Web Dashboard操作）。

**示例**：
```
/set roll_multiplier 2.5
```

### 其他命令

#### `/help` - 显示帮助信息
显示所有可用命令的说明。

**示例**：
```
/help
```

## 🔐 安全建议

1. **保护Bot Token**：不要将Bot Token泄露给他人
2. **验证Chat ID**：Bot只响应指定Chat ID的消息
3. **定期更换Token**：如果Token泄露，立即通过BotFather重新生成
4. **使用私聊**：不要在群组中使用Bot，避免命令被他人看到

## 🛠️ 高级用法

### 集成到交易脚本

在您的交易脚本中导入Telegram Bot模块：

```python
from telegram_bot import TelegramBot

# 初始化Bot
bot = TelegramBot()

# 发送交易通知
bot.send_message(f"✅ 开仓成功\n方向: 做多\n价格: {price} USDT")

# 发送风险警告
bot.send_message(f"⚠️ 风险警告\n单日亏损已达 {loss_pct}%")
```

### 自动化通知

在关键事件发生时自动发送通知：

- 开仓/平仓
- 止盈/止损触发
- 风险警告
- 系统错误

## 📝 注意事项

1. **网络要求**：需要稳定的网络连接访问Telegram API
2. **API限制**：Telegram API有速率限制，避免频繁发送消息
3. **时区问题**：Bot显示的时间为服务器时区
4. **配置修改**：建议通过Web Dashboard修改配置，更加直观和安全

## 🐛 常见问题

### Bot无法发送消息

1. 检查`TELEGRAM_BOT_TOKEN`是否正确
2. 检查`TELEGRAM_CHAT_ID`是否正确
3. 确认已经在Telegram中与Bot对话过（发送过`/start`）
4. 检查网络连接是否正常

### Bot无法接收命令

1. 确认Bot正在运行（`python3 telegram_bot.py`）
2. 检查Chat ID是否匹配
3. 确认命令格式正确（以`/`开头）

### 配置修改不生效

1. Bot只提供查询功能，配置修改需通过Web Dashboard
2. 修改配置后，Python脚本会在下次轮询时自动加载新配置

## 📚 相关文档

- [DB_INTEGRATION_GUIDE.md](./DB_INTEGRATION_GUIDE.md) - 数据库集成指南
- [V24_FEATURES_GUIDE.md](./V24_FEATURES_GUIDE.md) - v24功能指南
- [V27_FEATURES_GUIDE.md](./V27_FEATURES_GUIDE.md) - v27功能指南
