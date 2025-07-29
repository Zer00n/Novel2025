# MySQL版本的Flask应用（无外键约束）
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'XXXXXXXX'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://novol:XXXXXXXXX@X.X.X.X/novol'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 数据模型（无外键约束版本）
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Novel(db.Model):
    __tablename__ = 'novels'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))
    status = db.Column(db.String(20), default='ongoing')
    total_chapters = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    avg_rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, nullable=False)  # 移除外键约束
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def category(self):
        """手动获取分类"""
        return Category.query.get(self.category_id)
    
    @property
    def chapters(self):
        """手动获取章节"""
        return Chapter.query.filter_by(novel_id=self.id).order_by(Chapter.chapter_number).all()

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    novel_id = db.Column(db.Integer, nullable=False)  # 移除外键约束
    chapter_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def novel(self):
        """手动获取小说"""
        return Novel.query.get(self.novel_id)

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # 移除外键约束
    novel_id = db.Column(db.Integer, nullable=False)  # 移除外键约束
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def user(self):
        return User.query.get(self.user_id)
    
    @property
    def novel(self):
        return Novel.query.get(self.novel_id)

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # 移除外键约束
    novel_id = db.Column(db.Integer, nullable=False)  # 移除外键约束
    chapter_number = db.Column(db.Integer, default=1)  # 收藏时的章节
    scroll_position = db.Column(db.Integer, default=0)  # 收藏时的滚动位置
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReadingProgress(db.Model):
    __tablename__ = 'reading_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # 移除外键约束
    novel_id = db.Column(db.Integer, nullable=False)  # 移除外键约束
    chapter_number = db.Column(db.Integer, nullable=False)
    scroll_position = db.Column(db.Integer, default=0)  # 页面滚动位置
    reading_time = db.Column(db.Integer, default=0)  # 阅读时长(秒)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 路由处理函数
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
    sort_by = request.args.get('sort', 'created_at')  # 默认按创建时间排序
    show_favorites = request.args.get('favorites', 'false').lower() == 'true'
    date_filter = request.args.get('date', None)  # 新增日期筛选参数
    
    # 调试输出
    print(f"DEBUG: 接收到的排序参数 sort_by = {sort_by}")
    print(f"DEBUG: 完整URL参数 = {dict(request.args)}")
    
    # 模拟用户ID
    user_id = session.get('user_id', 1)
    
    # 构建基础查询，包含用户评分
    query = db.session.query(
        Novel,
        Review.rating.label('user_rating')
    ).outerjoin(
        Review,
        db.and_(Review.novel_id == Novel.id, Review.user_id == user_id)
    )
    
    # 收藏筛选
    if show_favorites:
        query = query.join(
            Favorite,
            db.and_(Favorite.novel_id == Novel.id, Favorite.user_id == user_id)
        )
    
    if category_id:
        query = query.filter(Novel.category_id == category_id)
    
    # 新增：按日期筛选
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            next_day = filter_date + timedelta(days=1)
            query = query.filter(
                Novel.created_at >= filter_date,
                Novel.created_at < next_day
            )
        except ValueError:
            pass  # 如果日期格式不正确，忽略筛选
    
    # 排序逻辑
    print(f"DEBUG: 开始应用排序逻辑，sort_by = {sort_by}")
    
    if sort_by == 'user_rating':
        # MySQL不支持NULLS LAST，使用CASE WHEN替代
        query = query.order_by(
            db.case(
                (Review.rating.is_(None), 0),
                else_=Review.rating
            ).desc(),
            Novel.created_at.desc()
        )
        print("DEBUG: 应用用户评分排序")
    elif sort_by == 'avg_rating':
        query = query.order_by(Novel.avg_rating.desc(), Novel.created_at.desc())
        print("DEBUG: 应用平均评分排序")
    elif sort_by == 'updated_at':
        query = query.order_by(Novel.updated_at.desc())
        print("DEBUG: 应用更新时间排序")
    elif sort_by == 'created_at':
        query = query.order_by(Novel.created_at.desc())
        print("DEBUG: 应用创建时间排序（降序）")
    elif sort_by == 'created_at_asc':
        query = query.order_by(Novel.created_at.asc())
        print("DEBUG: 应用创建时间排序（升序）")
    elif sort_by == 'title':
        # 使用COLLATE确保中文字符正确排序
        query = query.order_by(db.text("novels.title COLLATE utf8mb4_unicode_ci ASC"), Novel.created_at.desc())
        print("DEBUG: 应用标题排序（升序）")
    elif sort_by == 'title_desc':
        query = query.order_by(db.text("novels.title COLLATE utf8mb4_unicode_ci DESC"), Novel.created_at.desc())
        print("DEBUG: 应用标题排序（降序）")
    elif sort_by == 'rating':
        query = query.order_by(Novel.avg_rating.desc(), Novel.created_at.desc())
        print("DEBUG: 应用评分排序（降序）")
    elif sort_by == 'rating_asc':
        query = query.order_by(Novel.avg_rating.asc(), Novel.created_at.desc())
        print("DEBUG: 应用评分排序（升序）")
    elif sort_by == 'favorites':
        # 按收藏时间排序
        if show_favorites:
            query = query.order_by(Favorite.created_at.desc())
            print("DEBUG: 应用收藏时间排序")
        else:
            query = query.order_by(Novel.created_at.desc())
            print("DEBUG: 收藏排序但未筛选收藏，使用创建时间")
    else:
        query = query.order_by(Novel.created_at.desc())
        print(f"DEBUG: 未知排序类型 {sort_by}，使用默认创建时间排序")
    
    # 分页
    result = query.paginate(page=page, per_page=20, error_out=False)
    
    # 处理结果，添加用户评分信息
    novels_with_ratings = []
    for novel, user_rating in result.items:
        novel.user_rating = user_rating or 0
        novels_with_ratings.append(novel)
    
    # 重构分页对象
    result.items = novels_with_ratings
    
    categories = Category.query.all()
    
    return render_template('novel_list.html', 
                         novels=result, 
                         categories=categories,
                         current_category=category_id,
                         current_sort=sort_by,
                         show_favorites=show_favorites,
                         current_date=date_filter)

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
    # 确保有用户session
    if 'user_id' not in session:
        session['user_id'] = 1  # 临时使用固定用户ID
    
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

