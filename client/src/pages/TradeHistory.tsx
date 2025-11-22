import { useState } from "react";
import { trpc } from "@/lib/trpc";
import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Download, TrendingUp, TrendingDown, Filter, X } from "lucide-react";
import { toast } from "sonner";

export default function TradeHistory() {
  return (
    <>
      <Navigation />
      <TradeHistoryContent />
    </>
  );
}

function TradeHistoryContent() {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [symbol, setSymbol] = useState<string>("");
  const [direction, setDirection] = useState<"long" | "short" | "all">("all");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [sortBy, setSortBy] = useState<"exitTime" | "pnl" | "pnlPct">("exitTime");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  // 获取交易历史
  const { data: historyData, isLoading } = trpc.tradeHistory.list.useQuery({
    page,
    pageSize,
    symbol: symbol || undefined,
    direction,
    startDate: startDate || undefined,
    endDate: endDate || undefined,
    sortBy,
    sortOrder,
  });

  // 获取统计数据
  const { data: stats } = trpc.tradeHistory.stats.useQuery({
    symbol: symbol || undefined,
    startDate: startDate || undefined,
    endDate: endDate || undefined,
  });

  // 获取可用币种
  const { data: symbolsData } = trpc.tradeHistory.symbols.useQuery();

  // 导出CSV
  const exportCsv = trpc.tradeHistory.exportCsv.useQuery(
    {
      symbol: symbol || undefined,
      direction,
      startDate: startDate || undefined,
      endDate: endDate || undefined,
    },
    { enabled: false }
  );

  const handleExport = async () => {
    try {
      const result = await exportCsv.refetch();
      if (result.data?.csv) {
        const blob = new Blob([result.data.csv], { type: "text/csv;charset=utf-8;" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `trade_history_${new Date().toISOString().split("T")[0]}.csv`;
        link.click();
        toast.success("导出成功");
      }
    } catch (error) {
      toast.error("导出失败");
    }
  };

  const clearFilters = () => {
    setSymbol("");
    setDirection("all");
    setStartDate("");
    setEndDate("");
    setPage(1);
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleString("zh-CN");
  };

  const formatNumber = (num: string) => {
    return parseFloat(num).toFixed(2);
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 标题 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">交易历史</h1>
            <p className="text-muted-foreground mt-1">查看和分析历史交易记录</p>
          </div>
          <Button onClick={handleExport} disabled={exportCsv.isFetching}>
            <Download className="h-4 w-4 mr-2" />
            导出CSV
          </Button>
        </div>

        {/* 统计卡片 */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>总交易次数</CardDescription>
                <CardTitle className="text-2xl">{stats.totalTrades}</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>胜率</CardDescription>
                <CardTitle className="text-2xl text-green-600">{stats.winRate}%</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  盈利 {stats.winTrades} / 亏损 {stats.lossTrades}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>总盈亏</CardDescription>
                <CardTitle
                  className={`text-2xl ${
                    parseFloat(stats.totalPnl) >= 0 ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {parseFloat(stats.totalPnl) >= 0 ? "+" : ""}
                  {stats.totalPnl} USDT
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>平均盈亏</CardDescription>
                <CardTitle
                  className={`text-2xl ${
                    parseFloat(stats.avgPnl) >= 0 ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {parseFloat(stats.avgPnl) >= 0 ? "+" : ""}
                  {stats.avgPnl} USDT
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  平均盈利 {stats.avgWin} / 平均亏损 {stats.avgLoss}
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* 筛选器 */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>筛选条件</CardTitle>
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                <X className="h-4 w-4 mr-2" />
                清除筛选
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">交易对</label>
                <Select value={symbol} onValueChange={setSymbol}>
                  <SelectTrigger>
                    <SelectValue placeholder="全部" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">全部</SelectItem>
                    {symbolsData?.symbols.map((s) => (
                      <SelectItem key={s} value={s}>
                        {s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">方向</label>
                <Select value={direction} onValueChange={(v: any) => setDirection(v)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部</SelectItem>
                    <SelectItem value="long">做多</SelectItem>
                    <SelectItem value="short">做空</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">开始日期</label>
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">结束日期</label>
                <Input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">排序</label>
                <Select value={sortBy} onValueChange={(v: any) => setSortBy(v)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="exitTime">时间</SelectItem>
                    <SelectItem value="pnl">盈亏</SelectItem>
                    <SelectItem value="pnlPct">盈亏%</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 交易记录表格 */}
        <Card>
          <CardHeader>
            <CardTitle>交易记录</CardTitle>
            <CardDescription>
              共 {historyData?.total || 0} 条记录，第 {page} / {historyData?.totalPages || 1} 页
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">加载中...</div>
            ) : historyData?.trades.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">暂无交易记录</div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>交易对</TableHead>
                        <TableHead>方向</TableHead>
                        <TableHead>开仓价</TableHead>
                        <TableHead>平仓价</TableHead>
                        <TableHead>数量</TableHead>
                        <TableHead>盈亏</TableHead>
                        <TableHead>盈亏%</TableHead>
                        <TableHead>原因</TableHead>
                        <TableHead>阶段</TableHead>
                        <TableHead>平仓时间</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {historyData?.trades.map((trade) => (
                        <TableRow key={trade.id}>
                          <TableCell className="font-medium">{trade.symbol}</TableCell>
                          <TableCell>
                            <span
                              className={`inline-flex items-center ${
                                trade.direction === "long" ? "text-green-600" : "text-red-600"
                              }`}
                            >
                              {trade.direction === "long" ? (
                                <>
                                  <TrendingUp className="h-4 w-4 mr-1" />
                                  做多
                                </>
                              ) : (
                                <>
                                  <TrendingDown className="h-4 w-4 mr-1" />
                                  做空
                                </>
                              )}
                            </span>
                          </TableCell>
                          <TableCell>{formatNumber(trade.entryPrice)}</TableCell>
                          <TableCell>{formatNumber(trade.exitPrice)}</TableCell>
                          <TableCell>{formatNumber(trade.quantity)}</TableCell>
                          <TableCell
                            className={
                              parseFloat(trade.pnl) >= 0 ? "text-green-600" : "text-red-600"
                            }
                          >
                            {parseFloat(trade.pnl) >= 0 ? "+" : ""}
                            {formatNumber(trade.pnl)}
                          </TableCell>
                          <TableCell
                            className={
                              parseFloat(trade.pnlPct) >= 0 ? "text-green-600" : "text-red-600"
                            }
                          >
                            {parseFloat(trade.pnlPct) >= 0 ? "+" : ""}
                            {formatNumber(trade.pnlPct)}%
                          </TableCell>
                          <TableCell>{trade.reason}</TableCell>
                          <TableCell>{trade.stage}</TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {formatDate(trade.exitTime)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                {/* 分页 */}
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-muted-foreground">
                    显示 {(page - 1) * pageSize + 1} - {Math.min(page * pageSize, historyData?.total || 0)} 条，
                    共 {historyData?.total || 0} 条
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      上一页
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => p + 1)}
                      disabled={page >= (historyData?.totalPages || 1)}
                    >
                      下一页
                    </Button>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
