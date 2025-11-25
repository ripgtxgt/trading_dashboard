import { and, desc, eq, sql } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import Database from 'better-sqlite3';
import path from 'path';
import { backtestHistory, balanceSnapshots, BotState, botState, InsertUser, paramSimulations, positions, strategyConfig, StrategyConfig, strategyParams, StrategyParams, trades, users } from "../drizzle/schema";
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

// SQLite database for trading bot data
const SQLITE_DB_PATH = path.join(process.cwd(), 'scripts', 'trading_data.db');

function getSqliteDb() {
  try {
    return new Database(SQLITE_DB_PATH, { readonly: true });
  } catch (error) {
    console.error('[SQLite] Failed to connect:', error);
    return null;
  }
}

// Trading bot queries (read from SQLite)
export async function getBotState() {
  const db = getSqliteDb();
  if (!db) return null;
  
  try {
    const row = db.prepare('SELECT * FROM bot_state ORDER BY id DESC LIMIT 1').get() as any;
    db.close();
    
    if (!row) return null;
    
    return {
      id: row.id,
      isRunning: row.status === 'running' ? 1 : 0,
      capital: row.current_balance.toString(),
      initialCapital: row.initial_balance.toString(),
      currentStage: row.current_stage,
      dailyTrades: row.today_trades,
      dailyPnl: row.total_profit.toString(),
      totalTrades: row.total_trades,
      emergencyStopped: row.status === 'stopped' ? 1 : 0,
      createdAt: new Date(row.timestamp),
      updatedAt: new Date(row.timestamp),
    };
  } catch (error) {
    console.error('[SQLite] Error reading bot_state:', error);
    db?.close();
    return null;
  }
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
  const db = getSqliteDb();
  if (!db) return [];
  
  try {
    const rows = db.prepare('SELECT * FROM trades ORDER BY id DESC LIMIT ?').all(limit) as any[];
    db.close();
    
    return rows.map(row => ({
      id: row.id,
      symbol: row.symbol || 'XBTUSDTM',
      direction: row.side,
      entryPrice: row.entry_price.toString(),
      exitPrice: row.exit_price.toString(),
      quantity: row.size.toString(),
      margin: '0',
      pnl: row.pnl.toString(),
      pnlPct: row.pnl_rate.toString(),
      fee: '0',
      reason: row.reason || '',
      stage: row.stage || 'stage1',
      entryTime: new Date(row.timestamp),
      exitTime: new Date(row.timestamp),
      createdAt: new Date(row.timestamp),
    }));
  } catch (error) {
    console.error('[SQLite] Error reading trades:', error);
    db?.close();
    return [];
  }
}

export async function addTrade(trade: Omit<typeof trades.$inferInsert, "id" | "createdAt">) {
  const db = await getDb();
  if (!db) return;
  await db.insert(trades).values(trade);
}

export async function getCurrentPosition() {
  const db = getSqliteDb();
  if (!db) return null;
  
  try {
    const row = db.prepare('SELECT * FROM positions ORDER BY id DESC LIMIT 1').get() as any;
    db.close();
    
    if (!row) return null;
    
    return {
      id: row.id,
      symbol: row.symbol || 'XBTUSDTM',
      direction: row.side,
      entryPrice: row.entry_price.toString(),
      quantity: row.size.toString(),
      margin: row.margin.toString(),
      stopLossPct: '2',
      takeProfitPct: '3',
      stage: 'stage1',
      entryTime: new Date(row.timestamp),
      createdAt: new Date(row.timestamp),
      updatedAt: new Date(row.timestamp),
    };
  } catch (error) {
    console.error('[SQLite] Error reading position:', error);
    db?.close();
    return null;
  }
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

// Strategy parameters queries
export async function getActiveStrategyParams() {
  const db = await getDb();
  if (!db) return null;
  const result = await db.select().from(strategyParams).where(eq(strategyParams.isActive, 1)).limit(1);
  return result.length > 0 ? result[0] : null;
}

export async function getAllStrategyParams(limit: number = 10) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(strategyParams).orderBy(desc(strategyParams.createdAt)).limit(limit);
}

export async function createStrategyParams(params: Omit<typeof strategyParams.$inferInsert, "id" | "createdAt">) {
  const db = await getDb();
  if (!db) return null;
  const result = await db.insert(strategyParams).values(params);
  return result;
}

export async function applyStrategyParams(paramId: number) {
  const db = await getDb();
  if (!db) return;
  
  // Deactivate all params
  await db.update(strategyParams).set({ isActive: 0 });
  
  // Activate the selected param
  await db.update(strategyParams)
    .set({ isActive: 1, appliedAt: new Date() })
    .where(eq(strategyParams.id, paramId));
}

export async function saveParamSimulation(simulation: Omit<typeof paramSimulations.$inferInsert, "id" | "createdAt">) {
  const db = await getDb();
  if (!db) return;
  await db.insert(paramSimulations).values(simulation);
}

export async function getParamSimulation(paramId: number) {
  const db = await getDb();
  if (!db) return null;
  const result = await db.select().from(paramSimulations)
    .where(eq(paramSimulations.paramId, paramId))
    .orderBy(desc(paramSimulations.createdAt))
    .limit(1);
  return result.length > 0 ? result[0] : null;
}

// Backtest history queries
export async function saveBacktestResult(result: Omit<typeof backtestHistory.$inferInsert, "id" | "createdAt">) {
  const db = await getDb();
  if (!db) return null;
  const insertResult = await db.insert(backtestHistory).values(result);
  return insertResult;
}

export async function getBacktestHistory(limit: number = 50) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(backtestHistory).orderBy(desc(backtestHistory.createdAt)).limit(limit);
}

export async function getBacktestByParams(shortMa: number, longMa: number, timeframe: string) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(backtestHistory)
    .where(
      and(
        eq(backtestHistory.shortMaPeriod, shortMa),
        eq(backtestHistory.longMaPeriod, longMa),
        eq(backtestHistory.timeframe, timeframe)
      )
    )
    .orderBy(desc(backtestHistory.createdAt))
    .limit(10);
}

// Balance snapshots queries
export async function getBalanceSnapshots(limit: number = 100) {
  const db = getSqliteDb();
  if (!db) return [];
  
  try {
    const rows = db.prepare('SELECT * FROM balance_snapshots ORDER BY id DESC LIMIT ?').all(limit) as any[];
    db.close();
    
    return rows.map(row => ({
      id: row.id,
      capital: row.balance.toString(),
      timestamp: new Date(row.timestamp),
    }));
  } catch (error) {
    console.error('[SQLite] Error reading balance_snapshots:', error);
    db?.close();
    return [];
  }
}

// Strategy config queries
export async function getStrategyConfig() {
  const db = await getDb();
  if (!db) return null;
  const result = await db.select().from(strategyConfig).limit(1);
  return result.length > 0 ? result[0] : null;
}

export async function updateStrategyConfig(config: Partial<StrategyConfig>) {
  const db = await getDb();
  if (!db) return null;
  
  const existing = await getStrategyConfig();
  
  if (existing) {
    // Update existing config
    await db.update(strategyConfig)
      .set(config)
      .where(eq(strategyConfig.id, existing.id));
  } else {
    // Insert new config
    await db.insert(strategyConfig).values(config as any);
  }
  
  return await getStrategyConfig();
}
