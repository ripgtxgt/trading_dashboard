/**
 * 币种选型API路由 - KuCoin合约版本
 * 提供合约币种列表、筛选、评分、回测等功能
 */

import { router, publicProcedure } from "./_core/trpc";
import { z } from "zod";
import { defaultExchange } from "./exchanges";
import type { Contract } from "./exchanges";
import * as KuCoin from "./exchanges/kucoin";
import { backtestMA520Strategy, analyzeMarketEnvironments, calculateTechnicalIndicators } from "./backtesting";
import { multiCoinMonitor } from "./multiCoinMonitor";

/**
 * 币种综合评分
 */
export interface CoinScore {
  symbol: string;
  baseAsset: string;
  totalScore: number;          // 总分 (0-100)
  liquidityScore: number;      // 流动性得分
  volatilityScore: number;     // 波动率得分
  trendScore: number;          // 趋势得分
  riskScore: number;           // 风险得分
  recommendation: "excellent" | "good" | "fair" | "poor"; // 推荐等级
  reasons: string[];           // 推荐理由
  
  // 基础数据
  price: number;
  priceChange24hPercent: number;
  volume24h: number;
  turnover24h: number;
  fundingRate: number;
  maxLeverage: number;
}

/**
 * 筛选条件
 */
const DEFAULT_FILTERS = {
  minVolume: 10_000_000,       // 最小交易量 $10M
  maxSpread: 0.1,              // 最大价差 0.1%
  minLeverage: 20,             // 最小杠杆 20x
};

