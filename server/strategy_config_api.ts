import { router, publicProcedure } from "./_core/trpc";
import { z } from "zod";
import { getDb } from "./db";
import { strategyConfig } from "../drizzle/schema";
import { eq } from "drizzle-orm";

/**
 * 策略配置API
 * 支持在线调整策略参数并实时同步到Python交易脚本
 */
export const strategyConfigRouter = router({
  /**
   * 获取当前策略配置
   */
  getConfig: publicProcedure.query(async () => {
    const db = await getDb();
    if (!db) {
      throw new Error("Database not available");
    }

    const configs = await db.select().from(strategyConfig).limit(1);
    
    if (configs.length === 0) {
      // 如果没有配置，创建默认配置
      await db.insert(strategyConfig).values({
        symbol: "XBTUSDTM",
        rollMultiplier: "2.0",
        takeProfitPct: "5.0",
        stopLossPct: "2.0",
        maxDailyLoss: "10.0",
        maxDrawdown: "20.0",
        consecutiveLossLimit: 3,
        leverage: 10,
        positionSize: "0.01",
        isActive: "true" as "true" | "false",
      });
      
      const newConfigs = await db.select().from(strategyConfig).limit(1);
      return newConfigs[0];
    }
    
    return configs[0];
  }),

  /**
   * 更新策略配置
   */
  updateConfig: publicProcedure
    .input(
      z.object({
        symbol: z.string().optional(),
        rollMultiplier: z.string().optional(),
        takeProfitPct: z.string().optional(),
        stopLossPct: z.string().optional(),
        maxDailyLoss: z.string().optional(),
        maxDrawdown: z.string().optional(),
        consecutiveLossLimit: z.number().optional(),
        leverage: z.number().optional(),
        positionSize: z.string().optional(),
        isActive: z.enum(["true", "false"]).optional(),
      })
    )
    .mutation(async ({ input }) => {
      const db = await getDb();
      if (!db) {
        throw new Error("Database not available");
      }

      // 获取现有配置
      const existing = await db.select().from(strategyConfig).limit(1);
      
      if (existing.length === 0) {
        // 如果没有配置，创建新的
        await db.insert(strategyConfig).values({
          symbol: input.symbol || "XBTUSDTM",
          rollMultiplier: input.rollMultiplier || "2.0",
          takeProfitPct: input.takeProfitPct || "5.0",
          stopLossPct: input.stopLossPct || "2.0",
          maxDailyLoss: input.maxDailyLoss || "10.0",
          maxDrawdown: input.maxDrawdown || "20.0",
          consecutiveLossLimit: input.consecutiveLossLimit || 3,
          leverage: input.leverage || 10,
          positionSize: input.positionSize || "0.01",
          isActive: (input.isActive as "true" | "false") || "true",
        });
      } else {
        // 更新现有配置
        await db
          .update(strategyConfig)
          .set({
            ...input,
            updatedAt: new Date(),
          })
          .where(eq(strategyConfig.id, existing[0].id));
      }

      // 返回更新后的配置
      const updated = await db.select().from(strategyConfig).limit(1);
      return updated[0];
    }),

  /**
   * 重置为默认配置
   */
  resetConfig: publicProcedure.mutation(async () => {
    const db = await getDb();
    if (!db) {
      throw new Error("Database not available");
    }

    const existing = await db.select().from(strategyConfig).limit(1);
    
    const defaultConfig = {
      symbol: "XBTUSDTM",
      rollMultiplier: "2.0",
      takeProfitPct: "5.0",
      stopLossPct: "2.0",
      maxDailyLoss: "10.0",
      maxDrawdown: "20.0",
      consecutiveLossLimit: 3,
      leverage: 10,
      positionSize: "0.01",
      isActive: "true" as "true" | "false",
    };

    if (existing.length === 0) {
      await db.insert(strategyConfig).values(defaultConfig);
    } else {
      await db
        .update(strategyConfig)
        .set({
          ...defaultConfig,
          updatedAt: new Date(),
        })
        .where(eq(strategyConfig.id, existing[0].id));
    }

    const updated = await db.select().from(strategyConfig).limit(1);
    return updated[0];
  }),
});
