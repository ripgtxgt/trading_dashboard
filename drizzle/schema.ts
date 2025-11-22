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

// 策略配置表
export const strategyConfig = mysqlTable("strategy_config", {
  id: int("id").autoincrement().primaryKey(),
  symbol: varchar("symbol", { length: 20 }).notNull().default("XBTUSDTM"),
  // 滚仓参数
  rollMultiplier: varchar("rollMultiplier", { length: 20 }).notNull().default("2.0"),
  // 止盈止损
  takeProfitPct: varchar("takeProfitPct", { length: 20 }).notNull().default("5.0"),
  stopLossPct: varchar("stopLossPct", { length: 20 }).notNull().default("2.0"),
  // 风险控制
  maxDailyLoss: varchar("maxDailyLoss", { length: 20 }).notNull().default("10.0"),
  maxDrawdown: varchar("maxDrawdown", { length: 20 }).notNull().default("20.0"),
  consecutiveLossLimit: int("consecutiveLossLimit").notNull().default(3),
  // 交易参数
  leverage: int("leverage").notNull().default(10),
  positionSize: varchar("positionSize", { length: 20 }).notNull().default("0.01"),
  // 状态
  isActive: mysqlEnum("isActive", ["true", "false"]).default("true").notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type StrategyConfig = typeof strategyConfig.$inferSelect;
export type InsertStrategyConfig = typeof strategyConfig.$inferInsert;

// TODO: Add your tables here
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
  symbol: varchar("symbol", { length: 20 }).default("XBTUSDTM").notNull(), // 交易对
  direction: mysqlEnum("direction", ["long", "short"]).notNull(),
  entryPrice: varchar("entry_price", { length: 20 }).notNull(),
  exitPrice: varchar("exit_price", { length: 20 }).notNull(),
  quantity: varchar("quantity", { length: 20 }).notNull(), // 交易数量
  margin: varchar("margin", { length: 20 }).notNull(),
  pnl: varchar("pnl", { length: 20 }).notNull(),
  pnlPct: varchar("pnl_pct", { length: 20 }).notNull(),
  fee: varchar("fee", { length: 20 }).default("0").notNull(), // 手续费
  reason: varchar("reason", { length: 50 }).notNull(),
  stage: varchar("stage", { length: 20 }).notNull(),
  entryTime: timestamp("entry_time").notNull(),
  exitTime: timestamp("exit_time").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Position records table (current position)
export const positions = mysqlTable("positions", {
  id: int("id").autoincrement().primaryKey(),
  symbol: varchar("symbol", { length: 20 }).default("XBTUSDTM").notNull(), // 交易对
  direction: mysqlEnum("direction", ["long", "short"]).notNull(),
  entryPrice: varchar("entry_price", { length: 20 }).notNull(),
  quantity: varchar("quantity", { length: 20 }).notNull(), // 持仓数量
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

// Strategy parameters configuration
export const strategyParams = mysqlTable("strategy_params", {
  id: int("id").autoincrement().primaryKey(),
  shortMaPeriod: int("short_ma_period").default(5).notNull(),
  longMaPeriod: int("long_ma_period").default(20).notNull(),
  timeframe: varchar("timeframe", { length: 10 }).default("1h").notNull(),
  sensitivity: mysqlEnum("sensitivity", ["loose", "standard", "strict"]).default("standard").notNull(),
  isActive: int("is_active").default(1).notNull(), // 0=inactive, 1=active
  createdAt: timestamp("created_at").defaultNow().notNull(),
  appliedAt: timestamp("applied_at"),
});

// Parameter simulation results
export const paramSimulations = mysqlTable("param_simulations", {
  id: int("id").autoincrement().primaryKey(),
  paramId: int("param_id").notNull(),
  signalCount: int("signal_count").default(0).notNull(),
  longSignals: int("long_signals").default(0).notNull(),
  shortSignals: int("short_signals").default(0).notNull(),
  samplePeriod: varchar("sample_period", { length: 20 }).notNull(), // e.g., "24h", "7d"
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Backtest history table
export const backtestHistory = mysqlTable("backtest_history", {
  id: int("id").autoincrement().primaryKey(),
  shortMaPeriod: int("short_ma_period").notNull(),
  longMaPeriod: int("long_ma_period").notNull(),
  timeframe: varchar("timeframe", { length: 10 }).notNull(),
  sensitivity: varchar("sensitivity", { length: 20 }).notNull(),
  totalTrades: int("total_trades").default(0).notNull(),
  winTrades: int("win_trades").default(0).notNull(),
  winRate: varchar("win_rate", { length: 20 }).default("0").notNull(),
  totalPnl: varchar("total_pnl", { length: 20 }).default("0").notNull(),
  sharpeRatio: varchar("sharpe_ratio", { length: 20 }).default("0").notNull(),
  maxDrawdown: varchar("max_drawdown", { length: 20 }).default("0").notNull(),
  avgWin: varchar("avg_win", { length: 20 }).default("0").notNull(),
  avgLoss: varchar("avg_loss", { length: 20 }).default("0").notNull(),
  compositeScore: varchar("composite_score", { length: 20 }).default("0").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type BotState = typeof botState.$inferSelect;
export type Trade = typeof trades.$inferSelect;
export type Position = typeof positions.$inferSelect;
export type BalanceSnapshot = typeof balanceSnapshots.$inferSelect;
export type StrategyParams = typeof strategyParams.$inferSelect;
export type ParamSimulation = typeof paramSimulations.$inferSelect;
export type BacktestHistory = typeof backtestHistory.$inferSelect;

// Multi-symbol support tables
export const symbolConfigs = mysqlTable("symbol_configs", {
  id: int("id").autoincrement().primaryKey(),
  symbol: varchar("symbol", { length: 20 }).notNull().unique(),
  displayName: varchar("display_name", { length: 50 }).notNull(),
  isActive: int("is_active").default(1).notNull(),
  initialCapital: varchar("initial_capital", { length: 20 }).default("10").notNull(),
  leverage: int("leverage").default(10).notNull(),
  shortMaPeriod: int("short_ma_period").default(5).notNull(),
  longMaPeriod: int("long_ma_period").default(20).notNull(),
  timeframe: varchar("timeframe", { length: 10 }).default("1h").notNull(),
  sensitivity: mysqlEnum("sensitivity", ["loose", "standard", "strict"]).default("standard").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
});

export type SymbolConfig = typeof symbolConfigs.$inferSelect;
export type InsertSymbolConfig = typeof symbolConfigs.$inferInsert;