import { int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * 多币种配置表
 * 管理支持的交易对及其配置
 */
export const symbolConfigs = mysqlTable("symbol_configs", {
  id: int("id").autoincrement().primaryKey(),
  symbol: varchar("symbol", { length: 20 }).notNull().unique(), // 交易对，如 XBTUSDTM, ETHUSDTM
  displayName: varchar("display_name", { length: 50 }).notNull(), // 显示名称，如 BTC/USDT, ETH/USDT
  isActive: int("is_active").default(1).notNull(), // 是否启用 0=禁用, 1=启用
  initialCapital: varchar("initial_capital", { length: 20 }).default("10").notNull(), // 初始资金
  leverage: int("leverage").default(10).notNull(), // 杠杆倍数
  shortMaPeriod: int("short_ma_period").default(5).notNull(), // 短期均线周期
  longMaPeriod: int("long_ma_period").default(20).notNull(), // 长期均线周期
  timeframe: varchar("timeframe", { length: 10 }).default("1h").notNull(), // 时间周期
  sensitivity: mysqlEnum("sensitivity", ["loose", "standard", "strict"]).default("standard").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
});

/**
 * 多币种机器人状态表
 * 每个交易对独立的运行状态
 */
export const multiSymbolBotState = mysqlTable("multi_symbol_bot_state", {
  id: int("id").autoincrement().primaryKey(),
  symbol: varchar("symbol", { length: 20 }).notNull().unique(),
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

/**
 * 多币种持仓表
 * 每个交易对独立的持仓记录
 */
export const multiSymbolPositions = mysqlTable("multi_symbol_positions", {
  id: int("id").autoincrement().primaryKey(),
  symbol: varchar("symbol", { length: 20 }).notNull(),
  direction: mysqlEnum("direction", ["long", "short"]).notNull(),
  entryPrice: varchar("entry_price", { length: 20 }).notNull(),
  quantity: varchar("quantity", { length: 20 }).notNull(),
  margin: varchar("margin", { length: 20 }).notNull(),
  stopLossPct: varchar("stop_loss_pct", { length: 20 }).notNull(),
  takeProfitPct: varchar("take_profit_pct", { length: 20 }).notNull(),
  stage: varchar("stage", { length: 20 }).notNull(),
  entryTime: timestamp("entry_time").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
});

export type SymbolConfig = typeof symbolConfigs.$inferSelect;
export type InsertSymbolConfig = typeof symbolConfigs.$inferInsert;
export type MultiSymbolBotState = typeof multiSymbolBotState.$inferSelect;
export type MultiSymbolPosition = typeof multiSymbolPositions.$inferSelect;
