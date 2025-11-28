# Trading Bot 启动故障快速修复指南

## 🔍 问题诊断

Trading-bot服务stopped的原因通常是以下几种：

### 1. Python依赖缺失 ⚠️

**检查命令（Windows PowerShell）：**
```powershell
cd C:\trading_dashboard_fixed
python -c "import dotenv, ccxt, pandas, numpy, websockets, telegram"
```

**如果报错 `ModuleNotFoundError`，执行：**
```powershell
pip install python-dotenv ccxt pandas numpy websockets python-telegram-bot
```

### 2. 配置文件缺失或错误 ⚠️

**检查.env文件是否存在：**
```powershell
cat .env
```

**必需的配置项：**
```env
KUCOIN_API_KEY=6902f625f9a9a300014c3976
KUCOIN_API_SECRET=d71e4e3d-4369-4e77-94f8-fd456c5e0387
KUCOIN_API_PASSPHRASE=x5gU7dnL6bvrvbV!
TELEGRAM_BOT_TOKEN=7965687699:AAHWCHsHPyJEuvaFVU8yLCvSPohT8kU3G4U
TELEGRAM_CHAT_ID=5374455360
DATABASE_URL=mysql://trading:Zdm351026@localhost:3306/trading_dashboard
```

### 3. Python解释器路径问题 ⚠️

PM2配置使用`python`，但Windows可能找不到。

**检查Python路径：**
```powershell
where python
where python3
```

---

## ⚡ 快速修复步骤

### 步骤1：查看错误日志
```powershell
cd C:\trading_dashboard_fixed
pm2 logs trading-bot --lines 50
```

**常见错误及解决方案：**

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `ModuleNotFoundError: No module named 'dotenv'` | 缺少python-dotenv | `pip install python-dotenv` |
| `ModuleNotFoundError: No module named 'ccxt'` | 缺少ccxt | `pip install ccxt pandas numpy` |
| `Can't connect to MySQL server` | 数据库未启动 | `Start-Service MySQL80` |
| `Interpreter python not found` | Python路径问题 | 修改ecosystem.config.cjs |

### 步骤2：安装所有Python依赖
```powershell
pip install python-dotenv ccxt pandas numpy websockets python-telegram-bot
```

### 步骤3：手动测试启动
```powershell
cd C:\trading_dashboard_fixed\scripts
python start_trading_system.py
```

**如果手动启动成功：**
- 说明代码没问题
- 问题在PM2配置

**如果手动启动失败：**
- 查看错误信息
- 根据错误安装缺失的依赖

### 步骤4：修复PM2配置（如果需要）

如果手动启动成功但PM2失败，编辑`ecosystem.config.cjs`：

找到trading-bot配置（第30-44行）：
```javascript
{
  name: 'trading-bot',
  script: 'scripts/start_trading_system.py',
  interpreter: 'python',  // ← 这里可能需要改
  cwd: './',
  // ...
}
```

改为完整Python路径：
```javascript
{
  name: 'trading-bot',
  script: 'scripts/start_trading_system.py',
  interpreter: 'C:\\Python311\\python.exe',  // 使用where python查到的路径
  cwd: './',
  // ...
}
```

### 步骤5：重启trading-bot
```powershell
pm2 delete trading-bot
pm2 start ecosystem.config.cjs --only trading-bot
pm2 save
```

### 步骤6：验证运行
```powershell
pm2 list
pm2 logs trading-bot --lines 20
```

**成功标志：**
- PM2列表中trading-bot状态为`online`
- 日志中显示"Trading system started"
- 没有错误信息

---

## 🧪 测试脚本

创建`test_bot.py`测试所有依赖：

```python
#!/usr/bin/env python3
"""测试trading bot所有依赖"""
import sys

print("="*50)
print("Trading Bot Dependency Test")
print("="*50)

modules = {
    'dotenv': 'python-dotenv',
    'ccxt': 'ccxt',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'websockets': 'websockets',
    'telegram': 'python-telegram-bot'
}

missing = []
for module, package in modules.items():
    try:
        __import__(module)
        print(f"✓ {module:15} OK")
    except ImportError:
        print(f"✗ {module:15} MISSING - install with: pip install {package}")
        missing.append(package)

print("="*50)
if missing:
    print(f"FAILED: {len(missing)} packages missing")
    print(f"Run: pip install {' '.join(missing)}")
    sys.exit(1)
else:
    print("SUCCESS: All dependencies installed")
    sys.exit(0)
```

运行测试：
```powershell
python test_bot.py
```

---

## 📋 完整修复清单

- [ ] 安装Python依赖：`pip install python-dotenv ccxt pandas numpy websockets python-telegram-bot`
- [ ] 检查.env文件存在且包含所有必需配置
- [ ] 检查MySQL服务运行：`Get-Service MySQL*`
- [ ] 手动测试启动：`python scripts/start_trading_system.py`
- [ ] 如果需要，修改ecosystem.config.cjs中的Python路径
- [ ] 重启trading-bot：`pm2 restart trading-bot`
- [ ] 验证状态：`pm2 list`
- [ ] 查看日志确认无错误：`pm2 logs trading-bot`

---

## 🆘 仍然无法启动？

提供以下信息以便诊断：

1. **Python版本：**
```powershell
python --version
```

2. **已安装的包：**
```powershell
pip list > packages.txt
```

3. **PM2日志：**
```powershell
pm2 logs trading-bot --lines 100 > bot_error.txt
```

4. **手动启动输出：**
```powershell
cd scripts
python start_trading_system.py > manual_start.txt 2>&1
```

5. **环境变量：**
```powershell
cat .env > env_config.txt
```

---

**最后更新：** 2025-11-28  
**测试环境：** Manus开发环境 v5367b9da  
**核心模块测试：** ✅ 全部通过
