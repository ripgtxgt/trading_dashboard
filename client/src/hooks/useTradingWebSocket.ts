import { useEffect, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { toast } from "sonner";

interface TradingState {
  isRunning: boolean;
  balance: number;
  equity: number;
  unrealizedPnl: number;
  totalPnl: number;
  totalPnlPct: number;
  currentStage: string;
  winRate: number;
  totalTrades: number;
}

interface TradingSignal {
  type: "long" | "short";
  price: number;
  timestamp: number;
}

interface NewTrade {
  symbol: string;
  direction: "long" | "short";
  entryPrice: number;
  exitPrice: number;
  quantity: number;
  pnl: number;
  pnlPct: string;
  exitTime: string;
}

export function useTradingWebSocket() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [tradingState, setTradingState] = useState<TradingState | null>(null);
  const [latestSignal, setLatestSignal] = useState<TradingSignal | null>(null);
  const [latestTrade, setLatestTrade] = useState<NewTrade | null>(null);

  useEffect(() => {
    // 连接WebSocket
    const newSocket = io({
      path: "/api/socket.io",
    });

    newSocket.on("connect", () => {
      console.log("[Trading WebSocket] Connected");
      setConnected(true);
    });

    newSocket.on("disconnect", () => {
      console.log("[Trading WebSocket] Disconnected");
      setConnected(false);
    });

    // 监听交易状态更新
    newSocket.on("trading:state", (state: TradingState) => {
      console.log("[Trading WebSocket] Received trading state:", state);
      setTradingState(state);
    });

    // 监听交易信号
    newSocket.on("trading:signal", (signal: TradingSignal) => {
      console.log("[Trading WebSocket] Received trading signal:", signal);
      setLatestSignal(signal);
      
      // 显示通知
      const direction = signal.type === "long" ? "做多" : "做空";
      toast.info(`交易信号: ${direction}`, {
        description: `价格: ${signal.price}`,
      });
    });

    // 监听新交易
    newSocket.on("trading:newTrade", (trade: NewTrade) => {
      console.log("[Trading WebSocket] Received new trade:", trade);
      setLatestTrade(trade);
      
      // 显示通知
      const isProfit = parseFloat(trade.pnl.toString()) > 0;
      if (isProfit) {
        toast.success(`交易完成: +${trade.pnl} USDT`, {
          description: `${trade.symbol} ${trade.direction} (${trade.pnlPct})`,
        });
      } else {
        toast.error(`交易完成: ${trade.pnl} USDT`, {
          description: `${trade.symbol} ${trade.direction} (${trade.pnlPct})`,
        });
      }
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  // 请求当前状态
  const requestState = useCallback(() => {
    if (socket && connected) {
      socket.emit("request:state");
    }
  }, [socket, connected]);

  return {
    socket,
    connected,
    tradingState,
    latestSignal,
    latestTrade,
    requestState,
  };
}
