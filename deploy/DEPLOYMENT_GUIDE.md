# 小说阅读网站 V1.0 完整部署指南

## 📦 项目概述

**小说阅读网站 V1.0** 是一个基于Flask的在线小说阅读平台，支持小说管理、在线阅读、阅读进度保存、收藏管理、评分系统等功能。

### ✨ 主要功能
- 📚 小说分类管理
- 📖 在线阅读（单章节/完整阅读）
- ⭐ 评分和收藏系统
- 📊 阅读进度自动保存
- 🔍 搜索和筛选功能
- 📥 TXT文件批量导入
- 🎨 响应式UI设计

### 🏗️ 技术架构
- **后端**: Flask + SQLAlchemy ORM
- **数据库**: MySQL 5.7+
- **前端**: Bootstrap 5 + 原生JavaScript
- **文件处理**: 支持多编码TXT文件导入

## 🚀 快速部署

### 环境要求
- **Python**: 3.8+
- **MySQL**: 5.7+ 或 8.0+
- **操作系统**: Linux/Windows/macOS

### 1. 下载项目
```bash
# 解压项目包到目标目录
unzip novel_website_v1.0.zip
cd novel_website
```

### 2. 安装Python依赖
```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置数据库
编辑 `config.py` 文件，修改数据库配置：

```python
MYSQL_CONFIG = {
    'host': 'localhost',         # 你的数据库地址
    'port': 3306,
    'user': 'your_username',     # 你的数据库用户名
    'password': 'your_password', # 你的数据库密码
    'database': 'novel_db',      # 数据库名称
    'charset': 'utf8mb4'
}
```

### 4. 初始化数据库
```bash
# 测试环境和数据库连接
python config.py

# 初始化数据库表和默认数据
python deploy/init_database.py
```

### 5. 启动应用
```bash
# 开发环境启动
python app_mysql.py

# 或使用脚本启动
chmod +x start_stable.sh
./start_stable.sh
```

### 6. 访问网站
打开浏览器访问: http://localhost:5000

## 📋 详细部署步骤

### Step 1: 准备服务器环境

#### Ubuntu/Debian系统
```bash
# 更新系统包
sudo apt update
sudo apt upgrade -y

# 安装Python和MySQL
sudo apt install python3 python3-pip python3-venv mysql-server -y

# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### CentOS/RHEL系统
```bash
# 安装Python和MySQL
sudo yum install python3 python3-pip mysql-server -y

# 启动MySQL服务
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

### Step 2: 配置MySQL数据库

```sql
-- 连接MySQL
mysql -u root -p

-- 创建数据库用户
CREATE USER 'novol_user'@'localhost' IDENTIFIED BY 'strong_password';

-- 创建数据库
CREATE DATABASE novel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 授权
GRANT ALL PRIVILEGES ON novel_db.* TO 'novol_user'@'localhost';
FLUSH PRIVILEGES;

-- 退出
exit;
```

### Step 3: 项目配置

#### 3.1 修改配置文件
```bash
# 复制配置文件并修改
cp config.py config.local.py  # 备份配置
nano config.py  # 或使用其他编辑器
```

修改数据库配置：
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'novol_user',
    'password': 'strong_password',
    'database': 'novel_db',
    'charset': 'utf8mb4'
}

FLASK_CONFIG = {
    'SECRET_KEY': 'your-very-secret-key-here',  # 生产环境请使用复杂密钥
    'DEBUG': False,  # 生产环境设为False
    'HOST': '0.0.0.0',
    'PORT': 5000
}
```

#### 3.2 测试配置
```bash
# 测试环境
python config.py

# 应该看到：
# ✅ Python依赖检查通过
# ✅ 数据库连接测试成功
# 🎉 环境检测完成，系统准备就绪！
```

### Step 4: 初始化数据库

```bash
# 执行数据库初始化
python deploy/init_database.py

# 成功后会显示：
# 📊 数据库初始化完成 - 表结构信息
# 📚 可用分类 (8 个)
# 🎉 数据库初始化成功！
```

### Step 5: 导入测试数据（可选）

```bash
# 查看可用分类
python import_direct.py --list-categories

# 导入单个TXT文件测试
python import_direct.py test_novel.txt 1

# 批量导入目录
python import_direct.py /path/to/novel/files/ 1
```

### Step 6: 启动服务

#### 开发环境
```bash
python app_mysql.py
```

#### 生产环境（使用Gunicorn）
```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 app_mysql:app
```

#### 使用系统服务（推荐）
创建systemd服务文件：
```bash
sudo nano /etc/systemd/system/novel-website.service
```

