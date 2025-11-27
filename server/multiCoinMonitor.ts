/**
 * 多币种监控服务
 * 管理多个币种的实时监控、性能统计和自动轮换
 */

import { defaultExchange } from "./exchanges";
import type { Contract } from "./exchanges";
import { backtestMA520Strategy, type BacktestResult } from "./backtesting";
import { emitTradingSignal } from "./_core/websocket";

export interface MonitoredCoin {
  symbol: string;
  addedAt: number;
  lastUpdate: number;
  price: number;
  priceChange24h: number;
  fundingRate: number;
  volume24h: number;
  
  // 性能统计
  performance: CoinPerformance;
  
  // 回测结果
  backtest?: BacktestResult;
  
  // 交易信号
  signal?: TradingSignal;
}

export interface CoinPerformance {
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  winRate: number;
  totalReturn: number;
  avgReturn: number;
  consecutiveLosses: number;    // 连续亏损次数
  consecutiveWins: number;      // 连续盈利次数
  lastTradeProfit: number;
  lastTradeTime: number;
}

export interface TradingSignal {
  type: "buy" | "sell" | "hold";
  strength: number;             // 信号强度 0-100
  reason: string;
  timestamp: number;
  ma5: number;
  ma20: number;
  rsi?: number;
}

export interface RotationRule {
  enabled: boolean;
  
  // 触发条件
  consecutiveLosses: number;    // 连续亏损N次后轮换
  maxDrawdown: number;          // 最大回撤超过N%后轮换
  minWinRate: number;           // 胜率低于N%后轮换
  
  // 轮换策略
  cooldownPeriod: number;       // 冷却期（小时）
  minBacktestReturn: number;    // 新币种最小回测收益要求
  minVolume: number;            // 新币种最小交易量要求
}

export interface RotationEvent {
  timestamp: number;
  fromSymbol: string;
  toSymbol: string;
  reason: string;
  fromPerformance: CoinPerformance;
  toBacktest: BacktestResult;
}

/**
 * 多币种监控管理器
 */
class MultiCoinMonitorService {
  private monitoredCoins: Map<string, MonitoredCoin> = new Map();
  private rotationHistory: RotationEvent[] = [];
  private rotationRule: RotationRule = {
    enabled: false,
    consecutiveLosses: 3,
    maxDrawdown: 20,
    minWinRate: 40,
    cooldownPeriod: 24,
    minBacktestReturn: 50,
    minVolume: 10_000_000,
  };
  
  /**
   * 添加监控币种
   */
  async addCoin(symbol: string): Promise<MonitoredCoin | null> {
    try {
      // 检查是否已经在监控
      if (this.monitoredCoins.has(symbol)) {
        console.log(`[MultiCoinMonitor] ${symbol} is already being monitored`);
        return this.monitoredCoins.get(symbol)!;
      }
      
      // 检查监控数量限制
      if (this.monitoredCoins.size >= 10) {
        console.log(`[MultiCoinMonitor] Maximum 10 coins can be monitored`);
        return null;
      }
      
      // 获取合约信息
      const contractInfo = await defaultExchange.getContractInfo(symbol);
      if (!contractInfo) {
        console.log(`[MultiCoinMonitor] Contract ${symbol} not found`);
        return null;
      }
      
      // 执行回测
      const now = Date.now();
      const from = now - 30 * 24 * 60 * 60 * 1000;
      const klines = await defaultExchange.getKlines(symbol, "1h", from, now);
      
      let backtest: BacktestResult | undefined;
      if (klines.length >= 20) {
        backtest = backtestMA520Strategy(symbol, klines, 10);
      }
      
      const monitoredCoin: MonitoredCoin = {
        symbol,
        addedAt: Date.now(),
        lastUpdate: Date.now(),
        price: contractInfo.price,
        priceChange24h: contractInfo.priceChange24hPercent,
        fundingRate: contractInfo.fundingRate || 0,
        volume24h: contractInfo.turnover24h,
        performance: {
          totalTrades: 0,
          winningTrades: 0,
          losingTrades: 0,
          winRate: 0,
          totalReturn: 0,
          avgReturn: 0,
          consecutiveLosses: 0,
          consecutiveWins: 0,
          lastTradeProfit: 0,
          lastTradeTime: 0,
        },
        backtest,
      };
      
      this.monitoredCoins.set(symbol, monitoredCoin);
      console.log(`[MultiCoinMonitor] Added ${symbol} to monitoring`);
      
      return monitoredCoin;
    } catch (error) {
      console.error(`[MultiCoinMonitor] Failed to add ${symbol}:`, error);
      return null;
    }
  }
  
