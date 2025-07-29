#!/bin/bash

# 小说阅读网站 V1.0 - 版本打包脚本
# 用途: 创建完整的部署包

set -e

VERSION="1.0.0"
PACKAGE_NAME="novel_website_v${VERSION}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PACKAGE_DIR="${PACKAGE_NAME}_${TIMESTAMP}"

echo "=============================================="
echo "  小说阅读网站 V1.0 版本打包工具"
echo "=============================================="
echo "📦 版本: ${VERSION}"
echo "📁 包名: ${PACKAGE_DIR}"
echo "⏰ 时间: $(date)"
echo ""

# 创建临时目录
echo "🏗️  创建打包目录..."
mkdir -p "${PACKAGE_DIR}"

# 复制核心文件
echo "📄 复制应用文件..."
cp app_mysql.py "${PACKAGE_DIR}/"
cp config.py "${PACKAGE_DIR}/"
cp import_direct.py "${PACKAGE_DIR}/"
cp requirements.txt "${PACKAGE_DIR}/"

# 复制模板文件夹
echo "📋 复制模板文件..."
cp -r templates/ "${PACKAGE_DIR}/"

# 复制静态文件夹
echo "🎨 复制静态资源..."
cp -r static/ "${PACKAGE_DIR}/"

# 复制部署文件夹
echo "🚀 复制部署工具..."
cp -r deploy/ "${PACKAGE_DIR}/"

# 复制文档
echo "📚 复制文档文件..."
cp README.md "${PACKAGE_DIR}/"
cp CLAUDE.md "${PACKAGE_DIR}/"
cp RELEASE_NOTES_V1.0.md "${PACKAGE_DIR}/"

# 创建启动脚本
echo "⚡ 创建启动脚本..."
cat > "${PACKAGE_DIR}/start.sh" << 'EOF'
#!/bin/bash
# 小说阅读网站启动脚本

echo "启动小说阅读网站 V1.0..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查配置
echo "检查配置..."
python config.py

# 启动应用
echo "启动应用..."
python app_mysql.py
EOF

# 创建Windows启动脚本
cat > "${PACKAGE_DIR}/start.bat" << 'EOF'
@echo off
echo 启动小说阅读网站 V1.0...

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 检查配置
echo 检查配置...
python config.py

REM 启动应用
echo 启动应用...
python app_mysql.py

pause
EOF

# 设置执行权限
chmod +x "${PACKAGE_DIR}/start.sh"
chmod +x "${PACKAGE_DIR}/deploy/init_database.py"

# 创建版本信息文件
echo "📋 创建版本信息..."
cat > "${PACKAGE_DIR}/VERSION" << EOF
小说阅读网站 V1.0

版本号: ${VERSION}
打包时间: $(date)
构建标识: ${TIMESTAMP}

核心功能:
- 小说管理和分类
- 在线阅读(单章节/完整模式)
- 阅读进度自动保存
- 5星评分和收藏系统
- TXT文件批量导入
- 响应式Web界面

技术栈:
- Python 3.8+ + Flask 2.x
- MySQL 5.7+ (utf8mb4)
- Bootstrap 5 + JavaScript
- SQLAlchemy ORM

部署要求:
- Python 3.8+
- MySQL 5.7+
- 512MB+ RAM
- 100MB+ 磁盘空间

快速开始:
1. 修改 config.py 数据库配置
2. 运行 python deploy/init_database.py
3. 执行 ./start.sh (Linux) 或 start.bat (Windows)
4. 访问 http://localhost:5000

详细说明请查看 README.md 和 deploy/DEPLOYMENT_GUIDE.md
EOF

# 创建部署检查清单
echo "✅ 创建部署检查清单..."
cat > "${PACKAGE_DIR}/DEPLOYMENT_CHECKLIST.md" << 'EOF'
# 小说阅读网站 V1.0 部署检查清单

## 📋 部署前检查

### 环境要求
- [ ] Python 3.8+ 已安装
- [ ] MySQL 5.7+ 已安装并运行
- [ ] 网络端口 5000 可用
- [ ] 磁盘空间 >= 100MB

### 数据库准备
- [ ] MySQL服务正常运行
- [ ] 创建数据库用户和权限
- [ ] 测试数据库连接

## 🔧 配置修改

### 必修改文件
- [ ] `config.py` - 数据库连接配置
- [ ] 检查 `MYSQL_CONFIG` 中的host、user、password、database
- [ ] 设置 `FLASK_CONFIG` 中的SECRET_KEY (生产环境)
- [ ] 关闭DEBUG模式 (生产环境)