内容：
```ini
[Unit]
Description=Novel Website V1.0
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/novel_website
Environment=PATH=/path/to/novel_website/venv/bin
ExecStart=/path/to/novel_website/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app_mysql:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable novel-website
sudo systemctl start novel-website
sudo systemctl status novel-website
```

## 🔧 高级配置

### Nginx反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /path/to/novel_website/static;
        expires 30d;
    }
}
```

### SSL配置（HTTPS）
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📁 项目文件结构

```
novel_website/
├── 📄 app_mysql.py              # 主应用文件
├── 📄 config.py                 # 统一配置文件 ⭐
├── 📄 import_direct.py          # 小说导入工具
├── 📄 requirements.txt          # Python依赖
├── 📂 deploy/                   # 部署相关文件
│   ├── 📄 init_database.py      # 数据库初始化脚本 ⭐
│   └── 📄 DATABASE_CONFIG_FILES.md
├── 📂 templates/                # HTML模板
│   ├── 📄 base.html
│   ├── 📄 index.html
│   ├── 📄 novel_list.html
│   ├── 📄 novel_detail.html
│   ├── 📄 read_chapter.html
│   └── 📄 read_full_novel.html
├── 📂 static/                   # 静态文件
│   ├── 📂 css/
│   │   └── 📄 style.css
│   └── 📂 js/
│       └── 📄 script.js
└── 📂 docs/                     # 文档
    ├── 📄 DEPLOYMENT_GUIDE.md   # 本文档
    ├── 📄 IMPORT_TOOL_GUIDE.md
    └── 📄 README.md
```

## 🛠️ 常见问题解决

### 数据库连接失败
```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 检查端口是否开放
netstat -tulpn | grep :3306

# 测试连接
python config.py
```

### 权限问题
```bash
# 给脚本执行权限
chmod +x start_stable.sh
chmod +x deploy/init_database.py

# 检查文件所有者
ls -la
sudo chown -R www-data:www-data /path/to/novel_website
```

### 端口被占用
```bash
# 查看端口占用
sudo netstat -tulpn | grep :5000

# 杀死占用进程
sudo kill -9 <PID>

# 或修改config.py中的端口
```

### 导入文件编码问题
```bash
# 使用增强版导入工具
python import_direct.py /path/to/novels/ 1

# 查看失败报告
ls import_failed_files_*.json

# 重试失败文件
python import_direct.py --retry import_failed_files_20240101_120000.json 1 --retry-type encoding
```

## 📊 性能优化建议

### 数据库优化
```sql
-- 添加索引
CREATE INDEX idx_novels_category_rating ON novels(category_id, avg_rating);
CREATE INDEX idx_chapters_novel_number ON chapters(novel_id, chapter_number);

-- 优化配置（my.cnf）
[mysqld]
innodb_buffer_pool_size = 1G
query_cache_size = 256M
max_connections = 200
```

### 应用优化
- 使用Redis缓存热门数据
- 启用Gzip压缩
- 配置CDN加速静态资源
- 使用数据库连接池

## 🔐 安全建议

1. **数据库安全**
   - 修改默认密码
   - 限制数据库访问IP
   - 定期备份数据

2. **应用安全**
   - 设置复杂的SECRET_KEY
   - 关闭DEBUG模式
   - 配置防火墙

3. **服务器安全**
   - 及时更新系统
   - 配置SSL证书
   - 监控日志文件

## 📞 技术支持

### 日志查看
```bash
# 应用日志
tail -f server.log

# 系统服务日志
sudo journalctl -u novel-website -f

# MySQL日志
sudo tail -f /var/log/mysql/error.log
```

### 备份恢复
```bash
# 数据库备份
mysqldump -u novol_user -p novel_db > backup_$(date +%Y%m%d).sql

# 恢复数据库
mysql -u novol_user -p novel_db < backup_20240101.sql

# 项目文件备份
tar -czf novel_website_backup_$(date +%Y%m%d).tar.gz novel_website/
```

## 🎉 部署完成检查清单

- [ ] ✅ Python环境和依赖安装
- [ ] ✅ MySQL数据库配置
- [ ] ✅ 修改config.py配置文件
- [ ] ✅ 执行数据库初始化
- [ ] ✅ 导入测试小说数据
- [ ] ✅ 启动应用服务
- [ ] ✅ 访问网站正常
- [ ] ✅ 配置反向代理（可选）
- [ ] ✅ 设置SSL证书（可选）
- [ ] ✅ 配置自动备份（推荐）

恭喜！🎊 小说阅读网站V1.0部署完成！