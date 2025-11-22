CREATE TABLE `symbol_configs` (
	`id` int AUTO_INCREMENT NOT NULL,
	`symbol` varchar(20) NOT NULL,
	`display_name` varchar(50) NOT NULL,
	`is_active` int NOT NULL DEFAULT 1,
	`initial_capital` varchar(20) NOT NULL DEFAULT '10',
	`leverage` int NOT NULL DEFAULT 10,
	`short_ma_period` int NOT NULL DEFAULT 5,
	`long_ma_period` int NOT NULL DEFAULT 20,
	`timeframe` varchar(10) NOT NULL DEFAULT '1h',
	`sensitivity` enum('loose','standard','strict') NOT NULL DEFAULT 'standard',
	`created_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `symbol_configs_id` PRIMARY KEY(`id`),
	CONSTRAINT `symbol_configs_symbol_unique` UNIQUE(`symbol`)
);