### 可选修改
- [ ] 修改默认端口 (如需要)
- [ ] 配置日志文件路径
- [ ] 设置文件上传限制

## 🚀 部署步骤

### 1. 基础部署
- [ ] 解压部署包到目标目录
- [ ] 创建Python虚拟环境: `python3 -m venv venv`
- [ ] 激活虚拟环境: `source venv/bin/activate`
- [ ] 安装依赖: `pip install -r requirements.txt`

### 2. 数据库初始化
- [ ] 测试配置: `python config.py`
- [ ] 初始化数据库: `python deploy/init_database.py`
- [ ] 确认看到"数据库初始化成功"提示

### 3. 应用启动
- [ ] 开发环境: `python app_mysql.py`
- [ ] 或使用脚本: `./start.sh` (Linux) / `start.bat` (Windows)
- [ ] 确认看到"Running on http://..." 提示

### 4. 功能测试
- [ ] 访问首页: http://localhost:5000
- [ ] 检查小说列表页面加载正常
- [ ] 测试导入功能: `python import_direct.py --list-categories`
- [ ] 导入测试小说文件验证功能

## 🔒 生产环境额外步骤

### 安全配置
- [ ] 修改默认管理员密码
- [ ] 设置强密码的SECRET_KEY
- [ ] 关闭Flask DEBUG模式
- [ ] 配置防火墙规则

### 性能优化
- [ ] 安装Gunicorn: `pip install gunicorn`
- [ ] 使用多进程启动: `gunicorn -w 4 -b 0.0.0.0:5000 app_mysql:app`
- [ ] 配置Nginx反向代理 (可选)
- [ ] 设置SSL证书 (可选)

### 监控维护
- [ ] 配置日志轮转
- [ ] 设置数据库备份计划
- [ ] 创建系统服务 (systemd)
- [ ] 配置监控告警

## ❓ 常见问题

### 数据库连接失败
- 检查MySQL服务状态: `sudo systemctl status mysql`
- 验证用户权限和密码
- 确认端口3306开放

### 页面无法访问
- 检查应用是否启动成功
- 确认端口5000未被占用
- 检查防火墙设置

### 导入文件失败
- 使用 `import_direct.py` 查看详细错误
- 检查文件编码格式
- 查看错误报告JSON文件

## 📞 获取帮助

- 📖 查看详细部署指南: `deploy/DEPLOYMENT_GUIDE.md`
- 🔧 配置文件说明: `deploy/DATABASE_CONFIG_FILES.md`
- 📋 版本发布说明: `RELEASE_NOTES_V1.0.md`
- 📚 使用说明: `README.md`

## ✅ 部署完成确认

- [ ] 网站可以正常访问
- [ ] 所有页面加载正常
- [ ] 数据库操作功能正常
- [ ] 文件导入功能测试通过
- [ ] 阅读功能测试通过
- [ ] 评分收藏功能正常

🎉 恭喜！小说阅读网站V1.0部署完成！
EOF

# 计算包大小
PACKAGE_SIZE=$(du -sh "${PACKAGE_DIR}" | cut -f1)

echo ""
echo "✅ 打包完成！"
echo "📦 包名称: ${PACKAGE_DIR}"
echo "📏 包大小: ${PACKAGE_SIZE}"
echo ""
echo "📋 包含内容:"
echo "   ✓ 核心应用文件"
echo "   ✓ 模板和静态资源"
echo "   ✓ 部署工具和脚本"
echo "   ✓ 完整文档"
echo "   ✓ 启动脚本 (Linux/Windows)"
echo "   ✓ 部署检查清单"
echo ""

# 创建压缩包
if command -v tar &> /dev/null; then
    echo "🗜️  创建压缩包..."
    tar -czf "${PACKAGE_DIR}.tar.gz" "${PACKAGE_DIR}/"
    ARCHIVE_SIZE=$(du -sh "${PACKAGE_DIR}.tar.gz" | cut -f1)
    echo "✅ 压缩完成: ${PACKAGE_DIR}.tar.gz (${ARCHIVE_SIZE})"
fi

echo ""
echo "🎉 小说阅读网站 V1.0 版本包创建完成！"
echo ""
echo "下一步操作:"
echo "1. 解压部署包到目标服务器"
echo "2. 按照 DEPLOYMENT_CHECKLIST.md 进行部署"
echo "3. 或直接查看 README.md 快速开始"
echo ""
echo "Have a nice day! 📚✨"