@app.route('/read/<int:novel_id>')
def read_full_novel(novel_id):
    """阅读完整小说页面"""
    novel = Novel.query.get_or_404(novel_id)
    chapters = Chapter.query.filter_by(novel_id=novel_id).order_by(Chapter.chapter_number).all()
    
    # 合并所有章节内容，只保留正文
    full_content = ""
    for chapter in chapters:
        # 直接添加章节内容，不添加标题
        full_content += chapter.content + "\n\n"
    
    # 保存阅读进度（标记为已开始阅读）
    if 'user_id' in session:
        progress = ReadingProgress.query.filter_by(
            user_id=session['user_id'], 
            novel_id=novel_id
        ).first()
        
        if not progress:
            progress = ReadingProgress(
                user_id=session['user_id'],
                novel_id=novel_id,
                chapter_number=1
            )
            db.session.add(progress)
            db.session.commit()
    
    return render_template('read_full_novel.html', 
                         novel=novel, 
                         full_content=full_content,
                         total_chapters=len(chapters))

@app.route('/api/save_novel_content', methods=['POST'])
def save_novel_content():
    """保存编辑后的小说内容"""
    try:
        data = request.get_json()
        novel_id = data.get('novel_id')
        new_content = data.get('content', '')
        
        if not novel_id:
            return jsonify({'success': False, 'message': '缺少小说ID'})
        
        # 获取小说
        novel = Novel.query.get(novel_id)
        if not novel:
            return jsonify({'success': False, 'message': '小说不存在'})
        
        # 删除原有章节
        Chapter.query.filter_by(novel_id=novel_id).delete()
        
        # 创建新的单章节存储编辑后的内容
        new_chapter = Chapter(
            novel_id=novel_id,
            chapter_number=1,
            title="已编辑内容",
            content=new_content,
            word_count=len(new_content)
        )
        db.session.add(new_chapter)
        
        # 更新小说信息
        novel.total_chapters = 1
        novel.word_count = len(new_content)
        novel.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '内容保存成功',
            'word_count': len(new_content)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'})

