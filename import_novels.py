import os
import re
from datetime import datetime
from app_fixed import app, db, Novel, Chapter, Category

def clean_text(text):
    """清理文本内容"""
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 移除特殊字符
    text = re.sub(r'[^\u4e00-\u9fff\w\s，。！？；：""''（）【】《》、]', '', text)
    return text.strip()

def extract_chapters(content):
    """从txt内容中提取章节"""
    # 常见的章节标题模式
    chapter_patterns = [
        r'第[一二三四五六七八九十百千万\d]+章\s*[^\n]*',
        r'第[一二三四五六七八九十百千万\d]+回\s*[^\n]*',
        r'Chapter\s*\d+\s*[^\n]*',
        r'\d+[\.\-\s]*[^\n]*章[^\n]*'
    ]
    
    chapters = []
    current_chapter = {"title": "第一章", "content": ""}
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检查是否是章节标题
        is_chapter_title = False
        for pattern in chapter_patterns:
            if re.match(pattern, line):
                # 保存当前章节
                if current_chapter["content"]:
                    chapters.append(current_chapter)
                
                # 开始新章节
                current_chapter = {
                    "title": line,
                    "content": ""
                }
                is_chapter_title = True
                break
        
        if not is_chapter_title:
            current_chapter["content"] += line + "\n"
    
    # 添加最后一章
    if current_chapter["content"]:
        chapters.append(current_chapter)
    
    # 如果没有找到章节分割，将整个文件作为一章
    if not chapters:
        chapters = [{"title": "正文", "content": content}]
    
    return chapters

def extract_metadata_from_filename(filename):
    """从文件名提取元数据"""
    # 移除扩展名
    name = os.path.splitext(filename)[0]
    
    # 尝试匹配 "作者-书名" 或 "书名-作者" 格式
    if '-' in name:
        parts = name.split('-', 1)
        if len(parts) == 2:
            # 简单启发式：较短的可能是作者名
            if len(parts[0]) <= len(parts[1]):
                return parts[1].strip(), parts[0].strip()
            else:
                return parts[0].strip(), parts[1].strip()
    
    # 如果没有分隔符，使用文件名作为书名，作者为"未知"
    return name.strip(), "未知作者"

def import_txt_file(file_path, category_id=1):
    """导入单个txt文件"""
    print(f"正在导入: {file_path}")
    
    try:
        # 尝试不同的编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"成功使用编码 {encoding} 读取文件")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"无法读取文件 {file_path}，跳过")
            return False
        
        # 提取元数据
        filename = os.path.basename(file_path)
        title, author = extract_metadata_from_filename(filename)
        
        # 检查小说是否已存在
        existing_novel = Novel.query.filter_by(title=title, author=author).first()
        if existing_novel:
            print(f"小说 {title} 已存在，跳过")
            return False
        
        # 提取章节
        chapters_data = extract_chapters(content)
        
        # 创建小说记录
        novel = Novel(
            title=title,
            author=author,
            description=f"从txt文件导入的小说：{filename}",
            category_id=category_id,
            total_chapters=len(chapters_data),
            word_count=len(content),
            status='completed'
        )
        
        db.session.add(novel)
        db.session.flush()  # 获取novel.id
        
        # 创建章节记录
        for i, chapter_data in enumerate(chapters_data, 1):
            chapter = Chapter(
                novel_id=novel.id,
                chapter_number=i,
                title=chapter_data["title"],
                content=clean_text(chapter_data["content"]),
                word_count=len(chapter_data["content"])
            )
            db.session.add(chapter)
        
        db.session.commit()
        print(f"成功导入小说: {title}，共 {len(chapters_data)} 章")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"导入文件 {file_path} 时出错: {str(e)}")
        return False

def import_txt_directory(directory_path, category_id=1, max_files=None):
    """批量导入目录下的txt文件"""
    if not os.path.exists(directory_path):
        print(f"目录不存在: {directory_path}")
        return
    
    txt_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    
    if max_files:
        txt_files = txt_files[:max_files]
    
    print(f"找到 {len(txt_files)} 个txt文件")
    
    success_count = 0
    failed_count = 0
    
    for file_path in txt_files:
        if import_txt_file(file_path, category_id):
            success_count += 1
        else:
            failed_count += 1
    
    print(f"导入完成！成功: {success_count}, 失败: {failed_count}")

def create_default_categories():
    """创建默认分类"""
    default_categories = [
        {"name": "玄幻", "description": "玄幻小说"},
        {"name": "武侠", "description": "武侠小说"},
        {"name": "都市", "description": "都市小说"},
        {"name": "历史", "description": "历史小说"},
        {"name": "科幻", "description": "科幻小说"},
        {"name": "言情", "description": "言情小说"},
        {"name": "其他", "description": "其他类型"}
    ]
    
    for cat_data in default_categories:
        if not Category.query.filter_by(name=cat_data["name"]).first():
            category = Category(name=cat_data["name"], description=cat_data["description"])
            db.session.add(category)
    
    db.session.commit()
    print("默认分类创建完成")

if __name__ == "__main__":
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 创建默认分类
        create_default_categories()
        
        # 示例：导入txt文件
        # import_txt_directory("/path/to/your/txt/files", category_id=1, max_files=10)
        
        print("数据库初始化完成！")
        print("使用方法：")
        print("1. 修改数据库配置：编辑 app.py 中的数据库连接字符串")
        print("2. 导入txt文件：import_txt_directory('/path/to/txt/files')")