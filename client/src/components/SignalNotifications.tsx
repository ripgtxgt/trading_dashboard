import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bell, TrendingUp, TrendingDown, AlertTriangle } from "lucide-react";
import { toast } from "sonner";
import { io, Socket } from "socket.io-client";

interface Signal {
  type: string;
  data: any;
  timestamp: string;
}

export function SignalNotifications() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [connected, setConnected] = useState(false);
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    // 连接WebSocket
    const newSocket = io({
      path: "/api/socket.io",
    });

    newSocket.on("connect", () => {
      console.log("[WebSocket] Connected");
      setConnected(true);
      toast.success("实时信号已连接");
    });

    newSocket.on("disconnect", () => {
      console.log("[WebSocket] Disconnected");
      setConnected(false);
      toast.error("实时信号已断开");
    });

    // 监听交易信号
    newSocket.on("trading-signal", (signal: Signal) => {
      console.log("[WebSocket] Received signal:", signal);
      
      setSignals(prev => [signal, ...prev].slice(0, 10)); // 只保留最近10条
      
      // 显示通知
      if (signal.type === "open") {
        toast.success(`开仓信号: ${signal.data.side} @ ${signal.data.price}`, {
          description: `${signal.data.symbol} x${signal.data.quantity}`,
        });
      } else if (signal.type === "close") {
        const isProfit = signal.data.pnl > 0;
        if (isProfit) {
          toast.success(`平仓盈利: +${signal.data.pnl} USDT`, {
            description: `${signal.data.symbol} ${signal.data.side} (${(signal.data.pnlPct * 100).toFixed(2)}%)`,
          });
        } else {
          toast.error(`平仓亏损: ${signal.data.pnl} USDT`, {
            description: `${signal.data.symbol} ${signal.data.side} (${(signal.data.pnlPct * 100).toFixed(2)}%)`,
          });
        }
      } else if (signal.type === "alert") {
        const level = signal.data.level;
        if (level === "error") {
          toast.error(signal.data.message);
        } else if (level === "warning") {
          toast.warning(signal.data.message);
        } else {
          toast.info(signal.data.message);
        }
      }
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const getSignalIcon = (type: string) => {
    switch (type) {
      case "open":
        return <TrendingUp className="h-4 w-4" />;
      case "close":
        return <TrendingDown className="h-4 w-4" />;
      case "alert":
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Bell className="h-4 w-4" />;
    }
  };

  const getSignalColor = (signal: Signal) => {
    if (signal.type === "open") {
      return signal.data.side === "long" ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500";
    } else if (signal.type === "close") {
      return signal.data.pnl > 0 ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500";
    } else if (signal.type === "alert") {
      const level = signal.data.level;
      if (level === "error") return "bg-red-500/10 text-red-500";
      if (level === "warning") return "bg-yellow-500/10 text-yellow-500";
      return "bg-blue-500/10 text-blue-500";
    }
    return "bg-gray-500/10 text-gray-500";
  };

  const formatSignalText = (signal: Signal) => {
    if (signal.type === "open") {
      return `开仓 ${signal.data.side} @ ${signal.data.price}`;
    } else if (signal.type === "close") {
      return `平仓 ${signal.data.pnl > 0 ? "+" : ""}${signal.data.pnl} USDT`;
    } else if (signal.type === "alert") {
      return signal.data.message;
    }
    return "未知信号";
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>实时信号</CardTitle>
            <CardDescription>交易信号实时推送</CardDescription>
          </div>
          <Badge variant={connected ? "default" : "secondary"}>
            {connected ? "已连接" : "未连接"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {signals.length === 0 ? (
          <div className="text-center text-muted-foreground py-8">
            <Bell className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>暂无信号</p>
          </div>
        ) : (
          <div className="space-y-2">
            {signals.map((signal, index) => (
              <div
                key={index}
                className={`flex items-center gap-3 p-3 rounded-lg ${getSignalColor(signal)}`}
              >
                {getSignalIcon(signal.type)}
                <div className="flex-1">
                  <p className="font-medium">{formatSignalText(signal)}</p>
                  <p className="text-xs opacity-70">
                    {new Date(signal.timestamp).toLocaleString("zh-CN")}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
