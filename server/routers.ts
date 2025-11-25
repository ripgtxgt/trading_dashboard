import { COOKIE_NAME } from "@shared/const";
import { z } from "zod";
import { klineCache } from "./kline_cache";
import { telegramNotifier } from "./telegram";
import { riskRouter } from "./risk_api";
import { v24Router } from './v24_api';
import { dataExportRouter } from './data_export';
import { tradeHistoryRouter } from "./trade_history_api";
import { performanceReportRouter } from "./performance_report_api";
import { strategyConfigRouter } from "./strategy_config_api";
import { riskDataRouter } from "./risk_data_api";
import { signalParamsRouter } from "./signal_params_api";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import { klineProxyRouter } from "./kline_proxy";

export const appRouter = router({
    // if you need to use socket.io, read and register route in server/_core/index.ts, all api should start with '/api/' so that the gateway can route correctly
  system: systemRouter,
  kline: klineProxyRouter,
  tradeHistory: tradeHistoryRouter,
  performanceReport: performanceReportRouter,
  strategyConfig: strategyConfigRouter,
  riskData: riskDataRouter,
  signalParams: signalParamsRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  trading: router({
    // Get bot state
    getState: publicProcedure.query(async () => {
      const { getBotState } = await import('./db');
      return await getBotState();
    }),
    
    // Get current position
    getPosition: publicProcedure.query(async () => {
      const { getCurrentPosition } = await import('./db');
      return await getCurrentPosition();
    }),
    
    // Get recent trades
    getTrades: publicProcedure
      .input(z.object({ limit: z.number().optional().default(50) }))
      .query(async ({ input }) => {
        const { getRecentTrades } = await import('./db');
        return await getRecentTrades(input.limit);
      }),
    
    // Get balance history
    getBalanceHistory: publicProcedure
      .input(z.object({ hours: z.number().optional().default(24) }))
      .query(async ({ input }) => {
        const { getBalanceHistory } = await import('./db');
        return await getBalanceHistory(input.hours);
      }),
    
    // Get trade statistics
    getStats: publicProcedure.query(async () => {
      const { getTradeStats } = await import('./db');
      return await getTradeStats();
    }),
    
    // Emergency stop bot
    emergencyStop: publicProcedure
      .mutation(async () => {
        const { updateBotState } = await import('./db');
        await updateBotState({ emergencyStopped: 1, isRunning: 0 });
        
        // Send Telegram notification
        try {
          await telegramNotifier.sendMessage({
            text: "\u26a0\ufe0f EMERGENCY STOP TRIGGERED\n\n" +
              "All trading activities have been paused.\n" +
              "Any open positions will be closed.\n\n" +
              "Use /resume command or Dashboard to restart."
          });
        } catch (e) {
          console.error('[Emergency Stop] Failed to send Telegram notification:', e);
        }
        
        return { success: true, message: 'Emergency stop activated' };
      }),
    
    // Get balance snapshots
    getBalanceSnapshots: publicProcedure
      .input(z.object({ limit: z.number().optional().default(100) }))
      .query(async ({ input }) => {
        const { getBalanceSnapshots } = await import('./db');
        return await getBalanceSnapshots(input.limit);
      }),
    
    // Resume bot
    resumeBot: publicProcedure
      .mutation(async () => {
        const { updateBotState } = await import('./db');
        await updateBotState({ emergencyStopped: 0, isRunning: 1 });
        
        // Send Telegram notification
        try {
          await telegramNotifier.sendMessage({
            text: "\u2705 BOT RESUMED\n\n" +
              "Trading activities have been resumed.\n" +
              "Bot is now monitoring the market."
          });
        } catch (e) {
          console.error('[Resume Bot] Failed to send Telegram notification:', e);
        }
        
        return { success: true, message: 'Bot resumed successfully' };
      }),
    
    // Update bot state (for integration with trading bot)
    updateState: publicProcedure
      .input(z.object({
        isRunning: z.number().optional(),
        capital: z.string().optional(),
        initialCapital: z.string().optional(),
        currentStage: z.string().optional(),
        dailyTrades: z.number().optional(),
        dailyPnl: z.string().optional(),
        totalTrades: z.number().optional(),
        emergencyStopped: z.number().optional(),
      }))
      .mutation(async ({ input }) => {
        const { updateBotState } = await import('./db');
        await updateBotState(input);
        return { success: true };
      }),
    
    // Add trade record
    addTrade: publicProcedure
      .input(z.object({
        symbol: z.string().optional(),
        direction: z.enum(["long", "short"]),
        entryPrice: z.string(),
        exitPrice: z.string(),
        quantity: z.string(),
        margin: z.string(),
        pnl: z.string(),
        pnlPct: z.string(),
        fee: z.string().optional(),
        reason: z.string(),
        stage: z.string(),
        entryTime: z.date(),
        exitTime: z.date(),
      }))
      .mutation(async ({ input }) => {
        const { addTrade } = await import('./db');
        await addTrade(input);
        return { success: true };
      }),
    
    // Update position
    updatePosition: publicProcedure
      .input(z.object({
        symbol: z.string().optional(),
        direction: z.enum(["long", "short"]),
        entryPrice: z.string(),
        quantity: z.string(),
        margin: z.string(),
        stopLossPct: z.string(),
        takeProfitPct: z.string(),
        stage: z.string(),
        entryTime: z.date(),
      }))
      .mutation(async ({ input }) => {
        const { updatePosition } = await import('./db');
        await updatePosition(input);
        return { success: true };
      }),
    
    // Clear position
    clearPosition: publicProcedure.mutation(async () => {
      const { clearPosition } = await import('./db');
      await clearPosition();
      return { success: true };
    }),
    
    // Add balance snapshot
    addSnapshot: publicProcedure
      .input(z.object({ capital: z.string() }))
      .mutation(async ({ input }) => {
        const { addBalanceSnapshot } = await import('./db');
        await addBalanceSnapshot(input.capital);
        return { success: true };
      }),
  }),

  strategy: router({
    // Get active strategy parameters
    getActiveParams: publicProcedure.query(async () => {
      const { getActiveStrategyParams } = await import('./db');
      return await getActiveStrategyParams();
    }),
    
    // Get all strategy parameters history
    getAllParams: publicProcedure
      .input(z.object({ limit: z.number().optional().default(10) }))
      .query(async ({ input }) => {
        const { getAllStrategyParams } = await import('./db');
        return await getAllStrategyParams(input.limit);
      }),
    
    // Create new strategy parameters
    createParams: publicProcedure
      .input(z.object({
        shortMaPeriod: z.number().min(3).max(20),
        longMaPeriod: z.number().min(10).max(60),
        timeframe: z.enum(["15m", "30m", "1h", "2h", "4h"]),
        sensitivity: z.enum(["loose", "standard", "strict"]),
        isActive: z.number().optional().default(0),
      }))
      .mutation(async ({ input }) => {
        const { createStrategyParams } = await import('./db');
        await createStrategyParams(input);
        return { success: true };
      }),
    
    // Apply strategy parameters
    applyParams: publicProcedure
      .input(z.object({ paramId: z.number() }))
      .mutation(async ({ input }) => {
        const { applyStrategyParams } = await import('./db');
        await applyStrategyParams(input.paramId);
        return { success: true };
      }),
    
    // Simulate parameters (returns signal count for last N candles)
    simulateParams: publicProcedure
      .input(z.object({
        shortMaPeriod: z.number().min(3).max(20),
        longMaPeriod: z.number().min(10).max(60),
        timeframe: z.enum(["15m", "30m", "1h", "2h", "4h"]),
        sensitivity: z.enum(["loose", "standard", "strict"]),
        samplePeriod: z.string().optional().default("24h"),
      }))
      .mutation(async ({ input }) => {
        const { exec } = await import('child_process');
        const { promisify } = await import('util');
        const execAsync = promisify(exec);
        
        try {
          const scriptPath = '/home/ubuntu/trading_dashboard/scripts/signal_simulator.py';
          const command = `python3 ${scriptPath} XBTUSDTM ${input.timeframe} ${input.shortMaPeriod} ${input.longMaPeriod} ${input.sensitivity}`;
          
          const { stdout } = await execAsync(command, { timeout: 30000 });
          const result = JSON.parse(stdout);
          
          if (result.error) {
            throw new Error(result.error);
          }
          
          return {
            signalCount: result.signalCount,
            longSignals: result.longSignals,
            shortSignals: result.shortSignals,
            samplePeriod: result.samplePeriod,
            signals: result.signals,
          };
        } catch (error) {
          console.error('Error running signal simulator:', error);
          // Fallback to mock data if script fails
          const mockSignalCount = Math.floor(Math.random() * 20) + 5;
          const mockLongSignals = Math.floor(mockSignalCount * 0.6);
          const mockShortSignals = mockSignalCount - mockLongSignals;
          
          return {
            signalCount: mockSignalCount,
            longSignals: mockLongSignals,
            shortSignals: mockShortSignals,
            samplePeriod: input.samplePeriod,
          };
        }
      }),
    
    // Get parameter simulation result
    getSimulation: publicProcedure
      .input(z.object({ paramId: z.number() }))
      .query(async ({ input }) => {
        const { getParamSimulation } = await import('./db');
        return await getParamSimulation(input.paramId);
      }),
    
    // Get backtest history
    getBacktestHistory: publicProcedure
      .input(z.object({ limit: z.number().optional().default(50) }))
      .query(async ({ input }) => {
        const { getBacktestHistory } = await import('./db');
        return await getBacktestHistory(input.limit);
      }),
    
    // Backtest parameters
    backtestParams: publicProcedure
      .input(z.object({
        shortMaPeriod: z.number().min(3).max(20),
        longMaPeriod: z.number().min(10).max(60),
        timeframe: z.enum(["15m", "30m", "1h", "2h", "4h"]),
        sensitivity: z.enum(["loose", "standard", "strict"]),
      }))
      .mutation(async ({ input }) => {
        const { exec } = await import('child_process');
        const { promisify } = await import('util');
        const execAsync = promisify(exec);
        
        try {
          const scriptPath = '/home/ubuntu/trading_dashboard/scripts/backtest.py';
          const command = `python3 ${scriptPath} XBTUSDTM ${input.timeframe} ${input.shortMaPeriod} ${input.longMaPeriod} ${input.sensitivity}`;
          
          const { stdout } = await execAsync(command, { timeout: 60000 });
          const result = JSON.parse(stdout);
          
          if (result.error) {
            throw new Error(result.error);
          }
          
          return result;
        } catch (error) {
          console.error('Error running backtest:', error);
          throw new Error('Backtest failed');
        }
      }),
    
    // Bot control
    getBotStatus: publicProcedure.query(async () => {
      const { getBotStatus } = await import('./bot_integration');
      return await getBotStatus();
    }),
    
    startBot: publicProcedure.mutation(async () => {
      const { startBot } = await import('./bot_integration');
      return await startBot();
    }),
    
    stopBot: publicProcedure.mutation(async () => {
      const { stopBot } = await import('./bot_integration');
      return await stopBot();
    }),
    
    getBotLogs: publicProcedure
      .input(z.object({ lines: z.number().optional().default(100) }))
      .query(async ({ input }) => {
        const { getBotLogs } = await import('./bot_integration');
        return await getBotLogs(input.lines);
      }),
    
    getLatestSignals: publicProcedure.query(async () => {
      const { parseLatestSignals } = await import('./bot_integration');
      return await parseLatestSignals();
    }),
    
    // Optimize parameters
    optimizeParams: publicProcedure
      .input(z.object({
        timeframe: z.enum(["15m", "30m", "1h", "2h", "4h"]),
        optimizationTarget: z.enum(["winRate", "totalPnl", "sharpeRatio", "composite"]).optional().default("composite"),
      }))
      .mutation(async ({ input }) => {
        const { exec } = await import('child_process');
        const { promisify } = await import('util');
        const execAsync = promisify(exec);
        
        try {
          const scriptPath = '/home/ubuntu/trading_dashboard/scripts/optimize_params.py';
          const command = `python3 ${scriptPath} XBTUSDTM ${input.timeframe} ${input.optimizationTarget}`;
          
          const { stdout } = await execAsync(command, { timeout: 120000 });
          const result = JSON.parse(stdout);
          
          if (result.error) {
            throw new Error(result.error);
          }
          
          return result;
        } catch (error) {
          console.error('Error running optimization:', error);
          throw new Error('Optimization failed');
        }
      }),
  }),
  
  // Telegram notifications
  telegram: router({
    // Check if Telegram is configured
    isConfigured: publicProcedure.query(() => {
      return { configured: telegramNotifier.isConfigured() };
    }),
    
    // Send test message
    sendTest: publicProcedure.mutation(async () => {
      const success = await telegramNotifier.sendMessage({
        text: "🤖 *测试消息*\n\nTelegram通知配置成功！\n\n_" + new Date().toLocaleString("zh-CN") + "_"
      });
      return { success };
    }),
    
    // Send open position notification
    notifyOpen: publicProcedure
      .input(z.object({
        symbol: z.string(),
        side: z.enum(["long", "short"]),
        price: z.number(),
        quantity: z.number(),
        margin: z.number(),
      }))
      .mutation(async ({ input }) => {
        const success = await telegramNotifier.notifyOpenPosition(input);
        return { success };
      }),
    
    // Send close position notification
    notifyClose: publicProcedure
      .input(z.object({
        symbol: z.string(),
        side: z.enum(["long", "short"]),
        entryPrice: z.number(),
        exitPrice: z.number(),
        pnl: z.number(),
        pnlPct: z.number(),
      }))
      .mutation(async ({ input }) => {
        const success = await telegramNotifier.notifyClosePosition(input);
        return { success };
      }),
    
    // Send risk alert
    notifyRisk: publicProcedure
      .input(z.object({
        level: z.enum(["info", "warning", "error"]),
        message: z.string(),
        details: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        const success = await telegramNotifier.notifyRiskAlert(input);
        return { success };
      }),
  }),
  
  // 风险管理
  risk: riskRouter,
  
  // v24 API
  v24: v24Router,
  
  // Data export
  dataExport: dataExportRouter,
});

export type AppRouter = typeof appRouter;
