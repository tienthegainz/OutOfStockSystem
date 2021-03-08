BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `users` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`username`	TEXT NOT NULL UNIQUE,
	`password`	TEXT NOT NULL,
	`admin`	INTEGER DEFAULT 0
);
INSERT INTO `users` VALUES (1,'admin','$pbkdf2-sha256$29000$Ocd4D8FYy9n731sLAeAc4w$.KJRQu6tYrxDC7D9CHeQAkVvZLVG2FM3Kn/uttABmn4',1);
INSERT INTO `users` VALUES (2,'worker1','$pbkdf2-sha256$29000$//9fS2ktRShF6L0XojTmfA$f0dpE19fksOCvzSS3NkyfbvOaJFpQ8wwOCc.jZgqHA0',0);
CREATE TABLE IF NOT EXISTS `revoked_token` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`jti`	TEXT NOT NULL,
	`is_logout`	INTEGER NOT NULL,
	`is_expired`	INTEGER NOT NULL,
	`revoked_at`	TEXT NOT NULL
);
INSERT INTO `revoked_token` VALUES (1,'c46037bb-bd9c-4569-9b50-e6db1d8ebfc5',1,0,'2021-03-06 03:28:41.078682');
INSERT INTO `revoked_token` VALUES (2,'17d5405f-d91b-4585-976f-dcd6f31edfb1',0,1,'2021-03-06 03:38:07.792580');
INSERT INTO `revoked_token` VALUES (3,'a0aaf147-80aa-4f08-8c32-28a679cbab39',1,0,'2021-03-06 03:39:49.703382');
INSERT INTO `revoked_token` VALUES (4,'c221ebb6-9c95-41ae-9a73-ff7ffe5402b8',1,0,'2021-03-06 03:47:38.395150');
CREATE TABLE IF NOT EXISTS `products` (
	`id`	INTEGER NOT NULL,
	`name`	VARCHAR NOT NULL,
	`price`	INTEGER NOT NULL,
	PRIMARY KEY(`id`)
);
INSERT INTO `products` VALUES (1,'Gucci perfume',1500000);
INSERT INTO `products` VALUES (2,'Lavie bottle',10000);
CREATE TABLE IF NOT EXISTS `product_images` (
	`id`	INTEGER NOT NULL,
	`url`	VARCHAR NOT NULL,
	`product_id`	INTEGER NOT NULL,
	FOREIGN KEY(`product_id`) REFERENCES `products`(`id`),
	PRIMARY KEY(`id`)
);
INSERT INTO `product_images` VALUES (1,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/products%2F1%2Fc239xq.jpg?alt=media',1);
INSERT INTO `product_images` VALUES (2,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/products%2F1%2F8fzid6.jpg?alt=media',1);
INSERT INTO `product_images` VALUES (3,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/products%2F1%2Frf3b6h.jpg?alt=media',1);
INSERT INTO `product_images` VALUES (4,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/products%2F2%2Fhqf8ru.jpg?alt=media',2);
INSERT INTO `product_images` VALUES (5,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/products%2F2%2Fm7jkj0.jpg?alt=media',2);
INSERT INTO `product_images` VALUES (6,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/products%2F2%2Fkv5kqg.jpg?alt=media',2);
CREATE TABLE IF NOT EXISTS `log_texts` (
	`id`	INTEGER NOT NULL,
	`message`	VARCHAR NOT NULL,
	`time`	VARCHAR NOT NULL,
	`camera_id`	INTEGER NOT NULL,
	PRIMARY KEY(`id`),
	FOREIGN KEY(`camera_id`) REFERENCES `cameras`(`id`)
);
INSERT INTO `log_texts` VALUES (1,'[2021/02/22 05:00:22] Random logger','2021/02/22 05:00:22',1);
INSERT INTO `log_texts` VALUES (2,'[2021/02/23 11:00:22] Random logger','2021/02/23 11:00:22',1);
INSERT INTO `log_texts` VALUES (3,'[2021/02/23 11:05:22] Random logger','2021/02/23 11:05:22',1);
INSERT INTO `log_texts` VALUES (4,'[2021/02/23 22:00:22] kcqxamzYoMODq9VV71AEkcqxamzYoMODq9VV71AEkcqxamzYoMODq9VV71AEkcqxamzYoMODq9VV71AE','2021/02/23 22:00:22',1);
INSERT INTO `log_texts` VALUES (5,'[2021/02/25 05:00:22] Random logger','2021/02/25 05:00:22',1);
INSERT INTO `log_texts` VALUES (6,'[2021/02/25 06:00:22] Random logger','2021/02/25 06:00:22',1);
INSERT INTO `log_texts` VALUES (7,'[2021/02/25 08:00:22] Vea4jXUb5Hlt072wWCqNVea4jXUb5Hlt072wWCqNVea4jXUb5Hlt072wWCqNVea4jXUb5Hlt072wWCqNVea4jXUb5Hlt072wWCqN','2021/02/25 08:00:22',1);
INSERT INTO `log_texts` VALUES (8,'[2021/02/25 10:00:22] Random logger','2021/02/25 10:00:22',1);
INSERT INTO `log_texts` VALUES (9,'[2021/03/02 11:12:44] Detected product: Lavie bottle: 1','2021/03/02 11:12:44',1);
INSERT INTO `log_texts` VALUES (10,'[2021/03/02 11:13:25] Detected product: Lavie bottle: 1','2021/03/02 11:13:25',1);
INSERT INTO `log_texts` VALUES (11,'[2021/03/02 11:22:36] Detected product: Lavie bottle: 1','2021/03/02 11:22:36',1);
INSERT INTO `log_texts` VALUES (12,'[: 1] WARNING: May be missing: 2021/03/02 11:22:36. Please check. Saving image...','2021/03/02 11:22:36',1);
INSERT INTO `log_texts` VALUES (13,'[2021/03/02 11:26:57] Detected product: Lavie bottle: 1','2021/03/02 11:26:57',1);
INSERT INTO `log_texts` VALUES (14,'[2021/03/02 11:26:57] WARNING: May be missing: : 1. Please check. Saving image...','2021/03/02 11:26:57',1);
INSERT INTO `log_texts` VALUES (15,'[2021/03/02 11:30:08] Detected product: Lavie bottle: 1','2021/03/02 11:30:08',1);
INSERT INTO `log_texts` VALUES (16,'[2021/03/02 11:30:08] WARNING: May be missing: : 1. Please check. Saving image...','2021/03/02 11:30:08',1);
INSERT INTO `log_texts` VALUES (17,'[2021/03/02 11:37:37] No object detected','2021/03/02 11:37:37',1);
INSERT INTO `log_texts` VALUES (18,'[2021/03/02 11:37:37] WARNING: May be missing: Gucci perfume: 1, Lavie bottle: 1. Please check. Saving image...','2021/03/02 11:37:37',1);
INSERT INTO `log_texts` VALUES (19,'[2021/03/02 11:38:10] Detected product: Lavie bottle: 1','2021/03/02 11:38:10',1);
INSERT INTO `log_texts` VALUES (20,'[2021/03/02 11:38:10] WARNING: May be missing: Gucci perfume: 1. Please check. Saving image...','2021/03/02 11:38:10',1);
INSERT INTO `log_texts` VALUES (21,'[2021/03/02 11:38:56] Detected product: Lavie bottle: 1','2021/03/02 11:38:56',1);
INSERT INTO `log_texts` VALUES (22,'[2021/03/02 11:38:56] WARNING: May be missing: Gucci perfume: 1. Please check. Saving image...','2021/03/02 11:38:56',1);
INSERT INTO `log_texts` VALUES (23,'[2021/03/02 11:40:21] Detected product: Lavie bottle: 1','2021/03/02 11:40:21',1);
INSERT INTO `log_texts` VALUES (24,'[2021/03/02 11:40:21] WARNING: May be missing: Gucci perfume: 1. Please check. Saving image...','2021/03/02 11:40:21',1);
CREATE TABLE IF NOT EXISTS `log_images` (
	`id`	INTEGER NOT NULL,
	`url`	VARCHAR NOT NULL,
	`time`	VARCHAR NOT NULL,
	`camera_id`	INTEGER NOT NULL,
	FOREIGN KEY(`camera_id`) REFERENCES `cameras`(`id`),
	PRIMARY KEY(`id`)
);
INSERT INTO `log_images` VALUES (1,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/images%2F0z15y6.jpg?alt=media&token=07bf5b69-0039-4916-9993-d8a1ed9942eb','2021/02/25 08:00:22',1);
INSERT INTO `log_images` VALUES (2,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/images%2F2021-01-06-215056.jpg?alt=media&token=494b44f0-62b5-4f61-a128-3f4c23e84d9e','2021/02/25 09:00:22',1);
INSERT INTO `log_images` VALUES (3,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/images%2F2021-01-06-215110.jpg?alt=media&token=dcfe75f2-30e9-47a4-bd18-91eaf4b8dd21','2021/02/26 08:00:22',1);
INSERT INTO `log_images` VALUES (4,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/images%2F2021-01-07-220259.jpg?alt=media&token=edb471c7-aa1f-4339-93fb-c7d463fa152b','2021/02/27 08:00:22',1);
INSERT INTO `log_images` VALUES (5,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/images%2F2021-01-07-220314.jpg?alt=media&token=6e555025-de45-4d30-8140-9be96ba872d9','2021/02/27 08:02:22',1);
INSERT INTO `log_images` VALUES (6,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/images%2Fdgppb8.jpg?alt=media','2021/03/02 11:22:36',1);
INSERT INTO `log_images` VALUES (7,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/images%2Fu1lyab.jpg?alt=media','2021/03/02 11:26:57',1);
INSERT INTO `log_images` VALUES (8,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/images%2Fm9rnnt.jpg?alt=media','2021/03/02 11:30:08',1);
INSERT INTO `log_images` VALUES (9,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/images%2Fjh4674.jpg?alt=media','2021/03/02 11:37:37',1);
INSERT INTO `log_images` VALUES (10,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/images%2F0151wz.jpg?alt=media','2021/03/02 11:38:10',1);
INSERT INTO `log_images` VALUES (11,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/images%2Fuv9ewm.jpg?alt=media','2021/03/02 11:38:56',1);
INSERT INTO `log_images` VALUES (12,'https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/images%2F45scp3.jpg?alt=media','2021/03/02 11:40:21',1);
CREATE TABLE IF NOT EXISTS `cameras` (
	`id`	INTEGER NOT NULL,
	`name`	VARCHAR NOT NULL,
	`active`	BOOLEAN,
	CHECK(activeIN(0,1)),
	PRIMARY KEY(`id`)
);
INSERT INTO `cameras` VALUES (1,'Raspberry Pi 3',0);
CREATE TABLE IF NOT EXISTS `camera_products` (
	`product_id`	INTEGER NOT NULL,
	`camera_id`	INTEGER NOT NULL,
	`quantity`	INTEGER NOT NULL,
	FOREIGN KEY(`camera_id`) REFERENCES `cameras`(`id`),
	FOREIGN KEY(`product_id`) REFERENCES `products`(`id`),
	PRIMARY KEY(`product_id`,`camera_id`)
);
INSERT INTO `camera_products` VALUES (1,1,1);
INSERT INTO `camera_products` VALUES (2,1,1);
COMMIT;
