CREATE TABLE `strategy_config` (
	`id` int AUTO_INCREMENT NOT NULL,
	`symbol` varchar(20) NOT NULL DEFAULT 'XBTUSDTM',
	`rollMultiplier` varchar(20) NOT NULL DEFAULT '2.0',
	`takeProfitPct` varchar(20) NOT NULL DEFAULT '5.0',
	`stopLossPct` varchar(20) NOT NULL DEFAULT '2.0',
	`maxDailyLoss` varchar(20) NOT NULL DEFAULT '10.0',
	`maxDrawdown` varchar(20) NOT NULL DEFAULT '20.0',
	`consecutiveLossLimit` int NOT NULL DEFAULT 3,
	`leverage` int NOT NULL DEFAULT 10,
	`positionSize` varchar(20) NOT NULL DEFAULT '0.01',
	`isActive` enum('true','false') NOT NULL DEFAULT 'true',
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `strategy_config_id` PRIMARY KEY(`id`)
);
