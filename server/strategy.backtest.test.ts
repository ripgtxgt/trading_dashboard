import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

type AuthenticatedUser = NonNullable<TrpcContext["user"]>;

function createTestContext(): TrpcContext {
  const user: AuthenticatedUser = {
    id: 1,
    openId: "test-user",
    email: "test@example.com",
    name: "Test User",
    loginMethod: "manus",
    role: "user",
    createdAt: new Date(),
    updatedAt: new Date(),
    lastSignedIn: new Date(),
  };

  const ctx: TrpcContext = {
    user,
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      clearCookie: () => {},
    } as TrpcContext["res"],
  };

  return ctx;
}

describe("strategy.backtest", () => {
  it("should run backtest and return performance metrics", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.strategy.backtestParams({
      shortMaPeriod: 5,
      longMaPeriod: 20,
      timeframe: "1h",
      sensitivity: "standard",
    });

    // Should return backtest results
    expect(result).toBeDefined();
    expect(result.totalTrades).toBeGreaterThanOrEqual(0);
    expect(result.winRate).toBeGreaterThanOrEqual(0);
    expect(result.winRate).toBeLessThanOrEqual(100);
    expect(typeof result.totalPnlPct).toBe("number");
    expect(typeof result.sharpeRatio).toBe("number");
    expect(typeof result.maxDrawdown).toBe("number");
  }, 60000); // 60s timeout for backtest

  it("should optimize parameters and return recommendations", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.strategy.optimizeParams({
      timeframe: "1h",
      optimizationTarget: "composite",
    });

    // Should return optimization results
    expect(result).toBeDefined();
    expect(result.recommended).toBeDefined();
    expect(result.recommended.shortMaPeriod).toBeGreaterThanOrEqual(3);
    expect(result.recommended.shortMaPeriod).toBeLessThanOrEqual(20);
    expect(result.recommended.longMaPeriod).toBeGreaterThanOrEqual(10);
    expect(result.recommended.longMaPeriod).toBeLessThanOrEqual(60);
    expect(["loose", "standard", "strict"]).toContain(result.recommended.sensitivity);
    
    // Should have performance metrics
    expect(result.performance).toBeDefined();
    expect(typeof result.performance.winRate).toBe("number");
    expect(typeof result.performance.totalPnlPct).toBe("number");
  }, 120000); // 120s timeout for optimization

  it("should simulate parameters with real data", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.strategy.simulateParams({
      shortMaPeriod: 5,
      longMaPeriod: 20,
      timeframe: "1h",
      sensitivity: "standard",
      samplePeriod: "24h",
    });

    // Should return simulation results
    expect(result).toBeDefined();
    expect(result.signalCount).toBeGreaterThanOrEqual(0);
    expect(result.longSignals).toBeGreaterThanOrEqual(0);
    expect(result.shortSignals).toBeGreaterThanOrEqual(0);
    expect(result.signalCount).toBe(result.longSignals + result.shortSignals);
  }, 30000);
});