@app.route('/api/get_novel_content/<int:novel_id>')
def get_novel_content(novel_id):
    """获取小说原始内容用于编辑"""
    try:
        chapters = Chapter.query.filter_by(novel_id=novel_id).order_by(Chapter.chapter_number).all()
        
        # 合并所有章节内容
        full_content = ""
        for chapter in chapters:
            full_content += chapter.content + "\n\n"
        
        return jsonify({
            'success': True,
            'content': full_content.strip()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取内容失败: {str(e)}'})

@app.route('/api/rate_novel', methods=['POST'])
def rate_novel():
    """给小说评分"""
    try:
        data = request.get_json()
        novel_id = data.get('novel_id')
        rating = data.get('rating')
        
        if not novel_id or not rating:
            return jsonify({'success': False, 'message': '缺少必要参数'})
        
        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': '评分必须在1-5之间'})
        
        # 检查小说是否存在
        novel = Novel.query.get(novel_id)
        if not novel:
            return jsonify({'success': False, 'message': '小说不存在'})
        
        # 模拟用户ID（实际应用中应从session获取）
        user_id = session.get('user_id', 1)  # 临时使用固定用户ID
        
        # 检查用户是否已经评分过
        existing_review = Review.query.filter_by(user_id=user_id, novel_id=novel_id).first()
        
        if existing_review:
            # 更新现有评分
            existing_review.rating = rating
            existing_review.created_at = datetime.utcnow()
        else:
            # 创建新评分
            new_review = Review(
                user_id=user_id,
                novel_id=novel_id,
                rating=rating,
                comment=""
            )
            db.session.add(new_review)
        
        # 重新计算平均评分
        all_reviews = Review.query.filter_by(novel_id=novel_id).all()
        if all_reviews:
            avg_rating = sum(review.rating for review in all_reviews) / len(all_reviews)
            novel.avg_rating = round(avg_rating, 1)
            novel.review_count = len(all_reviews)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '评分成功',
            'avg_rating': novel.avg_rating,
            'review_count': novel.review_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'评分失败: {str(e)}'})

