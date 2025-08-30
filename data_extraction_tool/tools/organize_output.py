#!/usr/bin/env python3
"""
输出文件组织工具
Output File Organization Tool

重新组织现有的输出文件，创建更清晰的目录结构
Reorganize existing output files to create a cleaner directory structure
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json


def organize_output_files(output_dir="output"):
    """
    重新组织输出文件
    Reorganize output files into a structured format
    """
    
    if not os.path.exists(output_dir):
        print(f"❌ 输出目录不存在: {output_dir}")
        return False
    
    print(f"🔄 开始组织输出目录: {output_dir}")
    
    # 创建今天的日期文件夹
    today = datetime.now().strftime("%Y-%m-%d")
    organized_dir = os.path.join(output_dir, "organized", today)
    
    # 创建子目录结构
    subdirs = {
        "merged_results": "合并后的最终结果",
        "batch_results": "批次处理结果", 
        "reports": "处理报告和统计",
        "debug_files": "调试文件",
        "temp_backups": "临时文件备份"
    }
    
    for subdir, description in subdirs.items():
        subdir_path = os.path.join(organized_dir, subdir)
        Path(subdir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ 创建目录: {subdir} ({description})")
    
    # 移动现有文件
    moved_files = 0
    
    # 处理根目录下的文件
    for item in os.listdir(output_dir):
        item_path = os.path.join(output_dir, item)
        
        # 跳过已组织的目录
        if item == "organized":
            continue
            
        if os.path.isfile(item_path):
            # 根据文件类型和名称决定目标目录
            target_subdir = determine_target_directory(item)
            target_path = os.path.join(organized_dir, target_subdir, item)
            
            try:
                shutil.move(item_path, target_path)
                print(f"📁 移动文件: {item} -> {target_subdir}/")
                moved_files += 1
            except Exception as e:
                print(f"❌ 移动文件失败 {item}: {e}")
        
        elif os.path.isdir(item_path):
            # 处理子目录
            if item == "debug_files":
                target_path = os.path.join(organized_dir, "debug_files")
                try:
                    if os.path.exists(target_path):
                        # 合并目录内容
                        merge_directories(item_path, target_path)
                        shutil.rmtree(item_path)
                    else:
                        shutil.move(item_path, target_path)
                    print(f"📁 移动目录: {item} -> debug_files/")
                    moved_files += 1
                except Exception as e:
                    print(f"❌ 移动目录失败 {item}: {e}")
            
            elif item == "process_files":
                target_path = os.path.join(organized_dir, "batch_results", item)
                try:
                    shutil.move(item_path, target_path)
                    print(f"📁 移动目录: {item} -> batch_results/")
                    moved_files += 1
                except Exception as e:
                    print(f"❌ 移动目录失败 {item}: {e}")
    
    # 创建组织说明文件
    create_organization_readme(organized_dir)
    
    print(f"\n✅ 文件组织完成!")
    print(f"📊 总共移动了 {moved_files} 个文件/目录")
    print(f"📁 新的组织结构位于: {organized_dir}")
    
    return True


def determine_target_directory(filename):
    """
    根据文件名确定目标目录
    Determine target directory based on filename
    """
    filename_lower = filename.lower()
    
    if "merged" in filename_lower or "final" in filename_lower:
        return "merged_results"
    elif "batch" in filename_lower:
        return "batch_results"
    elif "report" in filename_lower or "stats" in filename_lower:
        return "reports"
    elif "debug" in filename_lower or "raw_response" in filename_lower:
        return "debug_files"
    elif filename_lower.endswith(('.xlsx', '.csv', '.json')):
        return "merged_results"  # 默认结果文件
    else:
        return "temp_backups"  # 其他文件


def merge_directories(source_dir, target_dir):
    """
    合并两个目录的内容
    Merge contents of two directories
    """
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        target_item = os.path.join(target_dir, item)
        
        if os.path.isfile(source_item):
            # 如果目标文件已存在，添加时间戳
            if os.path.exists(target_item):
                timestamp = datetime.now().strftime("%H%M%S")
                name, ext = os.path.splitext(item)
                new_name = f"{name}_{timestamp}{ext}"
                target_item = os.path.join(target_dir, new_name)
            
            shutil.move(source_item, target_item)
        elif os.path.isdir(source_item):
            if not os.path.exists(target_item):
                os.makedirs(target_item)
            merge_directories(source_item, target_item)


def create_organization_readme(organized_dir):
    """
    创建组织说明文件
    Create organization README file
    """
    readme_content = f"""# 输出文件组织结构说明
# Output File Organization Structure

组织时间 / Organization Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 目录结构 / Directory Structure

### 📁 merged_results/
合并后的最终提取结果
Final merged extraction results

### 📁 batch_results/
批次处理的中间结果
Intermediate results from batch processing

### 📁 reports/
处理统计报告和分析
Processing statistics reports and analysis

### 📁 debug_files/
调试文件和原始响应
Debug files and raw responses

### 📁 temp_backups/
临时文件和其他备份
Temporary files and other backups

## 使用说明 / Usage Notes

1. **merged_results/** 包含最终可用的数据提取结果
2. **batch_results/** 包含各个批次的处理结果，用于故障排除
3. **reports/** 包含处理统计和性能分析
4. **debug_files/** 包含调试信息，用于问题诊断
5. **temp_backups/** 包含其他临时文件

## 文件命名规范 / File Naming Convention

- 所有文件都包含时间戳以避免冲突
- 合并结果文件以 "merged_" 开头
- 批次结果文件以 "batch_" 开头
- 报告文件以 "report_" 或包含 "stats" 

---
Generated by SmartEBM Output Organization Tool
"""
    
    readme_path = os.path.join(organized_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)


def main():
    """主函数"""
    print("=" * 60)
    print("🗂️  SmartEBM 输出文件组织工具")
    print("   SmartEBM Output File Organization Tool")
    print("=" * 60)
    
    # 检查输出目录
    output_dir = "output"
    if not os.path.exists(output_dir):
        print(f"❌ 输出目录不存在: {output_dir}")
        print("请先运行数据提取工具生成输出文件")
        return
    
    # 显示当前目录内容
    print(f"\n📋 当前输出目录内容:")
    items = os.listdir(output_dir)
    if not items:
        print("  (空目录)")
        return
    
    for item in items:
        item_path = os.path.join(output_dir, item)
        if os.path.isdir(item_path):
            print(f"  📁 {item}/")
        else:
            print(f"  📄 {item}")
    
    # 询问是否继续
    print(f"\n❓ 是否要重新组织这些文件？")
    print("   这将创建新的目录结构并移动现有文件")
    choice = input("   继续? (y/n): ").lower().strip()
    
    if choice == 'y':
        success = organize_output_files(output_dir)
        if success:
            print(f"\n🎉 文件组织完成！")
            print(f"💡 提示: 查看 {output_dir}/organized/ 目录了解新的结构")
        else:
            print(f"\n❌ 文件组织失败")
    else:
        print("❌ 操作已取消")


if __name__ == "__main__":
    main()