from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://novoly:xxxxxx@localhost/novol'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    """首页"""
    latest_novels = Novel.query.order_by(Novel.created_at.desc()).limit(10).all()
    popular_novels = Novel.query.order_by(Novel.avg_rating.desc()).limit(10).all()
    categories = Category.query.all()
    
    return render_template('index.html', 
                         latest_novels=latest_novels,
                         popular_novels=popular_novels,
                         categories=categories)

@app.route('/novels')
def novel_list():
    """小说列表页"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', None, type=int)
    sort_by = request.args.get('sort', 'created_at')
    
    query = Novel.query
    
    if category_id:
        query = query.filter(Novel.category_id == category_id)
    
    if sort_by == 'rating':
        query = query.order_by(Novel.avg_rating.desc())
    elif sort_by == 'updated_at':
        query = query.order_by(Novel.updated_at.desc())
    else:
        query = query.order_by(Novel.created_at.desc())
    
    novels = query.paginate(page=page, per_page=20, error_out=False)
    categories = Category.query.all()
    
    return render_template('novel_list.html', 
                         novels=novels, 
                         categories=categories,
                         current_category=category_id,
                         current_sort=sort_by)

@app.route('/novel/<int:novel_id>')
def novel_detail(novel_id):
    """小说详情页"""
    novel = Novel.query.get_or_404(novel_id)
    chapters = Chapter.query.filter_by(novel_id=novel_id).order_by(Chapter.chapter_number).all()
    reviews = Review.query.filter_by(novel_id=novel_id).order_by(Review.created_at.desc()).limit(10).all()
    
    is_favorited = False
    if 'user_id' in session:
        is_favorited = Favorite.query.filter_by(
            user_id=session['user_id'], 
            novel_id=novel_id
        ).first() is not None
    
    return render_template('novel_detail.html', 
                         novel=novel, 
                         chapters=chapters, 
                         reviews=reviews,
                         is_favorited=is_favorited)

@app.route('/read/<int:novel_id>/<int:chapter_number>')
def read_chapter(novel_id, chapter_number):
    """阅读页面"""
    novel = Novel.query.get_or_404(novel_id)
    chapter = Chapter.query.filter_by(novel_id=novel_id, chapter_number=chapter_number).first_or_404()
    
    # 保存阅读进度
    if 'user_id' in session:
        progress = ReadingProgress.query.filter_by(
            user_id=session['user_id'], 
            novel_id=novel_id
        ).first()
        
        if not progress:
            progress = ReadingProgress(
                user_id=session['user_id'],
                novel_id=novel_id,
                chapter_number=chapter_number
            )
            db.session.add(progress)
        else:
            progress.chapter_number = chapter_number
            progress.updated_at = datetime.utcnow()
        
        db.session.commit()
    
    # 获取上一章和下一章
    prev_chapter = Chapter.query.filter_by(novel_id=novel_id, chapter_number=chapter_number-1).first()
    next_chapter = Chapter.query.filter_by(novel_id=novel_id, chapter_number=chapter_number+1).first()
    
    return render_template('read_chapter.html', 
                         novel=novel, 
                         chapter=chapter,
                         prev_chapter=prev_chapter,
                         next_chapter=next_chapter)

@app.route('/search')
def search():
    """搜索页面"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if query:
        novels = Novel.query.filter(
            db.or_(
                Novel.title.contains(query),
                Novel.author.contains(query),
                Novel.description.contains(query)
            )
        ).paginate(page=page, per_page=20, error_out=False)
    else:
        novels = None
    
    return render_template('search.html', novels=novels, query=query)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