@app.route('/api/get_user_rating/<int:novel_id>')
def get_user_rating(novel_id):
    """获取用户对小说的评分"""
    try:
        # 模拟用户ID（实际应用中应从session获取）
        user_id = session.get('user_id', 1)
        
        review = Review.query.filter_by(user_id=user_id, novel_id=novel_id).first()
        
        return jsonify({
            'success': True,
            'rating': review.rating if review else 0
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取评分失败: {str(e)}'})

@app.route('/api/add_category', methods=['POST'])
def add_category():
    """添加新分类"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': '分类名称不能为空'})
        
        # 检查分类名是否已存在
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category:
            return jsonify({'success': False, 'message': '分类名称已存在'})
        
        # 创建新分类
        new_category = Category(
            name=name,
            description=description,
            created_at=datetime.utcnow()
        )
        db.session.add(new_category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '分类添加成功',
            'category': {
                'id': new_category.id,
                'name': new_category.name,
                'description': new_category.description
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加分类失败: {str(e)}'})

@app.route('/api/update_category', methods=['POST'])
def update_category():
    """更新分类"""
    try:
        data = request.get_json()
        category_id = data.get('category_id')
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not category_id or not name:
            return jsonify({'success': False, 'message': '分类ID和名称不能为空'})
        
        # 获取要更新的分类
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'success': False, 'message': '分类不存在'})
        
        # 检查分类名是否与其他分类重复
        existing_category = Category.query.filter(
            db.and_(Category.name == name, Category.id != category_id)
        ).first()
        if existing_category:
            return jsonify({'success': False, 'message': '分类名称已存在'})
        
        # 更新分类信息
        category.name = name
        category.description = description
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '分类更新成功',
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新分类失败: {str(e)}'})

@app.route('/api/update_novel_title', methods=['POST'])
def update_novel_title():
    """更新小说标题"""
    try:
        data = request.get_json()
        novel_id = data.get('novel_id')
        new_title = data.get('title', '').strip()
        
        if not novel_id or not new_title:
            return jsonify({'success': False, 'message': '小说ID和标题不能为空'})
        
        # 获取要更新的小说
        novel = Novel.query.get(novel_id)
        if not novel:
            return jsonify({'success': False, 'message': '小说不存在'})
        
        # 检查标题是否与其他小说重复
        existing_novel = Novel.query.filter(
            db.and_(Novel.title == new_title, Novel.id != novel_id)
        ).first()
        if existing_novel:
            return jsonify({'success': False, 'message': '小说标题已存在'})
        
        # 保存原标题用于日志
        old_title = novel.title
        
        # 更新小说标题
        novel.title = new_title
        novel.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '标题更新成功',
            'novel': {
                'id': novel.id,
                'title': novel.title,
                'old_title': old_title
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新标题失败: {str(e)}'})

@app.route('/api/delete_novel', methods=['POST'])
def delete_novel():
    """删除小说及其相关数据"""
    try:
        data = request.get_json()
        novel_id = data.get('novel_id')
        
        if not novel_id:
            return jsonify({'success': False, 'message': '小说ID不能为空'})
        
        # 获取要删除的小说
        novel = Novel.query.get(novel_id)
        if not novel:
            return jsonify({'success': False, 'message': '小说不存在'})
        
        # 保存小说信息用于返回
        novel_info = {
            'id': novel.id,
            'title': novel.title,
            'author': novel.author
        }
        
        # 删除相关数据（按顺序删除以避免外键约束问题）
        
        # 1. 删除阅读进度
        ReadingProgress.query.filter_by(novel_id=novel_id).delete()
        
        # 2. 删除收藏
        Favorite.query.filter_by(novel_id=novel_id).delete()
        
        # 3. 删除评论和评分
        Review.query.filter_by(novel_id=novel_id).delete()
        
        # 4. 删除章节
        Chapter.query.filter_by(novel_id=novel_id).delete()
        
        # 5. 最后删除小说本身
        db.session.delete(novel)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '小说删除成功',
            'deleted_novel': novel_info
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除小说失败: {str(e)}'})

@app.route('/api/delete_category', methods=['POST'])
def delete_category():
    """删除分类"""
    try:
        data = request.get_json()
        category_id = data.get('category_id')
        
        if not category_id:
            return jsonify({'success': False, 'message': '分类ID不能为空'})
        
        # 获取要删除的分类
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'success': False, 'message': '分类不存在'})
        
        # 检查是否有小说使用此分类
        novels_count = Novel.query.filter_by(category_id=category_id).count()
        if novels_count > 0:
            return jsonify({
                'success': False, 
                'message': f'该分类下还有 {novels_count} 本小说，无法删除。请先移动或删除这些小说。'
            })
        
        # 删除分类
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '分类删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除分类失败: {str(e)}'})

@app.route('/api/toggle_favorite', methods=['POST'])
def toggle_favorite():
    """切换收藏状态"""
    try:
        data = request.get_json()
        novel_id = data.get('novel_id')
        
        if not novel_id:
            return jsonify({'success': False, 'message': '小说ID不能为空'})
        
        # 检查小说是否存在
        novel = Novel.query.get(novel_id)
        if not novel:
            return jsonify({'success': False, 'message': '小说不存在'})
        
        # 模拟用户ID（实际应用中应从session获取）
        user_id = session.get('user_id', 1)
        
        # 检查是否已收藏
        existing_favorite = Favorite.query.filter_by(user_id=user_id, novel_id=novel_id).first()
        
        if existing_favorite:
            # 取消收藏
            db.session.delete(existing_favorite)
            is_favorited = False
            message = '已取消收藏'
        else:
            # 添加收藏，支持位置记录
            chapter_number = data.get('chapter_number', 1)
            scroll_position = data.get('scroll_position', 0)
            
            new_favorite = Favorite(
                user_id=user_id,
                novel_id=novel_id,
                chapter_number=chapter_number,
                scroll_position=scroll_position
            )
            db.session.add(new_favorite)
            is_favorited = True
            message = '收藏成功'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'is_favorited': is_favorited
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'})

@app.route('/api/check_favorite/<int:novel_id>')
def check_favorite(novel_id):
    """检查收藏状态"""
    try:
        # 模拟用户ID（实际应用中应从session获取）
        user_id = session.get('user_id', 1)
        
        favorite = Favorite.query.filter_by(user_id=user_id, novel_id=novel_id).first()
        
        return jsonify({
            'success': True,
            'is_favorited': favorite is not None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'检查收藏状态失败: {str(e)}'})

@app.route('/api/save_reading_progress', methods=['POST'])
def save_reading_progress():
    """保存阅读进度"""
    try:
        data = request.get_json()
        novel_id = data.get('novel_id')
        chapter_number = data.get('chapter_number')
        scroll_position = data.get('scroll_position', 0)
        reading_time = data.get('reading_time', 0)
        
        if not all([novel_id, chapter_number]):
            return jsonify({'success': False, 'message': '参数不完整'})
        
        user_id = session.get('user_id', 1)
        
        # 查找或创建阅读进度记录
        progress = ReadingProgress.query.filter_by(
            user_id=user_id, 
            novel_id=novel_id
        ).first()
        
        if progress:
            progress.chapter_number = chapter_number
            progress.scroll_position = scroll_position
            progress.reading_time += reading_time
            progress.updated_at = datetime.utcnow()
        else:
            progress = ReadingProgress(
                user_id=user_id,
                novel_id=novel_id,
                chapter_number=chapter_number,
                scroll_position=scroll_position,
                reading_time=reading_time
            )
            db.session.add(progress)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '阅读进度已保存'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'保存进度失败: {str(e)}'})

@app.route('/api/get_reading_progress/<int:novel_id>')
def get_reading_progress(novel_id):
    """获取阅读进度"""
    try:
        user_id = session.get('user_id', 1)
        
        progress = ReadingProgress.query.filter_by(
            user_id=user_id, 
            novel_id=novel_id
        ).first()
        
        if progress:
            return jsonify({
                'success': True,
                'progress': {
                    'chapter_number': progress.chapter_number,
                    'scroll_position': progress.scroll_position,
                    'reading_time': progress.reading_time,
                    'updated_at': progress.updated_at.isoformat()
                }
            })
        else:
            return jsonify({
                'success': True,
                'progress': None
            })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取进度失败: {str(e)}'})

@app.route('/api/save_bookmark', methods=['POST'])
def save_bookmark():
    """保存书签位置"""
    try:
        data = request.get_json()
        novel_id = data.get('novel_id')
        chapter_number = data.get('chapter_number', 1)
        scroll_position = data.get('scroll_position', 0)
        
        if not novel_id:
            return jsonify({'success': False, 'message': '小说ID不能为空'})
        
        user_id = session.get('user_id', 1)
        
        # 查找现有收藏记录
        favorite = Favorite.query.filter_by(user_id=user_id, novel_id=novel_id).first()
        
        if favorite:
            # 更新收藏位置
            favorite.chapter_number = chapter_number
            favorite.scroll_position = scroll_position
            favorite.updated_at = datetime.utcnow()
            message = '书签位置已更新'
        else:
            # 创建新的收藏记录
            favorite = Favorite(
                user_id=user_id,
                novel_id=novel_id,
                chapter_number=chapter_number,
                scroll_position=scroll_position
            )
            db.session.add(favorite)
            message = '已添加到收藏并保存位置'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'is_favorited': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'保存书签失败: {str(e)}'})

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

# 测试添加小说的路由
@app.route('/add_test_data')
def add_test_data():
    """添加测试数据"""
    try:
        # 检查是否已有小说
        if Novel.query.first():
            return "已有小说数据，无需重复添加"
        
        # 获取玄幻分类
        xuanhuan_cat = Category.query.filter_by(name='玄幻').first()
        if not xuanhuan_cat:
            return "请先创建分类数据"
        
        # 创建测试小说
        novel = Novel(
            title="斗破苍穹",
            author="天蚕土豆",
            description="这里是斗气大陆，没有花俏的魔法，有的，仅仅是繁衍到巅峰的斗气！",
            category_id=xuanhuan_cat.id,
            total_chapters=3,
            word_count=500,
            status='ongoing',
            avg_rating=4.5,
            review_count=100
        )
        db.session.add(novel)
        db.session.flush()
        
        # 创建测试章节
        chapters_data = [
            {"title": "陨落的天才", "content": "斗气大陆，这是一个属于斗者的世界，没有花俏的魔法，有的，仅仅是繁衍到巅峰的斗气！\n\n在这里，斗气就是一切！\n\n三十年河东，三十年河西，莫欺少年穷！"},
            {"title": "来客", "content": "萧炎无奈的从床上爬起来，穿好衣服，走出房间。\n\n刚一出房间，一名衣着华贵的少女便出现在了他的视线之中。"},
            {"title": "退婚", "content": "\"萧炎哥哥，当年的你，确实是个天才，不过现在...\"少女轻笑道。"}
        ]
        
        for i, chapter_data in enumerate(chapters_data, 1):
            chapter = Chapter(
                novel_id=novel.id,
                chapter_number=i,
                title=chapter_data["title"],
                content=chapter_data["content"],
                word_count=len(chapter_data["content"])
            )
            db.session.add(chapter)
        
        db.session.commit()
        return "测试数据添加成功！<a href='/'>返回首页</a>"
        
    except Exception as e:
        db.session.rollback()
        return f"添加测试数据失败: {str(e)}"

@app.route('/api/novel_calendar')
def novel_calendar():
    """获取小说添加的月度日历数据"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # 获取指定月份的小说添加统计
        stats = db.session.query(
            func.date(Novel.created_at).label('date'),
            func.count(Novel.id).label('count')
        ).filter(
            extract('year', Novel.created_at) == year,
            extract('month', Novel.created_at) == month
        ).group_by(
            func.date(Novel.created_at)
        ).all()
        
        # 转换为字典格式
        calendar_data = {}
        for stat in stats:
            calendar_data[stat.date.strftime('%Y-%m-%d')] = stat.count
        
        return jsonify({
            'success': True,
            'year': year,
            'month': month,
            'data': calendar_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/novels_by_date')
def novels_by_date():
    """获取指定日期添加的小说列表"""
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({
                'success': False,
                'message': '缺少日期参数'
            }), 400
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        next_day = target_date + timedelta(days=1)
        
        novels = Novel.query.filter(
            Novel.created_at >= target_date,
            Novel.created_at < next_day
        ).order_by(Novel.created_at.desc()).all()
        
        novels_data = []
        for novel in novels:
            novels_data.append({
                'id': novel.id,
                'title': novel.title,
                'author': novel.author,
                'category': novel.category.name if novel.category else '未知',
                'created_at': novel.created_at.strftime('%H:%M')
            })
        
        return jsonify({
            'success': True,
            'date': date_str,
            'novels': novels_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/update_novel_category', methods=['POST'])
def update_novel_category():
    """更新小说分类"""
    try:
        data = request.get_json()
        novel_id = data.get('novel_id')
        new_category_id = data.get('category_id')
        
        if not novel_id or not new_category_id:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 查找小说
        novel = Novel.query.get(novel_id)
        if not novel:
            return jsonify({
                'success': False,
                'message': '小说不存在'
            }), 404
        
        # 查找分类
        category = Category.query.get(new_category_id)
        if not category:
            return jsonify({
                'success': False,
                'message': '分类不存在'
            }), 404
        
        # 更新分类
        old_category_name = novel.category.name if novel.category else '未知'
        novel.category_id = new_category_id
        novel.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'分类已从 "{old_category_name}" 更改为 "{category.name}"',
            'old_category': old_category_name,
            'new_category': category.name
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 500

@app.route('/api/get_categories')
def get_categories():
    """获取所有分类列表"""
    try:
        categories = Category.query.order_by(Category.name).all()
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description
            })
        
        return jsonify({
            'success': True,
            'categories': categories_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 启动小说阅读网站...")
    print("📊 数据库配置:")
    print(f"   - 数据库: MySQL 9.4.0")
    print(f"   - 地址: X.X.X.X:3306")
    print(f"   - 数据库: novol")
    print(f"   - 用户: novol")
    print("🌐 访问地址:")
    print("   - 本地: http://127.0.0.1:5000")
    print("   - 局域网: http://X.X.X.X:5000")
    print("   - 添加测试数据: http://X.X.X.X:5000/add_test_data")
    print("-" * 50)
    
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        use_reloader=True,  # 启用代码重载但更稳定
        reloader_type='stat',  # 使用stat重载器
        threaded=True  # 启用多线程处理
    )
