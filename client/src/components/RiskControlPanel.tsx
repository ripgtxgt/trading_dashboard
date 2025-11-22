import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { AlertTriangle, TrendingDown, Shield, Activity } from "lucide-react";
import { useMemo } from "react";

export function RiskControlPanel() {
  const { data: trades } = trpc.trading.getTrades.useQuery(
    { limit: 100 },
    { refetchInterval: 10000 }
  );

  const { data: state } = trpc.trading.getState.useQuery(undefined, {
    refetchInterval: 5000,
  });

  // 计算风险指标
  const riskMetrics = useMemo(() => {
    if (!trades || !state) {
      return {
        maxDrawdown: 0,
        currentDrawdown: 0,
        consecutiveLosses: 0,
        maxConsecutiveLosses: 0,
        positionRisk: 0,
        riskLevel: "low" as const,
      };
    }

    const initialCapital = parseFloat(state.initialCapital);
    const currentCapital = parseFloat(state.capital);
    
    // 计算最大回撤
    let peak = initialCapital;
    let maxDrawdown = 0;
    let cumulativePnL = 0;

    trades.slice().reverse().forEach((trade) => {
      const pnl = parseFloat(trade.pnl);
      cumulativePnL += pnl;
      const capital = initialCapital + cumulativePnL;
      
      if (capital > peak) {
        peak = capital;
      }
      
      const drawdown = ((peak - capital) / peak) * 100;
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown;
      }
    });

    // 当前回撤
    const currentPeak = Math.max(initialCapital, currentCapital);
    const currentDrawdown = ((currentPeak - currentCapital) / currentPeak) * 100;

    // 计算连续亏损
    let consecutiveLosses = 0;
    let maxConsecutiveLosses = 0;
    let currentStreak = 0;

    trades.forEach((trade) => {
      const pnl = parseFloat(trade.pnl);
      if (pnl < 0) {
        currentStreak++;
        if (currentStreak > maxConsecutiveLosses) {
          maxConsecutiveLosses = currentStreak;
        }
      } else {
        currentStreak = 0;
      }
    });

    // 当前连续亏损
    for (const trade of trades) {
      const pnl = parseFloat(trade.pnl);
      if (pnl < 0) {
        consecutiveLosses++;
      } else {
        break;
      }
    }

    // 仓位风险（假设每次使用资金的百分比）
    const positionRisk = (50 / currentCapital) * 100; // 假设每次50U保证金

    // 风险等级评估
    let riskLevel: "low" | "medium" | "high" = "low";
    if (currentDrawdown > 20 || consecutiveLosses >= 5 || positionRisk > 50) {
      riskLevel = "high";
    } else if (currentDrawdown > 10 || consecutiveLosses >= 3 || positionRisk > 30) {
      riskLevel = "medium";
    }

    return {
      maxDrawdown,
      currentDrawdown,
      consecutiveLosses,
      maxConsecutiveLosses,
      positionRisk,
      riskLevel,
    };
  }, [trades, state]);

  const getRiskColor = (level: string) => {
    switch (level) {
      case "high":
        return "text-red-600";
      case "medium":
        return "text-yellow-600";
      default:
        return "text-green-600";
    }
  };

  const getRiskBadgeVariant = (level: string) => {
    switch (level) {
      case "high":
        return "destructive" as const;
      case "medium":
        return "secondary" as const;
      default:
        return "default" as const;
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              风险控制面板
            </CardTitle>
            <CardDescription>实时监控交易风险指标</CardDescription>
          </div>
          <Badge variant={getRiskBadgeVariant(riskMetrics.riskLevel)}>
            {riskMetrics.riskLevel === "high" ? "高风险" :
             riskMetrics.riskLevel === "medium" ? "中等风险" : "低风险"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 回撤指标 */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">当前回撤</span>
            </div>
            <span className={`text-lg font-semibold ${riskMetrics.currentDrawdown > 15 ? "text-red-600" : "text-muted-foreground"}`}>
              {riskMetrics.currentDrawdown.toFixed(2)}%
            </span>
          </div>
          <Progress 
            value={Math.min(riskMetrics.currentDrawdown, 100)} 
            className="h-2"
          />
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>最大回撤: {riskMetrics.maxDrawdown.toFixed(2)}%</span>
            <span>安全阈值: 20%</span>
          </div>
        </div>

        {/* 连续亏损 */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">连续亏损</span>
            </div>
            <span className={`text-lg font-semibold ${riskMetrics.consecutiveLosses >= 3 ? "text-red-600" : "text-muted-foreground"}`}>
              {riskMetrics.consecutiveLosses} 笔
            </span>
          </div>
          <Progress 
            value={(riskMetrics.consecutiveLosses / 5) * 100} 
            className="h-2"
          />
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>历史最大: {riskMetrics.maxConsecutiveLosses} 笔</span>
            <span>预警阈值: 5笔</span>
          </div>
        </div>

        {/* 仓位风险 */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">仓位风险比例</span>
            </div>
            <span className={`text-lg font-semibold ${riskMetrics.positionRisk > 40 ? "text-red-600" : "text-muted-foreground"}`}>
              {riskMetrics.positionRisk.toFixed(2)}%
            </span>
          </div>
          <Progress 
            value={Math.min(riskMetrics.positionRisk, 100)} 
            className="h-2"
          />
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>单笔保证金占比</span>
            <span>建议 &lt; 30%</span>
          </div>
        </div>

        {/* 风险提示 */}
        {riskMetrics.riskLevel !== "low" && (
          <div className={`rounded-lg border p-4 ${
            riskMetrics.riskLevel === "high" 
              ? "bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-900" 
              : "bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-900"
          }`}>
            <div className="flex items-start gap-3">
              <AlertTriangle className={`h-5 w-5 mt-0.5 ${
                riskMetrics.riskLevel === "high" ? "text-red-600" : "text-yellow-600"
              }`} />
              <div className="space-y-1">
                <p className={`font-semibold ${
                  riskMetrics.riskLevel === "high" ? "text-red-600" : "text-yellow-600"
                }`}>
                  {riskMetrics.riskLevel === "high" ? "高风险警告" : "风险提示"}
                </p>
                <ul className="text-sm space-y-1">
                  {riskMetrics.currentDrawdown > 15 && (
                    <li>• 当前回撤已超过15%，建议暂停交易</li>
                  )}
                  {riskMetrics.consecutiveLosses >= 3 && (
                    <li>• 连续亏损{riskMetrics.consecutiveLosses}笔，建议检查策略</li>
                  )}
                  {riskMetrics.positionRisk > 40 && (
                    <li>• 仓位风险过高，建议降低单笔保证金</li>
                  )}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* 风控建议 */}
        <div className="rounded-lg border bg-muted/50 p-4">
          <h4 className="font-semibold mb-2">风控建议</h4>
          <ul className="text-sm space-y-1 text-muted-foreground">
            <li>• 单笔亏损不超过总资金的5%</li>
            <li>• 回撤超过20%立即停止交易</li>
            <li>• 连续亏损5笔后暂停并复盘</li>
            <li>• 定期检查并调整策略参数</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
