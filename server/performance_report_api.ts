/**
 * 性能分析报告API
 * 生成日报、周报、月报
 */

import { router, publicProcedure } from "./_core/trpc";
import { z } from "zod";
import { gte, lte, and, sql } from "drizzle-orm";
import { trades } from "../drizzle/schema";
import { getDb } from "./db";

/**
 * 计算日期范围
 */
function getDateRange(period: "day" | "week" | "month") {
  const now = new Date();
  const start = new Date();

  switch (period) {
    case "day":
      start.setHours(0, 0, 0, 0);
      break;
    case "week":
      start.setDate(now.getDate() - 7);
      start.setHours(0, 0, 0, 0);
      break;
    case "month":
      start.setMonth(now.getMonth() - 1);
      start.setHours(0, 0, 0, 0);
      break;
  }

  return { start, end: now };
}

/**
 * 计算性能指标
 */
function calculateMetrics(tradesList: any[]) {
  if (tradesList.length === 0) {
    return {
      totalTrades: 0,
      winTrades: 0,
      lossTrades: 0,
      winRate: "0",
      totalPnl: "0",
      totalFee: "0",
      avgPnl: "0",
      avgWin: "0",
      avgLoss: "0",
      maxWin: "0",
      maxLoss: "0",
      profitFactor: "0",
      sharpeRatio: "0",
    };
  }

  const winTrades = tradesList.filter((t) => parseFloat(t.pnl) > 0);
  const lossTrades = tradesList.filter((t) => parseFloat(t.pnl) <= 0);

  const totalPnl = tradesList.reduce((sum, t) => sum + parseFloat(t.pnl), 0);
  const totalFee = tradesList.reduce((sum, t) => sum + parseFloat(t.fee), 0);

  const avgPnl = totalPnl / tradesList.length;
  const avgWin =
    winTrades.length > 0
      ? winTrades.reduce((sum, t) => sum + parseFloat(t.pnl), 0) / winTrades.length
      : 0;
  const avgLoss =
    lossTrades.length > 0
      ? lossTrades.reduce((sum, t) => sum + parseFloat(t.pnl), 0) / lossTrades.length
      : 0;

  const maxWin =
    winTrades.length > 0 ? Math.max(...winTrades.map((t) => parseFloat(t.pnl))) : 0;
  const maxLoss =
    lossTrades.length > 0 ? Math.min(...lossTrades.map((t) => parseFloat(t.pnl))) : 0;

  const winRate =
    tradesList.length > 0
      ? ((winTrades.length / tradesList.length) * 100).toFixed(2)
      : "0";

  // 盈亏比 (Profit Factor)
  const totalWin = winTrades.reduce((sum, t) => sum + parseFloat(t.pnl), 0);
  const totalLoss = Math.abs(lossTrades.reduce((sum, t) => sum + parseFloat(t.pnl), 0));
  const profitFactor = totalLoss > 0 ? (totalWin / totalLoss).toFixed(2) : "0";

  // 夏普比率 (简化版)
  const returns = tradesList.map((t) => parseFloat(t.pnlPct));
  const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
  const stdDev = Math.sqrt(
    returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length
  );
  const sharpeRatio = stdDev > 0 ? (avgReturn / stdDev).toFixed(2) : "0";

  return {
    totalTrades: tradesList.length,
    winTrades: winTrades.length,
    lossTrades: lossTrades.length,
    winRate,
    totalPnl: totalPnl.toFixed(2),
    totalFee: totalFee.toFixed(2),
    avgPnl: avgPnl.toFixed(2),
    avgWin: avgWin.toFixed(2),
    avgLoss: avgLoss.toFixed(2),
    maxWin: maxWin.toFixed(2),
    maxLoss: maxLoss.toFixed(2),
    profitFactor,
    sharpeRatio,
  };
}

