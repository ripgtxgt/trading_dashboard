import { useState } from "react";
import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import { Settings, RefreshCw, Save } from "lucide-react";

export function StrategyConfigPanel() {
  const { data: config, isLoading, refetch } = trpc.strategyConfig.getConfig.useQuery();
  const updateConfig = trpc.strategyConfig.updateConfig.useMutation();
  const resetConfig = trpc.strategyConfig.resetConfig.useMutation();

  const [formData, setFormData] = useState({
    symbol: "",
    rollMultiplier: "",
    takeProfitPct: "",
    stopLossPct: "",
    maxDailyLoss: "",
    maxDrawdown: "",
    consecutiveLossLimit: 0,
    leverage: 0,
    positionSize: "",
    isActive: true,
  });

  // 当配置加载完成时，更新表单数据
  useState(() => {
    if (config) {
      setFormData({
        symbol: config.symbol,
        rollMultiplier: config.rollMultiplier,
        takeProfitPct: config.takeProfitPct,
        stopLossPct: config.stopLossPct,
        maxDailyLoss: config.maxDailyLoss,
        maxDrawdown: config.maxDrawdown,
        consecutiveLossLimit: config.consecutiveLossLimit,
        leverage: config.leverage,
        positionSize: config.positionSize,
        isActive: config.isActive === "true",
      });
    }
  });

  const handleSave = async () => {
    try {
      await updateConfig.mutateAsync({
        symbol: formData.symbol,
        rollMultiplier: formData.rollMultiplier,
        takeProfitPct: formData.takeProfitPct,
        stopLossPct: formData.stopLossPct,
        maxDailyLoss: formData.maxDailyLoss,
        maxDrawdown: formData.maxDrawdown,
        consecutiveLossLimit: formData.consecutiveLossLimit,
        leverage: formData.leverage,
        positionSize: formData.positionSize,
        isActive: formData.isActive ? "true" : "false",
      });
      
      toast.success("策略配置已保存");
      refetch();
    } catch (error) {
      toast.error("保存失败：" + (error as Error).message);
    }
  };

  const handleReset = async () => {
    try {
      const result = await resetConfig.mutateAsync();
      setFormData({
        symbol: result.symbol,
        rollMultiplier: result.rollMultiplier,
        takeProfitPct: result.takeProfitPct,
        stopLossPct: result.stopLossPct,
        maxDailyLoss: result.maxDailyLoss,
        maxDrawdown: result.maxDrawdown,
        consecutiveLossLimit: result.consecutiveLossLimit,
        leverage: result.leverage,
        positionSize: result.positionSize,
        isActive: result.isActive === "true",
      });
      
      toast.success("已重置为默认配置");
      refetch();
    } catch (error) {
      toast.error("重置失败：" + (error as Error).message);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>策略配置</CardTitle>
          <CardDescription>加载中...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              策略配置
            </CardTitle>
            <CardDescription>在线调整策略参数，实时同步到交易脚本</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleReset}>
              <RefreshCw className="h-4 w-4 mr-2" />
              重置默认
            </Button>
            <Button size="sm" onClick={handleSave} disabled={updateConfig.isPending}>
              <Save className="h-4 w-4 mr-2" />
              {updateConfig.isPending ? "保存中..." : "保存配置"}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 基础配置 */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">基础配置</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="symbol">交易对</Label>
              <Input
                id="symbol"
                value={formData.symbol}
                onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
                placeholder="XBTUSDTM"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="rollMultiplier">滚仓倍数</Label>
              <Input
                id="rollMultiplier"
                value={formData.rollMultiplier}
                onChange={(e) => setFormData({ ...formData, rollMultiplier: e.target.value })}
                placeholder="2.0"
              />
            </div>
          </div>
        </div>

        {/* 止盈止损 */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">止盈止损</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="takeProfitPct">止盈百分比 (%)</Label>
              <Input
                id="takeProfitPct"
                value={formData.takeProfitPct}
                onChange={(e) => setFormData({ ...formData, takeProfitPct: e.target.value })}
                placeholder="5.0"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="stopLossPct">止损百分比 (%)</Label>
              <Input
                id="stopLossPct"
                value={formData.stopLossPct}
                onChange={(e) => setFormData({ ...formData, stopLossPct: e.target.value })}
                placeholder="2.0"
              />
            </div>
          </div>
        </div>

        {/* 风险控制 */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">风险控制</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="maxDailyLoss">单日最大亏损 (%)</Label>
              <Input
                id="maxDailyLoss"
                value={formData.maxDailyLoss}
                onChange={(e) => setFormData({ ...formData, maxDailyLoss: e.target.value })}
                placeholder="10.0"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="maxDrawdown">最大回撤 (%)</Label>
              <Input
                id="maxDrawdown"
                value={formData.maxDrawdown}
                onChange={(e) => setFormData({ ...formData, maxDrawdown: e.target.value })}
                placeholder="20.0"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="consecutiveLossLimit">连续亏损限制</Label>
              <Input
                id="consecutiveLossLimit"
                type="number"
                value={formData.consecutiveLossLimit}
                onChange={(e) =>
                  setFormData({ ...formData, consecutiveLossLimit: parseInt(e.target.value) })
                }
                placeholder="3"
              />
            </div>
          </div>
        </div>

        {/* 交易参数 */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">交易参数</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="leverage">杠杆倍数</Label>
              <Input
                id="leverage"
                type="number"
                value={formData.leverage}
                onChange={(e) => setFormData({ ...formData, leverage: parseInt(e.target.value) })}
                placeholder="10"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="positionSize">仓位大小</Label>
              <Input
                id="positionSize"
                value={formData.positionSize}
                onChange={(e) => setFormData({ ...formData, positionSize: e.target.value })}
                placeholder="0.01"
              />
            </div>
          </div>
        </div>

        {/* 状态控制 */}
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div className="space-y-0.5">
            <Label htmlFor="isActive">启用策略</Label>
            <p className="text-sm text-muted-foreground">
              关闭后交易脚本将停止执行策略
            </p>
          </div>
          <Switch
            id="isActive"
            checked={formData.isActive}
            onCheckedChange={(checked) => setFormData({ ...formData, isActive: checked })}
          />
        </div>

        {/* 提示信息 */}
        <div className="bg-muted p-4 rounded-lg">
          <p className="text-sm text-muted-foreground">
            💡 <strong>提示：</strong>配置保存后，Python交易脚本会自动从数据库读取最新配置。
            请确保交易脚本已集成配置读取功能。
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
