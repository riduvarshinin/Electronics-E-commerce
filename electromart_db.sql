-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: electromart_db
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `electromart_db`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `electromart_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `electromart_db`;

--
-- Table structure for table `addresses`
--

DROP TABLE IF EXISTS `addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addresses` (
  `address_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `address_line` varchar(255) NOT NULL,
  `city` varchar(100) NOT NULL,
  `state` varchar(100) NOT NULL,
  `postal_code` varchar(10) NOT NULL,
  `country` varchar(100) DEFAULT 'India',
  PRIMARY KEY (`address_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `addresses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `addresses`
--

LOCK TABLES `addresses` WRITE;
/*!40000 ALTER TABLE `addresses` DISABLE KEYS */;
/*!40000 ALTER TABLE `addresses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart`
--

DROP TABLE IF EXISTS `cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart` (
  `cart_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cart_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_items` (
  `cart_item_id` int NOT NULL AUTO_INCREMENT,
  `cart_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`cart_item_id`),
  UNIQUE KEY `cart_id` (`cart_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `cart_items_ibfk_1` FOREIGN KEY (`cart_id`) REFERENCES `cart` (`cart_id`) ON DELETE CASCADE,
  CONSTRAINT `cart_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `category_name` varchar(100) NOT NULL,
  `description` text,
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `category_name` (`category_name`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Mobiles','Smartphones and mobile devices'),(2,'Laptops','Personal and gaming laptops'),(3,'Tablets','Tablets and iPads'),(4,'Headphones','Wired and wireless headphones'),(5,'Accessories','Electronic accessories'),(6,'Smart Watches','Smart watches and fitness bands'),(7,'Cameras','Digital cameras'),(8,'Televisions','Smart TVs and displays');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `order_item_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int DEFAULT NULL,
  `product_name` varchar(200) NOT NULL,
  `quantity` int NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`order_item_id`),
  KEY `order_id` (`order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `address_id` int DEFAULT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `order_status` enum('Pending','Confirmed','Shipped','Delivered','Cancelled') DEFAULT 'Pending',
  `ordered_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`order_id`),
  KEY `user_id` (`user_id`),
  KEY `address_id` (`address_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`address_id`) REFERENCES `addresses` (`address_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `payment_method` varchar(50) NOT NULL,
  `transaction_id` varchar(150) DEFAULT NULL,
  `payment_amount` decimal(10,2) NOT NULL,
  `payment_status` enum('Pending','Successful','Failed','Refunded') DEFAULT 'Pending',
  `payment_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`payment_id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `product_id` int NOT NULL AUTO_INCREMENT,
  `category_id` int DEFAULT NULL,
  `product_name` varchar(200) NOT NULL,
  `brand` varchar(100) DEFAULT NULL,
  `description` text,
  `price` decimal(10,2) NOT NULL,
  `stock_quantity` int DEFAULT '0',
  `image_url` varchar(500) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `model_number` varchar(100) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `original_price` decimal(10,2) DEFAULT NULL,
  `discount_price` decimal(10,2) DEFAULT NULL,
  `product_status` enum('Active','Inactive') DEFAULT 'Active',
  `colour` varchar(100) DEFAULT NULL,
  `ram` varchar(50) DEFAULT NULL,
  `storage` varchar(50) DEFAULT NULL,
  `processor` varchar(150) DEFAULT NULL,
  `display_size` varchar(50) DEFAULT NULL,
  `battery` varchar(100) DEFAULT NULL,
  `warranty` varchar(100) DEFAULT NULL,
  `product_image_path` varchar(500) DEFAULT NULL,
  `created_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`product_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,5,'Logitech Wireless Mouse','Logitech','Wireless computer mouse',899.00,30,NULL,'2026-11-20 18:41:37','M185','Accessories',899.00,899.00,'Active','Black',NULL,NULL,NULL,NULL,NULL,'1 Year Manufacturer Warranty','images/accessories/logitech-m185.jpg','2026-11-21 00:11:37','2026-11-21 02:02:35'),(2,7,'Canon EOS 1500D','Canon','Digital DSLR camera',38999.00,4,NULL,'2026-11-20 18:41:37','1500D','Cameras',38999.00,38999.00,'Active','Black',NULL,NULL,NULL,NULL,NULL,'1 Year Manufacturer Warranty','images/cameras/canon-1500d.jpg','2026-11-21 00:11:37','2026-11-21 02:02:36'),(3,4,'Sony WH-1000XM5','Sony','Wireless noise cancelling headphones',24999.00,15,NULL,'2026-11-20 18:41:37','WH1000XM5','Headphones',24999.00,24999.00,'Active','Black',NULL,NULL,NULL,NULL,NULL,'1 Year Manufacturer Warranty','images/headphones/sony-wh1000xm5.jpg','2026-11-21 00:11:37','2026-11-21 02:02:36'),(4,4,'Boat Rockerz 450','Boat','Wireless Bluetooth headphones',1499.00,25,NULL,'2026-11-20 18:41:37','Rockerz450','Headphones',1499.00,1499.00,'Active','Black',NULL,NULL,NULL,NULL,NULL,'1 Year Manufacturer Warranty','images/headphones/boat-rockerz-450.jpg','2026-11-21 00:11:37','2026-11-21 02:02:36'),(5,2,'HP Pavilion 15','HP','Everyday performance laptop',58999.00,12,NULL,'2026-11-20 18:41:37','15-eg','Laptops',58999.00,58999.00,'Active','Silver','8GB',NULL,NULL,NULL,NULL,'1 Year Manufacturer Warranty','images/laptops/hp-pavilion-15.jpg','2026-11-21 00:11:37','2026-11-21 02:02:36'),(6,2,'Dell Inspiron 14','Dell','Lightweight productivity laptop',62999.00,7,NULL,'2026-11-20 18:41:37','Inspiron14','Laptops',62999.00,62999.00,'Active','Silver','8GB',NULL,NULL,NULL,NULL,'1 Year Manufacturer Warranty','images/laptops/dell-inspiron-14.jpg','2026-11-21 00:11:37','2026-11-21 02:02:36'),(7,1,'Samsung Galaxy S24','Samsung','Premium Android smartphone',74999.00,10,NULL,'2026-11-20 18:41:37','SM-S921B','Mobiles',74999.00,74999.00,'Active','Onyx Black','8GB','128GB','Snapdragon 8 Gen 3','6.2 inch','4000 mAh','1 Year Manufacturer Warranty','images/mobiles/samsung-s24.jpg','2026-11-21 00:11:37','2026-11-21 02:02:36'),(8,1,'iPhone 16','Apple','Latest Apple smartphone',79900.00,8,NULL,'2026-11-20 18:41:37','A3287','Mobiles',79900.00,79900.00,'Active','Black','8GB','128GB','Apple A18','6.1 inch','3561 mAh','1 Year Manufacturer Warranty','images/mobiles/iphone-16.jpg','2026-11-21 00:11:37','2026-11-21 02:02:36'),(9,6,'Apple Watch SE','Apple','Smart watch with fitness features',24900.00,5,NULL,'2026-11-20 18:41:37','WatchSE','Smart Watches',24900.00,24900.00,'Active','Midnight',NULL,NULL,NULL,'40mm',NULL,'1 Year Manufacturer Warranty','images/smart_watches/apple-watch-se.jpg','2026-11-21 00:11:37','2026-11-21 02:02:36'),(10,3,'Samsung Galaxy Tab S9','Samsung','Premium Android tablet',45999.00,6,NULL,'2026-11-20 18:41:37','SM-X710','Tablets',45999.00,45999.00,'Active','Graphite','8GB','128GB','Snapdragon 8 Gen 2','11 inch','8400 mAh','1 Year Manufacturer Warranty','images/tablets/samsung-tab-s9.jpg','2026-11-21 00:11:37','2026-11-21 02:02:36'),(11,8,'Samsung 43 inch Smart TV','Samsung','Full HD Smart LED television',32999.00,9,NULL,'2026-11-20 18:41:37','UA43T5450','Televisions',32999.00,32999.00,'Active','Black',NULL,NULL,NULL,'43 inch',NULL,'1 Year Manufacturer Warranty','images/televisions/samsung-tv.jpg','2026-11-21 00:11:37','2026-11-21 02:02:36');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `review_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `product_id` int NOT NULL,
  `rating` int NOT NULL,
  `review_text` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`review_id`),
  UNIQUE KEY `user_id` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE,
  CONSTRAINT `reviews_chk_1` CHECK ((`rating` between 1 and 5))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `role` enum('customer','admin') DEFAULT 'customer',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Ridu Varshini','riduvarshini3112@gmail.com','scrypt:32768:8:1$kYSmPYs3e6Gkqq3n$c088627acfa507da3f1e0457eed1f05a0fc0a03a4233746a2319e4e934aa84fbef3ecc0b0b69c728f4455b0a47dc6d483d7a931b734ac939afe969e703ea1853',NULL,'customer','2026-11-20 19:19:49'),(2,'rid','ridu321@gmail.com','scrypt:32768:8:1$OUCRNeWeJwyX7KbE$39f8dfe23c1f374fb6421de7cd3c0ffe5fa65c3f87435445f96c6d09470351ec9d7ca78d9d3218898b4b38b76466c2583a5a11fc9e3bbd473f58ed9bfa2dbbd9',NULL,'customer','2026-11-20 19:24:39'),(3,'fijs','3@gmail.com','scrypt:32768:8:1$gSbNRPmM80ZbCNKD$ac624c53085d071c2816a8cb177bb724de575b36ada3850cb3a7315a85b2688e56338404b5474a9fb1b2a5e8ddee9c16479f2c41b510ab69b15a361948bcc358',NULL,'customer','2026-11-20 19:25:56'),(7,'dhaksha','dhaksha3112@gmail.com','scrypt:32768:8:1$0Ow6T2pQTKFIvg9i$aee95b468f5f269c6a96de6091a5bd9470054d4c9a03121648e268946159e333e9a4784e92892ea09d95432d823cbf4918e6f9f9aeb08f591db86cfc73ba5477',NULL,'customer','2026-11-20 19:36:00');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishlist`
--

DROP TABLE IF EXISTS `wishlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wishlist` (
  `wishlist_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `product_id` int NOT NULL,
  PRIMARY KEY (`wishlist_id`),
  UNIQUE KEY `user_id` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `wishlist_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishlist`
--

LOCK TABLES `wishlist` WRITE;
/*!40000 ALTER TABLE `wishlist` DISABLE KEYS */;
/*!40000 ALTER TABLE `wishlist` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-21  9:11:23
