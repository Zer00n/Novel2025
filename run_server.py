#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小说网站服务器启动脚本
提供多种启动模式选择
"""

import sys
import os
from app_mysql import app

def start_server(mode='dev'):
    """
    启动服务器
    
    Args:
        mode (str): 启动模式
            - 'dev': 开发模式，启用调试和自动重载
            - 'stable': 稳定模式，禁用自动重载
            - 'prod': 生产模式，禁用调试
    """
    
    print("🚀 小说阅读网站服务器")
    print("=" * 50)
    print("📊 数据库配置:")
    print("   - 数据库: MySQL 9.4.0")
    print("   - 地址: X.X.X.X:3306")
    print("   - 数据库: novol")
    print("   - 用户: novol")
    print("")
    print("🌐 访问地址:")
    print("   - 本地: http://127.0.0.1:5000")
    print("   - 局域网: http://X.X.X.X:5000")
    print("")
    
    if mode == 'dev':
        print("🔧 启动模式: 开发模式")
        print("   - 调试模式: 启用")
        print("   - 自动重载: 启用")
        print("   - 代码修改会自动重启服务器")
        print("=" * 50)
        
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True,
            reloader_type='stat',
            threaded=True
        )
        
    elif mode == 'stable':
        print("🛡️ 启动模式: 稳定模式")
        print("   - 调试模式: 启用")
        print("   - 自动重载: 禁用")
        print("   - 代码修改不会自动重启")
        print("   - 需要手动重启查看更改")
        print("=" * 50)
        
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False,  # 禁用自动重载
            threaded=True
        )
        
    elif mode == 'prod':
        print("🚀 启动模式: 生产模式")
        print("   - 调试模式: 禁用")
        print("   - 自动重载: 禁用")
        print("   - 适合生产环境")
        print("=" * 50)
        
        app.run(
            debug=False,
            host='0.0.0.0',
            port=5000,
            use_reloader=False,
            threaded=True
        )
    
    else:
        print(f"❌ 未知的启动模式: {mode}")
        print("可用模式: dev, stable, prod")
        sys.exit(1)

def main():
    """主函数"""
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("请选择启动模式:")
        print("1. dev - 开发模式 (默认)")
        print("2. stable - 稳定模式 (不自动重载)")
        print("3. prod - 生产模式")
        print("")
        
        choice = input("请输入选择 (1-3) 或直接回车使用稳定模式: ").strip()
        
        if choice == '1':
            mode = 'dev'
        elif choice == '2' or choice == '':
            mode = 'stable'
        elif choice == '3':
            mode = 'prod'
        else:
            print("默认使用稳定模式")
            mode = 'stable'
    
    try:
        start_server(mode)
    except KeyboardInterrupt:
        print("\n")
        print("🛑 服务器已停止")
        print("感谢使用小说阅读网站！")

if __name__ == '__main__':
    main()
