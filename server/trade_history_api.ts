/**
 * 交易历史API
 * 提供交易记录的查询、筛选、排序和导出功能
 */

import { router, publicProcedure } from "./_core/trpc";
import { z } from "zod";
import { desc, asc, and, eq, gte, lte, sql } from "drizzle-orm";
import { trades } from "../drizzle/schema";
import { getDb } from "./db";

export const tradeHistoryRouter = router({
  /**
   * 获取交易历史列表
   * 支持分页、筛选、排序
   */
  list: publicProcedure
    .input(
      z.object({
        page: z.number().min(1).default(1),
        pageSize: z.number().min(1).max(100).default(20),
        symbol: z.string().optional(), // 筛选币种
        direction: z.enum(["long", "short", "all"]).default("all"), // 筛选方向
        startDate: z.string().optional(), // 开始日期 ISO string
        endDate: z.string().optional(), // 结束日期 ISO string
        sortBy: z.enum(["exitTime", "pnl", "pnlPct"]).default("exitTime"), // 排序字段
        sortOrder: z.enum(["asc", "desc"]).default("desc"), // 排序方向
      })
    )
    .query(async ({ input }) => {
      const db = await getDb();
      if (!db) {
        return {
          trades: [],
          total: 0,
          page: input.page,
          pageSize: input.pageSize,
          totalPages: 0,
        };
      }

      // 构建筛选条件
      const conditions = [];

      if (input.symbol) {
        conditions.push(eq(trades.symbol, input.symbol));
      }

      if (input.direction !== "all") {
        conditions.push(eq(trades.direction, input.direction));
      }

      if (input.startDate) {
        conditions.push(gte(trades.exitTime, new Date(input.startDate)));
      }

      if (input.endDate) {
        conditions.push(lte(trades.exitTime, new Date(input.endDate)));
      }

      const whereClause = conditions.length > 0 ? and(...conditions) : undefined;

      // 获取总数
      const countResult = await db
        .select({ count: sql<number>`count(*)` })
        .from(trades)
        .where(whereClause);

      const total = Number(countResult[0]?.count || 0);

      // 构建排序
      const orderByClause =
        input.sortOrder === "desc"
          ? desc(trades[input.sortBy])
          : asc(trades[input.sortBy]);

      // 查询数据
      const offset = (input.page - 1) * input.pageSize;
      const tradesList = await db
        .select()
        .from(trades)
        .where(whereClause)
        .orderBy(orderByClause)
        .limit(input.pageSize)
        .offset(offset);

      return {
        trades: tradesList,
        total,
        page: input.page,
        pageSize: input.pageSize,
        totalPages: Math.ceil(total / input.pageSize),
      };
    }),

  /**
   * 获取交易统计
   */
  stats: publicProcedure
    .input(
      z.object({
        symbol: z.string().optional(),
        startDate: z.string().optional(),
        endDate: z.string().optional(),
      })
    )
    .query(async ({ input }) => {
      const db = await getDb();
      if (!db) {
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
        };
      }

      // 构建筛选条件
      const conditions = [];

      if (input.symbol) {
        conditions.push(eq(trades.symbol, input.symbol));
      }

      if (input.startDate) {
        conditions.push(gte(trades.exitTime, new Date(input.startDate)));
      }

      if (input.endDate) {
        conditions.push(lte(trades.exitTime, new Date(input.endDate)));
      }

      const whereClause = conditions.length > 0 ? and(...conditions) : undefined;

      // 查询所有交易
      const allTrades = await db.select().from(trades).where(whereClause);

      if (allTrades.length === 0) {
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
        };
      }

      // 计算统计数据
      const winTrades = allTrades.filter((t) => parseFloat(t.pnl) > 0);
      const lossTrades = allTrades.filter((t) => parseFloat(t.pnl) <= 0);

      const totalPnl = allTrades.reduce((sum, t) => sum + parseFloat(t.pnl), 0);
      const totalFee = allTrades.reduce((sum, t) => sum + parseFloat(t.fee), 0);

      const avgPnl = totalPnl / allTrades.length;
      const avgWin =
        winTrades.length > 0
          ? winTrades.reduce((sum, t) => sum + parseFloat(t.pnl), 0) /
            winTrades.length
          : 0;
      const avgLoss =
        lossTrades.length > 0
          ? lossTrades.reduce((sum, t) => sum + parseFloat(t.pnl), 0) /
            lossTrades.length
          : 0;

      const maxWin =
        winTrades.length > 0
          ? Math.max(...winTrades.map((t) => parseFloat(t.pnl)))
          : 0;
      const maxLoss =
        lossTrades.length > 0
          ? Math.min(...lossTrades.map((t) => parseFloat(t.pnl)))
          : 0;

      const winRate =
        allTrades.length > 0
          ? ((winTrades.length / allTrades.length) * 100).toFixed(2)
          : "0";

      return {
        totalTrades: allTrades.length,
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
      };
    }),

  /**
   * 导出交易历史为CSV
   */
  exportCsv: publicProcedure
    .input(
      z.object({
        symbol: z.string().optional(),
        direction: z.enum(["long", "short", "all"]).default("all"),
        startDate: z.string().optional(),
        endDate: z.string().optional(),
      })
    )
    .query(async ({ input }) => {
      const db = await getDb();
      if (!db) {
        return { csv: "" };
      }

      // 构建筛选条件
      const conditions = [];

      if (input.symbol) {
        conditions.push(eq(trades.symbol, input.symbol));
      }

      if (input.direction !== "all") {
        conditions.push(eq(trades.direction, input.direction));
      }

      if (input.startDate) {
        conditions.push(gte(trades.exitTime, new Date(input.startDate)));
      }

      if (input.endDate) {
        conditions.push(lte(trades.exitTime, new Date(input.endDate)));
      }

      const whereClause = conditions.length > 0 ? and(...conditions) : undefined;

      // 查询数据
      const tradesList = await db
        .select()
        .from(trades)
        .where(whereClause)
        .orderBy(desc(trades.exitTime));

      // 生成CSV
      const headers = [
        "ID",
        "交易对",
        "方向",
        "开仓价",
        "平仓价",
        "数量",
        "保证金",
        "盈亏",
        "盈亏%",
        "手续费",
        "原因",
        "阶段",
        "开仓时间",
        "平仓时间",
      ];

      const rows = tradesList.map((t) => [
        t.id,
        t.symbol,
        t.direction === "long" ? "做多" : "做空",
        t.entryPrice,
        t.exitPrice,
        t.quantity,
        t.margin,
        t.pnl,
        t.pnlPct,
        t.fee,
        t.reason,
        t.stage,
        t.entryTime.toISOString(),
        t.exitTime.toISOString(),
      ]);

      const csv = [headers, ...rows].map((row) => row.join(",")).join("\n");

      return { csv };
    }),

  /**
   * 获取可用的交易对列表
   */
  symbols: publicProcedure.query(async () => {
    const db = await getDb();
    if (!db) {
      return { symbols: [] };
    }

    const result = await db
      .select({ symbol: trades.symbol })
      .from(trades)
      .groupBy(trades.symbol);

    return {
      symbols: result.map((r) => r.symbol),
    };
  }),
});
