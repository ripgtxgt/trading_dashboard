import { Router } from "express";
import { getIO } from "./_core/websocket";

const router = Router();

/**
 * 接收来自Python脚本的信号并广播到所有WebSocket客户端
 */
router.post("/api/signal", (req, res) => {
  try {
    const { type, data, timestamp } = req.body;
    
    if (!type || !data) {
      return res.status(400).json({ error: "Missing required fields" });
    }
    
    // 获取WebSocket服务器实例
    const io = getIO();
    
    if (!io) {
      console.warn("[Signal API] WebSocket server not available");
      return res.status(503).json({ error: "WebSocket server not available" });
    }
    
    // 广播信号到所有连接的客户端
    io.emit("trading-signal", {
      type,
      data,
      timestamp: timestamp || new Date().toISOString()
    });
    
    console.log(`[Signal API] Broadcasted ${type} signal to clients`);
    
    return res.json({ success: true });
    
  } catch (error) {
    console.error("[Signal API] Error:", error);
    return res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
