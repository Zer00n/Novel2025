# 通用txt小说导入脚本
import os
import re
import pymysql
from datetime import datetime

def add_new_category(category_name, description=""):
    """添加新的小说分类"""
    config = {
        'host': 'X.X.X.X',
        'port': 3306,
        'user': 'novol',
        'password': 'XXXXXXXXXX',
        'database': 'novol',
        'charset': 'utf8mb4'
    }
    
    try:
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor:
            # 检查分类是否已存在
            cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"✅ 分类 '{category_name}' 已存在，ID: {existing[0]}")
                return existing[0]
            
            # 插入新分类
            cursor.execute(
                "INSERT INTO categories (name, description) VALUES (%s, %s)",
                (category_name, description)
            )
            connection.commit()
            category_id = cursor.lastrowid
            print(f"✅ 成功添加分类 '{category_name}'，ID: {category_id}")
            return category_id
            
    except Exception as e:
        print(f"❌ 添加分类失败: {e}")
        return None
    finally:
        if 'connection' in locals():
            connection.close()

def clean_filename(filename):
    """清理文件名，提取小说标题"""
    # 移除扩展名
    title = os.path.splitext(filename)[0]
    
    # 移除常见的标记
    patterns_to_remove = [
        r'\[.*?\]',  # 移除 [搜书吧] 等标记
        r'（.*?）',   # 移除中文括号内容
        r'\(.*?\)',  # 移除英文括号内容
        r'-soushu.*',  # 移除网站标记
        r'\.txt$',   # 移除.txt后缀
        r'第.*?章.*',  # 移除章节标记
        r'\d+-\d+',  # 移除数字范围 如 1-42
        r'完结?本?',  # 移除"完结"、"完本"
        r'作者[:：].*',  # 移除作者信息
    ]
    
    for pattern in patterns_to_remove:
        title = re.sub(pattern, '', title)
    
    # 清理多余空格和特殊字符
    title = re.sub(r'\s+', ' ', title).strip()
    title = re.sub(r'^[《【\'"]*|[》】\'"]*$', '', title)
    
    return title if title else filename

def extract_chapters_simple(content):
    """简单的章节提取（按段落分割）"""
    # 将整个内容按双换行分割成段落
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    if not paragraphs:
        return [{"title": "正文", "content": content}]
    
    # 如果内容较短，作为单章处理
    if len(content) < 3000:
        return [{"title": "正文", "content": content}]
    
    # 尝试按章节标题分割
    chapter_patterns = [
        r'^第[一二三四五六七八九十百千万\d]+章.*',
        r'^第[一二三四五六七八九十百千万\d]+节.*',
        r'^Chapter\s*\d+.*',
        r'^\d+[\.\-\s]*.*',
        r'^[一二三四五六七八九十]+[\.\-、\s]*.*'
    ]
    
    chapters = []
    current_chapter = {"title": "第一章", "content": ""}
    
    for paragraph in paragraphs:
        is_chapter_title = False
        
        # 检查是否是章节标题
        for pattern in chapter_patterns:
            if re.match(pattern, paragraph) and len(paragraph) < 100:
                # 保存当前章节
                if current_chapter["content"].strip():
                    chapters.append(current_chapter)
                
                # 开始新章节
                current_chapter = {
                    "title": paragraph,
                    "content": ""
                }
                is_chapter_title = True
                break
        
        if not is_chapter_title:
            current_chapter["content"] += paragraph + "\n\n"
    
    # 添加最后一章
    if current_chapter["content"].strip():
        chapters.append(current_chapter)
    
    # 如果没有找到章节分割，按长度分割
    if len(chapters) <= 1:
        return split_by_length(content)
    
    return chapters

def split_by_length(content, max_length=5000):
    """按长度分割内容"""
    if len(content) <= max_length:
        return [{"title": "正文", "content": content}]
    
    chapters = []
    sentences = content.split('。')
    current_chapter = ""
    chapter_num = 1
    
    for sentence in sentences:
        if len(current_chapter) + len(sentence) > max_length:
            if current_chapter:
                chapters.append({
                    "title": f"第{chapter_num}章",
                    "content": current_chapter.strip() + "。"
                })
                chapter_num += 1
                current_chapter = sentence
            else:
                current_chapter += sentence
        else:
            current_chapter += sentence + "。"
    
    # 添加最后一章
    if current_chapter:
        chapters.append({
            "title": f"第{chapter_num}章",
            "content": current_chapter.strip()
        })
    
    return chapters

