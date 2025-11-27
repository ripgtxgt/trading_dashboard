import { useState, useEffect } from "react";
import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Loader2, ArrowRight, TrendingUp, AlertTriangle } from "lucide-react";
import { toast } from "sonner";

export default function RotationSettings() {
  const { data: rule, isLoading, refetch } = trpc.coinSelection.getRotationRule.useQuery();
  const { data: history } = trpc.coinSelection.getRotationHistory.useQuery();
  
  const [enabled, setEnabled] = useState(false);
  const [consecutiveLosses, setConsecutiveLosses] = useState(3);
  const [maxDrawdown, setMaxDrawdown] = useState(20);
  const [minWinRate, setMinWinRate] = useState(40);
  const [cooldownPeriod, setCooldownPeriod] = useState(24);
  const [minBacktestReturn, setMinBacktestReturn] = useState(50);
  const [minVolume, setMinVolume] = useState(10);
  
  useEffect(() => {
    if (rule) {
      setEnabled(rule.enabled);
      setConsecutiveLosses(rule.consecutiveLosses);
      setMaxDrawdown(rule.maxDrawdown);
      setMinWinRate(rule.minWinRate);
      setCooldownPeriod(rule.cooldownPeriod);
      setMinBacktestReturn(rule.minBacktestReturn);
      setMinVolume(rule.minVolume / 1_000_000);
    }
  }, [rule]);
  
  const updateMutation = trpc.coinSelection.updateRotationRule.useMutation({
    onSuccess: () => {
      toast.success("轮换规则已更新");
      refetch();
    },
    onError: (error) => {
      toast.error(`更新失败: ${error.message}`);
    },
  });
  
  const handleSave = () => {
    updateMutation.mutate({
      enabled,
      consecutiveLosses,
      maxDrawdown,
      minWinRate,
      cooldownPeriod,
      minBacktestReturn,
      minVolume: minVolume * 1_000_000,
    });
  };
  
  if (isLoading) {
    return (
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto p-4 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">自动轮换设置</h1>
        <p className="text-muted-foreground mt-2">
          配置币种自动轮换规则，当币种表现不佳时自动切换到更好的币种
        </p>
      </div>
      
      {/* 轮换规则配置 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>轮换规则</CardTitle>
              <CardDescription>
                设置触发自动轮换的条件
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Label htmlFor="enabled">启用自动轮换</Label>
              <Switch
                id="enabled"
                checked={enabled}
                onCheckedChange={setEnabled}
              />
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* 触发条件 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">触发条件</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="consecutiveLosses">连续亏损次数</Label>
                <Input
                  id="consecutiveLosses"
                  type="number"
                  value={consecutiveLosses}
                  onChange={(e) => setConsecutiveLosses(Number(e.target.value))}
                  min={1}
                  max={10}
                  disabled={!enabled}
                />
                <p className="text-sm text-muted-foreground">
                  连续亏损达到此次数时触发轮换
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="maxDrawdown">最大回撤 (%)</Label>
                <Input
                  id="maxDrawdown"
                  type="number"
                  value={maxDrawdown}
                  onChange={(e) => setMaxDrawdown(Number(e.target.value))}
                  min={5}
                  max={50}
                  disabled={!enabled}
                />
                <p className="text-sm text-muted-foreground">
                  回撤超过此百分比时触发轮换
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="minWinRate">最低胜率 (%)</Label>
                <Input
                  id="minWinRate"
                  type="number"
                  value={minWinRate}
                  onChange={(e) => setMinWinRate(Number(e.target.value))}
                  min={0}
                  max={100}
                  disabled={!enabled}
                />
                <p className="text-sm text-muted-foreground">
                  胜率低于此百分比时触发轮换（需至少10次交易）
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="cooldownPeriod">冷却期 (小时)</Label>
                <Input
                  id="cooldownPeriod"
                  type="number"
                  value={cooldownPeriod}
                  onChange={(e) => setCooldownPeriod(Number(e.target.value))}
                  min={1}
                  max={168}
                  disabled={!enabled}
                />
                <p className="text-sm text-muted-foreground">
                  轮换后的冷却期，避免频繁切换
                </p>
              </div>
            </div>
          </div>
          
          <Separator />
          
          {/* 新币种要求 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">新币种要求</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="minBacktestReturn">最小回测收益 (%)</Label>
                <Input
                  id="minBacktestReturn"
                  type="number"
                  value={minBacktestReturn}
                  onChange={(e) => setMinBacktestReturn(Number(e.target.value))}
                  min={0}
                  max={200}
                  disabled={!enabled}
                />
                <p className="text-sm text-muted-foreground">
                  新币种30天回测收益必须达到此要求
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="minVolume">最小交易量 (M)</Label>
                <Input
                  id="minVolume"
                  type="number"
                  value={minVolume}
                  onChange={(e) => setMinVolume(Number(e.target.value))}
                  min={1}
                  max={1000}
                  disabled={!enabled}
                />
                <p className="text-sm text-muted-foreground">
                  新币种24小时交易量必须达到此要求（百万美元）
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2 p-4 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
            <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              自动轮换会在满足条件时自动切换币种，请谨慎设置触发条件
            </p>
          </div>
          
          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => refetch()}
            >
              重置
            </Button>
            <Button
              onClick={handleSave}
              disabled={updateMutation.isPending}
            >
              {updateMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  保存中...
                </>
              ) : (
                "保存设置"
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
      
      {/* 轮换历史 */}
      <Card>
        <CardHeader>
          <CardTitle>轮换历史</CardTitle>
          <CardDescription>
            查看过去的自动轮换记录
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!history || history.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              暂无轮换记录
            </div>
          ) : (
            <div className="space-y-4">
              {history.map((event, index) => (
                <div key={index} className="flex items-center gap-4 p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline">{event.fromSymbol}</Badge>
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                      <Badge>{event.toSymbol}</Badge>
                      <span className="text-sm text-muted-foreground">
                        {new Date(event.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      原因: {event.reason}
                    </div>
                    <div className="grid grid-cols-2 gap-4 mt-2 text-sm">
                      <div>
                        <span className="text-muted-foreground">原币种表现:</span>
                        <div className="font-medium">
                          胜率 {event.fromPerformance.winRate.toFixed(1)}% |
                          收益 {event.fromPerformance.totalReturn >= 0 ? "+" : ""}
                          {event.fromPerformance.totalReturn.toFixed(2)}%
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">新币种回测:</span>
                        <div className="font-medium">
                          胜率 {event.toBacktest.winRate.toFixed(1)}% |
                          收益 +{event.toBacktest.totalReturn.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
