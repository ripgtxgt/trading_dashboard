CREATE TABLE `param_simulations` (
	`id` int AUTO_INCREMENT NOT NULL,
	`param_id` int NOT NULL,
	`signal_count` int NOT NULL DEFAULT 0,
	`long_signals` int NOT NULL DEFAULT 0,
	`short_signals` int NOT NULL DEFAULT 0,
	`sample_period` varchar(20) NOT NULL,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `param_simulations_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `strategy_params` (
	`id` int AUTO_INCREMENT NOT NULL,
	`short_ma_period` int NOT NULL DEFAULT 5,
	`long_ma_period` int NOT NULL DEFAULT 20,
	`timeframe` varchar(10) NOT NULL DEFAULT '1h',
	`sensitivity` enum('loose','standard','strict') NOT NULL DEFAULT 'standard',
	`is_active` int NOT NULL DEFAULT 1,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	`applied_at` timestamp,
	CONSTRAINT `strategy_params_id` PRIMARY KEY(`id`)
);
