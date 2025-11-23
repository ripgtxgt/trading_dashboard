import { publicProcedure, router } from "./_core/trpc";
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";

const execAsync = promisify(exec);

/**
 * 风险数据API
 * 从Python风险管理模块获取实时数据
 */
export const riskDataRouter = router({
  /**
   * 获取当前风险状态
   */
  getCurrentRisk: publicProcedure.query(async () => {
    try {
      const scriptPath = path.join(process.cwd(), "scripts", "get_risk_status.py");
      const { stdout } = await execAsync(`python3 "${scriptPath}"`, {
        timeout: 10000,
      });
      
      const data = JSON.parse(stdout);
      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("[RiskAPI] 获取风险状态失败:", error);
      // 返回默认数据
      return {
        success: false,
        data: {
          volatility: {
            atr: 0,
            historical: 0,
            trend: "stable" as const,
          },
          riskLevel: "low" as const,
          positionMultiplier: 1.0,
          isPaused: false,
          lastUpdate: new Date().toISOString(),
        },
      };
    }
  }),

  /**
   * 获取风险历史数据
   */
  getRiskHistory: publicProcedure.query(async () => {
    try {
      const scriptPath = path.join(process.cwd(), "scripts", "get_risk_history.py");
      const { stdout } = await execAsync(`python3 "${scriptPath}"`, {
        timeout: 15000,
      });
      
      const data = JSON.parse(stdout);
      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("[RiskAPI] 获取风险历史失败:", error);
      return {
        success: false,
        data: {
          volatilityHistory: [],
          pauseEvents: [],
          positionAdjustments: [],
        },
      };
    }
  }),
});
