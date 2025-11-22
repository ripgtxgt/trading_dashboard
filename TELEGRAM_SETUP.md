# Telegram Bot 配置教程

本教程将指导你创建Telegram Bot并获取必要的配置信息，以便接收交易通知。

---

## 第一步：创建Telegram Bot

### 1.1 打开BotFather

在Telegram中搜索 **@BotFather** 并打开对话。

BotFather是Telegram官方的机器人管理工具，用于创建和管理所有Bot。

### 1.2 创建新Bot

发送命令：
```
/newbot
```

### 1.3 设置Bot名称

BotFather会要求你输入Bot的显示名称（可以包含空格和中文）。

示例：
```
10U战神交易助手
```

### 1.4 设置Bot用户名

接下来输入Bot的用户名（必须以`bot`结尾，只能包含字母、数字和下划线）。

示例：
```
trading_10u_bot
```

### 1.5 获取Bot Token

创建成功后，BotFather会返回一个Token，格式类似：
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567
```

**⚠️ 重要：请妥善保管这个Token，不要泄露给他人！**

复制这个Token，稍后需要配置到环境变量中。

---

## 第二步：获取Chat ID

### 2.1 启动你的Bot

在Telegram中搜索你刚创建的Bot（例如 `@trading_10u_bot`），点击 **START** 按钮。

### 2.2 发送测试消息

向Bot发送任意消息，例如：
```
Hello
```

### 2.3 获取Chat ID

打开浏览器，访问以下URL（替换`YOUR_BOT_TOKEN`为你的Bot Token）：

```
https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
```

完整示例：
```
https://api.telegram.org/bot1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567/getUpdates
```

### 2.4 查找Chat ID

在返回的JSON中找到 `"chat":{"id":` 字段，例如：

```json
{
  "ok": true,
  "result": [
    {
      "update_id": 123456789,
      "message": {
        "message_id": 1,
        "from": {
          "id": 987654321,
          "is_bot": false,
          "first_name": "Your Name"
        },
        "chat": {
          "id": 987654321,    ← 这就是你的Chat ID
          "first_name": "Your Name",
          "type": "private"
        },
        "date": 1234567890,
        "text": "Hello"
      }
    }
  ]
}
```

复制这个Chat ID（例如 `987654321`）。

---

## 第三步：配置环境变量

### 3.1 在Manus管理界面配置

1. 打开项目的Management UI
2. 点击左侧导航栏的 **Settings**
3. 点击 **Secrets** 子菜单
4. 点击 **Add Secret** 按钮

添加以下两个环境变量：

**变量1：**
- Key: `TELEGRAM_BOT_TOKEN`
- Value: 你的Bot Token（例如 `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567`）

**变量2：**
- Key: `TELEGRAM_CHAT_ID`
- Value: 你的Chat ID（例如 `987654321`）

### 3.2 在本地Python脚本配置

如果你在本地运行Python交易脚本，需要设置环境变量：

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567"
export TELEGRAM_CHAT_ID="987654321"
```

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567"
$env:TELEGRAM_CHAT_ID="987654321"
```

**Windows (CMD):**
```cmd
set TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567
set TELEGRAM_CHAT_ID=987654321
```

---

## 第四步：测试Telegram通知

### 4.1 使用Python脚本测试

运行测试脚本：

```bash
cd /home/ubuntu/trading_dashboard/scripts
python3 telegram_notifier.py
```

如果配置正确，你的Telegram会收到多条测试消息：
- 开仓通知
- 平仓通知
- 风险警告
- 每日统计
- 机器人状态

### 4.2 使用Web界面测试

1. 打开Dashboard
2. 找到"Telegram通知"相关设置（如果有）
3. 点击"发送测试消息"按钮

你应该会收到一条测试消息：
```
🤖 测试消息

Telegram通知配置成功！

_2024-11-22 11:30:00_
```

---

## 常见问题

### Q1: 访问getUpdates返回空数组？

**A:** 确保你已经向Bot发送过至少一条消息。如果还是空的，尝试：
1. 重新向Bot发送消息
2. 刷新浏览器页面
3. 检查URL中的Token是否正确

### Q2: 测试脚本报错"未配置"？

**A:** 检查环境变量是否正确设置：
```bash
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID
```

如果输出为空，说明环境变量未设置成功。

### Q3: 收不到通知消息？

**A:** 检查以下几点：
1. Bot Token和Chat ID是否正确
2. 是否已经点击Bot的START按钮
3. 检查Python脚本或Web服务器的日志
4. 确认网络连接正常（可以访问api.telegram.org）

### Q4: 如何创建群组Bot？

**A:** 
1. 创建Telegram群组
2. 将你的Bot添加到群组
3. 向群组发送消息
4. 访问getUpdates获取群组的Chat ID（通常是负数）
5. 使用群组的Chat ID配置环境变量

---

## 通知类型说明

配置完成后，你将收到以下类型的通知：

### 📈 开仓通知
当策略检测到交易信号并开仓时发送，包含：
- 交易对
- 方向（做多/做空）
- 价格
- 数量
- 保证金

### ✅ 平仓通知
当持仓平仓时发送，包含：
- 交易对
- 方向
- 入场价格
- 出场价格
- 盈亏金额和百分比

### ⚠️ 风险警告
当检测到风险时发送，包含：
- 警告级别（信息/警告/严重）
- 警告消息
- 详细信息

### 📊 每日统计
每日交易结束后发送，包含：
- 总交易笔数
- 盈利交易笔数
- 胜率
- 总盈亏
- 当前资金

---

## 安全建议

1. **不要分享Bot Token**：Token相当于Bot的密码，泄露后任何人都可以控制你的Bot
2. **定期更新Token**：如果怀疑Token泄露，在BotFather中使用 `/revoke` 命令重新生成
3. **使用私聊**：建议使用个人账号的Chat ID，避免在公开群组中接收敏感交易信息
4. **备份配置**：记录好Token和Chat ID，以防丢失

---

## 下一步

配置完成后，你可以：

1. **集成到交易脚本**：参考 `PYTHON_INTEGRATION.md` 将Telegram通知集成到你的交易机器人
2. **自定义通知内容**：修改 `scripts/telegram_notifier.py` 中的消息模板
3. **添加更多通知**：在交易脚本中调用不同的通知方法

祝交易顺利！🚀
