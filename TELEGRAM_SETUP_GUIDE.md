# Telegram Bot 配置完整指南

## 问题诊断

您遇到的 `401 Unauthorized` 错误通常是以下原因之一：

1. ❌ **Bot Token 错误或无效**
2. ❌ **Bot Token 格式不正确**
3. ❌ **环境变量未正确设置**
4. ❌ **Bot 被删除或禁用**

---

## 完整配置步骤

### 第一步：创建 Telegram Bot

1. **打开 Telegram**
   - 在手机或电脑上打开 Telegram

2. **找到 BotFather**
   - 在搜索框中输入：`@BotFather`
   - 点击官方的 BotFather（有蓝色认证标记）

3. **创建新 Bot**
   ```
   发送命令：/newbot
   
   BotFather 会问：
   "Alright, a new bot. How are we going to call it? Please choose a name for your bot."
   
   输入 Bot 名称（可以是中文）：
   10U战神交易助手
   
   BotFather 会问：
   "Good. Now let's choose a username for your bot. It must end in `bot`."
   
   输入 Bot 用户名（必须以bot结尾，只能用英文和数字）：
   trading_assistant_bot
   或
   my_trading_10u_bot
   ```

4. **获取 Bot Token**
   
   创建成功后，BotFather 会返回类似这样的消息：
   ```
   Done! Congratulations on your new bot. You will find it at t.me/trading_assistant_bot. 
   You can now add a description, about section and profile picture for your bot, see /help for a list of commands.

   Use this token to access the HTTP API:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
   
   Keep your token secure and store it safely, it can be used by anyone to control your bot.
   ```

   **⚠️ 重要：复制这个 Token！**
   
   格式应该是：`数字:字母数字混合`
   例如：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890`

### 第二步：获取 Chat ID

1. **启动你的 Bot**
   - 在 Telegram 搜索框中输入你的 Bot 用户名
   - 例如：`@trading_assistant_bot`
   - 点击进入，点击 "START" 按钮
   - 发送任意消息，例如："Hello"

2. **获取 Chat ID**

   **方法一：使用 @userinfobot（最简单）**
   ```
   1. 在 Telegram 搜索：@userinfobot
   2. 点击 START
   3. 它会立即显示你的 Chat ID
   4. 复制这个数字（例如：123456789）
   ```

   **方法二：使用 API（如果方法一不行）**
   ```
   1. 在浏览器中打开：
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   
   2. 将 <YOUR_BOT_TOKEN> 替换为你的 Bot Token
   
   例如：
   https://api.telegram.org/bot1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890/getUpdates
   
   3. 你会看到 JSON 响应，找到 "chat" 部分：
   {
     "ok": true,
     "result": [
       {
         "update_id": 123456789,
         "message": {
           "message_id": 1,
           "from": {
             "id": 123456789,  ← 这就是你的 Chat ID
             "is_bot": false,
             "first_name": "Your Name"
           },
           "chat": {
             "id": 123456789,  ← 这也是你的 Chat ID
             "first_name": "Your Name",
             "type": "private"
           },
           "date": 1234567890,
           "text": "Hello"
         }
       }
     ]
   }
   
   4. 复制 "id" 的值（数字）
   ```

### 第三步：配置环境变量

1. **打开 .env 文件**
   ```
   路径：C:\Projects\trading_dashboard\.env
   
   使用记事本或任何文本编辑器打开
   ```

2. **添加或修改以下配置**
   ```env
   # Telegram Bot 配置
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
   TELEGRAM_CHAT_ID=123456789
   ```

   **⚠️ 注意：**
   - Token 和 Chat ID 之间不要有空格
   - 不要用引号包裹
   - Token 格式必须是：`数字:字母数字`
   - Chat ID 必须是纯数字

3. **保存文件**
   - 按 `Ctrl + S` 保存
   - 关闭编辑器

### 第四步：测试配置

1. **运行测试脚本**
   ```powershell
   cd C:\Projects\trading_dashboard\scripts
   python telegram_notifier.py
   ```

2. **预期结果**
   
   **✅ 成功：**
   ```
   ========================================
   Telegram 通知测试
   ========================================

   测试 1: 发送简单消息
   [Telegram] 消息发送成功
   ✓ 测试通过

   测试 2: 发送格式化消息
   [Telegram] 消息发送成功
   ✓ 测试通过

   ...
   ```
   
   同时，你的 Telegram 会收到测试消息。

   **❌ 失败（401错误）：**
   ```
   [Telegram] 发送失败: 401
   ```
   
   说明 Bot Token 不正确，请检查：
   - Token 是否完整复制
   - Token 格式是否正确（数字:字母数字）
   - .env 文件是否正确保存
   - 是否有多余的空格或引号

---

## 常见错误排查

### 错误 1: 401 Unauthorized

**原因：** Bot Token 无效

**解决方案：**
```powershell
# 1. 重新检查 Token
# 在 Telegram 中找到 @BotFather
# 发送命令：/mybots
# 选择你的 Bot
# 点击 "API Token"
# 复制新的 Token

# 2. 更新 .env 文件
notepad C:\Projects\trading_dashboard\.env

# 3. 确保格式正确
TELEGRAM_BOT_TOKEN=完整的Token（不要有空格、引号）

