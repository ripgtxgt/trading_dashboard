import { trpc } from "@/lib/trpc";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, TrendingUp, TrendingDown, CheckCircle2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface ComparisonResult {
  params: {
    shortMa: number;
    longMa: number;
    timeframe: string;
    sensitivity: string;
  };
  performance: {
    winRate: number;
    totalPnlPct: number;
    totalTrades: number;
    sharpeRatio: number;
    maxDrawdown: number;
  };
}

export function ParamsComparison() {
  const [results, setResults] = useState<ComparisonResult[]>([]);
  const [isComparing, setIsComparing] = useState(false);

  const backtestMutation = trpc.strategy.backtestParams.useMutation();
  const createMutation = trpc.strategy.createParams.useMutation();
  const applyMutation = trpc.strategy.applyParams.useMutation();
  const utils = trpc.useUtils();

  // 预设参数组合
  const presetParams = [
    { shortMa: 3, longMa: 15, timeframe: "15m" as const, sensitivity: "loose" as const, name: "激进15分钟" },
    { shortMa: 5, longMa: 20, timeframe: "1h" as const, sensitivity: "standard" as const, name: "标准1小时" },
    { shortMa: 7, longMa: 30, timeframe: "1h" as const, sensitivity: "strict" as const, name: "稳健1小时" },
    { shortMa: 10, longMa: 30, timeframe: "4h" as const, sensitivity: "strict" as const, name: "保守4小时" },
  ];

  const handleCompare = async () => {
    setIsComparing(true);
    setResults([]);

    try {
      const comparisonResults: ComparisonResult[] = [];

      for (const preset of presetParams) {
        const result = await backtestMutation.mutateAsync({
          shortMaPeriod: preset.shortMa,
          longMaPeriod: preset.longMa,
          timeframe: preset.timeframe,
          sensitivity: preset.sensitivity,
        });

        comparisonResults.push({
          params: {
            shortMa: preset.shortMa,
            longMa: preset.longMa,
            timeframe: preset.timeframe,
            sensitivity: preset.sensitivity,
          },
          performance: {
            winRate: result.winRate,
            totalPnlPct: result.totalPnlPct,
            totalTrades: result.totalTrades,
            sharpeRatio: result.sharpeRatio,
            maxDrawdown: result.maxDrawdown,
          },
        });
      }

      setResults(comparisonResults);
      toast.success("参数对比完成");
    } catch (error) {
      toast.error("对比失败，请重试");
    } finally {
      setIsComparing(false);
    }
  };

  const handleApply = async (params: ComparisonResult["params"]) => {
    try {
      const created = await createMutation.mutateAsync({
        shortMaPeriod: params.shortMa,
        longMaPeriod: params.longMa,
        timeframe: params.timeframe as "15m" | "30m" | "1h" | "2h" | "4h",
        sensitivity: params.sensitivity as "loose" | "standard" | "strict",
        isActive: 0,
      });

      if (created.success) {
        // Get the latest param ID
        const allParams = await utils.strategy.getAllParams.fetch({ limit: 1 });
        if (allParams.length > 0) {
          await applyMutation.mutateAsync({ paramId: allParams[0]!.id });
          await utils.strategy.getActiveParams.invalidate();
          toast.success("参数已应用");
        }
      }
    } catch (error) {
      toast.error("应用失败");
    }
  };

  // 找出最佳参数
  const bestByWinRate = results.length > 0 
    ? results.reduce((best, current) => 
        current.performance.winRate > best.performance.winRate ? current : best
      )
    : null;

  const bestByProfit = results.length > 0
    ? results.reduce((best, current) =>
        current.performance.totalPnlPct > best.performance.totalPnlPct ? current : best
      )
    : null;

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">参数对比分析</h3>
            <p className="text-sm text-muted-foreground">
              对比不同参数组合的历史表现
            </p>
          </div>
          <Button
            onClick={handleCompare}
            disabled={isComparing}
          >
            {isComparing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            开始对比
          </Button>
        </div>

        {results.length > 0 && (
          <div className="rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>参数配置</TableHead>
                  <TableHead className="text-right">胜率</TableHead>
                  <TableHead className="text-right">总收益</TableHead>
                  <TableHead className="text-right">交易次数</TableHead>
                  <TableHead className="text-right">夏普比率</TableHead>
                  <TableHead className="text-right">最大回撤</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {results.map((result, index) => {
                  const isBestWinRate = bestByWinRate && 
                    result.params.shortMa === bestByWinRate.params.shortMa &&
                    result.params.longMa === bestByWinRate.params.longMa;
                  
                  const isBestProfit = bestByProfit &&
                    result.params.shortMa === bestByProfit.params.shortMa &&
                    result.params.longMa === bestByProfit.params.longMa;

                  return (
                    <TableRow key={index}>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="font-medium">
                            MA{result.params.shortMa}/MA{result.params.longMa}
                          </div>
                          <div className="flex gap-2">
                            <Badge variant="outline" className="text-xs">
                              {result.params.timeframe}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {result.params.sensitivity === "loose" ? "宽松" :
                               result.params.sensitivity === "strict" ? "严格" : "标准"}
                            </Badge>
                          </div>
                          {isBestWinRate && (
                            <Badge variant="secondary" className="text-xs">
                              <TrendingUp className="h-3 w-3 mr-1" />
                              最高胜率
                            </Badge>
                          )}
                          {isBestProfit && (
                            <Badge variant="secondary" className="text-xs">
                              <TrendingDown className="h-3 w-3 mr-1" />
                              最高收益
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right font-semibold">
                        {result.performance.winRate.toFixed(1)}%
                      </TableCell>
                      <TableCell className="text-right">
                        <span className={result.performance.totalPnlPct >= 0 ? "text-green-600 font-semibold" : "text-red-600 font-semibold"}>
                          {result.performance.totalPnlPct >= 0 ? "+" : ""}
                          {result.performance.totalPnlPct.toFixed(2)}%
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        {result.performance.totalTrades}
                      </TableCell>
                      <TableCell className="text-right">
                        {result.performance.sharpeRatio.toFixed(2)}
                      </TableCell>
                      <TableCell className="text-right text-red-600">
                        {result.performance.maxDrawdown.toFixed(2)}%
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleApply(result.params)}
                          disabled={createMutation.isPending || applyMutation.isPending}
                        >
                          <CheckCircle2 className="h-4 w-4 mr-1" />
                          应用
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        )}

        {results.length === 0 && !isComparing && (
          <div className="text-center py-12 text-muted-foreground">
            点击"开始对比"查看不同参数组合的表现
          </div>
        )}
      </div>
    </Card>
  );
}
