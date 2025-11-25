import { publicProcedure, router } from "./_core/trpc";
import Database from 'better-sqlite3';
import path from 'path';

// SQLite数据库路径
const DB_PATH = path.join(process.cwd(), 'scripts', 'trading_data.db');

// 获取数据库连接
function getDb() {
  try {
    const db = new Database(DB_PATH, { readonly: true });
    return db;
  } catch (error) {
    console.error('[Dashboard] Failed to connect to SQLite:', error);
    return null;
  }
}

export const dashboardRouter = router({
  // 获取机器人状态
  getBotState: publicProcedure.query(() => {
    const db = getDb();
    if (!db) {
      return {
        status: 'stopped',
        currentBalance: 0,
        initialBalance: 0,
        totalProfit: 0,
        profitRate: 0,
        currentStage: 'stage1',
        todayTrades: 0,
        totalTrades: 0,
        winRate: null,
        riskLevel: 'low',
        marketVolatility: 0,
        suggestedPosition: 100,
      };
    }

    try {
      const row = db.prepare('SELECT * FROM bot_state ORDER BY id DESC LIMIT 1').get() as any;
      db.close();

      if (!row) {
        return {
          status: 'stopped',
          currentBalance: 0,
          initialBalance: 0,
          totalProfit: 0,
          profitRate: 0,
          currentStage: 'stage1',
          todayTrades: 0,
          totalTrades: 0,
          winRate: null,
          riskLevel: 'low',
          marketVolatility: 0,
          suggestedPosition: 100,
        };
      }

      return {
        status: row.status,
        currentBalance: row.current_balance,
        initialBalance: row.initial_balance,
        totalProfit: row.total_profit,
        profitRate: row.profit_rate,
        currentStage: row.current_stage,
        todayTrades: row.today_trades,
        totalTrades: row.total_trades,
        winRate: row.win_rate,
        riskLevel: row.risk_level,
        marketVolatility: row.market_volatility,
        suggestedPosition: row.suggested_position,
      };
    } catch (error) {
      console.error('[Dashboard] Error fetching bot state:', error);
      db?.close();
      throw error;
    }
  }),

  // 获取当前持仓
  getPositions: publicProcedure.query(() => {
    const db = getDb();
    if (!db) return [];

    try {
      const rows = db.prepare('SELECT * FROM positions ORDER BY id DESC').all() as any[];
      db.close();

      return rows.map(row => ({
        id: row.id,
        timestamp: row.timestamp,
        symbol: row.symbol,
        side: row.side,
        size: row.size,
        entryPrice: row.entry_price,
        currentPrice: row.current_price,
        unrealizedPnl: row.unrealized_pnl,
        leverage: row.leverage,
        margin: row.margin,
        liquidationPrice: row.liquidation_price,
      }));
    } catch (error) {
      console.error('[Dashboard] Error fetching positions:', error);
      db?.close();
      return [];
    }
  }),

  // 获取交易历史
  getTrades: publicProcedure.query(() => {
    const db = getDb();
    if (!db) return [];

    try {
      const rows = db.prepare('SELECT * FROM trades ORDER BY id DESC LIMIT 100').all() as any[];
      db.close();

      return rows.map(row => ({
        id: row.id,
        timestamp: row.timestamp,
        symbol: row.symbol,
        side: row.side,
        size: row.size,
        entryPrice: row.entry_price,
        exitPrice: row.exit_price,
        pnl: row.pnl,
        pnlRate: row.pnl_rate,
        status: row.status,
        signalType: row.signal_type,
        stage: row.stage,
        reason: row.reason,
      }));
    } catch (error) {
      console.error('[Dashboard] Error fetching trades:', error);
      db?.close();
      return [];
    }
  }),

  // 获取余额快照（用于资金曲线图）
  getBalanceSnapshots: publicProcedure.query(() => {
    const db = getDb();
    if (!db) return [];

    try {
      // 获取最近24小时的数据
      const rows = db.prepare(`
        SELECT * FROM balance_snapshots 
        WHERE datetime(timestamp) >= datetime('now', '-24 hours')
        ORDER BY timestamp ASC
      `).all() as any[];
      db.close();

      return rows.map(row => ({
        timestamp: row.timestamp,
        balance: row.balance,
        equity: row.equity,
        unrealizedPnl: row.unrealized_pnl,
        marginUsed: row.margin_used,
        availableBalance: row.available_balance,
      }));
    } catch (error) {
      console.error('[Dashboard] Error fetching balance snapshots:', error);
      db?.close();
      return [];
    }
  }),

  // 获取K线数据
  getKlines: publicProcedure.query(() => {
    const db = getDb();
    if (!db) return [];

    try {
      // 获取最近100根K线
      const rows = db.prepare(`
        SELECT * FROM klines 
        WHERE symbol = 'XBTUSDTM' AND interval = '1h'
        ORDER BY timestamp DESC 
        LIMIT 100
      `).all() as any[];
      db.close();

      return rows.reverse().map(row => ({
        timestamp: row.timestamp,
        symbol: row.symbol,
        interval: row.interval,
        open: row.open,
        high: row.high,
        low: row.low,
        close: row.close,
        volume: row.volume,
        ma5: row.ma5,
        ma20: row.ma20,
      }));
    } catch (error) {
      console.error('[Dashboard] Error fetching klines:', error);
      db?.close();
      return [];
    }
  }),

  // 获取交易信号
  getSignals: publicProcedure.query(() => {
    const db = getDb();
    if (!db) return [];

    try {
      // 获取最近50个信号
      const rows = db.prepare(`
        SELECT * FROM signals 
        ORDER BY id DESC 
        LIMIT 50
      `).all() as any[];
      db.close();

      return rows.map(row => ({
        id: row.id,
        timestamp: row.timestamp,
        symbol: row.symbol,
        signalType: row.signal_type,
        price: row.price,
        ma5: row.ma5,
        ma20: row.ma20,
        reason: row.reason,
        executed: Boolean(row.executed),
      }));
    } catch (error) {
      console.error('[Dashboard] Error fetching signals:', error);
      db?.close();
      return [];
    }
  }),

  // 获取统计数据
  getStatistics: publicProcedure.query(() => {
    const db = getDb();
    if (!db) {
      return {
        totalTrades: 0,
        winningTrades: 0,
        losingTrades: 0,
        winRate: 0,
        totalProfit: 0,
        totalLoss: 0,
        netProfit: 0,
        averageProfit: 0,
        averageLoss: 0,
        profitFactor: 0,
        maxDrawdown: 0,
        maxConsecutiveWins: 0,
        maxConsecutiveLosses: 0,
      };
    }

    try {
      const stats = db.prepare(`
        SELECT 
          COUNT(*) as total_trades,
          SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
          SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
          SUM(CASE WHEN pnl > 0 THEN pnl ELSE 0 END) as total_profit,
          SUM(CASE WHEN pnl < 0 THEN pnl ELSE 0 END) as total_loss,
          SUM(pnl) as net_profit,
          AVG(CASE WHEN pnl > 0 THEN pnl ELSE NULL END) as avg_profit,
          AVG(CASE WHEN pnl < 0 THEN pnl ELSE NULL END) as avg_loss
        FROM trades 
        WHERE status = 'closed' AND pnl IS NOT NULL
      `).get() as any;
      
      db.close();

      const totalTrades = stats.total_trades || 0;
      const winningTrades = stats.winning_trades || 0;
      const losingTrades = stats.losing_trades || 0;
      const totalProfit = stats.total_profit || 0;
      const totalLoss = Math.abs(stats.total_loss || 0);
      const netProfit = stats.net_profit || 0;
      const avgProfit = stats.avg_profit || 0;
      const avgLoss = Math.abs(stats.avg_loss || 0);

      return {
        totalTrades,
        winningTrades,
        losingTrades,
        winRate: totalTrades > 0 ? (winningTrades / totalTrades) * 100 : 0,
        totalProfit,
        totalLoss,
        netProfit,
        averageProfit: avgProfit,
        averageLoss: avgLoss,
        profitFactor: totalLoss > 0 ? totalProfit / totalLoss : 0,
        maxDrawdown: 0, // TODO: 计算最大回撤
        maxConsecutiveWins: 0, // TODO: 计算最大连胜
        maxConsecutiveLosses: 0, // TODO: 计算最大连亏
      };
    } catch (error) {
      console.error('[Dashboard] Error fetching statistics:', error);
      db?.close();
      throw error;
    }
  }),
});
