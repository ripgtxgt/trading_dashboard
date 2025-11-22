import { z } from "zod";
import { publicProcedure, router } from "./_core/trpc";
import { exec } from "child_process";
import { promisify } from "util";
import * as fs from "fs/promises";
import * as path from "path";

const execAsync = promisify(exec);

/**
 * 风险管理API路由
 */
export const riskRouter = router({
  // 获取风险状态
  getStatus: publicProcedure.query(async () => {
    try {
      const stateFile = path.join(process.cwd(), 'scripts', 'risk_manager_state.json');
      const data = await fs.readFile(stateFile, 'utf-8');
      return JSON.parse(data);
    } catch (error) {
      // 如果文件不存在，返回默认状态
      return {
        is_trading_allowed: true,
        pause_reason: null,
        pause_until: null,
        daily_pnl: 0,
        total_pnl: 0,
        current_drawdown_pct: 0,
        consecutive_losses: 0,
        volatility: 0,
        recent_events: [],
      };
    }
  }),

  // 获取风险配置
  getConfig: publicProcedure.query(async () => {
    // 返回默认配置
    return {
      max_volatility: 0.05,
      volatility_window: 20,
      max_daily_loss_pct: 0.10,
      max_total_loss_pct: 0.30,
      max_consecutive_losses: 3,
      consecutive_loss_pause_hours: 1,
      max_drawdown_pct: 0.20,
      trading_hours: {
        enabled: false,
        start_hour: 0,
        end_hour: 24,
      },
      circuit_breaker: {
        enabled: true,
        price_change_pct: 0.10,
        time_window_minutes: 5,
      },
      auto_resume: {
        enabled: true,
        check_interval_minutes: 30,
      },
    };
  }),

  // 更新风险配置
  updateConfig: publicProcedure
    .input(z.object({
      max_volatility: z.number().optional(),
      max_daily_loss_pct: z.number().optional(),
      max_total_loss_pct: z.number().optional(),
      max_consecutive_losses: z.number().optional(),
      max_drawdown_pct: z.number().optional(),
    }))
    .mutation(async ({ input }) => {
      // TODO: 实现配置更新逻辑
      return { success: true, message: "配置已更新" };
    }),

  // 手动恢复交易
  resume: publicProcedure.mutation(async () => {
    try {
      const stateFile = path.join(process.cwd(), 'scripts', 'risk_manager_state.json');
      const data = await fs.readFile(stateFile, 'utf-8');
      const state = JSON.parse(data);
      
      // 更新状态
      state.is_trading_allowed = true;
      state.pause_reason = null;
      state.pause_until = null;
      
      await fs.writeFile(stateFile, JSON.stringify(state, null, 2));
      
      return { success: true, message: "交易已恢复" };
    } catch (error: any) {
      return { success: false, message: error.message };
    }
  }),

  // 手动暂停交易
  pause: publicProcedure
    .input(z.object({
      reason: z.string(),
      hours: z.number().optional(),
    }))
    .mutation(async ({ input }) => {
      try {
        const stateFile = path.join(process.cwd(), 'scripts', 'risk_manager_state.json');
        let state: any = {};
        
        try {
          const data = await fs.readFile(stateFile, 'utf-8');
          state = JSON.parse(data);
        } catch {
          // 文件不存在，使用默认状态
        }
        
        // 更新状态
        state.is_trading_allowed = false;
        state.pause_reason = input.reason;
        
        if (input.hours) {
          const pauseUntil = new Date();
          pauseUntil.setHours(pauseUntil.getHours() + input.hours);
          state.pause_until = pauseUntil.toISOString();
        } else {
          state.pause_until = null;
        }
        
        await fs.writeFile(stateFile, JSON.stringify(state, null, 2));
        
        return { success: true, message: "交易已暂停" };
      } catch (error: any) {
        return { success: false, message: error.message };
      }
    }),

  // 重置每日统计
  resetDaily: publicProcedure.mutation(async () => {
    try {
      const stateFile = path.join(process.cwd(), 'scripts', 'risk_manager_state.json');
      const data = await fs.readFile(stateFile, 'utf-8');
      const state = JSON.parse(data);
      
      // 重置每日统计
      state.daily_pnl = 0;
      
      await fs.writeFile(stateFile, JSON.stringify(state, null, 2));
      
      return { success: true, message: "每日统计已重置" };
    } catch (error: any) {
      return { success: false, message: error.message };
    }
  }),

  // 获取风险事件日志
  getEvents: publicProcedure
    .input(z.object({ limit: z.number().optional().default(50) }))
    .query(async ({ input }) => {
      try {
        const stateFile = path.join(process.cwd(), 'scripts', 'risk_manager_state.json');
        const data = await fs.readFile(stateFile, 'utf-8');
        const state = JSON.parse(data);
        
        const events = state.risk_events || [];
        return events.slice(-input.limit);
      } catch (error) {
        return [];
      }
    }),
});
