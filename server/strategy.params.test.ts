import { describe, expect, it, beforeEach } from "vitest";
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

describe("strategy.params", () => {
  it("should get active strategy parameters", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.strategy.getActiveParams();

    // Should return the default params we inserted
    expect(result).toBeDefined();
    if (result) {
      expect(result.shortMaPeriod).toBe(5);
      expect(result.longMaPeriod).toBe(20);
      expect(result.timeframe).toBe("1h");
      expect(result.sensitivity).toBe("standard");
      expect(result.isActive).toBe(1);
    }
  });

  it("should create new strategy parameters", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.strategy.createParams({
      shortMaPeriod: 3,
      longMaPeriod: 15,
      timeframe: "15m",
      sensitivity: "loose",
      isActive: 0,
    });

    expect(result).toEqual({ success: true });
  });

  it("should simulate parameters and return signal counts", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.strategy.simulateParams({
      shortMaPeriod: 3,
      longMaPeriod: 15,
      timeframe: "15m",
      sensitivity: "loose",
      samplePeriod: "24h",
    });

    expect(result).toBeDefined();
    expect(result.signalCount).toBeGreaterThan(0);
    expect(result.longSignals).toBeGreaterThanOrEqual(0);
    expect(result.shortSignals).toBeGreaterThanOrEqual(0);
    expect(result.signalCount).toBe(result.longSignals + result.shortSignals);
    expect(result.samplePeriod).toBe("24h");
  });

  it("should validate parameter ranges", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    // Test short MA period too small
    await expect(
      caller.strategy.createParams({
        shortMaPeriod: 2, // Below minimum of 3
        longMaPeriod: 20,
        timeframe: "1h",
        sensitivity: "standard",
      })
    ).rejects.toThrow();

    // Test long MA period too large
    await expect(
      caller.strategy.createParams({
        shortMaPeriod: 5,
        longMaPeriod: 100, // Above maximum of 60
        timeframe: "1h",
        sensitivity: "standard",
      })
    ).rejects.toThrow();
  });

  it("should get all strategy parameters with limit", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.strategy.getAllParams({ limit: 5 });

    expect(Array.isArray(result)).toBe(true);
    expect(result.length).toBeLessThanOrEqual(5);
  });
});
