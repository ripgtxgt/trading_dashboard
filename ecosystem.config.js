/**
 * PM2 配置文件
 * 用于管理所有服务进程
 */

module.exports = {
  apps: [
    // Web Dashboard (Express + tRPC Server)
    {
      name: 'trading-dashboard',
      script: 'node',
      args: 'dist/index.js',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
      },
      error_file: './logs/dashboard-error.log',
      out_file: './logs/dashboard-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    },

    // WebSocket 推送服务器
    {
      name: 'websocket-server',
      script: 'python',
      args: 'scripts/websocket_pusher.py',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      error_file: './logs/websocket-error.log',
      out_file: './logs/websocket-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    },

    // 交易机器人（默认不启动，需要手动启动）
    // 启动命令: pm2 start ecosystem.config.js --only trading-bot
    {
      name: 'trading-bot',
      script: 'python',
      args: 'scripts/kucoin_api.py',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      error_file: './logs/trading-bot-error.log',
      out_file: './logs/trading-bot-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      // 默认不启动
      autostart: false,
    },

    // Telegram Bot（可选）
    {
      name: 'telegram-bot',
      script: 'python',
      args: 'scripts/telegram_bot.py',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      error_file: './logs/telegram-bot-error.log',
      out_file: './logs/telegram-bot-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      // 默认不启动
      autostart: false,
    },
  ],
};