export const performanceReportRouter = router({
  /**
   * 生成日报
   */
  dailyReport: publicProcedure
    .input(
      z.object({
        date: z.string().optional(), // ISO date string, 默认今天
      })
    )
    .query(async ({ input }) => {
      const db = await getDb();
      if (!db) {
        return {
          period: "day",
          startDate: new Date().toISOString(),
          endDate: new Date().toISOString(),
          metrics: calculateMetrics([]),
          trades: [],
        };
      }

      const targetDate = input.date ? new Date(input.date) : new Date();
      const start = new Date(targetDate);
      start.setHours(0, 0, 0, 0);
      const end = new Date(targetDate);
      end.setHours(23, 59, 59, 999);

      const tradesList = await db
        .select()
        .from(trades)
        .where(and(gte(trades.exitTime, start), lte(trades.exitTime, end)));

      const metrics = calculateMetrics(tradesList);

      return {
        period: "day" as const,
        startDate: start.toISOString(),
        endDate: end.toISOString(),
        metrics,
        trades: tradesList,
      };
    }),

  /**
   * 生成周报
   */
  weeklyReport: publicProcedure.query(async () => {
    const db = await getDb();
    if (!db) {
      return {
        period: "week",
        startDate: new Date().toISOString(),
        endDate: new Date().toISOString(),
        metrics: calculateMetrics([]),
        trades: [],
        dailyStats: [],
      };
    }

    const { start, end } = getDateRange("week");

    const tradesList = await db
      .select()
      .from(trades)
      .where(and(gte(trades.exitTime, start), lte(trades.exitTime, end)));

    const metrics = calculateMetrics(tradesList);

    // 按天分组统计
    const dailyStats: any[] = [];
    for (let i = 0; i < 7; i++) {
      const dayStart = new Date(start);
      dayStart.setDate(start.getDate() + i);
      dayStart.setHours(0, 0, 0, 0);
      const dayEnd = new Date(dayStart);
      dayEnd.setHours(23, 59, 59, 999);

      const dayTrades = tradesList.filter(
        (t) => new Date(t.exitTime) >= dayStart && new Date(t.exitTime) <= dayEnd
      );

      const dayPnl = dayTrades.reduce((sum, t) => sum + parseFloat(t.pnl), 0);

      dailyStats.push({
        date: dayStart.toISOString().split("T")[0],
        trades: dayTrades.length,
        pnl: dayPnl.toFixed(2),
      });
    }

    return {
      period: "week" as const,
      startDate: start.toISOString(),
      endDate: end.toISOString(),
      metrics,
      trades: tradesList,
      dailyStats,
    };
  }),

  /**
   * 生成月报
   */
  monthlyReport: publicProcedure.query(async () => {
    const db = await getDb();
    if (!db) {
      return {
        period: "month",
        startDate: new Date().toISOString(),
        endDate: new Date().toISOString(),
        metrics: calculateMetrics([]),
        trades: [],
        weeklyStats: [],
      };
    }

    const { start, end } = getDateRange("month");

    const tradesList = await db
      .select()
      .from(trades)
      .where(and(gte(trades.exitTime, start), lte(trades.exitTime, end)));

    const metrics = calculateMetrics(tradesList);

    // 按周分组统计
    const weeklyStats: any[] = [];
    const weekCount = Math.ceil((end.getTime() - start.getTime()) / (7 * 24 * 60 * 60 * 1000));

    for (let i = 0; i < weekCount; i++) {
      const weekStart = new Date(start);
      weekStart.setDate(start.getDate() + i * 7);
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekStart.getDate() + 6);
      weekEnd.setHours(23, 59, 59, 999);

      const weekTrades = tradesList.filter(
        (t) => new Date(t.exitTime) >= weekStart && new Date(t.exitTime) <= weekEnd
      );

      const weekPnl = weekTrades.reduce((sum, t) => sum + parseFloat(t.pnl), 0);

      weeklyStats.push({
        weekStart: weekStart.toISOString().split("T")[0],
        weekEnd: weekEnd.toISOString().split("T")[0],
        trades: weekTrades.length,
        pnl: weekPnl.toFixed(2),
      });
    }

    return {
      period: "month" as const,
      startDate: start.toISOString(),
      endDate: end.toISOString(),
      metrics,
      trades: tradesList,
      weeklyStats,
    };
  }),

  /**
   * 获取历史报告列表
   */
  reportHistory: publicProcedure
    .input(
      z.object({
        period: z.enum(["day", "week", "month"]),
        limit: z.number().min(1).max(30).default(10),
      })
    )
    .query(async ({ input }) => {
      const db = await getDb();
      if (!db) {
        return { reports: [] };
      }

      const reports: any[] = [];
      const now = new Date();

      for (let i = 0; i < input.limit; i++) {
        const targetDate = new Date(now);

        switch (input.period) {
          case "day":
            targetDate.setDate(now.getDate() - i);
            break;
          case "week":
            targetDate.setDate(now.getDate() - i * 7);
            break;
          case "month":
            targetDate.setMonth(now.getMonth() - i);
            break;
        }

        const start = new Date(targetDate);
        start.setHours(0, 0, 0, 0);
        const end = new Date(targetDate);
        end.setHours(23, 59, 59, 999);

        if (input.period === "week") {
          start.setDate(targetDate.getDate() - 7);
        } else if (input.period === "month") {
          start.setMonth(targetDate.getMonth() - 1);
        }

        const tradesList = await db
          .select()
          .from(trades)
          .where(and(gte(trades.exitTime, start), lte(trades.exitTime, end)));

        const metrics = calculateMetrics(tradesList);

        reports.push({
          period: input.period,
          startDate: start.toISOString(),
          endDate: end.toISOString(),
          metrics,
        });
      }

      return { reports };
    }),
});
