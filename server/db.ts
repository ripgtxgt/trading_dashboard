import { desc, eq, sql } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { balanceSnapshots, BotState, botState, InsertUser, positions, trades, users } from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);

  return result.length > 0 ? result[0] : undefined;
}

// Trading bot queries
export async function getBotState() {
  const db = await getDb();
  if (!db) return null;
  const result = await db.select().from(botState).limit(1);
  return result.length > 0 ? result[0] : null;
}

export async function updateBotState(data: Partial<BotState>) {
  const db = await getDb();
  if (!db) return;
  
  const existing = await getBotState();
  if (existing) {
    await db.update(botState).set(data).where(eq(botState.id, existing.id));
  } else {
    await db.insert(botState).values({
      capital: data.capital || "0",
      initialCapital: data.initialCapital || "0",
      currentStage: data.currentStage || "stage1",
      ...data,
    });
  }
}

export async function getRecentTrades(limit: number = 50) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(trades).orderBy(desc(trades.exitTime)).limit(limit);
}

export async function addTrade(trade: Omit<typeof trades.$inferInsert, "id" | "createdAt">) {
  const db = await getDb();
  if (!db) return;
  await db.insert(trades).values(trade);
}

export async function getCurrentPosition() {
  const db = await getDb();
  if (!db) return null;
  const result = await db.select().from(positions).orderBy(desc(positions.createdAt)).limit(1);
  return result.length > 0 ? result[0] : null;
}

export async function updatePosition(data: Omit<typeof positions.$inferInsert, "id" | "createdAt" | "updatedAt">) {
  const db = await getDb();
  if (!db) return;
  
  // Clear old positions and insert new one
  await db.delete(positions);
  await db.insert(positions).values(data);
}

export async function clearPosition() {
  const db = await getDb();
  if (!db) return;
  await db.delete(positions);
}

export async function addBalanceSnapshot(capital: string) {
  const db = await getDb();
  if (!db) return;
  await db.insert(balanceSnapshots).values({ capital });
}

export async function getBalanceHistory(hours: number = 24) {
  const db = await getDb();
  if (!db) return [];
  const since = new Date(Date.now() - hours * 60 * 60 * 1000);
  return await db
    .select()
    .from(balanceSnapshots)
    .where(sql`${balanceSnapshots.timestamp} >= ${since}`)
    .orderBy(balanceSnapshots.timestamp);
}

export async function getTradeStats() {
  const db = await getDb();
  if (!db) return null;
  
  const allTrades = await db.select().from(trades);
  if (allTrades.length === 0) return null;
  
  const winningTrades = allTrades.filter(t => parseFloat(t.pnl) > 0);
  const totalPnl = allTrades.reduce((sum, t) => sum + parseFloat(t.pnl), 0);
  
  return {
    totalTrades: allTrades.length,
    winningTrades: winningTrades.length,
    winRate: (winningTrades.length / allTrades.length) * 100,
    totalPnl,
    avgPnl: totalPnl / allTrades.length,
  };
}
