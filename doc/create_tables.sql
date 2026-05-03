-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS test DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE test;


CREATE TABLE `smoke_record` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `uid` int DEFAULT NULL COMMENT '用户ID',
  `add_time` datetime NOT NULL COMMENT '添加时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='每次抽烟时间记录';


CREATE TABLE `expenses` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `uid` int DEFAULT NULL COMMENT '用户ID',
  `price` DECIMAL(10,2) NOT NULL COMMENT '价格',
  `category` TINYINT NOT NULL COMMENT '分类',
  `title` VARCHAR(255) NOT NULL COMMENT '标题',
  `add_time` datetime NOT NULL COMMENT '添加时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='消费记录';


CREATE TABLE `daily` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `uid` int DEFAULT NULL COMMENT '用户ID',
  `category` TINYINT NOT NULL COMMENT '分类',
  `title` VARCHAR(255) NOT NULL COMMENT '标题',
  `add_time` datetime NOT NULL COMMENT '添加时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='日常';
