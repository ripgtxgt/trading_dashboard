/**
 * 策略回测模块
 * 基于历史K线数据模拟MA5/MA20交叉策略
 */

import type { Kline } from "./exchanges";

export interface BacktestResult {
  symbol: string;
  period: string;
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  winRate: number;              // 胜率 (%)
  totalReturn: number;          // 总收益率 (%)
  maxDrawdown: number;          // 最大回撤 (%)
  profitFactor: number;         // 盈亏比
  avgWin: number;               // 平均盈利 (%)
  avgLoss: number;              // 平均亏损 (%)
  sharpeRatio: number;          // 夏普比率
  trades: Trade[];
}

export interface Trade {
  entryTime: number;
  entryPrice: number;
  exitTime: number;
  exitPrice: number;
  direction: "long" | "short";
  profit: number;               // 收益 (%)
  holdingPeriod: number;        // 持仓时间 (小时)
}

export interface MarketEnvironment {
  trend: "bullish" | "bearish" | "sideways";
  volatility: "high" | "medium" | "low";
  performance: number;          // 该环境下的收益率 (%)
  tradeCount: number;
}

/**
 * 计算移动平均线
 */
function calculateMA(klines: Kline[], period: number): number[] {
  const ma: number[] = [];
  
  for (let i = 0; i < klines.length; i++) {
    if (i < period - 1) {
      ma.push(NaN);
      continue;
    }
    
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += klines[i - j].close;
    }
    
    ma.push(sum / period);
  }
  
  return ma;
}

/**
 * MA5/MA20交叉策略回测
 */
