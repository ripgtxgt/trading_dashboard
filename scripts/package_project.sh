#!/bin/bash

# 项目打包脚本
# 用于打包整个项目供下载

set -e

echo "=========================================="
echo "10U战神滚仓策略 - 项目打包"
echo "=========================================="
echo ""

# 项目根目录
PROJECT_ROOT="/home/ubuntu/trading_dashboard"
cd "$PROJECT_ROOT"

# 打包目录
PACKAGE_DIR="/home/ubuntu/trading_dashboard_package"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="trading_dashboard_${TIMESTAMP}.tar.gz"

echo "1. 清理旧的打包文件..."
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

echo "2. 复制项目文件..."

# 复制核心文件
cp -r client "$PACKAGE_DIR/"
cp -r server "$PACKAGE_DIR/"
cp -r scripts "$PACKAGE_DIR/"
cp -r drizzle "$PACKAGE_DIR/"
cp -r shared "$PACKAGE_DIR/" 2>/dev/null || true
cp -r storage "$PACKAGE_DIR/" 2>/dev/null || true

# 复制配置文件
cp package.json "$PACKAGE_DIR/"
cp tsconfig.json "$PACKAGE_DIR/"
cp vite.config.ts "$PACKAGE_DIR/"
cp vitest.config.ts "$PACKAGE_DIR/" 2>/dev/null || true
cp drizzle.config.ts "$PACKAGE_DIR/"
cp tailwind.config.ts "$PACKAGE_DIR/" 2>/dev/null || true
cp postcss.config.js "$PACKAGE_DIR/" 2>/dev/null || true
cp components.json "$PACKAGE_DIR/"

# 复制文档
cp PROJECT_README.md "$PACKAGE_DIR/README.md"
cp RISK_MANAGEMENT_GUIDE.md "$PACKAGE_DIR/" 2>/dev/null || true
cp V24_FEATURES_GUIDE.md "$PACKAGE_DIR/" 2>/dev/null || true
cp todo.md "$PACKAGE_DIR/" 2>/dev/null || true

echo "3. 清理不必要的文件..."
cd "$PACKAGE_DIR"

# 删除node_modules（太大）
rm -rf node_modules

# 删除构建产物
rm -rf dist
rm -rf .next
rm -rf .turbo

# 删除临时文件
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete
find . -name ".DS_Store" -delete
find . -name "*.log" -delete
find . -name "*.tmp" -delete

# 删除状态文件
rm -f scripts/risk_state.json
rm -f scripts/test_mode_state.json
rm -f scripts/simulated_exchange_state.json
rm -f scripts/strategy_comparison.json

echo "4. 创建安装说明..."
cat > "$PACKAGE_DIR/INSTALL.md" << 'EOF'
# 安装指南

## 1. 环境要求

- Node.js 22+
- Python 3.11+
- MySQL 8.0+ (或TiDB)
- pnpm

## 2. 安装步骤

### 2.1 安装Node.js依赖

```bash
pnpm install
```

### 2.2 安装Python依赖

```bash
pip3 install ccxt pandas numpy python-telegram-bot websockets
```

### 2.3 配置环境变量

创建 `.env` 文件（或通过Manus平台配置）：

```env
# 数据库
DATABASE_URL=mysql://user:password@host:port/database

# OAuth (如果使用Manus平台，这些会自动注入)
JWT_SECRET=your_jwt_secret
VITE_APP_ID=your_app_id
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://auth.manus.im

# Manus API (如果使用Manus平台，这些会自动注入)
BUILT_IN_FORGE_API_KEY=your_api_key
BUILT_IN_FORGE_API_URL=https://api.manus.im
```

### 2.4 配置交易API

编辑 `scripts/config.py`：

```python
# KuCoin API配置
API_KEY = "your_kucoin_api_key"
API_SECRET = "your_kucoin_api_secret"
API_PASSPHRASE = "your_kucoin_passphrase"

# Telegram配置（可选）
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
TELEGRAM_CHAT_ID = "your_telegram_chat_id"
```

### 2.5 初始化数据库

```bash
pnpm db:push
```

## 3. 启动服务

### 3.1 启动Web服务

```bash
pnpm dev
```

访问: http://localhost:3000

### 3.2 启动WebSocket服务（可选）

```bash
python3 scripts/websocket_pusher.py
```

### 3.3 启动交易机器人（可选）

```bash
python3 scripts/trading_bot.py
```

## 4. 首次使用

1. 访问Dashboard并登录
2. 启用"测试模式"
3. 使用"策略向导"优化参数
4. 在测试模式下验证策略
5. 确认无误后切换到实盘

## 5. 故障排除

查看 `README.md` 中的故障排除章节。

---

**重要提示**: 请先在测试模式下充分验证系统功能，再进行实盘交易！
EOF

echo "5. 创建快速启动脚本..."
cat > "$PACKAGE_DIR/start.sh" << 'EOF'
#!/bin/bash

echo "=========================================="
echo "10U战神滚仓策略 - 快速启动"
echo "=========================================="
echo ""

# 检查依赖
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装"
    exit 1
fi

if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm未安装"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装Node.js依赖..."
    pnpm install
    echo ""
fi

# 启动开发服务器
echo "🚀 启动开发服务器..."
echo ""
echo "访问: http://localhost:3000"
echo "按 Ctrl+C 停止服务"
echo ""

pnpm dev
EOF

chmod +x "$PACKAGE_DIR/start.sh"

echo "6. 创建压缩包..."
cd /home/ubuntu
tar -czf "$PACKAGE_NAME" -C "$PACKAGE_DIR" .

# 移动到项目根目录
mv "$PACKAGE_NAME" "$PROJECT_ROOT/"

echo "7. 清理临时文件..."
rm -rf "$PACKAGE_DIR"

echo ""
echo "=========================================="
echo "✅ 打包完成！"
echo "=========================================="
echo ""
echo "打包文件: $PROJECT_ROOT/$PACKAGE_NAME"
echo "文件大小: $(du -h "$PROJECT_ROOT/$PACKAGE_NAME" | cut -f1)"
echo ""
echo "解压命令:"
echo "  tar -xzf $PACKAGE_NAME"
echo ""
echo "=========================================="
