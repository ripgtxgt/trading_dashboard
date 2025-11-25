import { router, publicProcedure } from "./_core/trpc";
import { z } from "zod";
import { getDb } from "./db";
import { strategyParams } from "../drizzle/schema";
import { eq, desc } from "drizzle-orm";

/**
 * Signal Strategy Parameters API
 * Manages MA5/MA20 parameters for trading signals
 */
export const signalParamsRouter = router({
  /**
   * Get current active signal parameters
   */
  getParams: publicProcedure.query(async () => {
    const db = await getDb();
    if (!db) {
      throw new Error("Database not available");
    }

    const params = await db
      .select()
      .from(strategyParams)
      .where(eq(strategyParams.isActive, 1))
      .orderBy(desc(strategyParams.createdAt))
      .limit(1);
    
    if (params.length === 0) {
      // Create default params if none exist
      await db.insert(strategyParams).values({
        shortMaPeriod: 5,
        longMaPeriod: 20,
        timeframe: "1h",
        sensitivity: "standard",
        isActive: 1,
      });
      
      const newParams = await db
        .select()
        .from(strategyParams)
        .where(eq(strategyParams.isActive, 1))
        .limit(1);
      return newParams[0];
    }
    
    return params[0];
  }),

  /**
   * Update signal parameters
   */
  updateParams: publicProcedure
    .input(
      z.object({
        shortMaPeriod: z.number().min(3).max(20),
        longMaPeriod: z.number().min(10).max(60),
        timeframe: z.enum(["15m", "30m", "1h", "2h", "4h"]),
      })
    )
    .mutation(async ({ input }) => {
      const db = await getDb();
      if (!db) {
        throw new Error("Database not available");
      }

      // Deactivate all existing params
      await db
        .update(strategyParams)
        .set({ isActive: 0 })
        .where(eq(strategyParams.isActive, 1));

      // Insert new params as active
      await db.insert(strategyParams).values({
        shortMaPeriod: input.shortMaPeriod,
        longMaPeriod: input.longMaPeriod,
        timeframe: input.timeframe,
        sensitivity: "standard",
        isActive: 1,
        appliedAt: new Date(),
      });

      // Return the new active params
      const updated = await db
        .select()
        .from(strategyParams)
        .where(eq(strategyParams.isActive, 1))
        .limit(1);
      
      return updated[0];
    }),

  /**
   * Reset to default parameters
   */
  resetParams: publicProcedure.mutation(async () => {
    const db = await getDb();
    if (!db) {
      throw new Error("Database not available");
    }

    // Deactivate all existing params
    await db
      .update(strategyParams)
      .set({ isActive: 0 })
      .where(eq(strategyParams.isActive, 1));

    // Insert default params
    await db.insert(strategyParams).values({
      shortMaPeriod: 5,
      longMaPeriod: 20,
      timeframe: "1h",
      sensitivity: "standard",
      isActive: 1,
      appliedAt: new Date(),
    });

    const updated = await db
      .select()
      .from(strategyParams)
      .where(eq(strategyParams.isActive, 1))
      .limit(1);
    
    return updated[0];
  }),
});
