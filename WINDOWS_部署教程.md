# Windows服务器部署教程

## 📋 目录

1. [准备工作](#准备工作)
2. [安装Python](#安装python)
3. [安装MySQL数据库](#安装mysql数据库)
4. [配置交易系统](#配置交易系统)
5. [启动系统](#启动系统)
6. [常见问题](#常见问题)

---

## 准备工作

### 需要准备的信息

在开始之前，请准备好以下信息：

- ✅ KuCoin API密钥（API Key、API Secret、API Passphrase）
- ✅ MySQL数据库连接信息（如果没有，后面会教你安装）
- ✅ Telegram Bot Token和Chat ID（可选，用于接收通知）

### 下载项目文件

1. 解压 `trading_dashboard_complete.tar.gz` 到任意目录
2. 建议解压到：`C:\trading_dashboard\`

---

## 安装Python

### 步骤1：下载Python

1. 打开浏览器，访问：https://www.python.org/downloads/
2. 点击黄色按钮 "Download Python 3.x.x"
3. 下载完成后，双击安装包

### 步骤2：安装Python

**重要：安装时必须勾选 "Add Python to PATH"！**

1. 勾选底部的 "Add Python to PATH"
2. 点击 "Install Now"
3. 等待安装完成
4. 点击 "Close"

### 步骤3：验证安装

1. 按 `Win + R` 键
2. 输入 `cmd` 并回车
3. 在命令提示符中输入：
   ```
   python --version
   ```
4. 如果显示 `Python 3.x.x`，说明安装成功

---

## 安装MySQL数据库

### 方案A：使用在线数据库（推荐新手）

如果你不想在本地安装MySQL，可以使用免费的在线数据库服务：

#### PlanetScale（推荐）

1. 访问：https://planetscale.com/
2. 注册账号（可以用GitHub登录）
3. 创建新数据库
4. 获取连接字符串（格式：`mysql://用户名:密码@主机:端口/数据库名`）

#### Railway

1. 访问：https://railway.app/
2. 注册账号
3. 创建MySQL数据库
4. 获取连接字符串

### 方案B：本地安装MySQL

#### 步骤1：下载MySQL

1. 访问：https://dev.mysql.com/downloads/installer/
2. 下载 "mysql-installer-community"
3. 选择较大的那个文件（约400MB）

#### 步骤2：安装MySQL

1. 双击安装包
2. 选择 "Custom" 安装类型
3. 只选择安装：
   - MySQL Server
   - MySQL Workbench（可选，图形化管理工具）
4. 点击 "Next" 继续
5. 点击 "Execute" 开始安装

#### 步骤3：配置MySQL

1. 选择 "Development Computer"
2. 端口保持默认 `3306`
3. 设置root密码（**请记住这个密码！**）
4. 点击 "Next" 完成配置

#### 步骤4：创建数据库

1. 按 `Win + R`，输入 `cmd`
2. 输入以下命令登录MySQL：
   ```
   mysql -u root -p
   ```
3. 输入刚才设置的密码
4. 创建数据库：
   ```sql
   CREATE DATABASE trading_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
5. 输入 `exit` 退出

---

## 配置交易系统

### 步骤1：安装Python依赖

1. 打开文件资源管理器
2. 进入项目目录：`C:\trading_dashboard\scripts\`
3. 双击运行 `install_dependencies.bat`
4. 等待安装完成（可能需要几分钟）

### 步骤2：创建配置文件

1. 在 `scripts` 目录下，双击运行 `create_config.bat`
2. 会自动创建 `config.env` 文件

### 步骤3：编辑配置文件

1. 用记事本打开 `config.env`
2. 填入你的配置信息：

```ini
# ========== 必需配置 ==========

# 数据库连接字符串
# 本地MySQL示例：
DATABASE_URL=mysql://root:你的密码@localhost:3306/trading_dashboard

# 在线数据库示例：
# DATABASE_URL=mysql://用户名:密码@主机地址:端口/数据库名

# KuCoin API配置
KUCOIN_API_KEY=你的API_KEY
KUCOIN_API_SECRET=你的API_SECRET
KUCOIN_API_PASSPHRASE=你的API_PASSPHRASE

# ========== 可选配置 ==========

# Telegram通知（可选）
TELEGRAM_BOT_TOKEN=你的Bot_Token
TELEGRAM_CHAT_ID=你的Chat_ID

# 交易配置
INITIAL_CAPITAL=10.0
KUCOIN_SANDBOX=false
```

3. 保存文件

### 步骤4：获取KuCoin API密钥

1. 登录 KuCoin 网站：https://www.kucoin.com/
2. 点击右上角头像 → API管理
3. 点击 "创建API"
4. 设置API名称（随意）
5. 设置API密码（**请记住！**）
6. 权限选择：
   - ✅ 通用权限
   - ✅ 交易权限
   - ❌ 提现权限（不要勾选！）
7. 复制保存：
   - API Key
   - API Secret
   - API Passphrase
8. 填入 `config.env` 文件

### 步骤5：检查环境

1. 双击运行 `check_environment.bat`
2. 检查所有项目是否通过
3. 如果有错误，根据提示修复

---

## 启动系统

### 方式1：双击启动（推荐）

1. 进入 `scripts` 目录
2. 双击 `start_trading.bat`
3. 系统会自动启动

### 方式2：命令行启动

1. 按 `Win + R`，输入 `cmd`
2. 进入scripts目录：
   ```
   cd C:\trading_dashboard\scripts
   ```
3. 运行启动脚本：
   ```
   start_trading.bat
   ```

### 启动后的界面

你会看到类似这样的输出：

```
========================================
  10U战神滚仓策略 - 交易系统启动
========================================

[✓] Python已安装
Python 3.11.0

[✓] 所有依赖包已安装

[✓] 配置文件已找到

[✓] 配置加载完成

========================================
  配置摘要
========================================
数据库: mysql://root:***@localhost...
KuCoin API: 6123abc...
初始资金: 10.0 USDT
沙盒模式: false
Telegram: 已配置
========================================

[启动] 正在启动交易系统...
按 Ctrl+C 可以停止系统

========================================
10U战神滚仓策略 - Web Dashboard集成版
========================================
系统初始化完成
初始资金: 10.00 USDT
当前阶段: stage1

交易系统启动
📊 信号分析:
  当前价格: 98234.50
  短MA(5): 98156.20
  长MA(20): 97892.40
  ...
```

### 停止系统

按 `Ctrl + C` 键，系统会优雅停止：
- 自动平掉所有持仓
- 保存状态到数据库
- 发送停止通知

---

## 访问Web Dashboard

### 本地访问

如果你在本地运行Web服务器：

1. 打开浏览器
2. 访问：`http://localhost:3000`

### 在线访问

如果你已经发布到Manus平台：

1. 打开浏览器
2. 访问：`https://你的域名.manus.space`

---

## 常见问题

### Q1：提示"Python未安装"

**解决方法**：
1. 重新安装Python
2. 安装时**必须勾选** "Add Python to PATH"
3. 重启电脑

### Q2：提示"数据库连接失败"

**解决方法**：
1. 检查MySQL服务是否启动：
   - 按 `Win + R`，输入 `services.msc`
   - 找到 "MySQL" 服务
   - 右键 → 启动
2. 检查 `config.env` 中的 `DATABASE_URL` 是否正确
3. 检查密码是否正确

### Q3：提示"KuCoin API错误"

**解决方法**：
1. 检查API密钥是否正确
2. 检查API权限是否包含"交易权限"
3. 检查API是否已激活
4. 如果是新创建的API，等待5分钟后再试

### Q4：如何查看日志？

日志文件位置：`C:\trading_dashboard\scripts\trading_system_YYYYMMDD.log`

用记事本打开即可查看。

### Q5：如何设置开机自动启动？

1. 按 `Win + R`，输入 `shell:startup`
2. 创建 `start_trading.bat` 的快捷方式
3. 将快捷方式复制到打开的文件夹

### Q6：系统占用CPU太高怎么办？

在 `config.env` 中调整检查间隔：

```ini
CHECK_INTERVAL=300
```

数值越大，CPU占用越低（单位：秒）

### Q7：如何备份数据？

**方式1：备份数据库**
```
mysqldump -u root -p trading_dashboard > backup.sql
```

**方式2：备份整个项目**

直接复制 `C:\trading_dashboard\` 文件夹

### Q8：如何更新系统？

1. 停止交易系统（Ctrl+C）
2. 备份 `config.env` 文件
3. 解压新版本到原目录（覆盖）
4. 恢复 `config.env` 文件
5. 重新启动系统

---

## 下一步

系统启动成功后，你可以：

1. **配置Telegram通知**
   - 查看 `TELEGRAM_SETUP.md`
   - 接收实时交易通知

2. **访问Web Dashboard**
   - 查看实时账户状态
   - 监控交易历史
   - 调整策略参数

3. **优化策略参数**
   - 编辑 `live_trading_config.py`
   - 调整MA周期、止损止盈等

---

## 技术支持

如果遇到问题：

1. 查看日志文件
2. 运行 `check_environment.bat` 检查环境
3. 查看本文档的"常见问题"部分

---

**祝交易顺利！** 🚀