export const coinSelectionRouter = router({
  /**
   * 获取所有USDT永续合约列表
   */
  getContracts: publicProcedure
    .input(z.object({
      minVolume: z.number().optional(),
      maxSpread: z.number().optional(),
      minLeverage: z.number().optional(),
    }))
    .query(async ({ input }) => {
      try {
        const contracts = await defaultExchange.getUSDTPerpetualContracts();
        
        // 应用筛选条件
        const minVolume = input.minVolume ?? DEFAULT_FILTERS.minVolume;
        const minLeverage = input.minLeverage ?? DEFAULT_FILTERS.minLeverage;
        
        const filtered = contracts.filter(c => 
          c.turnover24h >= minVolume &&
          c.maxLeverage >= minLeverage &&
          c.status === "Open"
        );
        
        return {
          success: true,
          count: filtered.length,
          contracts: filtered,
        };
      } catch (error) {
        console.error("[CoinSelection] Failed to fetch contracts:", error);
        return {
          success: false,
          count: 0,
          contracts: [],
          error: error instanceof Error ? error.message : "Unknown error",
        };
      }
    }),

  /**
   * 获取指定合约详细信息
   */
  getContractDetail: publicProcedure
    .input(z.object({
      symbol: z.string(),
    }))
    .query(async ({ input }) => {
      try {
        const contract = await defaultExchange.getContractInfo(input.symbol);
        
        if (!contract) {
          return {
            success: false,
            error: "Contract not found",
          };
        }
        
        // 获取订单簿数据
        const orderBook = await defaultExchange.getOrderBook(input.symbol, 20);
        const spreadPercent = defaultExchange.calculateSpreadPercent(orderBook);
        const depth = defaultExchange.calculateDepth(orderBook, 1);
        
        return {
          success: true,
          contract,
          liquidity: {
            spreadPercent,
            bidDepth: depth.bidDepth,
            askDepth: depth.askDepth,
            bidDepthValue: depth.bidDepthValue,
            askDepthValue: depth.askDepthValue,
          },
        };
      } catch (error) {
        console.error(`[CoinSelection] Failed to fetch contract detail for ${input.symbol}:`, error);
        return {
          success: false,
          error: error instanceof Error ? error.message : "Unknown error",
        };
      }
    }),

  /**
   * 获取推荐币种列表（综合评分）
   */
  getRecommendedCoins: publicProcedure
    .input(z.object({
      limit: z.number().min(1).max(50).default(10),
      minVolume: z.number().optional(),
      minLeverage: z.number().optional(),
    }))
    .query(async ({ input }) => {
      try {
        const contracts = await defaultExchange.getUSDTPerpetualContracts();
        
        // 应用基础筛选
        const minVolume = input.minVolume ?? DEFAULT_FILTERS.minVolume;
        const minLeverage = input.minLeverage ?? DEFAULT_FILTERS.minLeverage;
        
        const filtered = contracts.filter(c => 
          c.turnover24h >= minVolume &&
          c.maxLeverage >= minLeverage &&
          c.status === "Open"
        );
        
        // 计算每个币种的评分
        const scoredCoins: CoinScore[] = [];
        
        for (const contract of filtered.slice(0, 50)) { // 限制评估数量，避免API限流
          try {
            const score = await calculateCoinScore(contract);
            scoredCoins.push(score);
          } catch (error) {
            console.error(`[CoinSelection] Failed to score ${contract.symbol}:`, error);
          }
        }
        
        // 按总分排序
        scoredCoins.sort((a, b) => b.totalScore - a.totalScore);
        
        return {
          success: true,
          count: scoredCoins.length,
          coins: scoredCoins.slice(0, input.limit),
        };
      } catch (error) {
        console.error("[CoinSelection] Failed to get recommended coins:", error);
        return {
          success: false,
          count: 0,
          coins: [],
          error: error instanceof Error ? error.message : "Unknown error",
        };
      }
    }),

  /**
   * 回测指定币种的策略表现
   */
  backtestCoin: publicProcedure
    .input(z.object({
      symbol: z.string(),
      days: z.number().min(7).max(90).default(30),
      leverage: z.number().min(1).max(125).default(10),
    }))
    .query(async ({ input }) => {
      try {
        // 获取历史K线数据（1小时级别）
        const now = Date.now();
        const from = now - input.days * 24 * 60 * 60 * 1000;
        
        const klines = await defaultExchange.getKlines(
          input.symbol,
          "1h",
          from,
          now
        );
        
        if (klines.length < 20) {
          return {
            success: false,
            error: "Not enough historical data for backtest",
          };
        }
        
        // 执行回测
        const result = backtestMA520Strategy(input.symbol, klines, input.leverage);
        
        // 分析市场环境
        const environments = analyzeMarketEnvironments(klines, result.trades);
        
        return {
          success: true,
          backtest: result,
          environments,
        };
      } catch (error) {
        console.error(`[CoinSelection] Failed to backtest ${input.symbol}:`, error);
        return {
          success: false,
          error: error instanceof Error ? error.message : "Unknown error",
        };
      }
    }),

  /**
   * 添加监控币种
   */
  addMonitoredCoin: publicProcedure
    .input(z.object({ symbol: z.string() }))
    .mutation(async ({ input }) => {
      const coin = await multiCoinMonitor.addCoin(input.symbol);
      return {
        success: coin !== null,
        coin,
      };
    }),

  /**
   * 移除监控币种
   */
  removeMonitoredCoin: publicProcedure
    .input(z.object({ symbol: z.string() }))
    .mutation(async ({ input }) => {
      const removed = multiCoinMonitor.removeCoin(input.symbol);
      return { success: removed };
    }),

  /**
   * 获取所有监控币种
   */
  getMonitoredCoins: publicProcedure
    .query(() => {
      return multiCoinMonitor.getMonitoredCoins();
    }),

  /**
   * 更新所有监控币种数据
   */
  updateMonitoredCoins: publicProcedure
    .mutation(async () => {
      await multiCoinMonitor.updateAllCoins();
      return { success: true };
    }),

  /**
   * 记录交易结果
   */
  recordTrade: publicProcedure
    .input(z.object({
      symbol: z.string(),
      profit: z.number(),
    }))
    .mutation(({ input }) => {
      multiCoinMonitor.recordTrade(input.symbol, input.profit);
      return { success: true };
    }),

  /**
   * 获取轮换规则
   */
  getRotationRule: publicProcedure
    .query(() => {
      return multiCoinMonitor.getRotationRule();
    }),

  /**
   * 更新轮换规则
   */
  updateRotationRule: publicProcedure
    .input(z.object({
      enabled: z.boolean().optional(),
      consecutiveLosses: z.number().optional(),
      maxDrawdown: z.number().optional(),
      minWinRate: z.number().optional(),
      cooldownPeriod: z.number().optional(),
      minBacktestReturn: z.number().optional(),
      minVolume: z.number().optional(),
    }))
    .mutation(({ input }) => {
      multiCoinMonitor.updateRotationRule(input);
      return { success: true };
    }),

  /**
   * 获取轮换历史
   */
  getRotationHistory: publicProcedure
    .query(() => {
      return multiCoinMonitor.getRotationHistory();
    }),

  /**
   * 获取币种历史K线数据
   */
  getHistoricalKlines: publicProcedure
    .input(z.object({
      symbol: z.string(),
      interval: z.enum(["1m", "5m", "15m", "30m", "1h", "4h", "1d"]).default("1d"),
      days: z.number().min(1).max(90).default(30),
    }))
    .query(async ({ input }) => {
      try {
        const now = Date.now();
        const from = now - input.days * 24 * 60 * 60 * 1000;
        
        const klines = await defaultExchange.getKlines(
          input.symbol,
          input.interval,
          from,
          now
        );
        
        return {
          success: true,
          count: klines.length,
          klines,
        };
      } catch (error) {
        console.error(`[CoinSelection] Failed to fetch klines for ${input.symbol}:`, error);
        return {
          success: false,
          count: 0,
          klines: [],
          error: error instanceof Error ? error.message : "Unknown error",
        };
      }
    }),
});

