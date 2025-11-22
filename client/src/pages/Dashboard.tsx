import { trpc } from "@/lib/trpc";
import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowDownIcon, ArrowUpIcon, Activity, TrendingUp, DollarSign, BarChart3 } from "lucide-react";
import { BalanceChart } from "@/components/BalanceChart";
import { ControlPanel } from "@/components/ControlPanel";
import { ParamsPanel } from "@/components/ParamsPanel";
import { ParamsComparison } from "@/components/ParamsComparison";
import { TradeHistory } from "@/components/TradeHistory";
import { RiskControlPanel } from "@/components/RiskControlPanel";
import { KlineChartSimple } from "@/components/KlineChartSimple";
import { ReportExport } from "@/components/ReportExport";
import { SignalNotifications } from "@/components/SignalNotifications";
import { BacktestHistoryChart } from "@/components/BacktestHistoryChart";
import { RiskManagementPanel } from "@/components/RiskManagementPanel";

export default function Dashboard() {
  return (
    <>
      <Navigation />
      <DashboardContent />
    </>
  );
}

function DashboardContent() {
  const { data: state, isLoading: stateLoading } = trpc.trading.getState.useQuery(undefined, {
    refetchInterval: 5000, // 每5秒刷新一次
  });
  
  const { data: position } = trpc.trading.getPosition.useQuery(undefined, {
    refetchInterval: 5000,
  });
  
  const { data: stats } = trpc.trading.getStats.useQuery(undefined, {
    refetchInterval: 10000,
  });
  
  const { data: trades } = trpc.trading.getTrades.useQuery({ limit: 10 }, {
    refetchInterval: 10000,
  });

  if (stateLoading) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <Skeleton className="h-32 w-full" />
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      </div>
    );
  }

  const capital = parseFloat(state?.capital || "0");
  const initialCapital = parseFloat(state?.initialCapital || "0");
  const totalReturn = initialCapital > 0 ? ((capital - initialCapital) / initialCapital) * 100 : 0;
  const isProfit = totalReturn >= 0;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">10U战神滚仓策略</h1>
          <p className="text-muted-foreground mt-1">实时监控面板</p>
        </div>
        <Badge variant={state?.isRunning ? "default" : "secondary"} className="text-sm px-3 py-1">
          {state?.isRunning ? "运行中" : "已停止"}
        </Badge>
      </div>

      {/* Main Stats */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">当前资金</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{capital.toFixed(2)} USDT</div>
            <p className="text-xs text-muted-foreground mt-1">
              初始: {initialCapital.toFixed(2)} USDT
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总收益率</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${isProfit ? "text-green-600" : "text-red-600"}`}>
              {isProfit ? "+" : ""}{totalReturn.toFixed(2)}%
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              盈亏: {isProfit ? "+" : ""}{(capital - initialCapital).toFixed(2)} USDT
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">当前阶段</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{state?.currentStage || "N/A"}</div>
            <p className="text-xs text-muted-foreground mt-1">
              今日交易: {state?.dailyTrades || 0}笔
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">胜率</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats ? `${stats.winRate.toFixed(1)}%` : "N/A"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              总交易: {stats?.totalTrades || 0}笔
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Current Position */}
      {position && (
        <Card>
          <CardHeader>
            <CardTitle>当前持仓</CardTitle>
            <CardDescription>实时持仓信息</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <div>
                <p className="text-sm text-muted-foreground">方向</p>
                <div className="flex items-center gap-2 mt-1">
                  {position.direction === "long" ? (
                    <ArrowUpIcon className="h-4 w-4 text-green-600" />
                  ) : (
                    <ArrowDownIcon className="h-4 w-4 text-red-600" />
                  )}
                  <span className="font-semibold">
                    {position.direction === "long" ? "做多" : "做空"}
                  </span>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">开仓价</p>
                <p className="font-semibold mt-1">${parseFloat(position.entryPrice).toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">保证金</p>
                <p className="font-semibold mt-1">{parseFloat(position.margin).toFixed(2)} USDT</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">止损/止盈</p>
                <p className="font-semibold mt-1">
                  {(parseFloat(position.stopLossPct) * 100).toFixed(0)}% / 
                  {(parseFloat(position.takeProfitPct) * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Kline Chart */}
      <KlineChartSimple />

      {/* Balance Chart */}
      <BalanceChart />

      {/* Control Panel and Params Panel */}
      <div className="grid gap-4 md:gap-6 grid-cols-1 lg:grid-cols-2">
        <ControlPanel
          isRunning={state?.isRunning === 1}
          emergencyStopped={state?.emergencyStopped === 1}
        />
        <ParamsPanel />
      </div>

      {/* Params Comparison */}
      <ParamsComparison />

      {/* Risk Control Panel */}
      <RiskControlPanel />

      {/* Trade History */}
      <TradeHistory />

      {/* Backtest History */}
      <BacktestHistoryChart />
      
      {/* Signal Notifications */}
      <SignalNotifications />
      
      {/* Report Export */}
      <ReportExport />

      {/* Recent Trades */}
      <Card>
        <CardHeader>
          <CardTitle>最近交易</CardTitle>
          <CardDescription>最近10笔交易记录</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {trades && trades.length > 0 ? (
              trades.map((trade) => {
                const pnl = parseFloat(trade.pnl);
                const isWin = pnl > 0;
                
                return (
                  <div key={trade.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      {trade.direction === "long" ? (
                        <ArrowUpIcon className="h-4 w-4 text-green-600" />
                      ) : (
                        <ArrowDownIcon className="h-4 w-4 text-red-600" />
                      )}
                      <div>
                        <p className="font-medium">
                          {trade.direction === "long" ? "做多" : "做空"}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(trade.exitTime).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-semibold ${isWin ? "text-green-600" : "text-red-600"}`}>
                        {isWin ? "+" : ""}{pnl.toFixed(2)} USDT
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {parseFloat(trade.pnlPct).toFixed(2)}%
                      </p>
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="text-center text-muted-foreground py-8">暂无交易记录</p>
            )}
          </div>
        </CardContent>
      </Card>
      
      {/* 风险管理面板 */}
      <RiskManagementPanel />
    </div>
  );
}
