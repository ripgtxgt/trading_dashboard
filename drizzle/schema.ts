import { int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

// Trading bot state table
export const botState = mysqlTable("bot_state", {
  id: int("id").autoincrement().primaryKey(),
  isRunning: int("is_running").default(0).notNull(), // 0=stopped, 1=running
  capital: varchar("capital", { length: 20 }).notNull(),
  initialCapital: varchar("initial_capital", { length: 20 }).notNull(),
  currentStage: varchar("current_stage", { length: 20 }).notNull(),
  dailyTrades: int("daily_trades").default(0).notNull(),
  dailyPnl: varchar("daily_pnl", { length: 20 }).default("0").notNull(),
  totalTrades: int("total_trades").default(0).notNull(),
  emergencyStopped: int("emergency_stopped").default(0).notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
});

// Trading records table
export const trades = mysqlTable("trades", {
  id: int("id").autoincrement().primaryKey(),
  direction: mysqlEnum("direction", ["long", "short"]).notNull(),
  entryPrice: varchar("entry_price", { length: 20 }).notNull(),
  exitPrice: varchar("exit_price", { length: 20 }).notNull(),
  margin: varchar("margin", { length: 20 }).notNull(),
  pnl: varchar("pnl", { length: 20 }).notNull(),
  pnlPct: varchar("pnl_pct", { length: 20 }).notNull(),
  reason: varchar("reason", { length: 50 }).notNull(),
  stage: varchar("stage", { length: 20 }).notNull(),
  entryTime: timestamp("entry_time").notNull(),
  exitTime: timestamp("exit_time").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Position records table (current position)
export const positions = mysqlTable("positions", {
  id: int("id").autoincrement().primaryKey(),
  direction: mysqlEnum("direction", ["long", "short"]).notNull(),
  entryPrice: varchar("entry_price", { length: 20 }).notNull(),
  margin: varchar("margin", { length: 20 }).notNull(),
  stopLossPct: varchar("stop_loss_pct", { length: 20 }).notNull(),
  takeProfitPct: varchar("take_profit_pct", { length: 20 }).notNull(),
  stage: varchar("stage", { length: 20 }).notNull(),
  entryTime: timestamp("entry_time").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
});

// Account balance snapshots
export const balanceSnapshots = mysqlTable("balance_snapshots", {
  id: int("id").autoincrement().primaryKey(),
  capital: varchar("capital", { length: 20 }).notNull(),
  timestamp: timestamp("timestamp").defaultNow().notNull(),
});

export type BotState = typeof botState.$inferSelect;
export type Trade = typeof trades.$inferSelect;
export type Position = typeof positions.$inferSelect;
export type BalanceSnapshot = typeof balanceSnapshots.$inferSelect;