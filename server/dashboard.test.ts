import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

function createTestContext(): TrpcContext {
  return {
    user: null,
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {} as TrpcContext["res"],
  };
}

describe("Dashboard API", () => {
  it("should get bot state from SQLite", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.trading.getState();

    expect(result).toBeDefined();
    if (result) {
      expect(result).toHaveProperty("capital");
      expect(result).toHaveProperty("initialCapital");
      expect(result).toHaveProperty("currentStage");
      expect(result).toHaveProperty("totalTrades");
    }
  });

  it("should get current position from SQLite", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.trading.getPosition();

    expect(result).toBeDefined();
    if (result) {
      expect(result).toHaveProperty("symbol");
      expect(result).toHaveProperty("direction");
      expect(result).toHaveProperty("entryPrice");
      expect(result).toHaveProperty("quantity");
    }
  });

  it("should get recent trades from SQLite", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.trading.getTrades({ limit: 10 });

    expect(Array.isArray(result)).toBe(true);
    if (result.length > 0) {
      expect(result[0]).toHaveProperty("symbol");
      expect(result[0]).toHaveProperty("direction");
      expect(result[0]).toHaveProperty("pnl");
    }
  });

  it("should get balance snapshots from SQLite", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.trading.getBalanceSnapshots({ limit: 50 });

    expect(Array.isArray(result)).toBe(true);
    if (result.length > 0) {
      expect(result[0]).toHaveProperty("capital");
      expect(result[0]).toHaveProperty("timestamp");
    }
  });

  it("should get dashboard bot state", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.dashboard.getBotState();

    expect(result).toBeDefined();
    expect(result).toHaveProperty("status");
    expect(result).toHaveProperty("currentBalance");
    expect(result).toHaveProperty("totalProfit");
  });

  it("should get dashboard positions", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.dashboard.getPositions();

    expect(Array.isArray(result)).toBe(true);
    if (result.length > 0) {
      expect(result[0]).toHaveProperty("symbol");
      expect(result[0]).toHaveProperty("side");
      expect(result[0]).toHaveProperty("entryPrice");
    }
  });

  it("should get dashboard trades", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.dashboard.getTrades();

    expect(Array.isArray(result)).toBe(true);
    if (result.length > 0) {
      expect(result[0]).toHaveProperty("symbol");
      expect(result[0]).toHaveProperty("pnl");
      expect(result[0]).toHaveProperty("status");
    }
  });

  it("should get dashboard statistics", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.dashboard.getStatistics();

    expect(result).toBeDefined();
    expect(result).toHaveProperty("totalTrades");
    expect(result).toHaveProperty("winRate");
    expect(result).toHaveProperty("netProfit");
  });
});
