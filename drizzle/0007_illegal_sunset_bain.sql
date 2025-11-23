CREATE TABLE `risk_config` (
	`id` int AUTO_INCREMENT NOT NULL,
	`low_vol_threshold` varchar(20) NOT NULL DEFAULT '0.02',
	`medium_vol_threshold` varchar(20) NOT NULL DEFAULT '0.05',
	`high_vol_threshold` varchar(20) NOT NULL DEFAULT '0.08',
	`extreme_vol_threshold` varchar(20) NOT NULL DEFAULT '0.10',
	`low_risk_multiplier` varchar(20) NOT NULL DEFAULT '1.0',
	`medium_risk_multiplier` varchar(20) NOT NULL DEFAULT '0.7',
	`high_risk_multiplier` varchar(20) NOT NULL DEFAULT '0.4',
	`extreme_risk_multiplier` varchar(20) NOT NULL DEFAULT '0.0',
	`atr_period` int NOT NULL DEFAULT 14,
	`volatility_period` int NOT NULL DEFAULT 30,
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `risk_config_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `risk_history` (
	`id` int AUTO_INCREMENT NOT NULL,
	`event_type` enum('volatility','pause','resume','position_adjust') NOT NULL,
	`risk_level` enum('low','medium','high','extreme'),
	`volatility` varchar(20),
	`atr` varchar(20),
	`position_multiplier` varchar(20),
	`reason` text,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `risk_history_id` PRIMARY KEY(`id`)
);
