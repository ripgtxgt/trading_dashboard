ALTER TABLE `positions` ADD `symbol` varchar(20) DEFAULT 'XBTUSDTM' NOT NULL;--> statement-breakpoint
ALTER TABLE `positions` ADD `quantity` varchar(20) NOT NULL;--> statement-breakpoint
ALTER TABLE `trades` ADD `symbol` varchar(20) DEFAULT 'XBTUSDTM' NOT NULL;--> statement-breakpoint
ALTER TABLE `trades` ADD `quantity` varchar(20) NOT NULL;--> statement-breakpoint
ALTER TABLE `trades` ADD `fee` varchar(20) DEFAULT '0' NOT NULL;