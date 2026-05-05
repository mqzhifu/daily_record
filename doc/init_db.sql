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
  `real_time` datetime NOT NULL COMMENT '真实时间 （用户输入的时间）',
  `add_time` datetime NOT NULL COMMENT '记录添加时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='消费记录';


CREATE TABLE `daily` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `uid` int DEFAULT NULL COMMENT '用户ID',
  `category` TINYINT NOT NULL COMMENT '分类',
  `title` VARCHAR(255) NOT NULL COMMENT '标题',
  `real_time` datetime NOT NULL COMMENT '真实时间 （用户输入的时间）',
  `add_time` datetime NOT NULL COMMENT '记录添加时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='日常';

CREATE TABLE `user` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `username` VARCHAR(255) NOT NULL COMMENT '用户名',
  `gender` VARCHAR(255) NOT NULL COMMENT '性别',
  `avatar` VARCHAR(255) NOT NULL COMMENT '头像',
  `birthday` VARCHAR(255) NOT NULL COMMENT '生日',
  `age` VARCHAR(255) NOT NULL COMMENT '年龄',
  `email` VARCHAR(255) NOT NULL COMMENT '邮箱',
  `password` VARCHAR(255) NOT NULL COMMENT '密码',
  `add_time` datetime NOT NULL COMMENT '添加时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户';


CREATE TABLE `category` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `name` VARCHAR(255) NOT NULL COMMENT '分类名称',
  `type` TINYINT NOT NULL COMMENT '类型1：消费记录，2：日常',
  `sort` INT DEFAULT 0 COMMENT '排序',
  `description` VARCHAR(255) DEFAULT NULL COMMENT '描述',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='分类';







-- 插入分类数据
INSERT INTO `category` (`id`, `name`, `type`, `sort`, `description`) VALUES
(2, '餐饮', 1, 0, '在外面吃饭、即食产品'),
(3, '零食', 1, 0, '面包、饮料'),
(4, '交通', 1, 0, '公交、地铁、火车、飞机、打车'),
(5, '果蔬肉', 1, 0, '蔬菜、水果、肉、副食品、主食'),
(6, '服装', 1, 0, '鞋、衣服、裤子、帽子'),
(7, '生活缴费', 1, 0, '水、电、燃气、取暖、物业'),
(8, '家电', 1, 0, '冰箱、电视'),
(9, '数码', 1, 0, '电脑相关、消费电子、相机'),
(10, '烟', 1, 0, NULL),
(11, '网络会员', 1, 0, '各种平台的会员、虚拟电子消费'),
(12, '医疗', 1, 0, '看病'),
(13, '教育', 1, 0, '学费、补课费、兴趣班费用'),
(14, '娱乐', 1, 0, '电玩城、娱乐城、电影'),
(15, '日用品', 1, 0, '牙膏、洗发水、化妆品、居家小件'),
(16, '宠物', 1, 0, '猫砂、猫粮、罐头'),
(17, '玩具', 1, 0, '小孩的各种玩具'),
(18, '生活服务', 1, 0, '理发、洗车、美容、家政、美甲、快递'),
(19, '住房', 1, 0, '房贷、租房、酒店、装修'),
(20, '任意', 2, 0, '全部，不知道分类时用这个'),
(21, '打游戏', 2, 0, '手游 、主机游戏'),
(22, '玩手机', 2, 0, '刷视频'),
(23, '起床', 2, 0, NULL),
(24, '睡觉', 2, 0, NULL),
(25, '学习', 2, 0, 'AI、英语、编程'),
(26, '工作', 2, 0, '写代码、整理文档、开发APP'),
(27, '吃饭', 2, 0, NULL),
(28, '陪孩子', 2, 0, '去游乐场、逛公园'),
(29, '娱乐', 2, 0, '看电影、陪孩子、');
