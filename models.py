from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 这里不能导入app，需要在app.py中初始化后再导入
db = None

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    reviews = db.relationship('Review', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    reading_progress = db.relationship('ReadingProgress', backref='user', lazy=True)

class Category(db.Model):
    """分类模型"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    novels = db.relationship('Novel', backref='category', lazy=True)

class Novel(db.Model):
    """小说模型"""
    __tablename__ = 'novels'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))
    status = db.Column(db.String(20), default='ongoing')  # ongoing, completed, paused
    total_chapters = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    avg_rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    chapters = db.relationship('Chapter', backref='novel', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='novel', lazy=True)
    favorites = db.relationship('Favorite', backref='novel', lazy=True)
    reading_progress = db.relationship('ReadingProgress', backref='novel', lazy=True)

class Chapter(db.Model):
    """章节模型"""
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    novel_id = db.Column(db.Integer, db.ForeignKey('novels.id'), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 复合索引确保每本小说的章节号唯一
    __table_args__ = (db.UniqueConstraint('novel_id', 'chapter_number'),)

class Review(db.Model):
    """评价模型"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    novel_id = db.Column(db.Integer, db.ForeignKey('novels.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5星评分
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 确保每个用户对每本小说只能评价一次
    __table_args__ = (db.UniqueConstraint('user_id', 'novel_id'),)

class Favorite(db.Model):
    """收藏模型"""
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    novel_id = db.Column(db.Integer, db.ForeignKey('novels.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 确保每个用户对每本小说只能收藏一次
    __table_args__ = (db.UniqueConstraint('user_id', 'novel_id'),)

class ReadingProgress(db.Model):
    """阅读进度模型"""
    __tablename__ = 'reading_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    novel_id = db.Column(db.Integer, db.ForeignKey('novels.id'), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 确保每个用户对每本小说只有一个阅读进度记录
    __table_args__ = (db.UniqueConstraint('user_id', 'novel_id'),)