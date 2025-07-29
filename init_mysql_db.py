# MySQL数据库初始化脚本（无外键约束版本）
import pymysql
from datetime import datetime

def create_tables_without_fk():
    """创建数据表（不使用外键约束）"""
    
    config = {
        'host': 'X.X.X.X',
        'port': 3306,
        'user': 'novol',
        'password': 'XXXXXXXXXX',
        'database': 'novol',
        'charset': 'utf8mb4'
    }
    
    # SQL建表语句（移除外键约束）
    sql_statements = [
        # 用户表
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 分类表
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 小说表（移除外键约束）
        """
        CREATE TABLE IF NOT EXISTS novels (
            id INT PRIMARY KEY AUTO_INCREMENT,
            title VARCHAR(200) NOT NULL,
            author VARCHAR(100) NOT NULL,
            description TEXT,
            cover_image VARCHAR(255),
            status VARCHAR(20) DEFAULT 'ongoing',
            total_chapters INT DEFAULT 0,
            word_count INT DEFAULT 0,
            avg_rating FLOAT DEFAULT 0.0,
            review_count INT DEFAULT 0,
            view_count INT DEFAULT 0,
            category_id INT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_category_id (category_id),
            INDEX idx_author (author),
            INDEX idx_status (status),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 章节表
        """
        CREATE TABLE IF NOT EXISTS chapters (
            id INT PRIMARY KEY AUTO_INCREMENT,
            novel_id INT NOT NULL,
            chapter_number INT NOT NULL,
            title VARCHAR(200) NOT NULL,
            content LONGTEXT NOT NULL,
            word_count INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_novel_chapter (novel_id, chapter_number),
            INDEX idx_novel_id (novel_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 评价表
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            novel_id INT NOT NULL,
            rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_user_novel (user_id, novel_id),
            INDEX idx_novel_id (novel_id),
            INDEX idx_rating (rating)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 收藏表
        """
        CREATE TABLE IF NOT EXISTS favorites (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            novel_id INT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_user_novel (user_id, novel_id),
            INDEX idx_user_id (user_id),
            INDEX idx_novel_id (novel_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 阅读进度表
        """
        CREATE TABLE IF NOT EXISTS reading_progress (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            novel_id INT NOT NULL,
            chapter_number INT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY uk_user_novel (user_id, novel_id),
            INDEX idx_user_id (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    ]
    
    print("🔨 开始创建数据库表...")
    
    try:
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor:
            for i, sql in enumerate(sql_statements, 1):
                table_name = sql.split('IF NOT EXISTS ')[1].split(' (')[0]
                try:
                    cursor.execute(sql)
                    print(f"✅ 第{i}步: 创建表 {table_name} 成功")
                except Exception as e:
                    print(f"❌ 第{i}步: 创建表 {table_name} 失败: {e}")
                    
        connection.commit()
        print("\n🎉 所有表创建完成！")
        
        # 显示创建的表
        with connection.cursor() as cursor2:
            cursor2.execute("SHOW TABLES")
            tables = cursor2.fetchall()
            print(f"\n📋 当前数据库中的表 ({len(tables)}个):")
            for table in tables:
                cursor2.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor2.fetchone()[0]
                print(f"   - {table[0]} ({count} 条记录)")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        return False

def insert_default_categories():
    """插入默认分类数据"""
    
    config = {
        'host': 'X.X.X.X',
        'port': 3306,
        'user': 'novol',
        'password': 'XXXXXXX',
        'database': 'novol',
        'charset': 'utf8mb4'
    }
    
    categories = [
        ("玄幻", "玄幻小说"),
        ("武侠", "武侠小说"),
        ("都市", "都市小说"),
        ("历史", "历史小说"),
        ("科幻", "科幻小说"),
        ("言情", "言情小说"),
        ("其他", "其他类型")
    ]
    
    print("\n📚 插入默认分类...")
    
    try:
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor:
            # 检查是否已有分类
            cursor.execute("SELECT COUNT(*) FROM categories")
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"⚠️  已有 {count} 个分类，跳过插入")
                connection.close()
                return True
            
            # 插入分类
            for name, desc in categories:
                cursor.execute(
                    "INSERT INTO categories (name, description) VALUES (%s, %s)",
                    (name, desc)
                )
                print(f"✅ 插入分类: {name}")
            
            connection.commit()
            print(f"🎉 成功插入 {len(categories)} 个默认分类！")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 插入分类失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("        小说网站 - MySQL数据库初始化")
    print("=" * 60)
    
    # 步骤1: 创建表
    if create_tables_without_fk():
        # 步骤2: 插入默认数据
        insert_default_categories()
        print("\n🚀 数据库初始化完成！现在可以启动Flask应用了。")
    else:
        print("\n❌ 数据库初始化失败！请检查错误信息。")
