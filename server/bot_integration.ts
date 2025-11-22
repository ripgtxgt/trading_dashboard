import { exec } from "child_process";
import { promisify } from "util";
import fs from "fs/promises";
import path from "path";

const execAsync = promisify(exec);

// 机器人日志文件路径
const BOT_LOG_DIR = "/home/ubuntu/upload";
const BOT_SCRIPT_PATH = "/home/ubuntu/upload/trading_rolling.py";

/**
 * 检查机器人是否正在运行
 */
export async function isBotRunning(): Promise<boolean> {
  try {
    const { stdout } = await execAsync("ps aux | grep 'trading_rolling.py' | grep -v grep");
    return stdout.trim().length > 0;
  } catch {
    return false;
  }
}

/**
 * 启动交易机器人
 */
export async function startBot(): Promise<{ success: boolean; message: string; pid?: number }> {
  try {
    const isRunning = await isBotRunning();
    if (isRunning) {
      return { success: false, message: "机器人已在运行中" };
    }

    // 检查脚本是否存在
    try {
      await fs.access(BOT_SCRIPT_PATH);
    } catch {
      return { success: false, message: "交易脚本不存在" };
    }

    // 启动机器人（后台运行）
    const { stdout } = await execAsync(
      `nohup python3 ${BOT_SCRIPT_PATH} > ${BOT_LOG_DIR}/bot_output.log 2>&1 & echo $!`
    );
    
    const pid = parseInt(stdout.trim());
    
    return { 
      success: true, 
      message: "机器人启动成功", 
      pid 
    };
  } catch (error) {
    return { 
      success: false, 
      message: `启动失败: ${error instanceof Error ? error.message : String(error)}` 
    };
  }
}

/**
 * 停止交易机器人
 */
export async function stopBot(): Promise<{ success: boolean; message: string }> {
  try {
    const isRunning = await isBotRunning();
    if (!isRunning) {
      return { success: false, message: "机器人未在运行" };
    }

    // 获取进程ID并终止
    const { stdout } = await execAsync("ps aux | grep 'trading_rolling.py' | grep -v grep | awk '{print $2}'");
    const pids = stdout.trim().split("\n").filter(Boolean);
    
    if (pids.length === 0) {
      return { success: false, message: "未找到机器人进程" };
    }

    // 终止所有相关进程
    for (const pid of pids) {
      await execAsync(`kill -15 ${pid}`);
    }

    return { success: true, message: "机器人已停止" };
  } catch (error) {
    return { 
      success: false, 
      message: `停止失败: ${error instanceof Error ? error.message : String(error)}` 
    };
  }
}

/**
 * 获取机器人状态
 */
export async function getBotStatus(): Promise<{
  running: boolean;
  uptime?: string;
  lastLog?: string;
}> {
  const running = await isBotRunning();
  
  if (!running) {
    return { running: false };
  }

  try {
    // 获取进程启动时间
    const { stdout: psOutput } = await execAsync(
      "ps aux | grep 'trading_rolling.py' | grep -v grep | awk '{print $9}'"
    );
    const startTime = psOutput.trim().split("\n")[0];

    // 读取最新日志
    const logFiles = await fs.readdir(BOT_LOG_DIR);
    const tradingLogs = logFiles
      .filter(f => f.startsWith("trading_rolling_") && f.endsWith(".log"))
      .sort()
      .reverse();
    
    let lastLog = "";
    if (tradingLogs.length > 0) {
      const logPath = path.join(BOT_LOG_DIR, tradingLogs[0]);
      const logContent = await fs.readFile(logPath, "utf-8");
      const lines = logContent.trim().split("\n");
      lastLog = lines[lines.length - 1] || "";
    }

    return {
      running: true,
      uptime: startTime,
      lastLog,
    };
  } catch (error) {
    return { running: true };
  }
}

/**
 * 读取机器人日志
 */
export async function getBotLogs(lines: number = 100): Promise<string[]> {
  try {
    const logFiles = await fs.readdir(BOT_LOG_DIR);
    const tradingLogs = logFiles
      .filter(f => f.startsWith("trading_rolling_") && f.endsWith(".log"))
      .sort()
      .reverse();
    
    if (tradingLogs.length === 0) {
      return [];
    }

    const logPath = path.join(BOT_LOG_DIR, tradingLogs[0]);
    const logContent = await fs.readFile(logPath, "utf-8");
    const allLines = logContent.trim().split("\n");
    
    return allLines.slice(-lines);
  } catch (error) {
    return [];
  }
}

/**
 * 解析日志中的交易信号
 */
export async function parseLatestSignals(): Promise<{
  timestamp: string;
  signal: "buy" | "sell" | "none";
  price?: number;
  ma5?: number;
  ma20?: number;
}[]> {
  try {
    const logs = await getBotLogs(50);
    const signals: {
      timestamp: string;
      signal: "buy" | "sell" | "none";
      price?: number;
      ma5?: number;
      ma20?: number;
    }[] = [];

    for (const line of logs) {
      // 解析信号行
      if (line.includes("信号分析")) {
        const timestampMatch = line.match(/\[(.*?)\]/);
        const signalMatch = line.match(/信号: (买入|卖出|无信号)/);
        const priceMatch = line.match(/当前价格: ([\d.]+)/);
        const ma5Match = line.match(/MA5: ([\d.]+)/);
        const ma20Match = line.match(/MA20: ([\d.]+)/);

        if (timestampMatch && signalMatch) {
          signals.push({
            timestamp: timestampMatch[1],
            signal: signalMatch[1] === "买入" ? "buy" : signalMatch[1] === "卖出" ? "sell" : "none",
            price: priceMatch ? parseFloat(priceMatch[1]) : undefined,
            ma5: ma5Match ? parseFloat(ma5Match[1]) : undefined,
            ma20: ma20Match ? parseFloat(ma20Match[1]) : undefined,
          });
        }
      }
    }

    return signals;
  } catch (error) {
    return [];
  }
}
