#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说TXT导入工具
支持通过命令行参数指定目录和分类ID来批量导入TXT小说
"""

import os
import re
import sys
import argparse
import pymysql
import chardet
import json
from datetime import datetime
from pathlib import Path

# 数据库配置
DB_CONFIG = {
    'host': 'X.X.X.X',
    'port': 3306,
    'user': 'novol',
    'password': 'XXXXXXXXXXXXXX',
    'database': 'novol',
    'charset': 'utf8mb4'
}

# 全局失败文件跟踪
FAILED_FILES = {
    'encoding_errors': [],  # 编码错误的文件
    'content_errors': [],   # 内容错误的文件
    'database_errors': [],  # 数据库错误的文件
    'duplicate_files': [],  # 重复的文件
    'other_errors': []      # 其他错误的文件
}

def get_database_connection():
    """获取数据库连接"""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def verify_category_exists(category_id):
    """验证分类是否存在"""
    connection = get_database_connection()
    if not connection:
        return False, None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, description FROM categories WHERE id = %s", (category_id,))
            result = cursor.fetchone()
            if result:
                return True, {"id": result[0], "name": result[1], "description": result[2]}
            else:
                return False, None
    except Exception as e:
        print(f"❌ 查询分类失败: {e}")
        return False, None
    finally:
        connection.close()

def list_available_categories():
    """显示所有可用的分类"""
    connection = get_database_connection()
    if not connection:
        return
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, description FROM categories ORDER BY id")
            categories = cursor.fetchall()
            
            print("\n📚 可用的小说分类:")
            print("-" * 50)
            print(f"{'ID':<4} {'分类名称':<15} {'描述'}")
            print("-" * 50)
            for cat in categories:
                desc = cat[2] if cat[2] else "无描述"
                print(f"{cat[0]:<4} {cat[1]:<15} {desc}")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ 获取分类列表失败: {e}")
    finally:
        connection.close()

def detect_file_encoding(file_path):
    """
    增强的文件编码检测
    返回: (encoding, confidence, content) 或 (None, 0, None)
    """
    try:
        # 读取文件的一部分进行编码检测
        with open(file_path, 'rb') as f:
            raw_data = f.read(10240)  # 读取前10KB进行检测
        
        # 使用chardet检测编码
        detected = chardet.detect(raw_data)
        encoding = detected.get('encoding')
        confidence = detected.get('confidence', 0)
        
        print(f"   chardet检测: {encoding} (置信度: {confidence:.2f})")
        
        # 如果置信度太低，尝试常见编码
        if confidence < 0.7:
            print(f"   置信度较低，尝试常见编码...")
            
        # 按优先级尝试编码
        encoding_list = []
        
        # 如果chardet检测的编码置信度高，优先使用
        if encoding and confidence > 0.7:
            encoding_list.append(encoding)
        
        # 添加常见的中文编码
        common_encodings = [
            'utf-8', 'utf-8-sig',  # UTF-8 (with/without BOM)
            'gbk', 'gb2312', 'gb18030',  # 中文编码
            'utf-16', 'utf-16le', 'utf-16be',  # UTF-16
            'big5',  # 繁体中文
            'ascii', 'latin1', 'cp1252'  # 其他编码
        ]
        
        # 去重并保持顺序
        for enc in common_encodings:
            if enc not in encoding_list:
                encoding_list.append(enc)
        
        # 尝试每种编码
        for try_encoding in encoding_list:
            try:
                with open(file_path, 'r', encoding=try_encoding) as f:
                    content = f.read()
                
                # 验证内容质量
                if validate_content_quality(content, try_encoding):
                    print(f"   ✅ 成功使用编码: {try_encoding}")
                    return try_encoding, confidence, content
                else:
                    print(f"   ❌ 编码 {try_encoding} 内容质量差")
                    
            except (UnicodeDecodeError, UnicodeError) as e:
                print(f"   ❌ 编码 {try_encoding} 失败: {str(e)[:50]}")
                continue
            except Exception as e:
                print(f"   ❌ 编码 {try_encoding} 异常: {str(e)[:50]}")
                continue
        
        print(f"   ❌ 所有编码尝试都失败")
        return None, 0, None
        
    except Exception as e:
        print(f"   ❌ 编码检测异常: {e}")
        return None, 0, None

def validate_content_quality(content, encoding):
    """
    验证解码后的内容质量
    返回: True 如果内容质量好，False 如果质量差
    """
    if not content or len(content.strip()) < 10:
        return False
    
    # 计算可打印字符比例
    printable_chars = sum(1 for c in content if c.isprintable() or c.isspace())
    total_chars = len(content)
    printable_ratio = printable_chars / total_chars if total_chars > 0 else 0
    
    # 计算中文字符比例
    chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
    chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0
    
    # 检查是否有过多的替换字符
    replacement_chars = content.count('\ufffd')
    replacement_ratio = replacement_chars / total_chars if total_chars > 0 else 0
    
    print(f"     可打印字符比例: {printable_ratio:.3f}")
    print(f"     中文字符比例: {chinese_ratio:.3f}")
    print(f"     替换字符比例: {replacement_ratio:.3f}")
    
    # 质量判断标准
    if replacement_ratio > 0.01:  # 替换字符超过1%
        return False
    
    if printable_ratio < 0.8:  # 可打印字符少于80%
        return False
    
    # 对于中文文档，中文字符应该占一定比例
    if chinese_ratio > 0.1 and printable_ratio > 0.9:
        return True
    
    # 对于其他文档，可打印字符比例高即可
    if printable_ratio > 0.95:
        return True
    
    return False

def save_failed_files_report(output_dir="."):
    """保存失败文件报告"""
    if not any(FAILED_FILES.values()):
        print("📊 没有失败的文件，无需生成报告")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f"import_failed_files_{timestamp}.json")
    
    # 统计信息
    total_failed = sum(len(files) for files in FAILED_FILES.values())
    
    report_data = {
        "生成时间": datetime.now().isoformat(),
        "失败文件总数": total_failed,
        "失败分类统计": {
            "编码错误": len(FAILED_FILES['encoding_errors']),
            "内容错误": len(FAILED_FILES['content_errors']),
            "数据库错误": len(FAILED_FILES['database_errors']),
            "重复文件": len(FAILED_FILES['duplicate_files']),
            "其他错误": len(FAILED_FILES['other_errors'])
        },
        "失败文件详情": FAILED_FILES
    }
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 失败文件报告已保存: {report_file}")
        print(f"   总失败文件数: {total_failed}")
        
        # 显示各类错误统计
        for error_type, count in report_data["失败分类统计"].items():
            if count > 0:
                print(f"   {error_type}: {count}")
        
        return report_file
        
    except Exception as e:
        print(f"❌ 保存失败文件报告失败: {e}")
        return None

def retry_failed_files(report_file, category_id, retry_type=None):
    """
    重试失败的文件
    retry_type: 'encoding', 'content', 'database', 'duplicate', 'other' 或 None (全部重试)
    """
    if not os.path.exists(report_file):
        print(f"❌ 报告文件不存在: {report_file}")
        return False
    
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        failed_files = report_data.get("失败文件详情", {})
        
        # 确定要重试的文件
        files_to_retry = []
        if retry_type:
            retry_key = f"{retry_type}_errors"
            if retry_key in failed_files:
                files_to_retry = failed_files[retry_key]
                print(f"🔄 重试 {retry_type} 错误文件: {len(files_to_retry)} 个")
            else:
                print(f"❌ 无效的重试类型: {retry_type}")
                return False
        else:
            # 重试所有失败文件（除了重复文件）
            for key, files in failed_files.items():
                if key != 'duplicate_files':  # 跳过重复文件
                    files_to_retry.extend(files)
            print(f"🔄 重试所有失败文件: {len(files_to_retry)} 个")
        
        if not files_to_retry:
            print("📝 没有需要重试的文件")
            return True
        
        # 清空失败文件记录以记录新的失败
        global FAILED_FILES
        FAILED_FILES = {
            'encoding_errors': [],
            'content_errors': [],
            'database_errors': [],
            'duplicate_files': [],
            'other_errors': []
        }
        
        print("-" * 60)
        
        success_count = 0
        for i, file_info in enumerate(files_to_retry, 1):
            file_path = file_info if isinstance(file_info, str) else file_info.get('file_path', file_info)
            print(f"[{i}/{len(files_to_retry)}] 重试: {os.path.basename(file_path)}")
            
            if import_txt_file(file_path, category_id):
                success_count += 1
            print()
        
        print("=" * 60)
        print(f"🔄 重试完成统计:")
        print(f"   ✅ 成功: {success_count}")
        print(f"   ❌ 仍然失败: {len(files_to_retry) - success_count}")
        
        # 保存新的失败文件报告
        if any(FAILED_FILES.values()):
            new_report = save_failed_files_report()
            if new_report:
                print(f"📊 新的失败文件报告: {new_report}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ 重试失败文件时出错: {e}")
        return False

def clean_filename_basic(filename):
    """基础文件名清理，提取标题"""
    # 移除扩展名
    title = os.path.splitext(filename)[0]
    
    # 移除常见的标记
    patterns_to_remove = [
        r'\[搜书吧\]',
        r'-soushu.*',
        r'\.txt$',
        r'-\[搜书吧网址\]',
        r'--.*',
    ]
    
    for pattern in patterns_to_remove:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    # 清理多余空格和特殊字符
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title if title else filename

def extract_chapters_from_content(content):
    """从内容中提取章节"""
    # 常见的章节标题模式
    chapter_patterns = [
        r'第[一二三四五六七八九十百千万\d]+章[^\n]*',
        r'第[一二三四五六七八九十百千万\d]+节[^\n]*',
        r'Chapter\s*\d+[^\n]*',
        r'^\d+[\.\-\s]*[^\n]*',
        r'^[一二三四五六七八九十]+[\.\-、\s]*[^\n]*'
    ]
    
    lines = content.split('\n')
    chapters = []
    current_chapter = {"title": "第一章", "content": ""}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检查是否是章节标题
        is_chapter_title = False
        for pattern in chapter_patterns:
            if re.match(pattern, line) and len(line) < 200:
                # 保存当前章节
                if current_chapter["content"].strip():
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
    if current_chapter["content"].strip():
        chapters.append(current_chapter)
    
    # 如果没有找到章节分割，将整个文件作为一章
    if not chapters:
        chapters = [{"title": "正文", "content": content}]
    
    return chapters

def import_txt_file(file_path, category_id, default_author="未知作者"):
    """导入单个txt文件"""
    filename = os.path.basename(file_path)
    title = clean_filename_basic(filename)
    
    print(f"📖 正在导入: {filename}")
    print(f"   提取标题: {title}")
    print(f"   文件大小: {os.path.getsize(file_path) / 1024:.1f} KB")
    
    try:
        # 使用增强的编码检测
        encoding, confidence, content = detect_file_encoding(file_path)
        
        if not content:
            error_info = {
                "file_path": file_path,
                "filename": filename,
                "title": title,
                "error": "无法检测或读取文件编码",
                "file_size": os.path.getsize(file_path),
                "timestamp": datetime.now().isoformat()
            }
            FAILED_FILES['encoding_errors'].append(error_info)
            print(f"❌ 编码检测失败: {filename}")
            return False
        
        if len(content.strip()) < 50:
            error_info = {
                "file_path": file_path,
                "filename": filename,
                "title": title,
                "error": "内容过短",
                "content_length": len(content.strip()),
                "encoding": encoding,
                "timestamp": datetime.now().isoformat()
            }
            FAILED_FILES['content_errors'].append(error_info)
            print(f"⚠️  内容过短，跳过: {title}")
            return False
        
        # 连接数据库
        connection = get_database_connection()
        if not connection:
            error_info = {
                "file_path": file_path,
                "filename": filename,
                "title": title,
                "error": "数据库连接失败",
                "encoding": encoding,
                "timestamp": datetime.now().isoformat()
            }
            FAILED_FILES['database_errors'].append(error_info)
            return False
        
        try:
            with connection.cursor() as cursor:
                # 检查小说是否已存在
                cursor.execute("SELECT id FROM novels WHERE title = %s", (title,))
                if cursor.fetchone():
                    error_info = {
                        "file_path": file_path,
                        "filename": filename,
                        "title": title,
                        "error": "小说标题已存在",
                        "encoding": encoding,
                        "timestamp": datetime.now().isoformat()
                    }
                    FAILED_FILES['duplicate_files'].append(error_info)
                    print(f"⚠️  小说已存在，跳过: {title}")
                    return False
                
                # 提取章节
                chapters_data = extract_chapters_from_content(content)
                print(f"   检测到章节数: {len(chapters_data)}")
                
                if not chapters_data:
                    error_info = {
                        "file_path": file_path,
                        "filename": filename,
                        "title": title,
                        "error": "无法提取章节内容",
                        "encoding": encoding,
                        "content_length": len(content),
                        "timestamp": datetime.now().isoformat()
                    }
                    FAILED_FILES['content_errors'].append(error_info)
                    print(f"❌ 无法提取章节: {title}")
                    return False
                
                # 插入小说记录
                cursor.execute("""
                    INSERT INTO novels (title, author, description, category_id, total_chapters, word_count, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    title,
                    default_author,
                    f"从txt文件导入：{filename}（编码：{encoding}）",
                    category_id,
                    len(chapters_data),
                    len(content),
                    'completed',
                    datetime.now(),
                    datetime.now()
                ))
                
                novel_id = cursor.lastrowid
                
                # 插入章节
                for i, chapter_data in enumerate(chapters_data, 1):
                    cursor.execute("""
                        INSERT INTO chapters (novel_id, chapter_number, title, content, word_count, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        novel_id,
                        i,
                        chapter_data["title"][:200],  # 限制标题长度
                        chapter_data["content"],
                        len(chapter_data["content"]),
                        datetime.now()
                    ))
                
                connection.commit()
                print(f"✅ 成功导入: {title}")
                print(f"   章节数: {len(chapters_data)}")
                print(f"   总字数: {len(content):,}")
                print(f"   使用编码: {encoding}")
                print(f"   置信度: {confidence:.2f}")
                return True
                
        except Exception as e:
            error_info = {
                "file_path": file_path,
                "filename": filename,
                "title": title,
                "error": f"数据库操作失败: {str(e)}",
                "encoding": encoding,
                "timestamp": datetime.now().isoformat()
            }
            FAILED_FILES['database_errors'].append(error_info)
            print(f"❌ 数据库操作失败 {title}: {e}")
            connection.rollback()
            return False
        finally:
            connection.close()
            
    except Exception as e:
        error_info = {
            "file_path": file_path,
            "filename": filename,
            "title": title,
            "error": f"未知错误: {str(e)}",
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "timestamp": datetime.now().isoformat()
        }
        FAILED_FILES['other_errors'].append(error_info)
        print(f"❌ 导入失败 {title}: {e}")
        return False

def batch_import_directory(directory_path, category_id, max_files=None):
    """批量导入目录下的txt文件"""
    if not os.path.exists(directory_path):
        print(f"❌ 目录不存在: {directory_path}")
        return False
    
    if not os.path.isdir(directory_path):
        print(f"❌ 路径不是目录: {directory_path}")
        return False
    
    print(f"📂 扫描目录: {directory_path}")
    
    # 验证分类存在
    category_exists, category_info = verify_category_exists(category_id)
    if not category_exists:
        print(f"❌ 分类ID {category_id} 不存在")
        list_available_categories()
        return False
    
    print(f"📂 目标分类: {category_info['name']} (ID: {category_id})")
    
    # 获取txt文件列表
    txt_files = []
    for file in os.listdir(directory_path):
        if file.lower().endswith('.txt'):
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):  # 确保是文件而不是目录
                txt_files.append(file_path)
    
    if not txt_files:
        print(f"❌ 目录中没有找到txt文件: {directory_path}")
        return False
    
    # 应用文件数量限制
    if max_files and max_files > 0:
        txt_files = txt_files[:max_files]
        print(f"📚 找到 {len(txt_files)} 个txt文件（限制最多 {max_files} 个）")
    else:
        print(f"📚 找到 {len(txt_files)} 个txt文件")
    
    # 清空失败文件记录
    global FAILED_FILES
    FAILED_FILES = {
        'encoding_errors': [],
        'content_errors': [],
        'database_errors': [],
        'duplicate_files': [],
        'other_errors': []
    }
    
    print("-" * 60)
    
    success_count = 0
    failed_count = 0
    
    for i, file_path in enumerate(txt_files, 1):
        print(f"[{i}/{len(txt_files)}] ", end="")
        if import_txt_file(file_path, category_id):
            success_count += 1
        else:
            failed_count += 1
        print()  # 空行分隔
    
    print("=" * 60)
    print(f"📊 导入完成统计:")
    print(f"   ✅ 成功: {success_count}")
    print(f"   ❌ 失败: {failed_count}")
    print(f"   📖 总计: {len(txt_files)}")
    print(f"   📂 分类: {category_info['name']} (ID: {category_id})")
    
    # 生成失败文件报告
    if failed_count > 0:
        report_file = save_failed_files_report()
        if report_file:
            print(f"\n💡 使用以下命令重试失败的文件:")
            print(f"   python {sys.argv[0]} --retry {report_file} {category_id}")
            print(f"   python {sys.argv[0]} --retry {report_file} {category_id} --retry-type encoding")
    
    return success_count > 0

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="小说TXT导入工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s /path/to/txt/files 1                    # 导入目录下所有txt到分类ID 1
  %(prog)s /path/to/txt/files 1 --max-files 10    # 最多导入10个文件
  %(prog)s --list-categories                       # 查看所有可用分类
  %(prog)s single.txt 2                           # 导入单个文件到分类ID 2
  %(prog)s --retry report.json 1                  # 重试失败文件报告中的所有文件
  %(prog)s --retry report.json 1 --retry-type encoding  # 只重试编码错误的文件

注意事项:
  - 请确保指定的分类ID存在
  - 工具会自动跳过已存在的同名小说
  - 支持多种文本编码：UTF-8, GBK, GB2312, UTF-16, Big5等
  - 失败的文件会生成详细的错误报告
  - 重试类型: encoding, content, database, duplicate, other
        """
    )
    
    parser.add_argument('path', nargs='?', help='txt文件或目录路径')
    parser.add_argument('category_id', type=int, nargs='?', help='分类ID')
    parser.add_argument('--max-files', type=int, help='最大导入文件数量（用于测试）')
    parser.add_argument('--list-categories', action='store_true', help='显示所有可用分类')
    parser.add_argument('--author', default='未知作者', help='默认作者名称')
    parser.add_argument('--retry', help='重试失败文件报告的路径')
    parser.add_argument('--retry-type', choices=['encoding', 'content', 'database', 'duplicate', 'other'], 
                       help='指定重试的错误类型')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("        小说TXT导入工具 (增强版)")
    print("=" * 60)
    
    # 显示分类列表
    if args.list_categories:
        list_available_categories()
        return
    
    # 重试失败文件
    if args.retry:
        if args.category_id is None:
            print("❌ 错误: 重试时需要指定分类ID")
            print("\n使用示例: python import_direct.py --retry report.json 1")
            return
        
        print(f"🔄 重试失败文件报告: {args.retry}")
        if args.retry_type:
            print(f"   重试类型: {args.retry_type}")
        else:
            print("   重试所有失败文件（除重复文件）")
        print("-" * 60)
        
        if retry_failed_files(args.retry, args.category_id, args.retry_type):
            print("\n✅ 重试完成!")
        else:
            print("\n❌ 重试失败!")
        return
    
    # 检查必需参数
    if not args.path or args.category_id is None:
        print("❌ 错误: 需要指定路径和分类ID")
        print("\n使用 --help 查看帮助信息")
        print("使用 --list-categories 查看可用分类")
        print("使用 --retry <report.json> <category_id> 重试失败文件")
        return
    
    # 检查路径是否存在
    if not os.path.exists(args.path):
        print(f"❌ 路径不存在: {args.path}")
        return
    
    # 判断是文件还是目录
    if os.path.isfile(args.path):
        # 单个文件导入
        if not args.path.lower().endswith('.txt'):
            print(f"❌ 不是txt文件: {args.path}")
            return
        
        # 验证分类
        category_exists, category_info = verify_category_exists(args.category_id)
        if not category_exists:
            print(f"❌ 分类ID {args.category_id} 不存在")
            list_available_categories()
            return
        
        print(f"📖 导入单个文件: {args.path}")
        print(f"📂 目标分类: {category_info['name']} (ID: {args.category_id})")
        print("-" * 60)
        
        # 清空失败文件记录
        global FAILED_FILES
        FAILED_FILES = {
            'encoding_errors': [],
            'content_errors': [],
            'database_errors': [],
            'duplicate_files': [],
            'other_errors': []
        }
        
        if import_txt_file(args.path, args.category_id, args.author):
            print("\n✅ 单个文件导入成功!")
        else:
            print("\n❌ 单个文件导入失败!")
            # 生成失败报告
            report_file = save_failed_files_report()
            if report_file:
                print(f"📊 失败文件报告: {report_file}")
                print(f"💡 重试命令: python {sys.argv[0]} --retry {report_file} {args.category_id}")
            
    elif os.path.isdir(args.path):
        # 目录批量导入
        if batch_import_directory(args.path, args.category_id, args.max_files):
            print("\n✅ 批量导入完成!")
        else:
            print("\n❌ 批量导入失败!")
    else:
        print(f"❌ 无效的路径类型: {args.path}")

if __name__ == "__main__":
    main()