export function backtestMA520Strategy(
  symbol: string,
  klines: Kline[],
  leverage: number = 10
): BacktestResult {
  if (klines.length < 20) {
    throw new Error("Not enough data for backtest (minimum 20 candles required)");
  }
  
  // 计算MA5和MA20
  const ma5 = calculateMA(klines, 5);
  const ma20 = calculateMA(klines, 20);
  
  const trades: Trade[] = [];
  let position: "long" | "short" | null = null;
  let entryPrice = 0;
  let entryTime = 0;
  let entryIndex = 0;
  
  // 遍历K线，寻找交易信号
  for (let i = 20; i < klines.length; i++) {
    const prevMA5 = ma5[i - 1];
    const prevMA20 = ma20[i - 1];
    const currMA5 = ma5[i];
    const currMA20 = ma20[i];
    
    if (isNaN(prevMA5) || isNaN(prevMA20) || isNaN(currMA5) || isNaN(currMA20)) {
      continue;
    }
    
    // 金叉：MA5上穿MA20，做多
    if (prevMA5 <= prevMA20 && currMA5 > currMA20 && position !== "long") {
      // 如果有空头持仓，先平仓
      if (position === "short") {
        const exitPrice = klines[i].close;
        const profit = ((entryPrice - exitPrice) / entryPrice) * 100 * leverage;
        const holdingPeriod = (klines[i].timestamp - entryTime) / (1000 * 60 * 60);
        
        trades.push({
          entryTime,
          entryPrice,
          exitTime: klines[i].timestamp,
          exitPrice,
          direction: "short",
          profit,
          holdingPeriod,
        });
      }
      
      // 开多头
      position = "long";
      entryPrice = klines[i].close;
      entryTime = klines[i].timestamp;
      entryIndex = i;
    }
    // 死叉：MA5下穿MA20，做空
    else if (prevMA5 >= prevMA20 && currMA5 < currMA20 && position !== "short") {
      // 如果有多头持仓，先平仓
      if (position === "long") {
        const exitPrice = klines[i].close;
        const profit = ((exitPrice - entryPrice) / entryPrice) * 100 * leverage;
        const holdingPeriod = (klines[i].timestamp - entryTime) / (1000 * 60 * 60);
        
        trades.push({
          entryTime,
          entryPrice,
          exitTime: klines[i].timestamp,
          exitPrice,
          direction: "long",
          profit,
          holdingPeriod,
        });
      }
      
      // 开空头
      position = "short";
      entryPrice = klines[i].close;
      entryTime = klines[i].timestamp;
      entryIndex = i;
    }
  }
  
  // 如果最后还有持仓，按最后价格平仓
  if (position) {
    const lastKline = klines[klines.length - 1];
    const exitPrice = lastKline.close;
    const profit = position === "long"
      ? ((exitPrice - entryPrice) / entryPrice) * 100 * leverage
      : ((entryPrice - exitPrice) / entryPrice) * 100 * leverage;
    const holdingPeriod = (lastKline.timestamp - entryTime) / (1000 * 60 * 60);
    
    trades.push({
      entryTime,
      entryPrice,
      exitTime: lastKline.timestamp,
      exitPrice,
      direction: position,
      profit,
      holdingPeriod,
    });
  }
  
  // 计算统计指标
  const totalTrades = trades.length;
  const winningTrades = trades.filter(t => t.profit > 0).length;
  const losingTrades = trades.filter(t => t.profit < 0).length;
  const winRate = totalTrades > 0 ? (winningTrades / totalTrades) * 100 : 0;
  
  const totalReturn = trades.reduce((sum, t) => sum + t.profit, 0);
  
  const wins = trades.filter(t => t.profit > 0);
  const losses = trades.filter(t => t.profit < 0);
  const avgWin = wins.length > 0 ? wins.reduce((sum, t) => sum + t.profit, 0) / wins.length : 0;
  const avgLoss = losses.length > 0 ? losses.reduce((sum, t) => sum + Math.abs(t.profit), 0) / losses.length : 0;
  
  const totalWin = wins.reduce((sum, t) => sum + t.profit, 0);
  const totalLoss = Math.abs(losses.reduce((sum, t) => sum + t.profit, 0));
  const profitFactor = totalLoss > 0 ? totalWin / totalLoss : totalWin > 0 ? Infinity : 0;
  
  // 计算最大回撤
  let maxDrawdown = 0;
  let peak = 0;
  let cumReturn = 0;
  
  for (const trade of trades) {
    cumReturn += trade.profit;
    if (cumReturn > peak) {
      peak = cumReturn;
    }
    const drawdown = peak - cumReturn;
    if (drawdown > maxDrawdown) {
      maxDrawdown = drawdown;
    }
  }
  
  // 计算夏普比率（简化版）
  const returns = trades.map(t => t.profit);
  const avgReturn = returns.length > 0 ? returns.reduce((sum, r) => sum + r, 0) / returns.length : 0;
  const variance = returns.length > 0 
    ? returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length 
    : 0;
  const stdDev = Math.sqrt(variance);
  const sharpeRatio = stdDev > 0 ? avgReturn / stdDev : 0;
  
  const startDate = new Date(klines[0].timestamp).toISOString().split('T')[0];
  const endDate = new Date(klines[klines.length - 1].timestamp).toISOString().split('T')[0];
  
  return {
    symbol,
    period: `${startDate} to ${endDate}`,
    totalTrades,
    winningTrades,
    losingTrades,
    winRate,
    totalReturn,
    maxDrawdown,
    profitFactor,
    avgWin,
    avgLoss,
    sharpeRatio,
    trades,
  };
}

/**
 * 分析不同市场环境下的表现
 */
