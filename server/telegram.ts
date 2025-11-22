/**
 * Telegram Bot通知模块
 * 用于发送交易信号和风险警告到Telegram
 */

interface TelegramMessage {
  text: string;
  parse_mode?: "Markdown" | "HTML";
  disable_notification?: boolean;
}

class TelegramNotifier {
  private botToken: string | undefined;
  private chatId: string | undefined;
  private apiUrl: string;

  constructor() {
    this.botToken = process.env.TELEGRAM_BOT_TOKEN;
    this.chatId = process.env.TELEGRAM_CHAT_ID;
    this.apiUrl = this.botToken
      ? `https://api.telegram.org/bot${this.botToken}`
      : "";
  }

  /**
   * 检查Telegram是否已配置
   */
  isConfigured(): boolean {
    return Boolean(this.botToken && this.chatId);
  }

  /**
   * 发送消息到Telegram
   */
  async sendMessage(message: TelegramMessage): Promise<boolean> {
    if (!this.isConfigured()) {
      console.warn("[Telegram] Not configured, skipping notification");
      return false;
    }

    try {
      const response = await fetch(`${this.apiUrl}/sendMessage`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          chat_id: this.chatId,
          text: message.text,
          parse_mode: message.parse_mode || "Markdown",
          disable_notification: message.disable_notification || false,
        }),
      });

      if (!response.ok) {
        const error = await response.text();
        console.error("[Telegram] Send failed:", error);
        return false;
      }

      console.log("[Telegram] Message sent successfully");
      return true;
    } catch (error) {
      console.error("[Telegram] Error sending message:", error);
      return false;
    }
  }

  /**
   * 发送开仓通知
   */
  async notifyOpenPosition(data: {
    symbol: string;
    side: "long" | "short";
    price: number;
    quantity: number;
    margin: number;
  }): Promise<boolean> {
    const emoji = data.side === "long" ? "📈" : "📉";
    const direction = data.side === "long" ? "做多" : "做空";

    const text = `
${emoji} *开仓通知*

交易对: \`${data.symbol}\`
方向: *${direction}*
价格: $${data.price.toFixed(2)}
数量: ${data.quantity.toFixed(6)}
保证金: ${data.margin.toFixed(2)} USDT

_${new Date().toLocaleString("zh-CN")}_
    `.trim();

    return this.sendMessage({ text });
  }

  /**
   * 发送平仓通知
   */
  async notifyClosePosition(data: {
    symbol: string;
    side: "long" | "short";
    entryPrice: number;
    exitPrice: number;
    pnl: number;
    pnlPct: number;
  }): Promise<boolean> {
    const isProfit = data.pnl > 0;
    const emoji = isProfit ? "✅" : "❌";
    const direction = data.side === "long" ? "做多" : "做空";

    const text = `
${emoji} *平仓通知*

交易对: \`${data.symbol}\`
方向: *${direction}*
入场价: $${data.entryPrice.toFixed(2)}
出场价: $${data.exitPrice.toFixed(2)}
盈亏: ${isProfit ? "+" : ""}${data.pnl.toFixed(2)} USDT (${(data.pnlPct * 100).toFixed(2)}%)

_${new Date().toLocaleString("zh-CN")}_
    `.trim();

    return this.sendMessage({ text, disable_notification: !isProfit });
  }

  /**
   * 发送风险警告
   */
  async notifyRiskAlert(data: {
    level: "info" | "warning" | "error";
    message: string;
    details?: string;
  }): Promise<boolean> {
    const emojiMap = {
      info: "ℹ️",
      warning: "⚠️",
      error: "🚨",
    };

    const emoji = emojiMap[data.level];
    const levelText = {
      info: "信息",
      warning: "警告",
      error: "严重警告",
    }[data.level];

    let text = `
${emoji} *${levelText}*

${data.message}
    `.trim();

    if (data.details) {
      text += `\n\n${data.details}`;
    }

    text += `\n\n_${new Date().toLocaleString("zh-CN")}_`;

    return this.sendMessage({
      text,
      disable_notification: data.level === "info",
    });
  }

  /**
   * 发送每日统计
   */
  async notifyDailyStats(data: {
    totalTrades: number;
    winTrades: number;
    winRate: number;
    totalPnl: number;
    capital: number;
  }): Promise<boolean> {
    const text = `
📊 *每日统计*

总交易: ${data.totalTrades}笔
盈利交易: ${data.winTrades}笔
胜率: ${data.winRate.toFixed(1)}%
总盈亏: ${data.totalPnl > 0 ? "+" : ""}${data.totalPnl.toFixed(2)} USDT
当前资金: ${data.capital.toFixed(2)} USDT

_${new Date().toLocaleString("zh-CN")}_
    `.trim();

    return this.sendMessage({ text });
  }

  /**
   * 发送机器人状态变更通知
   */
  async notifyBotStatus(data: {
    isRunning: boolean;
    reason?: string;
  }): Promise<boolean> {
    const emoji = data.isRunning ? "▶️" : "⏸️";
    const status = data.isRunning ? "已启动" : "已停止";

    let text = `
${emoji} *机器人状态*

状态: *${status}*
    `.trim();

    if (data.reason) {
      text += `\n原因: ${data.reason}`;
    }

    text += `\n\n_${new Date().toLocaleString("zh-CN")}_`;

    return this.sendMessage({ text });
  }
}

// 单例实例
export const telegramNotifier = new TelegramNotifier();

// 导出类型
export type { TelegramMessage };
