import { useState, useMemo } from "react";
import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2, TrendingUp, TrendingDown, DollarSign, Activity, Star, Plus } from "lucide-react";
import { toast } from "sonner";

export default function CoinSelector() {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState<"score" | "volume" | "volatility">("score");
  const [minVolume, setMinVolume] = useState(10); // Million USD
  
  // 获取推荐币种
  const { data: recommendations, isLoading: loadingRecs, refetch: refetchRecs } = 
    trpc.coinSelection.getRecommendedCoins.useQuery({
      minVolume: minVolume * 1_000_000,
      minScore: 60,
      limit: 50,
    });
  
  // 获取已监控币种
  const { data: monitoredCoins, refetch: refetchMonitored } = 
    trpc.coinSelection.getMonitoredCoins.useQuery();
  
  // 添加监控
  const addMonitor = trpc.coinSelection.addMonitoredCoin.useMutation({
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`已添加 ${data.coin?.symbol} 到监控列表`);
        refetchMonitored();
      } else {
        toast.error("添加失败，可能已达到最大监控数量（10个）");
      }
    },
    onError: (error) => {
      toast.error(`添加失败: ${error.message}`);
    },
  });
  
  // 筛选和排序
  const filteredCoins = useMemo(() => {
    if (!recommendations) return [];
    
    let filtered = recommendations.filter(coin =>
      coin.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    // 排序
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "score":
          return b.score - a.score;
        case "volume":
          return b.volume24h - a.volume24h;
        case "volatility":
          return (b.indicators?.volatility || 0) - (a.indicators?.volatility || 0);
        default:
          return 0;
      }
    });
    
    return filtered;
  }, [recommendations, searchTerm, sortBy]);
  
  const monitoredSymbols = useMemo(() => 
    new Set(monitoredCoins?.map(c => c.symbol) || []),
    [monitoredCoins]
  );
  
  const getRankColor = (rank: string) => {
    switch (rank) {
      case "S": return "bg-purple-500";
      case "A": return "bg-blue-500";
      case "B": return "bg-green-500";
      case "C": return "bg-yellow-500";
      case "D": return "bg-orange-500";
      default: return "bg-gray-500";
    }
  };
  
  const handleAddMonitor = (symbol: string) => {
    addMonitor.mutate({ symbol });
  };
  
  return (
    <div className="container mx-auto p-4 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">币种选择器</h1>
        <p className="text-muted-foreground mt-2">
          基于综合评分系统，为您推荐最适合10U滚仓策略的合约币种
        </p>
      </div>
      
      {/* 筛选控制 */}
      <Card>
        <CardHeader>
          <CardTitle>筛选条件</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">搜索币种</label>
              <Input
                placeholder="输入币种符号..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">排序方式</label>
              <Select value={sortBy} onValueChange={(v: any) => setSortBy(v)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="score">综合评分</SelectItem>
                  <SelectItem value="volume">交易量</SelectItem>
                  <SelectItem value="volatility">波动率</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">最小交易量 (M)</label>
              <Input
                type="number"
                value={minVolume}
                onChange={(e) => setMinVolume(Number(e.target.value))}
                min={1}
                max={1000}
              />
            </div>
          </div>
          
          <Button onClick={() => refetchRecs()} variant="outline" size="sm">
            刷新数据
          </Button>
        </CardContent>
      </Card>
      
      {/* 推荐列表 */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">推荐币种</h2>
          <Badge variant="outline">
            {filteredCoins.length} 个币种符合条件
          </Badge>
        </div>
        
        {loadingRecs ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : filteredCoins.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              没有找到符合条件的币种
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredCoins.map((coin) => {
              const isMonitored = monitoredSymbols.has(coin.symbol);
              
              return (
                <Card key={coin.symbol} className="relative">
                  <CardHeader>
                    <div className="flex items-start justify-between">
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
                      <Badge className={getRankColor(coin.rank)}>
                        {coin.rank}
                      </Badge>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    {/* 综合评分 */}
                    <div>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-muted-foreground">综合评分</span>
                        <span className="font-bold">{coin.score.toFixed(1)}</span>
                      </div>
                      <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary transition-all"
                          style={{ width: `${coin.score}%` }}
                        />
                      </div>
                    </div>
                    
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
                          <div className="text-muted-foreground">波动率</div>
                          <div className="font-medium">
                            {coin.indicators?.volatility?.toFixed(2) || "N/A"}%
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="text-muted-foreground">资金费率</div>
                          <div className={`font-medium ${(coin.fundingRate || 0) >= 0 ? "text-green-500" : "text-red-500"}`}>
                            {((coin.fundingRate || 0) * 100).toFixed(4)}%
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Star className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="text-muted-foreground">杠杆</div>
                          <div className="font-medium">{coin.maxLeverage}x</div>
                        </div>
                      </div>
                    </div>
                    
                    {/* 推荐理由 */}
                    <div className="text-sm text-muted-foreground border-t pt-2">
                      {coin.reason}
                    </div>
                    
                    {/* 操作按钮 */}
                    <Button
                      className="w-full"
                      onClick={() => handleAddMonitor(coin.symbol)}
                      disabled={isMonitored || addMonitor.isPending}
                      variant={isMonitored ? "outline" : "default"}
                    >
                      {addMonitor.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          添加中...
                        </>
                      ) : isMonitored ? (
                        "已监控"
                      ) : (
                        <>
                          <Plus className="mr-2 h-4 w-4" />
                          添加到监控
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