export function analyzeMarketEnvironments(
  klines: Kline[],
  trades: Trade[]
): MarketEnvironment[] {
  const environments: MarketEnvironment[] = [];
  
  // 将数据分成3段，分析每段的市场环境
  const segmentSize = Math.floor(klines.length / 3);
  
  for (let i = 0; i < 3; i++) {
    const start = i * segmentSize;
    const end = i === 2 ? klines.length : (i + 1) * segmentSize;
    const segment = klines.slice(start, end);
    
    if (segment.length === 0) continue;
    
    // 判断趋势
    const firstPrice = segment[0].close;
    const lastPrice = segment[segment.length - 1].close;
    const priceChange = ((lastPrice - firstPrice) / firstPrice) * 100;
    
    let trend: "bullish" | "bearish" | "sideways";
    if (priceChange > 5) trend = "bullish";
    else if (priceChange < -5) trend = "bearish";
    else trend = "sideways";
    
    // 判断波动率
    const returns = segment.slice(1).map((k, idx) => 
      ((k.close - segment[idx].close) / segment[idx].close) * 100
    );
    const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
    const stdDev = Math.sqrt(variance);
    
    let volatility: "high" | "medium" | "low";
    if (stdDev > 3) volatility = "high";
    else if (stdDev > 1.5) volatility = "medium";
    else volatility = "low";
    
    // 计算该时间段内的交易表现
    const segmentStartTime = segment[0].timestamp;
    const segmentEndTime = segment[segment.length - 1].timestamp;
    const segmentTrades = trades.filter(t => 
      t.entryTime >= segmentStartTime && t.exitTime <= segmentEndTime
    );
    
    const performance = segmentTrades.reduce((sum, t) => sum + t.profit, 0);
    
    environments.push({
      trend,
      volatility,
      performance,
      tradeCount: segmentTrades.length,
    });
  }
  
  return environments;
}

/**
 * 计算技术指标
 */
export function calculateTechnicalIndicators(klines: Kline[]): {
  ma5: number[];
  ma20: number[];
  rsi: number[];
  atr: number[];
} {
  const ma5 = calculateMA(klines, 5);
  const ma20 = calculateMA(klines, 20);
  
  // 计算RSI
  const rsi = calculateRSI(klines, 14);
  
  // 计算ATR
  const atr = calculateATR(klines, 14);
  
  return { ma5, ma20, rsi, atr };
}

/**
 * 计算RSI
 */
function calculateRSI(klines: Kline[], period: number = 14): number[] {
  const rsi: number[] = [];
  
  if (klines.length < period + 1) {
    return klines.map(() => NaN);
  }
  
  // 计算价格变化
  const changes: number[] = [];
  for (let i = 1; i < klines.length; i++) {
    changes.push(klines[i].close - klines[i - 1].close);
  }
  
  for (let i = 0; i < klines.length; i++) {
    if (i < period) {
      rsi.push(NaN);
      continue;
    }
    
    const recentChanges = changes.slice(i - period, i);
    const gains = recentChanges.filter(c => c > 0);
    const losses = recentChanges.filter(c => c < 0).map(c => Math.abs(c));
    
    const avgGain = gains.length > 0 ? gains.reduce((sum, g) => sum + g, 0) / period : 0;
    const avgLoss = losses.length > 0 ? losses.reduce((sum, l) => sum + l, 0) / period : 0;
    
    if (avgLoss === 0) {
      rsi.push(100);
    } else {
      const rs = avgGain / avgLoss;
      rsi.push(100 - (100 / (1 + rs)));
    }
  }
  
  return rsi;
}

/**
 * 计算ATR
 */
function calculateATR(klines: Kline[], period: number = 14): number[] {
  const atr: number[] = [];
  
  if (klines.length < period + 1) {
    return klines.map(() => NaN);
  }
  
  const trueRanges: number[] = [];
  
  for (let i = 1; i < klines.length; i++) {
    const high = klines[i].high;
    const low = klines[i].low;
    const prevClose = klines[i - 1].close;
    
    const tr = Math.max(
      high - low,
      Math.abs(high - prevClose),
      Math.abs(low - prevClose)
    );
    
    trueRanges.push(tr);
  }
  
  atr.push(NaN); // 第一个K线没有ATR
  
  for (let i = 0; i < trueRanges.length; i++) {
    if (i < period - 1) {
      atr.push(NaN);
      continue;
    }
    
    const recentTRs = trueRanges.slice(i - period + 1, i + 1);
    const avgTR = recentTRs.reduce((sum, tr) => sum + tr, 0) / period;
    atr.push(avgTR);
  }
  
  return atr;
}