/**
 * 计算币种综合评分
 */
async function calculateCoinScore(contract: Contract): Promise<CoinScore> {
  // 1. 流动性评分 (30%)
  let liquidityScore = 0;
  const turnover = contract.turnover24h;
  
  if (turnover >= 100_000_000) liquidityScore = 100;      // >= $100M
  else if (turnover >= 50_000_000) liquidityScore = 85;   // >= $50M
  else if (turnover >= 20_000_000) liquidityScore = 70;   // >= $20M
  else if (turnover >= 10_000_000) liquidityScore = 55;   // >= $10M
  else liquidityScore = 40;
  
  // 2. 波动率评分 (35%)
  // 滚仓策略需要适度波动，3-10%最佳
  let volatilityScore = 0;
  const absChange = Math.abs(contract.priceChange24hPercent);
  
  if (absChange >= 3 && absChange <= 10) {
    volatilityScore = 100;
  } else if (absChange >= 2 && absChange < 3) {
    volatilityScore = 80;
  } else if (absChange >= 10 && absChange < 15) {
    volatilityScore = 75;
  } else if (absChange >= 1 && absChange < 2) {
    volatilityScore = 60;
  } else if (absChange >= 15 && absChange < 20) {
    volatilityScore = 50;
  } else if (absChange < 1) {
    volatilityScore = 30; // 波动太小
  } else {
    volatilityScore = 30; // 波动太大，风险高
  }
  
  // 3. 趋势评分 (20%)
  // 简化版：根据24h涨跌判断
  let trendScore = 50; // 默认中性
  if (contract.priceChange24hPercent > 5) {
    trendScore = 80; // 强势上涨
  } else if (contract.priceChange24hPercent > 2) {
    trendScore = 70; // 温和上涨
  } else if (contract.priceChange24hPercent < -5) {
    trendScore = 40; // 强势下跌
  } else if (contract.priceChange24hPercent < -2) {
    trendScore = 50; // 温和下跌
  } else {
    trendScore = 60; // 盘整
  }
  
  // 4. 风险评分 (15%)
  // 考虑资金费率和波动风险
  let riskScore = 70; // 默认
  
  // 资金费率影响
  const fundingRate = contract.fundingRate || 0;
  const fundingRatePercent = Math.abs(fundingRate * 100);
  
  if (fundingRatePercent < 0.01) {
    riskScore += 20; // 资金费率很低
  } else if (fundingRatePercent < 0.05) {
    riskScore += 10; // 资金费率适中
  } else if (fundingRatePercent > 0.1) {
    riskScore -= 20; // 资金费率过高
  }
  
  // 极端波动惩罚
  if (absChange > 20) {
    riskScore -= 30;
  } else if (absChange > 15) {
    riskScore -= 15;
  }
  
  riskScore = Math.max(0, Math.min(100, riskScore));
  
  // 综合评分（权重：流动性30%，波动率35%，趋势20%，风险15%）
  const totalScore = 
    liquidityScore * 0.30 +
    volatilityScore * 0.35 +
    trendScore * 0.20 +
    riskScore * 0.15;
  
  // 推荐等级
  let recommendation: "excellent" | "good" | "fair" | "poor";
  if (totalScore >= 80) recommendation = "excellent";
  else if (totalScore >= 70) recommendation = "good";
  else if (totalScore >= 60) recommendation = "fair";
  else recommendation = "poor";
  
  // 推荐理由
  const reasons: string[] = [];
  if (liquidityScore >= 85) reasons.push("流动性充足");
  if (volatilityScore >= 80) reasons.push("波动率适中");
  if (turnover >= 50_000_000) reasons.push("交易量大");
  if (fundingRatePercent < 0.05) reasons.push("资金费率低");
  if (contract.maxLeverage >= 50) reasons.push("高杠杆可用");
  if (trendScore >= 70) reasons.push("趋势明确");
  
  return {
    symbol: contract.symbol,
    baseAsset: contract.baseAsset,
    totalScore,
    liquidityScore,
    volatilityScore,
    trendScore,
    riskScore,
    recommendation,
    reasons,
    price: contract.price,
    priceChange24hPercent: contract.priceChange24hPercent,
    volume24h: contract.volume24h,
    turnover24h: contract.turnover24h,
    fundingRate: contract.fundingRate || 0,
    maxLeverage: contract.maxLeverage,
  };
}
