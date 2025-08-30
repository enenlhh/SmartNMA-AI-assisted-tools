#!/usr/bin/env python3
"""
输出结构展示工具
Output Structure Display Tool

展示当前的输出文件组织结构
Display current output file organization structure
"""

import os
from pathlib import Path


def show_directory_tree(directory, prefix="", max_depth=3, current_depth=0):
    """
    显示目录树结构
    Display directory tree structure
    """
    if current_depth >= max_depth:
        return
    
    if not os.path.exists(directory):
        return
    
    items = sorted(os.listdir(directory))
    
    for i, item in enumerate(items):
        if item.startswith('.'):
            continue
            
        item_path = os.path.join(directory, item)
        is_last = i == len(items) - 1
        
        # 选择合适的前缀符号
        current_prefix = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "
        
        if os.path.isdir(item_path):
            print(f"{prefix}{current_prefix}📁 {item}/")
            show_directory_tree(item_path, prefix + next_prefix, max_depth, current_depth + 1)
        else:
            # 显示文件大小
            try:
                size = os.path.getsize(item_path)
                size_str = format_file_size(size)
                print(f"{prefix}{current_prefix}📄 {item} ({size_str})")
            except:
                print(f"{prefix}{current_prefix}📄 {item}")


def format_file_size(size_bytes):
    """
    格式化文件大小
    Format file size
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def count_files_by_type(directory):
    """
    统计各类型文件数量
    Count files by type
    """
    if not os.path.exists(directory):
        return {}
    
    file_counts = {}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith('.'):
                continue
                
            ext = os.path.splitext(file)[1].lower()
            if not ext:
                ext = "无扩展名"
            
            file_counts[ext] = file_counts.get(ext, 0) + 1
    
    return file_counts


def main():
    """主函数"""
    print("=" * 60)
    print("📊 SmartEBM 输出结构展示")
    print("   SmartEBM Output Structure Display")
    print("=" * 60)
    
    output_dir = "output"
    
    if not os.path.exists(output_dir):
        print(f"❌ 输出目录不存在: {output_dir}")
        print("请先运行数据提取工具或组织工具")
        return
    
    print(f"\n📁 输出目录结构: {output_dir}")
    print("─" * 40)
    show_directory_tree(output_dir)
    
    # 统计文件信息
    file_counts = count_files_by_type(output_dir)
    if file_counts:
        print(f"\n📈 文件类型统计:")
        print("─" * 20)
        for ext, count in sorted(file_counts.items()):
            print(f"  {ext}: {count} 个文件")
    
    # 检查是否有组织后的结构
    organized_dir = os.path.join(output_dir, "organized")
    if os.path.exists(organized_dir):
        print(f"\n✅ 发现组织后的结构")
        
        # 找到最新的日期目录
        date_dirs = [d for d in os.listdir(organized_dir) 
                    if os.path.isdir(os.path.join(organized_dir, d))]
        
        if date_dirs:
            latest_date = max(date_dirs)
            latest_dir = os.path.join(organized_dir, latest_date)
            
            print(f"📅 最新组织日期: {latest_date}")
            print(f"📁 组织后的目录结构:")
            print("─" * 30)
            
            subdirs = ["merged_results", "batch_results", "reports", "debug_files", "temp_backups"]
            for subdir in subdirs:
                subdir_path = os.path.join(latest_dir, subdir)
                if os.path.exists(subdir_path):
                    file_count = len([f for f in os.listdir(subdir_path) 
                                    if os.path.isfile(os.path.join(subdir_path, f)) and not f.startswith('.')])
                    dir_count = len([d for d in os.listdir(subdir_path) 
                                   if os.path.isdir(os.path.join(subdir_path, d))])
                    
                    status = ""
                    if file_count > 0 or dir_count > 0:
                        status = f"({file_count} 文件, {dir_count} 目录)"
                    else:
                        status = "(空)"
                    
                    print(f"  📁 {subdir}/ {status}")
    
    print(f"\n💡 提示:")
    print(f"  - 使用 'python tools/organize_output.py' 重新组织文件")
    print(f"  - 查看 README.md 了解目录结构说明")
    print(f"  - 最终结果通常在 merged_results/ 目录中")


if __name__ == "__main__":
    main()