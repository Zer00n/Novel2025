# 小说阅读网站 V1.0 - 数据库配置文件清单

## 📋 需要修改数据库配置的文件

### 🔧 主要配置文件
1. **`config.py`** - 统一配置文件 ⭐ **主要修改此文件**
   - `MYSQL_CONFIG` - 数据库连接配置
   - `FLASK_CONFIG` - Flask应用配置

### 📂 应用文件
2. **`app_mysql.py`** - 主应用文件（当前版本）
   - 第10行: `SQLALCHEMY_DATABASE_URI`
   - 第11行: `SECRET_KEY`

3. **`app_fixed.py`** - 带外键约束的版本（备用）
   - 第10行: `SQLALCHEMY_DATABASE_URI`
   - 第11行: `SECRET_KEY`

### 🛠️ 工具文件
4. **`import_direct.py`** - 小说导入工具
   - 第19-26行: `DB_CONFIG` 字典

5. **`init_mysql_db.py`** - 数据库初始化工具（已过时，请使用 `deploy/init_database.py`）
   - 第8-15行: `DB_CONFIG` 字典

6. **`update_db_schema.py`** - 数据库结构更新工具
   - 第8-15行: `DB_CONFIG` 字典

7. **`test_db_connection.py`** - 数据库连接测试
   - 第7-14行: `DB_CONFIG` 字典

### 🧪 测试文件
8. **`add_sample_data.py`** - 添加示例数据
   - 第11-18行: `DB_CONFIG` 字典

9. **`import_general_novels.py`** - 通用小说导入
   - 第11-18行: `DB_CONFIG` 字典

10. **`app.py`** - 早期版本（已废弃）
    - 第15行: `SECRET_KEY`

11. **`app_sqlite.py`** - SQLite版本（测试用）
    - 第11行: `SECRET_KEY`

### 🚀 部署文件
12. **`run_server.py`** - 服务启动脚本
    - 第7行: 数据库地址引用

## 🎯 推荐的配置修改流程

### 方案1: 使用统一配置文件（推荐）
1. **只修改 `config.py`** 中的配置
2. 其他文件导入配置: `from config import MYSQL_CONFIG, FLASK_CONFIG`
3. 统一管理，避免遗漏

### 方案2: 直接修改各文件
如果不想重构代码，可以逐个修改上述文件中的配置。

## 🔧 具体修改内容

### 数据库配置
```python
MYSQL_CONFIG = {
    'host': '你的数据库地址',        # 如: localhost, 192.168.1.100
    'port': 3306,                   # 数据库端口
    'user': '你的数据库用户名',      # 如: root, novol_user
    'password': '你的数据库密码',    # 强密码
    'database': '你的数据库名',      # 如: novol, novel_db
    'charset': 'utf8mb4'
}
```

### Flask配置
```python
FLASK_CONFIG = {
    'SECRET_KEY': '生产环境请使用随机密钥',  # 如: os.urandom(24)
    'DEBUG': False,                          # 生产环境设为False
    'HOST': '0.0.0.0',
    'PORT': 5000
}
```

## ⚠️ 安全提醒

1. **生产环境**:
   - 修改默认密码
   - 设置复杂的SECRET_KEY
   - 关闭DEBUG模式
   - 限制数据库访问权限

2. **备份配置**:
   - 修改前备份原配置
   - 记录修改的地方
   - 测试连接正常

3. **权限管理**:
   - 数据库用户只给必要权限
   - 不要使用root用户
   - 配置防火墙规则