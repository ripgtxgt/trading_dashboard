/**
 * K线数据缓存服务
 * 减少API调用频率，提升图表加载速度
 */

interface KlineData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  ma5?: number;
  ma20?: number;
}

interface CacheEntry {
  data: KlineData[];
  timestamp: number;
}

class KlineCache {
  private cache: Map<string, CacheEntry> = new Map();
  private readonly CACHE_TTL = 60 * 1000; // 1分钟缓存

  /**
   * 生成缓存键
   */
  private getCacheKey(symbol: string, interval: string, limit: number): string {
    return `${symbol}_${interval}_${limit}`;
  }

  /**
   * 获取缓存数据
   */
  get(symbol: string, interval: string, limit: number): KlineData[] | null {
    const key = this.getCacheKey(symbol, interval, limit);
    const entry = this.cache.get(key);

    if (!entry) {
      return null;
    }

    // 检查缓存是否过期
    if (Date.now() - entry.timestamp > this.CACHE_TTL) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  /**
   * 设置缓存数据
   */
  set(symbol: string, interval: string, limit: number, data: KlineData[]): void {
    const key = this.getCacheKey(symbol, interval, limit);
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * 增量更新缓存
   * 只更新最新的K线数据，避免重新获取全部数据
   */
  updateLatest(symbol: string, interval: string, limit: number, newKline: KlineData): void {
    const key = this.getCacheKey(symbol, interval, limit);
    const entry = this.cache.get(key);

    if (!entry) {
      return;
    }

    const data = entry.data;
    const lastKline = data[data.length - 1];

    // 如果时间相同，更新最后一根K线
    if (lastKline && lastKline.time === newKline.time) {
      data[data.length - 1] = newKline;
    } else {
      // 否则添加新K线，并移除最旧的
      data.push(newKline);
      if (data.length > limit) {
        data.shift();
      }
    }

    // 重新计算MA指标
    this.calculateMA(data);

    // 更新缓存
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * 计算MA指标
   */
  private calculateMA(data: KlineData[]): void {
    for (let i = 0; i < data.length; i++) {
      // 计算MA5
      if (i >= 4) {
        let sum = 0;
        for (let j = 0; j < 5; j++) {
          sum += data[i - j].close;
        }
        data[i].ma5 = sum / 5;
      }

      // 计算MA20
      if (i >= 19) {
        let sum = 0;
        for (let j = 0; j < 20; j++) {
          sum += data[i - j].close;
        }
        data[i].ma20 = sum / 20;
      }
    }
  }

  /**
   * 清除所有缓存
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * 清除过期缓存
   */
  clearExpired(): void {
    const now = Date.now();
    const keysToDelete: string[] = [];
    
    this.cache.forEach((entry, key) => {
      if (now - entry.timestamp > this.CACHE_TTL) {
        keysToDelete.push(key);
      }
    });
    
    keysToDelete.forEach(key => this.cache.delete(key));
  }
}

// 单例实例
export const klineCache = new KlineCache();

// 定期清理过期缓存
setInterval(() => {
  klineCache.clearExpired();
}, 60 * 1000); // 每分钟清理一次
