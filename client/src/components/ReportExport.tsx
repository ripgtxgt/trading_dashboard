import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FileDown, FileSpreadsheet, Loader2 } from "lucide-react";
import { trpc } from "@/lib/trpc";
import { toast } from "sonner";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import * as XLSX from "xlsx";

export function ReportExport() {
  const [generating, setGenerating] = useState(false);
  
  const { data: state } = trpc.trading.getState.useQuery();
  const { data: trades } = trpc.trading.getTrades.useQuery({ limit: 100 });
  const { data: allParams } = trpc.strategy.getAllParams.useQuery({ limit: 100 });

  const generatePDFReport = async () => {
    setGenerating(true);
    try {
      const doc = new jsPDF();
      
      // 标题
      doc.setFontSize(20);
      doc.text("10U战神滚仓策略 - 交易报告", 14, 20);
      
      // 生成时间
      doc.setFontSize(10);
      doc.text(`生成时间: ${new Date().toLocaleString('zh-CN')}`, 14, 28);
      
      // 账户概览
      doc.setFontSize(14);
      doc.text("账户概览", 14, 40);
      
      const accountData = [
        ["当前资金", `${state?.capital || 0} USDT`],
        ["初始资金", `${state?.initialCapital || 0} USDT`],
        ["总盈利", `${state?.dailyPnl || 0} USDT`],
        ["收益率", `${state?.capital && state?.initialCapital ? ((parseFloat(String(state.capital)) - parseFloat(String(state.initialCapital))) / parseFloat(String(state.initialCapital)) * 100).toFixed(2) : 0}%`],
        ["当前阶段", state?.currentStage || "N/A"],
        ["总交易次数", `${state?.totalTrades || 0}`],
        ["盈利交易", `0`],
        ["胜率", `0%`],
      ];
      
      autoTable(doc, {
        startY: 45,
        head: [["指标", "数值"]],
        body: accountData,
        theme: "grid",
      });
      
      // 策略参数历史
      if (allParams && allParams.length > 0) {
        const finalY = (doc as any).lastAutoTable.finalY || 45;
        doc.setFontSize(14);
        doc.text("策略参数历史", 14, finalY + 10);
        
        const paramsData = allParams.slice(0, 10).map((p: any) => [
          `MA${p.shortMaPeriod}/MA${p.longMaPeriod}`,
          p.timeframe,
          p.sensitivity,
          p.isActive ? "是" : "否",
          new Date(p.createdAt).toLocaleDateString('zh-CN'),
        ]);
        
        autoTable(doc, {
          startY: finalY + 15,
          head: [["参数组合", "时间框架", "灵敏度", "激活", "创建时间"]],
          body: paramsData,
          theme: "grid",
        });
      }
      
      // 交易历史
      if (trades && trades.length > 0) {
        const finalY = (doc as any).lastAutoTable.finalY || 100;
        
        // 如果内容太长，添加新页
        if (finalY > 250) {
          doc.addPage();
          doc.setFontSize(14);
          doc.text("交易历史（最近20笔）", 14, 20);
          
          const tradesData = trades.slice(0, 20).map((t: any) => [
            t.symbol,
            t.side === "long" ? "做多" : "做空",
            t.entryPrice?.toFixed(2) || "-",
            t.exitPrice?.toFixed(2) || "-",
            t.pnl?.toFixed(2) || "-",
            t.pnlPct ? `${(t.pnlPct * 100).toFixed(2)}%` : "-",
            t.status === "open" ? "持仓中" : "已平仓",
          ]);
          
          autoTable(doc, {
            startY: 25,
            head: [["交易对", "方向", "入场价", "出场价", "盈亏", "盈亏率", "状态"]],
            body: tradesData,
            theme: "grid",
          });
        } else {
          doc.setFontSize(14);
          doc.text("交易历史（最近20笔）", 14, finalY + 10);
          
          const tradesData = trades.slice(0, 20).map((t: any) => [
            t.symbol,
            t.side === "long" ? "做多" : "做空",
            t.entryPrice?.toFixed(2) || "-",
            t.exitPrice?.toFixed(2) || "-",
            t.pnl?.toFixed(2) || "-",
            t.pnlPct ? `${(t.pnlPct * 100).toFixed(2)}%` : "-",
            t.status === "open" ? "持仓中" : "已平仓",
          ]);
          
          autoTable(doc, {
            startY: finalY + 15,
            head: [["交易对", "方向", "入场价", "出场价", "盈亏", "盈亏率", "状态"]],
            body: tradesData,
            theme: "grid",
          });
        }
      }
      
      // 保存PDF
      doc.save(`trading_report_${new Date().toISOString().split('T')[0]}.pdf`);
      toast.success("PDF报告已生成");
    } catch (error) {
      console.error("Failed to generate PDF:", error);
      toast.error("PDF生成失败");
    } finally {
      setGenerating(false);
    }
  };

  const generateExcelReport = async () => {
    setGenerating(true);
    try {
      const wb = XLSX.utils.book_new();
      
      // 账户概览工作表
      const accountData = [
        ["指标", "数值"],
        ["当前资金", `${state?.capital || 0} USDT`],
        ["初始资金", `${state?.initialCapital || 0} USDT`],
        ["总盈利", `${state?.dailyPnl || 0} USDT`],
        ["收益率", `${state?.capital && state?.initialCapital ? ((parseFloat(String(state.capital)) - parseFloat(String(state.initialCapital))) / parseFloat(String(state.initialCapital)) * 100).toFixed(2) : 0}%`],
        ["当前阶段", state?.currentStage || "N/A"],
        ["总交易次数", state?.totalTrades || 0],
        ["盈利交易", 0],
        ["胜率", `0%`],
      ];
      
      const wsAccount = XLSX.utils.aoa_to_sheet(accountData);
      XLSX.utils.book_append_sheet(wb, wsAccount, "账户概览");
      
      // 策略参数工作表
      if (allParams && allParams.length > 0) {
        const paramsData = [
          ["参数组合", "短期MA", "长期MA", "时间框架", "灵敏度", "激活", "创建时间"],
          ...allParams.map((p: any) => [
            `MA${p.shortMaPeriod}/MA${p.longMaPeriod}`,
            p.shortMaPeriod,
            p.longMaPeriod,
            p.timeframe,
            p.sensitivity,
            p.isActive ? "是" : "否",
            new Date(p.createdAt).toLocaleString('zh-CN'),
          ]),
        ];
        
        const wsParams = XLSX.utils.aoa_to_sheet(paramsData);
        XLSX.utils.book_append_sheet(wb, wsParams, "策略参数");
      }
      
      // 交易历史工作表
      if (trades && trades.length > 0) {
        const tradesData = [
          ["交易对", "方向", "入场价", "出场价", "数量", "杠杆", "盈亏", "盈亏率", "状态", "开仓时间", "平仓时间"],
          ...trades.map((t: any) => [
            t.symbol,
            t.side === "long" ? "做多" : "做空",
            t.entryPrice || "-",
            t.exitPrice || "-",
            t.quantity || "-",
            t.leverage || "-",
            t.pnl || "-",
            t.pnlPct ? `${(t.pnlPct * 100).toFixed(2)}%` : "-",
            t.status === "open" ? "持仓中" : "已平仓",
            new Date(t.createdAt).toLocaleString('zh-CN'),
            t.closedAt ? new Date(t.closedAt).toLocaleString('zh-CN') : "-",
          ]),
        ];
        
        const wsTrades = XLSX.utils.aoa_to_sheet(tradesData);
        XLSX.utils.book_append_sheet(wb, wsTrades, "交易历史");
      }
      
      // 保存Excel
      XLSX.writeFile(wb, `trading_report_${new Date().toISOString().split('T')[0]}.xlsx`);
      toast.success("Excel报告已生成");
    } catch (error) {
      console.error("Failed to generate Excel:", error);
      toast.error("Excel生成失败");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>报告导出</CardTitle>
        <CardDescription>导出交易数据和分析报告</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col sm:flex-row gap-4">
          <Button
            onClick={generatePDFReport}
            disabled={generating}
            className="flex-1"
          >
            {generating ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <FileDown className="mr-2 h-4 w-4" />
            )}
            导出PDF报告
          </Button>
          
          <Button
            onClick={generateExcelReport}
            disabled={generating}
            variant="outline"
            className="flex-1"
          >
            {generating ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <FileSpreadsheet className="mr-2 h-4 w-4" />
            )}
            导出Excel报告
          </Button>
        </div>
        
        <div className="mt-4 text-sm text-muted-foreground">
          <p>报告包含以下内容：</p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>账户概览（资金、盈亏、胜率等）</li>
            <li>策略参数历史记录</li>
            <li>交易历史详细数据</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
