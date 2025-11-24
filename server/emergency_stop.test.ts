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
    role: "admin",
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

describe("Emergency Stop Functionality", () => {
  let caller: ReturnType<typeof appRouter.createCaller>;

  beforeEach(() => {
    const ctx = createTestContext();
    caller = appRouter.createCaller(ctx);
  });

  it("should activate emergency stop", async () => {
    const result = await caller.trading.emergencyStop();
    
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(result.message).toContain("Emergency stop activated");
  });

  it("should resume bot after emergency stop", async () => {
    // First activate emergency stop
    await caller.trading.emergencyStop();
    
    // Then resume
    const result = await caller.trading.resumeBot();
    
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(result.message).toContain("Bot resumed successfully");
  });

  it("should update bot state when emergency stop is activated", async () => {
    // Activate emergency stop
    await caller.trading.emergencyStop();
    
    // Check bot state
    const state = await caller.trading.getState();
    
    expect(state).toBeDefined();
    if (state) {
      expect(state.emergencyStopped).toBe(1);
      expect(state.isRunning).toBe(0);
    }
  });

  it("should update bot state when bot is resumed", async () => {
    // Activate emergency stop first
    await caller.trading.emergencyStop();
    
    // Then resume
    await caller.trading.resumeBot();
    
    // Check bot state
    const state = await caller.trading.getState();
    
    expect(state).toBeDefined();
    if (state) {
      expect(state.emergencyStopped).toBe(0);
      expect(state.isRunning).toBe(1);
    }
  });
});