def import_single_txt(file_path, category_id, default_author="未知作者"):
    """导入单个txt文件"""
    config = {
        'host': 'X.X.X.X',
        'port': 3306,
        'user': 'novol',
        'password': 'XXXXXXXX',
        'database': 'novol',
        'charset': 'utf8mb4'
    }
    
    filename = os.path.basename(file_path)
    title = clean_filename(filename)
    
    print(f"📖 正在导入: {filename}")
    print(f"   提取标题: {title}")
    
    # 检查内容类型（基本过滤）
    if any(keyword in title.lower() for keyword in ['成人', '情色', '性', '淫']):
        print(f"⚠️  跳过不适宜内容: {title}")
        return False
    
    try:
        # 尝试不同编码读取文件
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"   使用编码: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if not content:
            print(f"❌ 无法读取文件编码: {filename}")
            return False
        
        # 基本内容过滤
        if len(content) < 100:
            print(f"⚠️  内容过短，跳过: {title}")
            return False
        
        # 连接数据库
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor:
            # 检查小说是否已存在
            cursor.execute("SELECT id FROM novels WHERE title = %s", (title,))
            if cursor.fetchone():
                print(f"⚠️  小说已存在，跳过: {title}")
                return False
            
            # 提取章节
            chapters_data = extract_chapters_simple(content)
            
            # 插入小说记录
            cursor.execute("""
                INSERT INTO novels (title, author, description, category_id, total_chapters, word_count, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                title,
                default_author,
                f"从txt文件导入的小说：{filename}",
                category_id,
                len(chapters_data),
                len(content),
                'completed'
            ))
            
            novel_id = cursor.lastrowid
            
            # 插入章节
            for i, chapter_data in enumerate(chapters_data, 1):
                cursor.execute("""
                    INSERT INTO chapters (novel_id, chapter_number, title, content, word_count)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    novel_id,
                    i,
                    chapter_data["title"],
                    chapter_data["content"],
                    len(chapter_data["content"])
                ))
            
            connection.commit()
            print(f"✅ 成功导入: {title} ({len(chapters_data)}章, {len(content)}字)")
            return True
            
    except Exception as e:
        print(f"❌ 导入失败 {title}: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def import_directory(directory_path, category_name, category_description="", max_files=None):
    """批量导入目录下的txt文件"""
    if not os.path.exists(directory_path):
        print(f"❌ 目录不存在: {directory_path}")
        return
    
    # 添加或获取分类
    category_id = add_new_category(category_name, category_description)
    if not category_id:
        print("❌ 无法创建分类，导入中止")
        return
    
    # 获取txt文件列表
    txt_files = []
    for file in os.listdir(directory_path):
        if file.lower().endswith('.txt'):
            txt_files.append(os.path.join(directory_path, file))
    
    if max_files:
        txt_files = txt_files[:max_files]
    
    print(f"📚 找到 {len(txt_files)} 个txt文件")
    print(f"📂 目标分类: {category_name} (ID: {category_id})")
    print("-" * 60)
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for file_path in txt_files:
        result = import_single_txt(file_path, category_id)
        if result is True:
            success_count += 1
        elif result is False:
            failed_count += 1
        else:
            skipped_count += 1
        print()  # 空行分隔
    
    print("=" * 60)
    print(f"📊 导入完成统计:")
    print(f"   ✅ 成功: {success_count}")
    print(f"   ❌ 失败: {failed_count}")
    print(f"   ⚠️  跳过: {skipped_count}")
    print(f"   📖 总计: {len(txt_files)}")

if __name__ == "__main__":
    print("=" * 60)
    print("        通用txt小说导入工具")
    print("=" * 60)
    print()
    print("🔧 使用方法:")
    print("   1. 修改下方的目录路径和分类信息")
    print("   2. 运行脚本进行导入")
    print()
    print("⚠️  注意: 该工具会自动过滤不适宜内容")
    print()
    
    # 示例使用 - 请修改为你的实际路径和分类
    """
    import_directory(
        directory_path="/path/to/your/novels",
        category_name="现代文学",
        category_description="现代文学作品",
        max_files=10  # 限制导入数量，用于测试
    )
    """
    
    print("💡 请编辑脚本，取消注释并修改上述示例代码来使用")