# 4. 保存并重新测试
python telegram_notifier.py
```

### 错误 2: 400 Bad Request

**原因：** Chat ID 错误或消息格式问题

**解决方案：**
```powershell
# 1. 确认 Chat ID 是纯数字
# 打开 .env 检查：
TELEGRAM_CHAT_ID=123456789  # 必须是数字，不要有引号

# 2. 重新获取 Chat ID
# 使用 @userinfobot 获取正确的 Chat ID
```

### 错误 3: 找不到 TELEGRAM_BOT_TOKEN

**原因：** 环境变量未加载

**解决方案：**
```powershell
# 1. 检查 .env 文件是否在正确位置
dir C:\Projects\trading_dashboard\.env

# 2. 检查文件内容
type C:\Projects\trading_dashboard\.env

# 3. 确保没有拼写错误
# 正确：TELEGRAM_BOT_TOKEN
# 错误：TELEGRAM_TOKEN 或 BOT_TOKEN
```

### 错误 4: 消息发送成功但收不到

**原因：** Chat ID 不正确或 Bot 被屏蔽

**解决方案：**
```
1. 确认你已经在 Telegram 中启动了 Bot（点击 START）
2. 确认 Chat ID 是你自己的 ID（使用 @userinfobot 验证）
3. 检查 Bot 是否被你屏蔽了（在 Bot 聊天界面点击右上角，查看是否有"解除屏蔽"选项）
4. 尝试给 Bot 发送一条消息，然后重新测试
```

---

## 验证配置脚本

创建一个简单的验证脚本：

```python
# verify_telegram.py
import os
import requests

def verify_telegram_config():
    """验证 Telegram 配置"""
    print("=" * 50)
    print("Telegram 配置验证")
    print("=" * 50)
    
    # 1. 检查环境变量
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print("\n1. 环境变量检查：")
    if not token:
        print("   ❌ TELEGRAM_BOT_TOKEN 未设置")
        return False
    else:
        print(f"   ✓ TELEGRAM_BOT_TOKEN: {token[:10]}...{token[-10:]}")
    
    if not chat_id:
        print("   ❌ TELEGRAM_CHAT_ID 未设置")
        return False
    else:
        print(f"   ✓ TELEGRAM_CHAT_ID: {chat_id}")
    
    # 2. 验证 Token 格式
    print("\n2. Token 格式检查：")
    if ':' not in token:
        print("   ❌ Token 格式错误（应包含冒号）")
        return False
    
    parts = token.split(':')
    if len(parts) != 2:
        print("   ❌ Token 格式错误")
        return False
    
    if not parts[0].isdigit():
        print("   ❌ Token 第一部分应该是数字")
        return False
    
    print("   ✓ Token 格式正确")
    
    # 3. 测试 Bot API
    print("\n3. Bot API 测试：")
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"   ✓ Bot 验证成功")
                print(f"   Bot 名称: {bot_info.get('first_name')}")
                print(f"   Bot 用户名: @{bot_info.get('username')}")
            else:
                print(f"   ❌ Bot API 返回错误: {data}")
                return False
        else:
            print(f"   ❌ Bot API 请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False
    
    # 4. 发送测试消息
    print("\n4. 发送测试消息：")
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': '✅ Telegram 配置验证成功！\n\n如果你看到这条消息，说明配置正确。'
        }
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            print("   ✓ 测试消息发送成功")
            print("   请检查 Telegram 是否收到消息")
            return True
        else:
            print(f"   ❌ 消息发送失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 发送异常: {e}")
        return False

if __name__ == "__main__":
    # 加载 .env 文件
    from pathlib import Path
    env_path = Path(__file__).parent.parent / '.env'
    
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    # 运行验证
    success = verify_telegram_config()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 所有检查通过！配置正确。")
    else:
        print("❌ 配置有问题，请根据上面的提示修复。")
    print("=" * 50)
```

**使用方法：**
```powershell
cd C:\Projects\trading_dashboard\scripts
python verify_telegram.py
```

---

## 快速参考

### 正确的配置示例

```env
# .env 文件
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
TELEGRAM_CHAT_ID=123456789
```

### BotFather 常用命令

```
/newbot - 创建新 Bot
/mybots - 查看你的 Bot 列表
/token - 获取 Bot Token
/setname - 修改 Bot 名称
/setdescription - 设置 Bot 描述
/setabouttext - 设置 Bot 简介
/setuserpic - 设置 Bot 头像
/deletebot - 删除 Bot
```

### 测试 API 的浏览器链接

```
# 获取 Bot 信息
https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# 获取更新（查看 Chat ID）
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates

# 发送测试消息
https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage?chat_id=<YOUR_CHAT_ID>&text=Test
```

---

## 总结

完成以上步骤后，你应该能够：

- ✅ 成功创建 Telegram Bot
- ✅ 获取正确的 Bot Token
- ✅ 获取你的 Chat ID
- ✅ 正确配置 .env 文件
- ✅ 成功发送测试消息
- ✅ 在 Telegram 中收到通知

如果仍有问题，请检查：
1. Token 是否完整复制（包括冒号）
2. Chat ID 是否是纯数字
3. .env 文件是否保存
4. 是否在 Telegram 中启动了 Bot（点击 START）
5. Bot 是否被屏蔽

祝配置顺利！🎉