  /**
   * 移除监控币种
   */
  removeCoin(symbol: string): boolean {
    const removed = this.monitoredCoins.delete(symbol);
    if (removed) {
      console.log(`[MultiCoinMonitor] Removed ${symbol} from monitoring`);
    }
    return removed;
  }
  
  /**
   * 获取所有监控币种
   */
  getMonitoredCoins(): MonitoredCoin[] {
    return Array.from(this.monitoredCoins.values());
  }
  
  /**
   * 获取单个币种信息
   */
  getCoin(symbol: string): MonitoredCoin | undefined {
    return this.monitoredCoins.get(symbol);
  }
  
  /**
   * 更新币种实时数据
   */
  async updateCoinData(symbol: string): Promise<void> {
    const coin = this.monitoredCoins.get(symbol);
    if (!coin) return;
    
    try {
      const contractInfo = await defaultExchange.getContractInfo(symbol);
      if (!contractInfo) return;
      
      coin.price = contractInfo.price;
      coin.priceChange24h = contractInfo.priceChange24hPercent;
      coin.fundingRate = contractInfo.fundingRate || 0;
      coin.volume24h = contractInfo.turnover24h;
      coin.lastUpdate = Date.now();
      
      // 更新交易信号
      await this.updateTradingSignal(symbol);
      
    } catch (error) {
      console.error(`[MultiCoinMonitor] Failed to update ${symbol}:`, error);
    }
  }
  
  /**
   * 更新所有币种数据
   */
  async updateAllCoins(): Promise<void> {
    const symbols = Array.from(this.monitoredCoins.keys());
    await Promise.all(symbols.map(symbol => this.updateCoinData(symbol)));
  }
  
  /**
   * 更新交易信号
   */
  private async updateTradingSignal(symbol: string): Promise<void> {
    const coin = this.monitoredCoins.get(symbol);
    if (!coin) return;
    
    try {
      // 获取最近100根K线计算MA
      const now = Date.now();
      const from = now - 100 * 60 * 60 * 1000; // 100小时
      const klines = await defaultExchange.getKlines(symbol, "1h", from, now);
      
      if (klines.length < 20) return;
      
      // 计算MA5和MA20
      const ma5 = this.calculateMA(klines, 5);
      const ma20 = this.calculateMA(klines, 20);
      
      const lastMA5 = ma5[ma5.length - 1];
      const lastMA20 = ma20[ma20.length - 1];
      const prevMA5 = ma5[ma5.length - 2];
      const prevMA20 = ma20[ma20.length - 2];
      
      if (isNaN(lastMA5) || isNaN(lastMA20) || isNaN(prevMA5) || isNaN(prevMA20)) {
        return;
      }
      
      let signal: TradingSignal;
      
      // 金叉：MA5上穿MA20
      if (prevMA5 <= prevMA20 && lastMA5 > lastMA20) {
        const strength = Math.min(100, ((lastMA5 - lastMA20) / lastMA20) * 1000);
        signal = {
          type: "buy",
          strength,
          reason: "MA5上穿MA20，出现金叉买入信号",
          timestamp: Date.now(),
          ma5: lastMA5,
          ma20: lastMA20,
        };
        
        // 发送WebSocket通知
        emitTradingSignal({
          symbol,
          type: "buy",
          price: coin.price,
          reason: signal.reason,
          timestamp: signal.timestamp,
        });
      }
      // 死叉：MA5下穿MA20
      else if (prevMA5 >= prevMA20 && lastMA5 < lastMA20) {
        const strength = Math.min(100, ((lastMA20 - lastMA5) / lastMA20) * 1000);
        signal = {
          type: "sell",
          strength,
          reason: "MA5下穿MA20，出现死叉卖出信号",
          timestamp: Date.now(),
          ma5: lastMA5,
          ma20: lastMA20,
        };
        
        // 发送WebSocket通知
        emitTradingSignal({
          symbol,
          type: "sell",
          price: coin.price,
          reason: signal.reason,
          timestamp: signal.timestamp,
        });
      }
      // 持有
      else {
        const distance = Math.abs(lastMA5 - lastMA20) / lastMA20 * 100;
        signal = {
          type: "hold",
          strength: 50,
          reason: lastMA5 > lastMA20 ? "MA5在MA20上方，持有多头" : "MA5在MA20下方，持有空头",
          timestamp: Date.now(),
          ma5: lastMA5,
          ma20: lastMA20,
        };
      }
      
      coin.signal = signal;
      
    } catch (error) {
      console.error(`[MultiCoinMonitor] Failed to update signal for ${symbol}:`, error);
    }
  }
  
