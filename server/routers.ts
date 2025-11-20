import { COOKIE_NAME } from "@shared/const";
import { z } from "zod";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";

export const appRouter = router({
    // if you need to use socket.io, read and register route in server/_core/index.ts, all api should start with '/api/' so that the gateway can route correctly
  system: systemRouter,
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
        direction: z.enum(["long", "short"]),
        entryPrice: z.string(),
        exitPrice: z.string(),
        margin: z.string(),
        pnl: z.string(),
        pnlPct: z.string(),
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
        direction: z.enum(["long", "short"]),
        entryPrice: z.string(),
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
});

export type AppRouter = typeof appRouter;
