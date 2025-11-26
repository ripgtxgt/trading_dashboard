module.exports = {
  apps: [
    {
      name: 'trading-dashboard',
      script: 'server/_core/index.ts',
      interpreter: 'node',
      interpreter_args: '--loader tsx',
      cwd: 'C:\\trading_dashboard',
      env: {
        NODE_ENV: 'production',
        PORT: '3000'
      },
      error_file: 'logs/dashboard-error.log',
      out_file: 'logs/dashboard-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      instances: 1,
      exec_mode: 'fork'
    },
    {
      name: 'trading-bot',
      script: 'scripts/v24_strategy.py',
      interpreter: 'python',
      cwd: 'C:\\trading_dashboard\\scripts',
      error_file: 'C:\\trading_dashboard\\logs\\bot-error.log',
      out_file: 'C:\\trading_dashboard\\logs\\bot-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      instances: 1,
      exec_mode: 'fork'
    },
    {
      name: 'telegram-bot',
      script: 'scripts/telegram_bot.py',
      interpreter: 'python',
      cwd: 'C:\\trading_dashboard\\scripts',
      error_file: 'C:\\trading_dashboard\\logs\\telegram-error.log',
      out_file: 'C:\\trading_dashboard\\logs\\telegram-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      instances: 1,
      exec_mode: 'fork'
    },
    {
      name: 'websocket-server',
      script: 'scripts/websocket_server.py',
      interpreter: 'python',
      cwd: 'C:\\trading_dashboard\\scripts',
      error_file: 'C:\\trading_dashboard\\logs\\websocket-error.log',
      out_file: 'C:\\trading_dashboard\\logs\\websocket-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      instances: 1,
      exec_mode: 'fork'
    },
    {
      name: 'daily-report',
      script: 'scripts/daily_report.py',
      interpreter: 'python',
      cwd: 'C:\\trading_dashboard\\scripts',
      error_file: 'C:\\trading_dashboard\\logs\\report-error.log',
      out_file: 'C:\\trading_dashboard\\logs\\report-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      instances: 1,
      exec_mode: 'fork',
      cron_restart: '0 0 * * *' // 每天凌晨0点重启
    }
  ]
};
