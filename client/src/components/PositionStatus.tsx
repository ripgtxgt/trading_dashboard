import { useEffect, useState } from "react";
import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, TrendingUp, TrendingDown, DollarSign, Activity } from "lucide-react";

export default function PositionStatus() {
  const { data: position, isLoading, refetch } = trpc.trading.getPosition.useQuery();
  const [currentPrice, setCurrentPrice] = useState<number | null>(null);
  const [unrealizedPnl, setUnrealizedPnl] = useState<number>(0);
  const [unrealizedPnlPct, setUnrealizedPnlPct] = useState<number>(0);

  // Auto refresh every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refetch();
    }, 5000);
    return () => clearInterval(interval);
  }, [refetch]);

  // Calculate unrealized PnL when position or current price changes
  useEffect(() => {
    if (position && currentPrice) {
      const entryPrice = parseFloat(position.entryPrice);
      const quantity = parseFloat(position.quantity);
      
      let pnl = 0;
      if (position.direction === "long") {
        pnl = (currentPrice - entryPrice) * quantity;
      } else {
        pnl = (entryPrice - currentPrice) * quantity;
      }
      
      const pnlPct = (pnl / parseFloat(position.margin)) * 100;
      
      setUnrealizedPnl(pnl);
      setUnrealizedPnlPct(pnlPct);
    }
  }, [position, currentPrice]);

  // Fetch current price (mock for now, should be from WebSocket or API)
  useEffect(() => {
    if (position) {
      // TODO: Replace with real-time price from WebSocket or API
      // For now, use entry price as current price
      setCurrentPrice(parseFloat(position.entryPrice));
    }
  }, [position]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Current Position</CardTitle>
          <CardDescription>Real-time position status and P&L</CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (!position) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Current Position</CardTitle>
          <CardDescription>Real-time position status and P&L</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
            <Activity className="h-12 w-12 mb-3 opacity-50" />
            <p className="text-lg font-medium">No Open Position</p>
            <p className="text-sm">Waiting for trading signal...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const isLong = position.direction === "long";
  const isProfitable = unrealizedPnl >= 0;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Current Position</CardTitle>
            <CardDescription>Real-time position status and P&L</CardDescription>
          </div>
          <Badge variant={isLong ? "default" : "destructive"} className="text-sm px-3 py-1">
            {isLong ? (
              <>
                <TrendingUp className="mr-1 h-4 w-4" />
                LONG
              </>
            ) : (
              <>
                <TrendingDown className="mr-1 h-4 w-4" />
                SHORT
              </>
            )}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Symbol and Stage */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Symbol</p>
            <p className="text-lg font-semibold">{position.symbol || "XBTUSDTM"}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Stage</p>
            <p className="text-lg font-semibold">{position.stage}</p>
          </div>
        </div>

        {/* Price Information */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Entry Price</p>
            <p className="text-lg font-semibold">${parseFloat(position.entryPrice).toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Current Price</p>
            <p className="text-lg font-semibold">
              ${currentPrice?.toFixed(2) || parseFloat(position.entryPrice).toFixed(2)}
            </p>
          </div>
        </div>

        {/* Position Size */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Quantity</p>
            <p className="text-lg font-semibold">{parseFloat(position.quantity).toFixed(4)} BTC</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Margin</p>
            <p className="text-lg font-semibold">${parseFloat(position.margin).toFixed(2)}</p>
          </div>
        </div>

        {/* Stop Loss & Take Profit */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Stop Loss</p>
            <p className="text-lg font-semibold text-red-600">
              {parseFloat(position.stopLossPct).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Take Profit</p>
            <p className="text-lg font-semibold text-green-600">
              {parseFloat(position.takeProfitPct).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Unrealized P&L */}
        <div className="pt-4 border-t">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-muted-foreground" />
              <p className="text-sm font-medium text-muted-foreground">Unrealized P&L</p>
            </div>
            <div className="text-right">
              <p className={`text-2xl font-bold ${isProfitable ? "text-green-600" : "text-red-600"}`}>
                {isProfitable ? "+" : ""}${unrealizedPnl.toFixed(2)}
              </p>
              <p className={`text-sm font-medium ${isProfitable ? "text-green-600" : "text-red-600"}`}>
                {isProfitable ? "+" : ""}{unrealizedPnlPct.toFixed(2)}%
              </p>
            </div>
          </div>
        </div>

        {/* Entry Time */}
        <div className="pt-2 text-xs text-muted-foreground text-center">
          Opened at {new Date(position.entryTime).toLocaleString()}
        </div>
      </CardContent>
    </Card>
  );
}
