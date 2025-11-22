/**
 * v24.0 新增功能API路由
 * 包含测试模式、模拟交易和策略对比功能
 */

import { z } from "zod";
import { publicProcedure, router } from "./_core/trpc";
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import path from 'path';

const execAsync = promisify(exec);

export const v24Router = router({
  // ========== 测试模式管理 ==========
  
  getTestModeStatus: publicProcedure.query(async () => {
    try {
      const scriptPath = path.join(process.cwd(), 'scripts/test_mode.py');
      const { stdout } = await execAsync(`python3 -c "from test_mode import get_test_config; import json; config = get_test_config(); print(json.dumps(config.get_config()))"`, {
        cwd: path.dirname(scriptPath),
        timeout: 5000
      });
      
      return JSON.parse(stdout.trim());
    } catch (error) {
      console.error('获取测试模式状态失败:', error);
      return {
        enabled: false,
        initial_balance: 100.0,
        leverage: 10,
      };
    }
  }),

  setTestMode: publicProcedure
    .input(z.object({ enabled: z.boolean() }))
    .mutation(async ({ input }) => {
      try {
        const scriptPath = path.join(process.cwd(), 'scripts/test_mode.py');
        const action = input.enabled ? 'enable' : 'disable';
        await execAsync(`python3 -c "from test_mode import get_test_config; config = get_test_config(); config.${action}()"`, {
          cwd: path.dirname(scriptPath),
          timeout: 5000
        });
        
        return { success: true };
      } catch (error) {
        console.error('设置测试模式失败:', error);
        return { success: false, error: String(error) };
      }
    }),

  // ========== 模拟交易 ==========

  getSimulatedBalance: publicProcedure.query(async () => {
    try {
      const scriptPath = path.join(process.cwd(), 'scripts/test_mode.py');
      const { stdout } = await execAsync(`python3 -c "from test_mode import get_simulated_exchange; import json; exchange = get_simulated_exchange(); print(json.dumps(exchange.get_balance()))"`, {
        cwd: path.dirname(scriptPath),
        timeout: 5000
      });
      
      return JSON.parse(stdout.trim());
    } catch (error) {
      console.error('获取模拟余额失败:', error);
      return {
        total: 100.0,
        available: 100.0,
        used: 0.0,
        currency: 'USDT'
      };
    }
  }),

  getSimulatedPositions: publicProcedure.query(async () => {
    try {
      const scriptPath = path.join(process.cwd(), 'scripts/test_mode.py');
      const { stdout } = await execAsync(`python3 -c "from test_mode import get_simulated_exchange; import json; exchange = get_simulated_exchange(); print(json.dumps(exchange.get_positions()))"`, {
        cwd: path.dirname(scriptPath),
        timeout: 5000
      });
      
      return JSON.parse(stdout.trim());
    } catch (error) {
      console.error('获取模拟持仓失败:', error);
      return [];
    }
  }),

  createSimulatedOrder: publicProcedure
    .input(z.object({
      symbol: z.string(),
      side: z.enum(['buy', 'sell']),
      size: z.number(),
      price: z.number(),
    }))
    .mutation(async ({ input }) => {
      try {
        const scriptPath = path.join(process.cwd(), 'scripts/test_mode.py');
        const command = `python3 -c "from test_mode import get_simulated_exchange; import json; exchange = get_simulated_exchange(); result = exchange.create_order('${input.symbol}', '${input.side}', ${input.size}, ${input.price}); print(json.dumps(result))"`;
        
        const { stdout } = await execAsync(command, {
          cwd: path.dirname(scriptPath),
          timeout: 5000
        });
        
        return JSON.parse(stdout.trim());
      } catch (error) {
        console.error('创建模拟订单失败:', error);
        return { success: false, error: String(error) };
      }
    }),

  resetTestMode: publicProcedure.mutation(async () => {
    try {
      const scriptPath = path.join(process.cwd(), 'scripts/test_mode.py');
      await execAsync(`python3 -c "from test_mode import get_simulated_exchange; exchange = get_simulated_exchange(); exchange.reset()"`, {
        cwd: path.dirname(scriptPath),
        timeout: 5000
      });
      
      return { success: true };
    } catch (error) {
      console.error('重置测试模式失败:', error);
      return { success: false, error: String(error) };
    }
  }),

  // ========== 风险管理集成 ==========

  getRiskStatus: publicProcedure.query(async () => {
    try {
      const scriptPath = path.join(process.cwd(), 'scripts/risk_manager.py');
      const { stdout } = await execAsync(`python3 -c "from risk_manager import RiskManager; import json; rm = RiskManager(); print(json.dumps(rm.get_risk_status()))"`, {
        cwd: path.dirname(scriptPath),
        timeout: 5000
      });
      
      return JSON.parse(stdout.trim());
    } catch (error) {
      console.error('获取风险状态失败:', error);
      return {
        is_trading_allowed: true,
        pause_reason: null,
        daily_pnl: 0,
        total_pnl: 0,
        consecutive_losses: 0,
        current_drawdown_pct: 0,
        volatility: 0,
        recent_events: []
      };
    }
  }),

  recordTestTrade: publicProcedure
    .input(z.object({
      pnl: z.number(),
      is_win: z.boolean(),
    }))
    .mutation(async ({ input }) => {
      try {
        const scriptPath = path.join(process.cwd(), 'scripts/risk_manager.py');
        const isWin = input.is_win ? 'True' : 'False';
        await execAsync(`python3 -c "from risk_manager import RiskManager; rm = RiskManager(); rm.record_trade(${input.pnl}, ${isWin})"`, {
          cwd: path.dirname(scriptPath),
          timeout: 5000
        });
        
        return { success: true };
      } catch (error) {
        console.error('记录测试交易失败:', error);
        return { success: false, error: String(error) };
      }
    }),

  // ========== 策略对比 ==========

  getStrategyComparison: publicProcedure.query(async () => {
    try {
      const filePath = path.join(process.cwd(), 'scripts/strategy_comparison.json');
      const content = await fs.readFile(filePath, 'utf-8');
      return JSON.parse(content);
    } catch (error) {
      console.error('获取策略对比结果失败:', error);
      return { results: [] };
    }
  }),

  startStrategyBacktest: publicProcedure
    .input(z.object({
      strategies: z.array(z.object({
        name: z.string(),
        params: z.record(z.string(), z.any()),
      })),
      timeframe: z.string(),
      days: z.number(),
    }))
    .mutation(async ({ input }) => {
      try {
        // 创建临时配置文件
        const configPath = path.join(process.cwd(), 'scripts/backtest_config.json');
        await fs.writeFile(configPath, JSON.stringify(input, null, 2), 'utf-8');
        
        // 启动后台回测（异步）
        const scriptPath = path.join(process.cwd(), 'scripts/strategy_comparison.py');
        execAsync(`python3 ${scriptPath}`, {
          cwd: path.dirname(scriptPath),
          timeout: 120000
        }).catch(err => console.error('回测执行失败:', err));
        
        return { status: 'started', message: '回测已启动，请稍后查看结果' };
      } catch (error) {
        console.error('启动策略回测失败:', error);
        return { status: 'error', error: String(error) };
      }
    }),

  // ========== WebSocket配置 ==========

  getWebSocketConfig: publicProcedure.query(async () => {
    return {
      url: process.env.VITE_WS_URL || 'ws://localhost:8765',
      enabled: true,
    };
  }),
});
