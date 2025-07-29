#!/usr/bin/env python3
"""
数据库架构更新脚本 - 添加阅读进度和收藏位置字段
"""

import pymysql
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': 'X.X.X.X',
    'port': 3306,
    'user': 'novol',
    'password': 'XXXXXXXXXX',
    'database': 'novol',
    'charset': 'utf8mb4'
}

def update_database_schema():
    """更新数据库架构"""
    connection = None
    try:
        # 连接数据库
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("🔄 开始更新数据库架构...")
        
        # 更新 reading_progress 表
        print("📝 更新 reading_progress 表...")
        
        # 检查 scroll_position 字段是否存在
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'novol' 
            AND TABLE_NAME = 'reading_progress' 
            AND COLUMN_NAME = 'scroll_position'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE reading_progress 
                ADD COLUMN scroll_position INT DEFAULT 0 COMMENT '页面滚动位置'
            """)
            print("   ✅ 添加 scroll_position 字段")
        else:
            print("   ⏭️ scroll_position 字段已存在")
        
        # 检查 reading_time 字段是否存在
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'novol' 
            AND TABLE_NAME = 'reading_progress' 
            AND COLUMN_NAME = 'reading_time'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE reading_progress 
                ADD COLUMN reading_time INT DEFAULT 0 COMMENT '阅读时长(秒)'
            """)
            print("   ✅ 添加 reading_time 字段")
        else:
            print("   ⏭️ reading_time 字段已存在")
        
        # 更新 favorites 表
        print("📝 更新 favorites 表...")
        
        # 检查 chapter_number 字段是否存在
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'novol' 
            AND TABLE_NAME = 'favorites' 
            AND COLUMN_NAME = 'chapter_number'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE favorites 
                ADD COLUMN chapter_number INT DEFAULT 1 COMMENT '收藏时的章节'
            """)
            print("   ✅ 添加 chapter_number 字段")
        else:
            print("   ⏭️ chapter_number 字段已存在")
        
        # 检查 scroll_position 字段是否存在
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'novol' 
            AND TABLE_NAME = 'favorites' 
            AND COLUMN_NAME = 'scroll_position'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE favorites 
                ADD COLUMN scroll_position INT DEFAULT 0 COMMENT '收藏时的滚动位置'
            """)
            print("   ✅ 添加 scroll_position 字段")
        else:
            print("   ⏭️ scroll_position 字段已存在")
        
        # 检查 updated_at 字段是否存在
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'novol' 
            AND TABLE_NAME = 'favorites' 
            AND COLUMN_NAME = 'updated_at'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE favorites 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
            """)
            print("   ✅ 添加 updated_at 字段")
        else:
            print("   ⏭️ updated_at 字段已存在")
        
        # 提交更改
        connection.commit()
        print("✅ 数据库架构更新完成！")
        
        # 显示表结构
        print("\n📊 更新后的表结构:")
        
        print("\n📖 reading_progress 表:")
        cursor.execute("DESCRIBE reading_progress")
        for row in cursor.fetchall():
            print(f"   {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")
        
        print("\n❤️ favorites 表:")
        cursor.execute("DESCRIBE favorites")
        for row in cursor.fetchall():
            print(f"   {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")
        
    except Exception as e:
        print(f"❌ 更新数据库架构失败: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if connection:
            connection.close()
    
    return True

if __name__ == '__main__':
    print("🚀 小说网站数据库架构更新工具")
    print("=" * 50)
    
    if update_database_schema():
        print("\n🎉 数据库更新成功！现在可以使用新的阅读进度和收藏位置功能了。")
    else:
        print("\n💥 数据库更新失败！请检查错误信息并重试。")
