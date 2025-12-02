/**
 * PM2 Configuration File
 * Manages all service processes
 */

module.exports = {
  apps: [
    // Web Dashboard (Node.js + tRPC Server)
    {
      name: 'trading-dashboard',
      script: 'server/_core/index.ts',
      interpreter: 'node',
      interpreter_args: '--import tsx/esm',
      cwd: './',
      instances: 1,
      exec_mode: 'fork',
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

    // Trading Bot (Start Trading System)
    {
      name: 'trading-bot',
      script: 'scripts/start_trading_system.py',
      interpreter: 'python3',
      cwd: './',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      error_file: './logs/trading-bot-error.log',
      out_file: './logs/trading-bot-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      autostart: true,
    },

    // Telegram Bot
    {
      name: 'telegram-bot',
      script: 'scripts/telegram_bot.py',
      interpreter: 'python3',
      cwd: './',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      error_file: './logs/telegram-bot-error.log',
      out_file: './logs/telegram-bot-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      autostart: true,
    },

    // WebSocket Server
    {
      name: 'websocket-server',
      script: 'scripts/websocket_pusher.py',
      interpreter: 'python3',
      cwd: './',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      error_file: './logs/websocket-error.log',
      out_file: './logs/websocket-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      autostart: true,
    },

    // Daily Report Scheduler
    {
      name: 'daily-report',
      script: 'scripts/daily_report.py',
      interpreter: 'python3',
      cwd: './',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      error_file: './logs/daily-report-error.log',
      out_file: './logs/daily-report-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      autostart: true,
      cron_restart: '0 0 * * *',
    },

    // Webhook Deploy Server (Auto-deployment on GitHub push)
    {
      name: 'webhook-deploy-server',
      script: 'webhook-deploy-server.cjs',
      interpreter: 'node',
      cwd: './',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        NODE_ENV: 'production',
        WEBHOOK_SECRET: process.env.WEBHOOK_SECRET || 'your-webhook-secret-here',
      },
      error_file: './logs/webhook-error.log',
      out_file: './logs/webhook-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      autostart: true,
    },
  ],
};
