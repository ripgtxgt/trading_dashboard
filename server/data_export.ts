import { router, publicProcedure } from "./_core/trpc";
import { z } from "zod";

export const dataExportRouter = router({
  // Export all data as JSON
  exportAllData: publicProcedure.query(async () => {
    const { getDb } = await import('./db');
    const { botState, positions, trades, balanceSnapshots, strategyConfig, strategyParams } = await import('../drizzle/schema');
    
    const db = await getDb();
    if (!db) {
      throw new Error("Database not available");
    }

    // Fetch all data
    const [
      botStateData,
      positionsData,
      tradesData,
      balanceData,
      strategyConfigData,
      strategyParamsData
    ] = await Promise.all([
      db.select().from(botState).limit(1),
      db.select().from(positions).orderBy(positions.id).limit(100),
      db.select().from(trades).orderBy(trades.id).limit(100),
      db.select().from(balanceSnapshots).orderBy(balanceSnapshots.timestamp).limit(100),
      db.select().from(strategyConfig).limit(10),
      db.select().from(strategyParams).limit(10)
    ]);

    return {
      exportTime: new Date().toISOString(),
      botState: botStateData[0] || null,
      positions: positionsData,
      trades: tradesData,
      balanceSnapshots: balanceData,
      strategyConfig: strategyConfigData,
      strategyParams: strategyParamsData,
      counts: {
        positions: positionsData.length,
        trades: tradesData.length,
        balanceSnapshots: balanceData.length
      }
    };
  }),

  // Export bot state only
  exportBotState: publicProcedure.query(async () => {
    const { getBotState } = await import('./db');
    const botState = await getBotState();
    
    return {
      exportTime: new Date().toISOString(),
      botState: botState || null,
      isEmpty: !botState
    };
  }),

  // Export recent trades
  exportTrades: publicProcedure
    .input(z.object({ limit: z.number().optional().default(100) }))
    .query(async ({ input }) => {
      const { getRecentTrades } = await import('./db');
      const trades = await getRecentTrades(input.limit);
      
      return {
        exportTime: new Date().toISOString(),
        trades,
        count: trades.length
      };
    }),
});