  /**
   * 计算移动平均线
   */
  private calculateMA(klines: any[], period: number): number[] {
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
   * 记录交易结果
   */
  recordTrade(symbol: string, profit: number): void {
    const coin = this.monitoredCoins.get(symbol);
    if (!coin) return;
    
    const perf = coin.performance;
    perf.totalTrades++;
    perf.totalReturn += profit;
    perf.avgReturn = perf.totalReturn / perf.totalTrades;
    perf.lastTradeProfit = profit;
    perf.lastTradeTime = Date.now();
    
    if (profit > 0) {
      perf.winningTrades++;
      perf.consecutiveWins++;
      perf.consecutiveLosses = 0;
    } else {
      perf.losingTrades++;
      perf.consecutiveLosses++;
      perf.consecutiveWins = 0;
    }
    
    perf.winRate = (perf.winningTrades / perf.totalTrades) * 100;
    
    // 检查是否需要轮换
    if (this.rotationRule.enabled) {
      this.checkRotation(symbol);
    }
  }
  
  /**
   * 检查是否需要轮换币种
   */
  private async checkRotation(symbol: string): Promise<void> {
    const coin = this.monitoredCoins.get(symbol);
    if (!coin) return;
    
    const perf = coin.performance;
    const rule = this.rotationRule;
    
    let shouldRotate = false;
    let reason = "";
    
    // 连续亏损触发
    if (perf.consecutiveLosses >= rule.consecutiveLosses) {
      shouldRotate = true;
      reason = `连续亏损${perf.consecutiveLosses}次`;
    }
    
    // 胜率过低触发
    if (perf.totalTrades >= 10 && perf.winRate < rule.minWinRate) {
      shouldRotate = true;
      reason = `胜率${perf.winRate.toFixed(1)}%低于${rule.minWinRate}%`;
    }
    
    // 最大回撤触发
    if (coin.backtest && coin.backtest.maxDrawdown > rule.maxDrawdown) {
      shouldRotate = true;
      reason = `最大回撤${coin.backtest.maxDrawdown.toFixed(1)}%超过${rule.maxDrawdown}%`;
    }
    
    if (shouldRotate) {
      await this.rotateCoin(symbol, reason);
    }
  }
  
  /**
   * 执行币种轮换
   */
  private async rotateCoin(fromSymbol: string, reason: string): Promise<void> {
    try {
      console.log(`[MultiCoinMonitor] Rotating ${fromSymbol}: ${reason}`);
      
      // 查找替代币种
      const replacement = await this.findReplacementCoin(fromSymbol);
      if (!replacement) {
        console.log(`[MultiCoinMonitor] No suitable replacement found for ${fromSymbol}`);
        return;
      }
      
      const fromCoin = this.monitoredCoins.get(fromSymbol);
      if (!fromCoin) return;
      
      // 记录轮换事件
      const event: RotationEvent = {
        timestamp: Date.now(),
        fromSymbol,
        toSymbol: replacement.symbol,
        reason,
        fromPerformance: { ...fromCoin.performance },
        toBacktest: replacement.backtest!,
      };
      
      this.rotationHistory.push(event);
      
      // 移除旧币种，添加新币种
      this.removeCoin(fromSymbol);
      await this.addCoin(replacement.symbol);
      
      console.log(`[MultiCoinMonitor] Rotated from ${fromSymbol} to ${replacement.symbol}`);
      
      // 发送通知
      emitTradingSignal({
        symbol: replacement.symbol,
        type: "buy",
        price: replacement.price,
        reason: `自动轮换：${reason}`,
        timestamp: Date.now(),
      });
      
    } catch (error) {
      console.error(`[MultiCoinMonitor] Failed to rotate ${fromSymbol}:`, error);
    }
  }
  
  /**
   * 查找替代币种
   */
  private async findReplacementCoin(excludeSymbol: string): Promise<Contract | null> {
    try {
      // 获取所有合约
      const contracts = await defaultExchange.getUSDTPerpetualContracts();
      
      // 过滤掉已监控的币种和被排除的币种
      const monitoredSymbols = Array.from(this.monitoredCoins.keys());
      const candidates = contracts.filter(c => 
        c.symbol !== excludeSymbol &&
        !monitoredSymbols.includes(c.symbol) &&
        c.turnover24h >= this.rotationRule.minVolume &&
        c.maxLeverage >= 20
      );
      
      if (candidates.length === 0) return null;
      
      // 对候选币种进行回测
      const results: Array<{ contract: Contract; backtest: BacktestResult }> = [];
      
      for (const contract of candidates.slice(0, 20)) { // 只测试前20个
        try {
          const now = Date.now();
          const from = now - 30 * 24 * 60 * 60 * 1000;
          const klines = await defaultExchange.getKlines(contract.symbol, "1h", from, now);
          
          if (klines.length < 20) continue;
          
          const backtest = backtestMA520Strategy(contract.symbol, klines, 10);
          
          if (backtest.totalReturn >= this.rotationRule.minBacktestReturn) {
            results.push({ contract, backtest });
          }
        } catch (error) {
          continue;
        }
      }
      
      if (results.length === 0) return null;
      
      // 按回测收益排序，选择最好的
      results.sort((a, b) => b.backtest.totalReturn - a.backtest.totalReturn);
      
      const best = results[0];
      best.contract.backtest = best.backtest;
      
      return best.contract;
      
    } catch (error) {
      console.error(`[MultiCoinMonitor] Failed to find replacement:`, error);
      return null;
    }
  }
  
  /**
   * 获取轮换规则
   */
  getRotationRule(): RotationRule {
    return { ...this.rotationRule };
  }
  
  /**
   * 更新轮换规则
   */
  updateRotationRule(rule: Partial<RotationRule>): void {
    this.rotationRule = { ...this.rotationRule, ...rule };
    console.log(`[MultiCoinMonitor] Rotation rule updated:`, this.rotationRule);
  }
  
  /**
   * 获取轮换历史
   */
  getRotationHistory(): RotationEvent[] {
    return [...this.rotationHistory];
  }
  
  /**
   * 清空所有监控
   */
  clear(): void {
    this.monitoredCoins.clear();
    console.log(`[MultiCoinMonitor] Cleared all monitored coins`);
  }
}

// 单例实例
export const multiCoinMonitor = new MultiCoinMonitorService();
