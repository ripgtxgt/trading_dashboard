CREATE TABLE `backtest_history` (
	`id` int AUTO_INCREMENT NOT NULL,
	`short_ma_period` int NOT NULL,
	`long_ma_period` int NOT NULL,
	`timeframe` varchar(10) NOT NULL,
	`sensitivity` varchar(20) NOT NULL,
	`total_trades` int NOT NULL DEFAULT 0,
	`win_trades` int NOT NULL DEFAULT 0,
	`win_rate` varchar(20) NOT NULL DEFAULT '0',
	`total_pnl` varchar(20) NOT NULL DEFAULT '0',
	`sharpe_ratio` varchar(20) NOT NULL DEFAULT '0',
	`max_drawdown` varchar(20) NOT NULL DEFAULT '0',
	`avg_win` varchar(20) NOT NULL DEFAULT '0',
	`avg_loss` varchar(20) NOT NULL DEFAULT '0',
	`composite_score` varchar(20) NOT NULL DEFAULT '0',
	`created_at` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `backtest_history_id` PRIMARY KEY(`id`)
);
