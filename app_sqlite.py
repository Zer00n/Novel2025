# 使用SQLite的简化版本（用于快速测试）
import os
import re
from datetime import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

# 创建应用和数据库实例
app = Flask(__name__)
app.config['SECRET_KEY'] = 'XXXXXXXX'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///novel.db'  # 使用SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 数据模型（简化版）
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    novels = db.relationship('Novel', backref='category', lazy=True)

class Novel(db.Model):
    __tablename__ = 'novels'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='completed')
    total_chapters = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    avg_rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chapters = db.relationship('Chapter', backref='novel', lazy=True, cascade='all, delete-orphan')

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    novel_id = db.Column(db.Integer, db.ForeignKey('novels.id'), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('novel_id', 'chapter_number'),)

# 基础路由
@app.route('/')
def index():
    novels = Novel.query.order_by(Novel.created_at.desc()).limit(10).all()
    categories = Category.query.all()
    return render_template('index.html', latest_novels=novels, popular_novels=novels, categories=categories)

@app.route('/novels')
def novel_list():
    page = request.args.get('page', 1, type=int)
    novels = Novel.query.paginate(page=page, per_page=20, error_out=False)
    categories = Category.query.all()
    return render_template('novel_list.html', novels=novels, categories=categories, current_category=None, current_sort='created_at')

@app.route('/novel/<int:novel_id>')
def novel_detail(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    chapters = Chapter.query.filter_by(novel_id=novel_id).order_by(Chapter.chapter_number).all()
    return render_template('novel_detail.html', novel=novel, chapters=chapters, reviews=[], is_favorited=False)

@app.route('/read/<int:novel_id>/<int:chapter_number>')
def read_chapter(novel_id, chapter_number):
    novel = Novel.query.get_or_404(novel_id)
    chapter = Chapter.query.filter_by(novel_id=novel_id, chapter_number=chapter_number).first_or_404()
    prev_chapter = Chapter.query.filter_by(novel_id=novel_id, chapter_number=chapter_number-1).first()
    next_chapter = Chapter.query.filter_by(novel_id=novel_id, chapter_number=chapter_number+1).first()
    return render_template('read_chapter.html', novel=novel, chapter=chapter, prev_chapter=prev_chapter, next_chapter=next_chapter)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        novels = Novel.query.filter(Novel.title.contains(query) | Novel.author.contains(query)).all()
        novels = type('obj', (object,), {'items': novels, 'total': len(novels), 'pages': 1, 'page': 1})()
    else:
        novels = None
    return render_template('search.html', novels=novels, query=query)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # 创建默认分类
        if not Category.query.first():
            categories = [
                {"name": "玄幻", "description": "玄幻小说"},
                {"name": "武侠", "description": "武侠小说"},
                {"name": "都市", "description": "都市小说"},
                {"name": "历史", "description": "历史小说"},
                {"name": "科幻", "description": "科幻小说"},
                {"name": "言情", "description": "言情小说"},
                {"name": "其他", "description": "其他类型"}
            ]
            for cat_data in categories:
                category = Category(name=cat_data["name"], description=cat_data["description"])
                db.session.add(category)
            db.session.commit()
            print("默认分类创建完成")
        
        print("数据库初始化完成！")
        print("访问 http://localhost:5000 查看网站")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
