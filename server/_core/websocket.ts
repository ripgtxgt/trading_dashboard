import { Server as HTTPServer } from "http";
import { Server as SocketIOServer } from "socket.io";

let io: SocketIOServer | null = null;

export function initializeWebSocket(server: HTTPServer) {
  io = new SocketIOServer(server, {
    cors: {
      origin: "*",
      methods: ["GET", "POST"],
    },
    path: "/api/socket.io",
  });

  io.on("connection", (socket) => {
    console.log(`[WebSocket] Client connected: ${socket.id}`);

    socket.on("disconnect", () => {
      console.log(`[WebSocket] Client disconnected: ${socket.id}`);
    });
  });

  return io;
}

export function getIO(): SocketIOServer {
  if (!io) {
    throw new Error("WebSocket not initialized");
  }
  return io;
}

// 发送交易信号通知
export function emitTradingSignal(signal: {
  type: "long" | "short";
  price: number;
  shortMa: number;
  longMa: number;
  timestamp: number;
}) {
  if (io) {
    io.emit("trading:signal", signal);
    console.log(`[WebSocket] Emitted trading signal: ${signal.type} at ${signal.price}`);
  }
}

// 发送交易状态更新
export function emitTradingState(state: {
  isRunning: boolean;
  capital: number;
  currentStage: string;
}) {
  if (io) {
    io.emit("trading:state", state);
  }
}

// 发送新交易记录
export function emitNewTrade(trade: {
  id: number;
  direction: string;
  entryPrice: string;
  exitPrice: string;
  pnl: string;
  pnlPct: string;
}) {
  if (io) {
    io.emit("trading:newTrade", trade);
    console.log(`[WebSocket] Emitted new trade: ${trade.direction} PnL: ${trade.pnl}`);
  }
}
