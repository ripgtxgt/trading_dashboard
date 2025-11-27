/**
 * KuCoin交易所适配器
 * 实现Exchange接口
 */

import type { Exchange, Contract, OrderBook, Kline } from "./index";
import * as KuCoin from "./kucoin";

export class KuCoinExchange implements Exchange {
  name = "KuCoin";
  
  /**
   * 获取所有USDT永续合约
   */
  async getUSDTPerpetualContracts(): Promise<Contract[]> {
    const contracts = await KuCoin.getUSDTPerpetualContracts();
    
    return contracts.map(c => this.normalizeContract(c));
  }
  
  /**
   * 获取指定合约信息
   */
  async getContractInfo(symbol: string): Promise<Contract | null> {
    const contract = await KuCoin.getContractInfo(symbol);
    
    if (!contract) {
      return null;
    }
    
    return this.normalizeContract(contract);
  }
  
  /**
   * 获取订单簿
   */
  async getOrderBook(symbol: string, depth: number = 20): Promise<OrderBook> {
    const orderBook = await KuCoin.getOrderBook(symbol, depth);
    
    return {
      symbol: orderBook.symbol,
      bids: orderBook.bids,
      asks: orderBook.asks,
      timestamp: orderBook.ts,
    };
  }
  
  /**
   * 获取K线数据
   */
  async getKlines(
    symbol: string,
    interval: string,
    from?: number,
    to?: number
  ): Promise<Kline[]> {
    // 转换interval格式
    const granularity = this.intervalToGranularity(interval);
    
    const klines = await KuCoin.getKlines(symbol, granularity, from, to);
    
    return klines.map(k => ({
      timestamp: k[0],
      open: k[1],
      high: k[2],
      low: k[3],
      close: k[4],
      volume: k[5],
    }));
  }
  
  /**
   * 计算买卖价差
   */
  calculateSpreadPercent(orderBook: OrderBook): number {
    return KuCoin.calculateSpreadPercent({
      symbol: orderBook.symbol,
      sequence: 0,
      bids: orderBook.bids,
      asks: orderBook.asks,
      ts: orderBook.timestamp,
    });
  }
  
  /**
   * 计算订单簿深度
   */
  calculateDepth(orderBook: OrderBook, pricePercent: number = 1): {
    bidDepth: number;
    askDepth: number;
    bidDepthValue: number;
    askDepthValue: number;
  } {
    return KuCoin.calculateDepth({
      symbol: orderBook.symbol,
      sequence: 0,
      bids: orderBook.bids,
      asks: orderBook.asks,
      ts: orderBook.timestamp,
    }, pricePercent);
  }
  
  /**
   * 标准化合约信息
   */
  private normalizeContract(c: KuCoin.KuCoinContract): Contract {
    return {
      symbol: c.symbol,
      baseAsset: c.baseCurrency,
      quoteAsset: c.quoteCurrency,
      status: c.status,
      maxLeverage: c.maxLeverage,
      price: c.lastTradePrice,
      volume24h: c.volumeOf24h,
      turnover24h: c.turnoverOf24h,
      priceChange24hPercent: c.priceChgPct * 100,
      high24h: c.highPrice,
      low24h: c.lowPrice,
      fundingRate: c.fundingFeeRate,
      openInterest: c.openInterest,
    };
  }
  
  /**
   * 转换interval格式为KuCoin的granularity（分钟数）
   */
  private intervalToGranularity(interval: string): number {
    const map: Record<string, number> = {
      "1m": 1,
      "5m": 5,
      "15m": 15,
      "30m": 30,
      "1h": 60,
      "2h": 120,
      "4h": 240,
      "8h": 480,
      "12h": 720,
      "1d": 1440,
      "1w": 10080,
    };
    
    return map[interval] || 1440; // 默认1天
  }
}
