#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说阅读网站 V1.0 - 数据库初始化脚本
功能: 创建数据库表结构和初始数据
用途: 部署时一键初始化数据库
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from datetime import datetime
from config import get_pymysql_config

def create_database_connection():
    """创建数据库连接"""
    try:
        config = get_pymysql_config()
        # 先连接到MySQL服务器（不指定数据库）
        server_config = config.copy()
        database_name = server_config.pop('database')
        
        connection = pymysql.connect(**server_config)
        return connection, database_name
    except Exception as e:
        print(f"❌ 连接数据库服务器失败: {e}")
        return None, None

def create_database_if_not_exists(connection, database_name):
    """创建数据库（如果不存在）"""
    try:
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ 数据库 '{database_name}' 已创建或已存在")
            
            # 使用数据库
            cursor.execute(f"USE `{database_name}`")
            
        connection.commit()
        return True
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False

def create_tables(connection):
    """创建数据表"""
    tables = {
        'categories': '''
            CREATE TABLE IF NOT EXISTS `categories` (
                `id` int NOT NULL AUTO_INCREMENT,
                `name` varchar(50) NOT NULL,
                `description` text,
                `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`),
                UNIQUE KEY `name` (`name`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        
        'users': '''
            CREATE TABLE IF NOT EXISTS `users` (
                `id` int NOT NULL AUTO_INCREMENT,
                `username` varchar(80) NOT NULL,
                `email` varchar(120) NOT NULL,
                `password_hash` varchar(255) NOT NULL,
                `is_admin` tinyint(1) DEFAULT '0',
                `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`),
                UNIQUE KEY `username` (`username`),
                UNIQUE KEY `email` (`email`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        
        'novels': '''
            CREATE TABLE IF NOT EXISTS `novels` (
                `id` int NOT NULL AUTO_INCREMENT,
                `title` varchar(200) NOT NULL,
                `author` varchar(100) NOT NULL,
                `description` text,
                `cover_image` varchar(255) DEFAULT NULL,
                `status` varchar(20) DEFAULT 'ongoing',
                `total_chapters` int DEFAULT '0',
                `word_count` int DEFAULT '0',
                `avg_rating` float DEFAULT '0',
                `review_count` int DEFAULT '0',
                `view_count` int DEFAULT '0',
                `category_id` int NOT NULL,
                `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
                `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`),
                KEY `idx_category_id` (`category_id`),
                KEY `idx_title` (`title`),
                KEY `idx_author` (`author`),
                KEY `idx_status` (`status`),
                KEY `idx_created_at` (`created_at`),
                KEY `idx_avg_rating` (`avg_rating`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        
        'chapters': '''
            CREATE TABLE IF NOT EXISTS `chapters` (
                `id` int NOT NULL AUTO_INCREMENT,
                `novel_id` int NOT NULL,
                `chapter_number` int NOT NULL,
                `title` varchar(200) NOT NULL,
                `content` longtext NOT NULL,
                `word_count` int DEFAULT '0',
                `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`),
                UNIQUE KEY `novel_chapter` (`novel_id`, `chapter_number`),
                KEY `idx_novel_id` (`novel_id`),
                KEY `idx_chapter_number` (`chapter_number`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        
        'reviews': '''
            CREATE TABLE IF NOT EXISTS `reviews` (
                `id` int NOT NULL AUTO_INCREMENT,
                `user_id` int NOT NULL,
                `novel_id` int NOT NULL,
                `rating` int NOT NULL,
                `comment` text,
                `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`),
                UNIQUE KEY `user_novel` (`user_id`, `novel_id`),
                KEY `idx_novel_id` (`novel_id`),
                KEY `idx_rating` (`rating`),
                CHECK (`rating` >= 1 AND `rating` <= 5)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        
        'favorites': '''
            CREATE TABLE IF NOT EXISTS `favorites` (
                `id` int NOT NULL AUTO_INCREMENT,
                `user_id` int NOT NULL,
                `novel_id` int NOT NULL,
                `chapter_number` int DEFAULT '1',
                `scroll_position` int DEFAULT '0',
                `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
                `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`),
                UNIQUE KEY `user_novel` (`user_id`, `novel_id`),
                KEY `idx_novel_id` (`novel_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        
        'reading_progress': '''
            CREATE TABLE IF NOT EXISTS `reading_progress` (
                `id` int NOT NULL AUTO_INCREMENT,
                `user_id` int NOT NULL,
                `novel_id` int NOT NULL,
                `chapter_number` int NOT NULL,
                `scroll_position` int DEFAULT '0',
                `reading_time` int DEFAULT '0',
                `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`),
                UNIQUE KEY `user_novel` (`user_id`, `novel_id`),
                KEY `idx_novel_id` (`novel_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''
    }
    
    try:
        with connection.cursor() as cursor:
            for table_name, create_sql in tables.items():
                print(f"📝 创建表: {table_name}")
                cursor.execute(create_sql)
                
        connection.commit()
        print("✅ 所有数据表创建完成")
        return True
    except Exception as e:
        print(f"❌ 创建数据表失败: {e}")
        return False

def insert_default_data(connection):
    """插入默认数据"""
    try:
        with connection.cursor() as cursor:
            # 检查是否已有分类数据
            cursor.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] > 0:
                print("📋 分类数据已存在，跳过初始化")
                return True
            
            # 插入默认分类
            categories = [
                ('玄幻', '玄幻修真类小说'),
                ('都市', '都市生活类小说'),
                ('历史', '历史军事类小说'),
                ('科幻', '科幻未来类小说'),
                ('游戏', '游戏竞技类小说'),
                ('悬疑', '悬疑推理类小说'),
                ('言情', '言情穿越类小说'),
                ('其他', '其他类型小说')
            ]
            
            print("📋 插入默认分类数据...")
            for name, desc in categories:
                cursor.execute("""
                    INSERT INTO categories (name, description, created_at)
                    VALUES (%s, %s, %s)
                """, (name, desc, datetime.now()))
                print(f"   ✓ {name}: {desc}")
            
            # 创建默认用户
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, is_admin, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, ('admin', 'admin@novol.local', 'admin123', True, datetime.now()))
            print("👤 创建默认管理员用户: admin/admin123")
            
        connection.commit()
        print("✅ 默认数据插入完成")
        return True
    except Exception as e:
        print(f"❌ 插入默认数据失败: {e}")
        return False

def show_database_info(connection):
    """显示数据库信息"""
    try:
        with connection.cursor() as cursor:
            # 显示表信息
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print("\n" + "=" * 60)
            print("📊 数据库初始化完成 - 表结构信息")
            print("=" * 60)
            
            for (table_name,) in tables:
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                count = cursor.fetchone()[0]
                print(f"📋 {table_name:<20} - {count:>6} 条记录")
            
            # 显示分类信息
            cursor.execute("SELECT id, name, description FROM categories ORDER BY id")
            categories = cursor.fetchall()
            
            if categories:
                print(f"\n📚 可用分类 ({len(categories)} 个):")
                print("-" * 50)
                for cat_id, name, desc in categories:
                    print(f"ID: {cat_id:<2} | {name:<8} | {desc}")
            
        print("\n🎉 数据库初始化成功！")
        print("\n下一步操作:")
        print("1. 导入小说: python import_direct.py /path/to/novels/ 1")
        print("2. 启动应用: python app_mysql.py")
        print("3. 访问网站: http://localhost:5000")
        
    except Exception as e:
        print(f"❌ 显示数据库信息失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("        小说阅读网站 V1.0 - 数据库初始化")
    print("=" * 60)
    
    # 1. 连接数据库服务器
    print("🔗 连接数据库服务器...")
    connection, database_name = create_database_connection()
    if not connection:
        sys.exit(1)
    
    try:
        # 2. 创建数据库
        print(f"🏗️  创建数据库: {database_name}")
        if not create_database_if_not_exists(connection, database_name):
            sys.exit(1)
        
        # 3. 创建数据表
        print("📋 创建数据表...")
        if not create_tables(connection):
            sys.exit(1)
        
        # 4. 插入默认数据
        print("📥 插入默认数据...")
        if not insert_default_data(connection):
            sys.exit(1)
        
        # 5. 显示数据库信息
        show_database_info(connection)
        
    finally:
        connection.close()

if __name__ == "__main__":
    main()