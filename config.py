#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说阅读网站 - 数据库配置文件
版本: V1.0
用途: 统一管理数据库连接配置，方便部署时修改
"""

# =============================================================================
# 数据库配置 - 部署时需要修改此部分
# =============================================================================

# MySQL数据库配置
MYSQL_CONFIG = {
    'host': 'X.X.X.X',          # 数据库服务器地址 - 请修改为实际地址
    'port': 3306,                    # 数据库端口
    'user': 'novol',                 # 数据库用户名 - 请修改为实际用户名
    'password': 'XXXXXXXXX',     # 数据库密码 - 请修改为实际密码
    'database': 'novol',             # 数据库名称 - 请修改为实际数据库名
    'charset': 'utf8mb4'             # 字符集，建议保持utf8mb4
}

# Flask应用配置
FLASK_CONFIG = {
    'SECRET_KEY': 'XXXXXXXX',   # 应用密钥 - 生产环境请使用复杂密钥
    'DEBUG': True,                   # 调试模式 - 生产环境请设为False
    'HOST': '0.0.0.0',              # 监听地址
    'PORT': 5000                     # 监听端口
}

# SQLAlchemy配置
def get_database_uri():
    """生成数据库连接URI"""
    return f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"

# PyMySQL连接配置
def get_pymysql_config():
    """获取PyMySQL连接配置"""
    return MYSQL_CONFIG.copy()

# =============================================================================
# 部署环境检测
# =============================================================================

import os
import sys

def check_environment():
    """检查部署环境和依赖"""
    required_modules = [
        'flask',
        'flask_sqlalchemy', 
        'pymysql',
        'chardet'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ 缺少以下Python模块:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\n请运行: pip install -r requirements.txt")
        return False
    
    print("✅ Python依赖检查通过")
    return True

def test_database_connection():
    """测试数据库连接"""
    try:
        import pymysql
        connection = pymysql.connect(**get_pymysql_config())
        connection.ping()
        connection.close()
        print("✅ 数据库连接测试成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请检查数据库配置和服务状态")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("        小说阅读网站 V1.0 - 环境检测")
    print("=" * 60)
    
    # 检查Python依赖
    if not check_environment():
        sys.exit(1)
    
    # 检查数据库连接
    if not test_database_connection():
        sys.exit(1)
    
    print("\n🎉 环境检测完成，系统准备就绪！")
    print("\n下一步:")
    print("1. 初始化数据库: python deploy/init_database.py")
    print("2. 启动应用: python app_mysql.py")
