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

  return {
    user,
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      clearCookie: () => {},
    } as TrpcContext["res"],
  };
}

describe("v35.0 New Features", () => {
  describe("Balance Snapshots API", () => {
    it("should fetch balance snapshots with default limit", async () => {
      const ctx = createTestContext();
      const caller = appRouter.createCaller(ctx);

      const snapshots = await caller.trading.getBalanceSnapshots({});

      expect(Array.isArray(snapshots)).toBe(true);
      // Should return array (empty or with data)
    });

    it("should fetch balance snapshots with custom limit", async () => {
      const ctx = createTestContext();
      const caller = appRouter.createCaller(ctx);

      const snapshots = await caller.trading.getBalanceSnapshots({ limit: 50 });

      expect(Array.isArray(snapshots)).toBe(true);
      expect(snapshots.length).toBeLessThanOrEqual(50);
    });
  });

  describe("Emergency Stop & Resume", () => {
    it("should activate emergency stop", async () => {
      const ctx = createTestContext();
      const caller = appRouter.createCaller(ctx);

      const result = await caller.trading.emergencyStop();

      expect(result.success).toBe(true);
      expect(result.message).toBe('Emergency stop activated');
    });

    it("should resume bot after emergency stop", async () => {
      const ctx = createTestContext();
      const caller = appRouter.createCaller(ctx);

      // First stop
      await caller.trading.emergencyStop();

      // Then resume
      const result = await caller.trading.resumeBot();

      expect(result.success).toBe(true);
      expect(result.message).toBe('Bot resumed successfully');
    });
  });

  describe("Bot State Management", () => {
    it("should get current bot state", async () => {
      const ctx = createTestContext();
      const caller = appRouter.createCaller(ctx);

      const state = await caller.trading.getState();

      // Should return bot state or null
      if (state) {
        expect(state).toHaveProperty('isRunning');
        expect(state).toHaveProperty('emergencyStopped');
      }
    });

    it("should update bot state", async () => {
      const ctx = createTestContext();
      const caller = appRouter.createCaller(ctx);

      const result = await caller.trading.updateState({
        isRunning: 1,
        emergencyStopped: 0,
      });

      expect(result.success).toBe(true);
    });
  });
});
