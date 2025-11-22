import { useState } from "react";
import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  TrendingUp,
  TrendingDown,
  Calendar,
  BarChart3,
  Download,
  Target,
  Award,
  AlertCircle,
} from "lucide-react";
import { toast } from "sonner";

export default function PerformanceReport() {
  const [selectedPeriod, setSelectedPeriod] = useState<"day" | "week" | "month">("day");

  // 获取报告数据
  const { data: dailyReport, isLoading: dailyLoading } =
    trpc.performanceReport.dailyReport.useQuery({});
  const { data: weeklyReport, isLoading: weeklyLoading } =
    trpc.performanceReport.weeklyReport.useQuery();
  const { data: monthlyReport, isLoading: monthlyLoading } =
    trpc.performanceReport.monthlyReport.useQuery();

  const currentReport =
    selectedPeriod === "day"
      ? dailyReport
      : selectedPeriod === "week"
      ? weeklyReport
      : monthlyReport;

  const isLoading = dailyLoading || weeklyLoading || monthlyLoading;

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("zh-CN");
  };

  const exportReport = () => {
    if (!currentReport) return;

    const content = `
# 交易性能报告

## 报告周期
- 开始日期: ${formatDate(currentReport.startDate)}
- 结束日期: ${formatDate(currentReport.endDate)}

## 核心指标
- 总交易次数: ${currentReport.metrics.totalTrades}
- 盈利交易: ${currentReport.metrics.winTrades}
- 亏损交易: ${currentReport.metrics.lossTrades}
- 胜率: ${currentReport.metrics.winRate}%
- 总盈亏: ${currentReport.metrics.totalPnl} USDT
- 总手续费: ${currentReport.metrics.totalFee} USDT
- 平均盈亏: ${currentReport.metrics.avgPnl} USDT
- 平均盈利: ${currentReport.metrics.avgWin} USDT
- 平均亏损: ${currentReport.metrics.avgLoss} USDT
- 最大盈利: ${currentReport.metrics.maxWin} USDT
- 最大亏损: ${currentReport.metrics.maxLoss} USDT
- 盈亏比: ${currentReport.metrics.profitFactor}
- 夏普比率: ${currentReport.metrics.sharpeRatio}
    `.trim();

    const blob = new Blob([content], { type: "text/markdown;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `performance_report_${selectedPeriod}_${new Date().toISOString().split("T")[0]}.md`;
    link.click();
    toast.success("报告已导出");
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 标题 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">性能分析报告</h1>
            <p className="text-muted-foreground mt-1">查看详细的交易性能分析和统计</p>
          </div>
          <Button onClick={exportReport} disabled={!currentReport}>
            <Download className="h-4 w-4 mr-2" />
            导出报告
          </Button>
        </div>

        {/* 周期选择 */}
        <Tabs value={selectedPeriod} onValueChange={(v: any) => setSelectedPeriod(v)}>
          <TabsList className="grid w-full max-w-md grid-cols-3">
            <TabsTrigger value="day">
              <Calendar className="h-4 w-4 mr-2" />
              日报
            </TabsTrigger>
            <TabsTrigger value="week">
              <BarChart3 className="h-4 w-4 mr-2" />
              周报
            </TabsTrigger>
            <TabsTrigger value="month">
              <TrendingUp className="h-4 w-4 mr-2" />
              月报
            </TabsTrigger>
          </TabsList>

          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">加载中...</div>
          ) : !currentReport ? (
            <div className="text-center py-12 text-muted-foreground">暂无数据</div>
          ) : (
            <>
              <TabsContent value={selectedPeriod} className="space-y-6">
                {/* 报告周期 */}
                <Card>
                  <CardHeader>
                    <CardTitle>报告周期</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(currentReport.startDate)} 至 {formatDate(currentReport.endDate)}
                    </p>
                  </CardContent>
                </Card>

                {/* 核心指标 */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardDescription className="flex items-center">
                        <BarChart3 className="h-4 w-4 mr-2" />
                        总交易次数
                      </CardDescription>
                      <CardTitle className="text-2xl">
                        {currentReport.metrics.totalTrades}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        盈利 {currentReport.metrics.winTrades} / 亏损{" "}
                        {currentReport.metrics.lossTrades}
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardDescription className="flex items-center">
                        <Target className="h-4 w-4 mr-2" />
                        胜率
                      </CardDescription>
                      <CardTitle className="text-2xl text-green-600">
                        {currentReport.metrics.winRate}%
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        盈亏比 {currentReport.metrics.profitFactor}
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardDescription className="flex items-center">
                        {parseFloat(currentReport.metrics.totalPnl) >= 0 ? (
                          <TrendingUp className="h-4 w-4 mr-2 text-green-600" />
                        ) : (
                          <TrendingDown className="h-4 w-4 mr-2 text-red-600" />
                        )}
                        总盈亏
                      </CardDescription>
                      <CardTitle
                        className={`text-2xl ${
                          parseFloat(currentReport.metrics.totalPnl) >= 0
                            ? "text-green-600"
                            : "text-red-600"
                        }`}
                      >
                        {parseFloat(currentReport.metrics.totalPnl) >= 0 ? "+" : ""}
                        {currentReport.metrics.totalPnl}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        手续费 {currentReport.metrics.totalFee} USDT
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardDescription className="flex items-center">
                        <Award className="h-4 w-4 mr-2" />
                        夏普比率
                      </CardDescription>
                      <CardTitle className="text-2xl">
                        {currentReport.metrics.sharpeRatio}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        平均盈亏 {currentReport.metrics.avgPnl} USDT
                      </p>
                    </CardContent>
                  </Card>
                </div>

                {/* 详细统计 */}
                <Card>
                  <CardHeader>
                    <CardTitle>详细统计</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">平均盈利</p>
                          <p className="text-2xl font-bold text-green-600">
                            +{currentReport.metrics.avgWin} USDT
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">最大盈利</p>
                          <p className="text-2xl font-bold text-green-600">
                            +{currentReport.metrics.maxWin} USDT
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">盈利交易数</p>
                          <p className="text-2xl font-bold">
                            {currentReport.metrics.winTrades}
                          </p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">平均亏损</p>
                          <p className="text-2xl font-bold text-red-600">
                            {currentReport.metrics.avgLoss} USDT
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">最大亏损</p>
                          <p className="text-2xl font-bold text-red-600">
                            {currentReport.metrics.maxLoss} USDT
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">亏损交易数</p>
                          <p className="text-2xl font-bold">
                            {currentReport.metrics.lossTrades}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* 周报/月报的额外统计 */}
                {selectedPeriod === "week" && "dailyStats" in currentReport && (
                  <Card>
                    <CardHeader>
                      <CardTitle>每日统计</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {currentReport.dailyStats.map((stat: any) => (
                          <div
                            key={stat.date}
                            className="flex items-center justify-between p-3 border rounded-lg"
                          >
                            <div>
                              <p className="font-medium">{formatDate(stat.date)}</p>
                              <p className="text-sm text-muted-foreground">
                                {stat.trades} 笔交易
                              </p>
                            </div>
                            <p
                              className={`text-lg font-bold ${
                                parseFloat(stat.pnl) >= 0 ? "text-green-600" : "text-red-600"
                              }`}
                            >
                              {parseFloat(stat.pnl) >= 0 ? "+" : ""}
                              {stat.pnl} USDT
                            </p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {selectedPeriod === "month" && "weeklyStats" in currentReport && (
                  <Card>
                    <CardHeader>
                      <CardTitle>每周统计</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {currentReport.weeklyStats.map((stat: any, idx: number) => (
                          <div
                            key={idx}
                            className="flex items-center justify-between p-3 border rounded-lg"
                          >
                            <div>
                              <p className="font-medium">
                                第 {idx + 1} 周 ({formatDate(stat.weekStart)} -{" "}
                                {formatDate(stat.weekEnd)})
                              </p>
                              <p className="text-sm text-muted-foreground">
                                {stat.trades} 笔交易
                              </p>
                            </div>
                            <p
                              className={`text-lg font-bold ${
                                parseFloat(stat.pnl) >= 0 ? "text-green-600" : "text-red-600"
                              }`}
                            >
                              {parseFloat(stat.pnl) >= 0 ? "+" : ""}
                              {stat.pnl} USDT
                            </p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* 建议和警告 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <AlertCircle className="h-5 w-5 mr-2" />
                      分析建议
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {parseFloat(currentReport.metrics.winRate) < 40 && (
                      <div className="p-3 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg">
                        <p className="text-sm text-red-800 dark:text-red-200">
                          ⚠️ 胜率较低（{currentReport.metrics.winRate}%），建议优化策略参数或暂停交易
                        </p>
                      </div>
                    )}

                    {parseFloat(currentReport.metrics.profitFactor) < 1 && (
                      <div className="p-3 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg">
                        <p className="text-sm text-red-800 dark:text-red-200">
                          ⚠️ 盈亏比小于1（{currentReport.metrics.profitFactor}），亏损大于盈利
                        </p>
                      </div>
                    )}

                    {parseFloat(currentReport.metrics.winRate) >= 60 &&
                      parseFloat(currentReport.metrics.profitFactor) >= 1.5 && (
                        <div className="p-3 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-lg">
                          <p className="text-sm text-green-800 dark:text-green-200">
                            ✅ 策略表现良好，胜率和盈亏比都在健康范围
                          </p>
                        </div>
                      )}

                    {currentReport.metrics.totalTrades < 10 && (
                      <div className="p-3 bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                        <p className="text-sm text-yellow-800 dark:text-yellow-200">
                          ℹ️ 交易样本较少，统计结果可能不够准确
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </>
          )}
        </Tabs>
      </div>
    </div>
  );
}
