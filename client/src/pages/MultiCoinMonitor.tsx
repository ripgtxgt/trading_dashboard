import { useState, useEffect } from "react";
import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  AlertCircle,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  X,
  RefreshCw,
  Settings,
  ArrowUpDown,
} from "lucide-react";
import { toast } from "sonner";
import { Link } from "wouter";

export default function MultiCoinMonitor() {
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  // 获取监控币种
  const { data: monitoredCoins, refetch } = trpc.coinSelection.getMonitoredCoins.useQuery(
    undefined,
    {
      refetchInterval: autoRefresh ? 30000 : false, // 30秒自动刷新
    }
  );
  
  // 更新数据
  const updateMutation = trpc.coinSelection.updateMonitoredCoins.useMutation({
    onSuccess: () => {
      refetch();
      toast.success("数据已更新");
    },
  });
  
  // 移除监控
  const removeMutation = trpc.coinSelection.removeMonitoredCoin.useMutation({
    onSuccess: (_, variables) => {
      toast.success(`已移除 ${variables.symbol}`);
      refetch();
    },
  });
  
  const handleRemove = (symbol: string) => {
    if (confirm(`确定要移除 ${symbol} 的监控吗？`)) {
      removeMutation.mutate({ symbol });
    }
  };
  
  const handleRefresh = () => {
    updateMutation.mutate();
  };
  
  const getSignalBadge = (signal?: any) => {
    if (!signal) return null;
    
    switch (signal.type) {
      case "buy":
        return <Badge className="bg-green-500">买入</Badge>;
      case "sell":
        return <Badge className="bg-red-500">卖出</Badge>;
      case "hold":
        return <Badge variant="outline">持有</Badge>;
      default:
        return null;
    }
  };
  
  const getPerformanceColor = (value: number) => {
    if (value > 0) return "text-green-500";
    if (value < 0) return "text-red-500";
    return "text-muted-foreground";
  };
  
  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">多币种监控</h1>
          <p className="text-muted-foreground mt-2">
            实时监控多个币种的价格、信号和性能
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${autoRefresh ? "animate-spin" : ""}`} />
            {autoRefresh ? "自动刷新" : "手动刷新"}
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={updateMutation.isPending}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            刷新
          </Button>
          
          <Link href="/coin-selector">
            <Button size="sm">
              添加币种
            </Button>
          </Link>
          
          <Link href="/rotation-settings">
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              轮换设置
            </Button>
          </Link>
        </div>
      </div>
      
      {!monitoredCoins || monitoredCoins.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">暂无监控币种</h3>
            <p className="text-muted-foreground mb-4">
              请先添加币种到监控列表
            </p>
            <Link href="/coin-selector">
              <Button>
                前往选择币种
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {monitoredCoins.map((coin) => (
            <Card key={coin.symbol} className="relative">
              <Button
                variant="ghost"
                size="icon"
                className="absolute top-2 right-2 h-6 w-6"
                onClick={() => handleRemove(coin.symbol)}
              >
                <X className="h-4 w-4" />
              </Button>
              
              <CardHeader>
                <div className="flex items-start justify-between pr-8">
                  <div>
                    <CardTitle className="text-xl">{coin.symbol}</CardTitle>
                    <CardDescription>
                      ${coin.price.toFixed(2)}
                      <span className={coin.priceChange24h >= 0 ? "text-green-500 ml-2" : "text-red-500 ml-2"}>
                        {coin.priceChange24h >= 0 ? "+" : ""}
                        {coin.priceChange24h.toFixed(2)}%
                      </span>
                    </CardDescription>
                  </div>
                  {getSignalBadge(coin.signal)}
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* 交易信号 */}
                {coin.signal && (
                  <div className="bg-secondary p-3 rounded-lg text-sm">
                    <div className="font-medium mb-1">交易信号</div>
                    <div className="text-muted-foreground">{coin.signal.reason}</div>
                    <div className="flex items-center gap-4 mt-2 text-xs">
                      <span>MA5: ${coin.signal.ma5.toFixed(2)}</span>
                      <span>MA20: ${coin.signal.ma20.toFixed(2)}</span>
                    </div>
                  </div>
                )}
                
                {/* 关键指标 */}
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex items-center gap-2">
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-muted-foreground">24h量</div>
                      <div className="font-medium">
                        ${(coin.volume24h / 1_000_000).toFixed(0)}M
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-muted-foreground">资金费率</div>
                      <div className={`font-medium ${coin.fundingRate >= 0 ? "text-green-500" : "text-red-500"}`}>
                        {(coin.fundingRate * 100).toFixed(4)}%
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* 性能统计 */}
                <div className="border-t pt-3">
                  <div className="text-sm font-medium mb-2">性能统计</div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <div className="text-muted-foreground">总交易</div>
                      <div className="font-medium">{coin.performance.totalTrades}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">胜率</div>
                      <div className="font-medium">{coin.performance.winRate.toFixed(1)}%</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">总收益</div>
                      <div className={`font-medium ${getPerformanceColor(coin.performance.totalReturn)}`}>
                        {coin.performance.totalReturn >= 0 ? "+" : ""}
                        {coin.performance.totalReturn.toFixed(2)}%
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">连续</div>
                      <div className="font-medium">
                        {coin.performance.consecutiveWins > 0 && (
                          <span className="text-green-500">
                            +{coin.performance.consecutiveWins}
                          </span>
                        )}
                        {coin.performance.consecutiveLosses > 0 && (
                          <span className="text-red-500">
                            -{coin.performance.consecutiveLosses}
                          </span>
                        )}
                        {coin.performance.consecutiveWins === 0 && coin.performance.consecutiveLosses === 0 && (
                          <span className="text-muted-foreground">0</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* 回测结果 */}
                {coin.backtest && (
                  <div className="border-t pt-3">
                    <div className="text-sm font-medium mb-2">30天回测</div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <div className="text-muted-foreground">收益</div>
                        <div className={`font-medium ${getPerformanceColor(coin.backtest.totalReturn)}`}>
                          {coin.backtest.totalReturn >= 0 ? "+" : ""}
                          {coin.backtest.totalReturn.toFixed(2)}%
                        </div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">盈亏比</div>
                        <div className="font-medium">{coin.backtest.profitFactor.toFixed(2)}</div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* 最后更新时间 */}
                <div className="text-xs text-muted-foreground text-center">
                  更新于 {new Date(coin.lastUpdate).toLocaleTimeString()}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
