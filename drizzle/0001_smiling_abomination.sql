CREATE TABLE `balance_snapshots` (
	`id` int AUTO_INCREMENT NOT NULL,
	`capital` varchar(20) NOT NULL,
	`timestamp` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `balance_snapshots_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `bot_state` (
	`id` int AUTO_INCREMENT NOT NULL,
	`is_running` int NOT NULL DEFAULT 0,
	`capital` varchar(20) NOT NULL,
	`initial_capital` varchar(20) NOT NULL,
	`current_stage` varchar(20) NOT NULL,
	`daily_trades` int NOT NULL DEFAULT 0,
	`daily_pnl` varchar(20) NOT NULL DEFAULT '0',
	`total_trades` int NOT NULL DEFAULT 0,
	`emergency_stopped` int NOT NULL DEFAULT 0,
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `bot_state_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `positions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`direction` enum('long','short') NOT NULL,
	`entry_price` varchar(20) NOT NULL,
	`margin` varchar(20) NOT NULL,
	`stop_loss_pct` varchar(20) NOT NULL,
	`take_profit_pct` varchar(20) NOT NULL,
	`stage` varchar(20) NOT NULL,
	`entry_time` timestamp NOT NULL,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `positions_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `trades` (
	`id` int AUTO_INCREMENT NOT NULL,
	`direction` enum('long','short') NOT NULL,
	`entry_price` varchar(20) NOT NULL,
	`exit_price` varchar(20) NOT NULL,
	`margin` varchar(20) NOT NULL,
	`pnl` varchar(20) NOT NULL,
	`pnl_pct` varchar(20) NOT NULL,
	`reason` varchar(50) NOT NULL,
	`stage` varchar(20) NOT NULL,
	`entry_time` timestamp NOT NULL,
	`exit_time` timestamp NOT NULL,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `trades_id` PRIMARY KEY(`id`)
);
