import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useState } from "react";
import { Loader2, TrendingUp, TrendingDown, Activity, CheckCircle2, AlertCircle, BarChart3 } from "lucide-react";
import { toast } from "sonner";

export function ParamsPanel() {
  const utils = trpc.useUtils();
  
  // 获取当前激活的参数
  const { data: activeParams, isLoading } = trpc.strategy.getActiveParams.useQuery(undefined, {
    refetchInterval: 10000,
  });

  // 本地状态：用户正在调整的参数
  const [shortMaPeriod, setShortMaPeriod] = useState(activeParams?.shortMaPeriod || 5);
  const [longMaPeriod, setLongMaPeriod] = useState(activeParams?.longMaPeriod || 20);
  const [timeframe, setTimeframe] = useState<"15m" | "30m" | "1h" | "2h" | "4h">(
    (activeParams?.timeframe as "15m" | "30m" | "1h" | "2h" | "4h") || "1h"
  );
  const [sensitivity, setSensitivity] = useState<"loose" | "standard" | "strict">(
    (activeParams?.sensitivity as "loose" | "standard" | "strict") || "standard"
  );

  // 模拟参数
  const simulateMutation = trpc.strategy.simulateParams.useMutation({
    onSuccess: (data) => {
      toast.success(`模拟完成：预计${data.signalCount}个信号 (做多${data.longSignals}, 做空${data.shortSignals})`);
    },
    onError: () => {
      toast.error("模拟失败，请重试");
    },
  });

  // 回测参数
  const backtestMutation = trpc.strategy.backtestParams.useMutation({
    onSuccess: (data) => {
      toast.success(`回测完成：胜率${data.winRate}%, 总收益${data.totalPnlPct}%`);
    },
    onError: () => {
      toast.error("回测失败，请重试");
    },
  });

  // 优化参数
  const optimizeMutation = trpc.strategy.optimizeParams.useMutation({
    onSuccess: (data) => {
      if (data.recommended) {
        const rec = data.recommended;
        setShortMaPeriod(rec.shortMaPeriod);
        setLongMaPeriod(rec.longMaPeriod);
        setSensitivity(rec.sensitivity as typeof sensitivity);
        toast.success(`找到最优参数：MA${rec.shortMaPeriod}/MA${rec.longMaPeriod}`);
      }
    },
    onError: () => {
      toast.error("优化失败，请重试");
    },
  });

  // 创建并应用参数
  const createMutation = trpc.strategy.createParams.useMutation({
    onSuccess: async (_, variables) => {
      // 创建成功后，获取新参数的ID并应用
      const allParams = await utils.strategy.getAllParams.fetch({ limit: 1 });
      if (allParams && allParams.length > 0) {
        const newParamId = allParams[0]!.id;
        await applyMutation.mutateAsync({ paramId: newParamId });
      }
    },
    onError: () => {
      toast.error("保存参数失败");
    },
  });

  // 应用参数
  const applyMutation = trpc.strategy.applyParams.useMutation({
    onSuccess: () => {
      toast.success("参数已应用！请重启交易机器人以生效");
      utils.strategy.getActiveParams.invalidate();
    },
    onError: () => {
      toast.error("应用参数失败");
    },
  });

  // 处理模拟
  const handleSimulate = () => {
    simulateMutation.mutate({
      shortMaPeriod,
      longMaPeriod,
      timeframe,
      sensitivity,
      samplePeriod: "24h",
    });
  };

  // 处理回测
  const handleBacktest = () => {
    backtestMutation.mutate({
      shortMaPeriod,
      longMaPeriod,
      timeframe,
      sensitivity,
    });
  };

  // 处理优化
  const handleOptimize = () => {
    optimizeMutation.mutate({
      timeframe,
      optimizationTarget: "composite",
    });
  };

  // 处理应用
  const handleApply = async () => {
    await createMutation.mutateAsync({
      shortMaPeriod,
      longMaPeriod,
      timeframe,
      sensitivity,
      isActive: 0, // 先创建为非激活状态
    });
  };

  // 检查参数是否有变化
  const hasChanges = 
    shortMaPeriod !== activeParams?.shortMaPeriod ||
    longMaPeriod !== activeParams?.longMaPeriod ||
    timeframe !== activeParams?.timeframe ||
    sensitivity !== activeParams?.sensitivity;

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>策略参数调整</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>策略参数调整</CardTitle>
            <CardDescription>实时调整MA参数和时间框架，查看模拟效果</CardDescription>
          </div>
          {hasChanges && (
            <Badge variant="outline" className="text-orange-600 border-orange-600">
              <AlertCircle className="h-3 w-3 mr-1" />
              未保存
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 当前激活参数 */}
        <div className="rounded-lg bg-muted/50 p-4 space-y-2">
          <div className="flex items-center gap-2 text-sm font-medium">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            当前激活参数
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">短期MA:</span>{" "}
              <span className="font-semibold">MA{activeParams?.shortMaPeriod || 5}</span>
            </div>
            <div>
              <span className="text-muted-foreground">长期MA:</span>{" "}
              <span className="font-semibold">MA{activeParams?.longMaPeriod || 20}</span>
            </div>
            <div>
              <span className="text-muted-foreground">时间框架:</span>{" "}
              <span className="font-semibold">{activeParams?.timeframe || "1h"}</span>
            </div>
            <div>
              <span className="text-muted-foreground">灵敏度:</span>{" "}
              <span className="font-semibold">
                {activeParams?.sensitivity === "loose" ? "宽松" : 
                 activeParams?.sensitivity === "strict" ? "严格" : "标准"}
              </span>
            </div>
          </div>
        </div>

        <Separator />

        {/* 参数调整 */}
        <div className="space-y-6">
          {/* 短期MA */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>短期MA周期</Label>
              <Badge variant="secondary">MA{shortMaPeriod}</Badge>
            </div>
            <Slider
              value={[shortMaPeriod]}
              onValueChange={(value) => setShortMaPeriod(value[0]!)}
              min={3}
              max={20}
              step={1}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground">
              推荐: 3-10 (数值越小越灵敏，信号越多)
            </p>
          </div>

          {/* 长期MA */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>长期MA周期</Label>
              <Badge variant="secondary">MA{longMaPeriod}</Badge>
            </div>
            <Slider
              value={[longMaPeriod]}
              onValueChange={(value) => setLongMaPeriod(value[0]!)}
              min={10}
              max={60}
              step={5}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground">
              推荐: 15-30 (必须大于短期MA)
            </p>
          </div>

          {/* 时间框架 */}
          <div className="space-y-3">
            <Label>时间框架</Label>
            <Select value={timeframe} onValueChange={(v) => setTimeframe(v as typeof timeframe)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="15m">15分钟 (信号最多，风险较高)</SelectItem>
                <SelectItem value="30m">30分钟</SelectItem>
                <SelectItem value="1h">1小时 (默认)</SelectItem>
                <SelectItem value="2h">2小时</SelectItem>
                <SelectItem value="4h">4小时 (信号最少，风险较低)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* 灵敏度 */}
          <div className="space-y-3">
            <Label>信号灵敏度</Label>
            <Select value={sensitivity} onValueChange={(v) => setSensitivity(v as typeof sensitivity)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="loose">宽松 (信号多，准确率较低)</SelectItem>
                <SelectItem value="standard">标准 (默认平衡)</SelectItem>
                <SelectItem value="strict">严格 (信号少，准确率较高)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <Separator />

        {/* 回测结果 */}
        {backtestMutation.data && (
          <div className="rounded-lg border bg-card p-4 space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium">
              <BarChart3 className="h-4 w-4" />
              回测结果
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">胜率</span>
                  <span className="font-semibold">{backtestMutation.data.winRate}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">总收益</span>
                  <span className={`font-semibold ${backtestMutation.data.totalPnlPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {backtestMutation.data.totalPnlPct >= 0 ? '+' : ''}{backtestMutation.data.totalPnlPct}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">总交易</span>
                  <span className="font-semibold">{backtestMutation.data.totalTrades}笔</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">夏普比率</span>
                  <span className="font-semibold">{backtestMutation.data.sharpeRatio}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">最大回撤</span>
                  <span className="font-semibold text-red-600">{backtestMutation.data.maxDrawdown}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">平均盈亏</span>
                  <span className={`font-semibold ${backtestMutation.data.avgPnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {backtestMutation.data.avgPnl >= 0 ? '+' : ''}{backtestMutation.data.avgPnl}U
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 优化结果 */}
        {optimizeMutation.data && optimizeMutation.data.recommended && (
          <div className="rounded-lg border bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 p-4 space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium">
              <CheckCircle2 className="h-4 w-4 text-blue-600" />
              推荐最优参数
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-muted-foreground">短期MA</div>
                <div className="text-lg font-bold">MA{optimizeMutation.data.recommended.shortMaPeriod}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">长期MA</div>
                <div className="text-lg font-bold">MA{optimizeMutation.data.recommended.longMaPeriod}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">灵敏度</div>
                <div className="text-lg font-bold">
                  {optimizeMutation.data.recommended.sensitivity === 'loose' ? '宽松' :
                   optimizeMutation.data.recommended.sensitivity === 'strict' ? '严格' : '标准'}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">预期胜率</div>
                <div className="text-lg font-bold text-green-600">{optimizeMutation.data.performance.winRate}%</div>
              </div>
            </div>
          </div>
        )}

        {/* 模拟结果 */}
        {simulateMutation.data && (
          <div className="rounded-lg border bg-card p-4 space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium">
              <Activity className="h-4 w-4" />
              模拟结果 (最近24小时)
            </div>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold">{simulateMutation.data.signalCount}</div>
                <div className="text-xs text-muted-foreground">总信号数</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600 flex items-center justify-center gap-1">
                  <TrendingUp className="h-5 w-5" />
                  {simulateMutation.data.longSignals}
                </div>
                <div className="text-xs text-muted-foreground">做多信号</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-600 flex items-center justify-center gap-1">
                  <TrendingDown className="h-5 w-5" />
                  {simulateMutation.data.shortSignals}
                </div>
                <div className="text-xs text-muted-foreground">做空信号</div>
              </div>
            </div>
          </div>
        )}

        {/* 操作按钮 */}
        <div className="grid grid-cols-2 gap-3">
          <Button
            onClick={handleSimulate}
            variant="outline"
            disabled={simulateMutation.isPending}
          >
            {simulateMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            信号模拟
          </Button>
          <Button
            onClick={handleBacktest}
            variant="outline"
            disabled={backtestMutation.isPending}
          >
            {backtestMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            历史回测
          </Button>
          <Button
            onClick={handleOptimize}
            variant="secondary"
            disabled={optimizeMutation.isPending}
          >
            {optimizeMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            AI优化
          </Button>
          <Button
            onClick={handleApply}
            disabled={createMutation.isPending || applyMutation.isPending || !hasChanges}
          >
            {(createMutation.isPending || applyMutation.isPending) && (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            )}
            应用参数
          </Button>
        </div>

        {/* 提示信息 */}
        <div className="rounded-lg bg-blue-50 dark:bg-blue-950/20 p-3 text-xs text-blue-900 dark:text-blue-100">
          <p className="font-medium mb-1">💡 使用提示：</p>
          <ul className="space-y-1 list-disc list-inside">
            <li>点击"模拟预览"查看参数在过去24小时会产生多少信号</li>
            <li>满意后点击"应用参数"保存并激活新参数</li>
            <li>应用后需要<strong>重启交易机器人</strong>才能生效</li>
            <li>建议先用小周期(15m)测试，确认有信号后再切换回1h</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
