import { z } from "zod";
import { publicProcedure, router } from "./_core/trpc";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

/**
 * System Monitor Router
 * Provides endpoints to monitor PM2 processes and system status
 */

interface PM2Process {
  name: string;
  pm_id: number;
  status: string;
  cpu: number;
  memory: number;
  uptime: number;
  restarts: number;
}

interface SystemStatus {
  processes: PM2Process[];
  timestamp: number;
  healthy: boolean;
}

/**
 * Parse PM2 list output to structured data
 */
function parsePM2List(output: string): PM2Process[] {
  try {
    const data = JSON.parse(output);
    return data.map((proc: any) => ({
      name: proc.name || "unknown",
      pm_id: proc.pm_id || 0,
      status: proc.pm2_env?.status || "unknown",
      cpu: proc.monit?.cpu || 0,
      memory: proc.monit?.memory || 0,
      uptime: proc.pm2_env?.pm_uptime || 0,
      restarts: proc.pm2_env?.restart_time || 0,
    }));
  } catch (error) {
    console.error("[SystemMonitor] Failed to parse PM2 output:", error);
    return [];
  }
}

/**
 * Get PM2 process list
 */
async function getPM2Processes(): Promise<PM2Process[]> {
  try {
    const { stdout } = await execAsync("pm2 jlist");
    return parsePM2List(stdout);
  } catch (error) {
    console.error("[SystemMonitor] Failed to get PM2 processes:", error);
    return [];
  }
}

/**
 * Restart a PM2 process by name
 */
async function restartPM2Process(name: string): Promise<boolean> {
  try {
    await execAsync(`pm2 restart ${name}`);
    return true;
  } catch (error) {
    console.error(`[SystemMonitor] Failed to restart process ${name}:`, error);
    return false;
  }
}

/**
 * Stop a PM2 process by name
 */
async function stopPM2Process(name: string): Promise<boolean> {
  try {
    await execAsync(`pm2 stop ${name}`);
    return true;
  } catch (error) {
    console.error(`[SystemMonitor] Failed to stop process ${name}:`, error);
    return false;
  }
}

/**
 * Start a PM2 process by name
 */
async function startPM2Process(name: string): Promise<boolean> {
  try {
    await execAsync(`pm2 start ${name}`);
    return true;
  } catch (error) {
    console.error(`[SystemMonitor] Failed to start process ${name}:`, error);
    return false;
  }
}

export const systemMonitorRouter = router({
  /**
   * Get all PM2 processes status
   */
  getProcesses: publicProcedure.query(async (): Promise<SystemStatus> => {
    const processes = await getPM2Processes();
    const healthy = processes.every((p) => p.status === "online");

    return {
      processes,
      timestamp: Date.now(),
      healthy,
    };
  }),

  /**
   * Restart a specific process
   */
  restartProcess: publicProcedure
    .input(
      z.object({
        name: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      const success = await restartPM2Process(input.name);
      return {
        success,
        message: success
          ? `Process ${input.name} restarted successfully`
          : `Failed to restart process ${input.name}`,
      };
    }),

  /**
   * Stop a specific process
   */
  stopProcess: publicProcedure
    .input(
      z.object({
        name: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      const success = await stopPM2Process(input.name);
      return {
        success,
        message: success
          ? `Process ${input.name} stopped successfully`
          : `Failed to stop process ${input.name}`,
      };
    }),

  /**
   * Start a specific process
   */
  startProcess: publicProcedure
    .input(
      z.object({
        name: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      const success = await startPM2Process(input.name);
      return {
        success,
        message: success
          ? `Process ${input.name} started successfully`
          : `Failed to start process ${input.name}`,
      };
    }),

  /**
   * Restart all processes
   */
  restartAll: publicProcedure.mutation(async () => {
    try {
      await execAsync("pm2 restart all");
      return {
        success: true,
        message: "All processes restarted successfully",
      };
    } catch (error) {
      console.error("[SystemMonitor] Failed to restart all processes:", error);
      return {
        success: false,
        message: "Failed to restart all processes",
      };
    }
  }),
});
