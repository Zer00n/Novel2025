# 小说阅读网站 V1.0

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-5.7+-orange.svg)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

一个功能完整的在线小说阅读平台，支持小说管理、在线阅读、进度保存、收藏评分等功能。

## ✨ 主要特性

### 📚 小说管理
- 🏷️ **分类管理**: 8个预设分类，支持自定义分类
- 📥 **批量导入**: TXT文件批量导入，智能章节分割
- 🔤 **多编码支持**: UTF-8、GBK、GB2312、UTF-16、Big5等
- ✏️ **在线编辑**: 支持小说内容在线编辑
- 🗂️ **分类切换**: 灵活的分类管理

### 📖 阅读体验
- 📄 **双模式阅读**: 单章节阅读 + 完整阅读
- 💾 **进度保存**: 自动保存阅读位置，跨设备同步
- 🎨 **阅读设置**: 字体大小、主题色、行间距调节
- ⭐ **收藏评分**: 一键收藏，5星评分系统
- 📊 **进度显示**: 实时进度条和百分比显示
- ⏱️ **阅读统计**: 阅读时长记录

### 🎯 用户功能
- 🔍 **搜索筛选**: 多维度搜索和筛选
- 📱 **响应式设计**: 完美适配PC、平板、手机
- 🚀 **流畅交互**: Ajax异步操作，无刷新体验
- 🎪 **动画效果**: 丰富的交互动画

## 🚀 快速开始

### 环境要求
- Python 3.8+
- MySQL 5.7+
- 现代浏览器

### 5分钟快速部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd novel_website

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置数据库
cp config.py config.local.py
nano config.py  # 修改数据库配置

# 4. 初始化数据库
python deploy/init_database.py

# 5. 启动应用
python app_mysql.py
```

### 访问网站
打开浏览器访问: http://localhost:5000

<img width="1298" height="992" alt="image" src="https://github.com/user-attachments/assets/d4711694-1d49-4e5e-94bc-6be7b39f305c" />
<img width="1331" height="1099" alt="image" src="https://github.com/user-attachments/assets/47d97e1b-0595-4fde-836b-c1ae1055702d" />
<img width="1629" height="1056" alt="image" src="https://github.com/user-attachments/assets/58551a23-ed4e-48f1-96f5-74718c042a0b" />
<img width="1252" height="1004" alt="image" src="https://github.com/user-attachments/assets/1aa38775-2970-4f94-84b9-715976a75f43" />


## 📁 项目结构

```
novel_website/
├── 📄 app_mysql.py              # 主应用文件
├── 📄 config.py                 # 统一配置管理 ⭐
├── 📄 import_direct.py          # 增强版导入工具
├── 📄 requirements.txt          # Python依赖
├── 📂 deploy/                   # 部署相关 ⭐
│   ├── 📄 init_database.py      # 数据库初始化脚本
│   ├── 📄 DEPLOYMENT_GUIDE.md   # 详细部署指南
│   └── 📄 DATABASE_CONFIG_FILES.md
├── 📂 templates/                # HTML模板
│   ├── 📄 base.html
│   ├── 📄 index.html
│   ├── 📄 novel_list.html
│   ├── 📄 novel_detail.html
│   ├── 📄 read_chapter.html     # 单章节阅读
│   └── 📄 read_full_novel.html  # 完整阅读
├── 📂 static/                   # 静态文件
│   ├── 📂 css/style.css
│   └── 📂 js/script.js
└── 📂 docs/                     # 文档
```

## 🛠️ 核心功能

### 数据库设计
- **7个核心表**: novels, chapters, categories, users, reviews, favorites, reading_progress
- **无外键约束**: 手动管理关系，提高灵活性
- **utf8mb4字符集**: 完美支持中文和emoji

### 技术架构
- **后端**: Flask + SQLAlchemy ORM + PyMySQL
- **前端**: Bootstrap 5 + 原生JavaScript + Fetch API
- **数据库**: MySQL with optimized indexes

## 📖 使用指南

### 导入小说
```bash
# 查看可用分类
python import_direct.py --list-categories

# 导入单个文件
python import_direct.py novel.txt 1

# 批量导入目录
python import_direct.py /path/to/novels/ 1

# 重试失败文件
python import_direct.py --retry failed_report.json 1
```

### 配置修改
主要配置在 `config.py` 文件中：

```python
# 数据库配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'novel_db'
}

# Flask配置
FLASK_CONFIG = {
    'SECRET_KEY': 'your-secret-key',
    'DEBUG': False,  # 生产环境设为False
    'PORT': 5000
}
```

## 📚 文档

| 文档 | 描述 |
|------|------|
| [部署指南](deploy/DEPLOYMENT_GUIDE.md) | 完整的生产环境部署指南 |
| [导入工具说明](IMPORT_TOOL_GUIDE.md) | TXT文件导入工具使用指南 |
| [配置文件清单](deploy/DATABASE_CONFIG_FILES.md) | 需要修改的配置文件列表 |
| [版本发布说明](RELEASE_NOTES_V1.0.md) | V1.0版本详细说明 |
| [功能使用指南](READING_FEATURES_GUIDE.md) | 阅读功能使用说明 |

## 🔧 开发

### 本地开发
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装开发依赖
pip install -r requirements.txt

# 启动开发服务器
python app_mysql.py
```

### 数据库操作
```bash
# 重置数据库
python deploy/init_database.py

# 测试数据库连接
python config.py

# 更新数据库结构
python update_db_schema.py
```

## 🚀 生产部署

### 使用Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_mysql:app
```

### 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/novel_website/static;
        expires 30d;
    }
}
```

详细部署说明请参考: [部署指南](deploy/DEPLOYMENT_GUIDE.md)

## 📊 功能截图

### 首页
- 📋 最新小说列表
- ⭐ 热门推荐
- 🏷️ 分类导航

### 小说列表
- 🔍 多维筛选搜索
- 📊 多种排序方式
- ⭐ 评分显示
- 💖 收藏状态

### 阅读页面
- 📖 清晰的阅读界面
- 📊 实时进度显示
- 🎨 阅读设置面板
- 💾 进度保存按钮

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 技术支持

### 常见问题
- **数据库连接失败**: 检查 `config.py` 配置
- **编码导入错误**: 使用 `import_direct.py` 重试功能
- **页面无法访问**: 检查防火墙和端口设置

### 获取帮助
- 📚 查看[部署指南](deploy/DEPLOYMENT_GUIDE.md)
- 🐛 提交[Issue](../../issues)
- 💬 查看[讨论区](../../discussions)

---

## 🎉 致谢

感谢所有贡献者和用户的支持！

**小说阅读网站 V1.0** - 让阅读更美好 📚✨
# Novel-NEW
