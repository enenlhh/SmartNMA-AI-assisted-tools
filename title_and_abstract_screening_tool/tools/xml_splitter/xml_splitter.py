#!/usr/bin/env python3
"""
XML文献文件分割工具
支持EndNote和Zotero的XML文件按指定数量分割成多个小文件

作者: Kiro AI Assistant
版本: 1.0
"""

import xml.etree.ElementTree as ET
import os
import argparse
import json
from datetime import datetime
from pathlib import Path
import sys

# Add i18n support
I18N_AVAILABLE = False
get_message = None
get_language_manager = None

try:
    # 尝试多种方式导入i18n模块
    import sys
    import os
    
    # 方法1：直接从相对路径导入
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    i18n_dir = os.path.join(project_root, 'i18n')
    
    if os.path.exists(i18n_dir) and i18n_dir not in sys.path:
        sys.path.insert(0, i18n_dir)
    
    # 方法2：尝试从 i18n_manager 直接导入
    from i18n_manager import get_message, get_language_manager  # type: ignore
    I18N_AVAILABLE = True
    
except ImportError:
    try:
        # 方法3：尝试从 i18n.i18n_manager 导入
        from i18n.i18n_manager import get_message, get_language_manager  # type: ignore
        I18N_AVAILABLE = True
    except ImportError:
        # 所有导入方式都失败，使用回退方案
        I18N_AVAILABLE = False
        get_message = None
        get_language_manager = None
        print("Warning: i18n module not available, using fallback messages")

def get_message_fallback(key, **kwargs):
    """Get localized message with fallback to English"""
    # 先尝试使用i18n模块（如果可用）
    if I18N_AVAILABLE and 'get_message' in globals() and get_message is not None:
        try:
            return get_message(key, **kwargs)
        except Exception:
            pass
    
    # Fallback messages (English)
    fallback_messages = {
        "xml_splitter_tool": "=== XML Bibliography File Splitter Tool ===",
        "endnote_zotero_support": "Supports EndNote and Zotero XML format splitting",
        "config_file_run": "=== Running with configuration file ===",
        "config_file_label": "Configuration file: {file}",
        "input_file_label": "Input file: {file}",
        "output_dir_label": "Output directory: {dir}",
        "records_per_file_label": "Records per file: {count}",
        "file_prefix_label": "File prefix: {prefix}",
        "config_missing_paths": "Error: Missing required path information in configuration file",
        "check_input_output_config": "Please check input_xml_path and output_directory configuration",
        "config_input_not_exist": "Error: Input file specified in configuration does not exist: {path}",
        "interactive_mode_defaults": "=== Interactive Mode (using configuration file as defaults) ===",
        "enter_xml_file_path": "Please enter XML file path{default}: ",
        "file_not_exist_retry": "File does not exist, please re-enter",
        "file_info_label": "File Information:",
        "format_label": "  Format: {format}",
        "total_records_info": "  Total Records: {count}",
        "file_size_label": "  File Size: {size} MB",
        "unsupported_xml_format": "Error: Unsupported XML format",
        "records_per_file_prompt": "How many records per file? (default: {default}): ",
        "enter_positive_number": "Please enter a number greater than 0",
        "output_dir_prompt": "Output directory path (default: {default}): ",
        "file_prefix_prompt": "File prefix (default: {default}): ",
        "start_splitting_file": "Starting file splitting...",
        "splitting_completed": "Splitting completed!",
        "generated_files_count": "Generated {count} files",
        "output_directory_label": "Output directory: {dir}",
        "split_report_label": "Split report: {report}",
        "user_interrupted_operation": "User interrupted operation",
        "error_occurred": "Error: {error}",
        "file_generated": "Generated: {filename} (records {start}-{end})",
        "load_config_error": "Error loading configuration file: {error}",
        "xml_format_detected": "Detected XML format: {format}",
        "total_records_count": "Total records: {count}",
        "records_per_file_count": "Records per file: {count}",
        "will_generate_files": "Will generate {count} files",
        "xml_format_error": "Error detecting XML format: {error}",
        "record_count_error": "Error counting records: {error}",
        "unsupported_format_error": "Unsupported XML format or unable to recognize format",
        "no_valid_records": "No valid records found"
    }
    
    message = fallback_messages.get(key, key)
    if message and kwargs:
        try:
            return message.format(**kwargs)
        except (KeyError, ValueError):
            return message
    return message or key

class XMLSplitter:
    """XML文献文件分割器"""
    
    def __init__(self):
        self.supported_formats = ['endnote', 'zotero']
        self.xml_format = None
        
    def detect_xml_format(self, xml_path):
        """检测XML文件格式"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # 检查source-app属性
            source_app = root.find('.//source-app')
            if source_app is not None:
                app_name = source_app.get('name', '').lower()
                if 'zotero' in app_name:
                    return 'zotero'
                elif 'endnote' in app_name:
                    return 'endnote'
            
            # 检查第一个记录的结构
            first_record = root.find('.//record')
            if first_record is not None:
                title_elem = first_record.find('.//titles/title')
                if title_elem is not None:
                    # 检查是否有style标签（EndNote特征）
                    style_elem = title_elem.find('.//style')
                    if style_elem is not None:
                        return 'endnote'
                    elif title_elem.text is not None:
                        return 'zotero'
            
            return 'unknown'
            
        except Exception as e:
            print(f"检测XML格式时出错: {str(e)}")
            return 'unknown'
    
    def count_records(self, xml_path):
        """统计XML文件中的记录数量"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            records = root.findall('.//record')
            return len(records)
        except Exception as e:
            print(get_message_fallback("record_count_error", error=str(e)))
            return 0
    
    def split_xml_file(self, input_path, output_dir, records_per_file, prefix="split"):
        """
        分割XML文件
        
        Args:
            input_path (str): 输入XML文件路径
            output_dir (str): 输出目录路径
            records_per_file (int): 每个文件的记录数
            prefix (str): 输出文件前缀
            
        Returns:
            list: 生成的文件列表
        """
        # 检测文件格式
        self.xml_format = self.detect_xml_format(input_path)
        if self.xml_format == 'unknown':
            raise ValueError(get_message_fallback("unsupported_format_error"))
        
        print(get_message_fallback("xml_format_detected", format=self.xml_format.upper()))
        
        # 统计总记录数
        total_records = self.count_records(input_path)
        if total_records == 0:
            raise ValueError(get_message_fallback("no_valid_records"))
        
        print(get_message_fallback("total_records_count", count=total_records))
        print(get_message_fallback("records_per_file_count", count=records_per_file))
        
        # 计算需要生成的文件数
        num_files = (total_records + records_per_file - 1) // records_per_file
        print(get_message_fallback("will_generate_files", count=num_files))
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 解析原始XML
        tree = ET.parse(input_path)
        root = tree.getroot()
        records = root.findall('.//record')
        
        # 生成的文件列表
        generated_files = []
        
        # 分割文件
        for file_index in range(num_files):
            start_idx = file_index * records_per_file
            end_idx = min(start_idx + records_per_file, total_records)
            
            # 创建新的XML结构
            new_root = self._create_xml_structure(root)
            
            # 添加记录到新的XML
            records_container = new_root.find('.//records')
            if records_container is None:
                records_container = ET.SubElement(new_root, 'records')
            
            for i in range(start_idx, end_idx):
                records_container.append(records[i])
            
            # 生成输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{file_index + 1:03d}_records_{start_idx + 1}-{end_idx}_{timestamp}.xml"
            output_file = output_path / filename
            
            # 保存文件
            new_tree = ET.ElementTree(new_root)
            ET.indent(new_tree, space="  ", level=0)  # 格式化XML
            new_tree.write(output_file, encoding='utf-8', xml_declaration=True)
            
            generated_files.append(str(output_file))
            print(get_message_fallback("file_generated", filename=filename, start=start_idx + 1, end=end_idx))
        
        return generated_files
    
    def _create_xml_structure(self, original_root):
        """创建新的XML结构，保持原有格式"""
        # 创建新的根元素
        new_root = ET.Element(original_root.tag)
        
        # 复制根元素的属性
        for key, value in original_root.attrib.items():
            new_root.set(key, value)
        
        # 复制非records的子元素
        for child in original_root:
            if child.tag != 'records':
                new_root.append(child)
        
        # 创建新的records容器
        records_elem = ET.SubElement(new_root, 'records')
        
        return new_root
    
    def generate_split_report(self, input_path, output_dir, generated_files, records_per_file):
        """Generate split report in table format"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Collect file information
        file_infos = []
        total_records = 0
        total_size_mb = 0
        
        for file_path in generated_files:
            record_count = self.count_records(file_path)
            file_size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)
            
            file_infos.append({
                'filename': os.path.basename(file_path),
                'record_count': record_count,
                'file_size_mb': file_size_mb
            })
            
            total_records += record_count
            total_size_mb += file_size_mb
        
        # Generate table report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("XML Bibliography File Split Report")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Basic information
        report_lines.append("Basic Information:")
        report_lines.append(f"  Input File: {os.path.basename(input_path)}")
        report_lines.append(f"  Full Path: {input_path}")
        report_lines.append(f"  Output Directory: {output_dir}")
        report_lines.append(f"  XML Format: {self.xml_format.upper() if self.xml_format else 'UNKNOWN'}")
        report_lines.append(f"  Split Time: {timestamp}")
        report_lines.append("")
        
        # Split settings
        report_lines.append("Split Settings:")
        report_lines.append(f"  Records per File: {records_per_file}")
        report_lines.append(f"  Files Generated: {len(generated_files)}")
        report_lines.append(f"  Total Records: {total_records}")
        report_lines.append(f"  Total File Size: {total_size_mb:.2f} MB")
        report_lines.append("")
        
        # File details table
        report_lines.append("Generated Files Details:")
        report_lines.append("-" * 80)
        
        # Table header
        header = f"{'No.':<4} {'Filename':<35} {'Records':<8} {'Size(MB)':<10}"
        report_lines.append(header)
        report_lines.append("-" * 80)
        
        # File list
        for i, info in enumerate(file_infos, 1):
            row = f"{i:<4} {info['filename']:<35} {info['record_count']:<8} {info['file_size_mb']:<10.2f}"
            report_lines.append(row)
        
        report_lines.append("-" * 80)
        
        # Statistics summary
        avg_records = total_records / len(generated_files) if generated_files else 0
        avg_size = total_size_mb / len(generated_files) if generated_files else 0
        
        report_lines.append(f"{'Total':<4} {'':<35} {total_records:<8} {total_size_mb:<10.2f}")
        report_lines.append(f"{'Avg':<4} {'':<35} {avg_records:<8.1f} {avg_size:<10.2f}")
        report_lines.append("")
        
        # Recommendations
        report_lines.append("Recommendations:")
        report_lines.append("  - Please verify that all generated files are complete")
        report_lines.append("  - It's recommended to backup the original file")
        report_lines.append("  - You can import the split files into reference management software")
        report_lines.append("")
        report_lines.append("=" * 80)
        
        # Save report
        report_content = "\n".join(report_lines)
        report_file = Path(output_dir) / f"split_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\nSplit report saved: {report_file}")
        return str(report_file)

def load_config_file(config_path="splitter_config.json"):
    """加载配置文件"""
    try:
        # 首先尝试当前目录下的配置文件
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        
        # 然后尝试脚本所在目录的配置文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path_in_script_dir = os.path.join(script_dir, config_path)
        if os.path.exists(config_path_in_script_dir):
            with open(config_path_in_script_dir, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
                
        return None
    except Exception as e:
        print(get_message_fallback("load_config_error", error=str(e)))
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="XML文献文件分割工具 - 支持EndNote和Zotero格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python xml_splitter.py                              # 使用配置文件
  python xml_splitter.py -c custom_config.json       # 使用指定配置文件
  python xml_splitter.py -i input.xml -o output_dir -n 100
  python xml_splitter.py --interactive
        """
    )
    
    parser.add_argument('-i', '--input', type=str, help='输入XML文件路径')
    parser.add_argument('-o', '--output', type=str, help='输出目录路径')
    parser.add_argument('-n', '--number', type=int, help='每个文件的记录数量')
    parser.add_argument('-p', '--prefix', type=str, default='split', help='输出文件前缀 (默认: split)')
    parser.add_argument('-c', '--config', type=str, default='splitter_config.json', help='配置文件路径 (默认: splitter_config.json)')
    parser.add_argument('--interactive', action='store_true', help='交互式模式')
    
    args = parser.parse_args()
    
    # 尝试加载配置文件
    config = load_config_file(args.config)
    
    # 如果没有命令行参数且有配置文件，使用配置文件
    if config and not any([args.input, args.output, args.number, args.interactive]):
        print(get_message_fallback("config_file_run"))
        print(get_message_fallback("config_file_label", file=args.config))
        
        # 从配置文件获取参数
        input_path = config.get('input_settings', {}).get('input_xml_path', '')
        output_dir = config.get('output_settings', {}).get('output_directory', '')
        records_per_file = config.get('split_settings', {}).get('records_per_file', 100)
        prefix = config.get('output_settings', {}).get('file_prefix', 'split')
        
        # 验证配置
        if not input_path or not output_dir:
            print(get_message_fallback("config_missing_paths"))
            print(get_message_fallback("check_input_output_config"))
            return 1
            
        if not os.path.exists(input_path):
            print(get_message_fallback("config_input_not_exist", path=input_path))
            return 1
            
        print(get_message_fallback("input_file_label", file=input_path))
        print(get_message_fallback("output_dir_label", dir=output_dir))
        print(get_message_fallback("records_per_file_label", count=records_per_file))
        print(get_message_fallback("file_prefix_label", prefix=prefix))
        
    elif config and args.interactive:
        # 交互模式但有配置文件，可以作为默认值
        print(get_message_fallback("interactive_mode_defaults"))
        input_path = None
        output_dir = None
        records_per_file = None
        prefix = None
    else:
        # 使用命令行参数或完全交互模式
        input_path = args.input
        output_dir = args.output
        records_per_file = args.number
        prefix = args.prefix
    
    try:
        splitter = XMLSplitter()
        
        if args.interactive or (not config and not all([input_path, output_dir, records_per_file])):
            # 交互式模式
            print(get_message_fallback("xml_splitter_tool"))
            print(get_message_fallback("endnote_zotero_support"))
            
            # 获取输入文件（如果有配置文件，显示默认值）
            default_input = config.get('input_settings', {}).get('input_xml_path', '') if config else ''
            while True:
                prompt = get_message_fallback("enter_xml_file_path", default=f' (默认: {default_input})' if default_input else '')
                user_input = input(prompt).strip().strip('"\'')
                input_path = user_input if user_input else default_input
                
                if input_path and os.path.exists(input_path):
                    break
                print(get_message_fallback("file_not_exist_retry"))
            
            # 检测格式并显示信息
            xml_format = splitter.detect_xml_format(input_path)
            total_records = splitter.count_records(input_path)
            
            print(get_message_fallback("file_info_label"))
            print(get_message_fallback("format_label", format=xml_format.upper()))
            print(get_message_fallback("total_records_info", count=total_records))
            print(get_message_fallback("file_size_label", size=round(os.path.getsize(input_path) / (1024 * 1024), 2)))
            
            if xml_format == 'unknown':
                print(get_message_fallback("unsupported_xml_format"))
                return 1
            
            # 获取分割参数
            default_records = config.get('split_settings', {}).get('records_per_file', min(100, total_records//2)) if config else min(100, total_records//2)
            while True:
                try:
                    prompt = get_message_fallback("records_per_file_prompt", default=default_records)
                    user_input = input(prompt).strip()
                    records_per_file = int(user_input) if user_input else default_records
                    if records_per_file > 0:
                        break
                    print(get_message_fallback("enter_positive_number"))
                except ValueError:
                    print("Please enter a valid number")
            
            # 获取输出目录
            default_output = config.get('output_settings', {}).get('output_directory', 'split_output') if config else 'split_output'
            prompt = get_message_fallback("output_dir_prompt", default=default_output)
            user_input = input(prompt).strip().strip('"\'')
            output_dir = user_input if user_input else default_output
            
            # 获取文件前缀
            default_prefix = config.get('output_settings', {}).get('file_prefix', 'split') if config else 'split'
            prompt = get_message_fallback("file_prefix_prompt", default=default_prefix)
            user_input = input(prompt).strip()
            prefix = user_input if user_input else default_prefix
            
        elif not config:
            # 纯命令行模式，没有配置文件
            if input_path and not os.path.exists(input_path):
                print(get_message_fallback("error_occurred", error=f"Input file does not exist: {input_path}"))
                return 1
        
        # 执行分割
        print(get_message_fallback("start_splitting_file"))
        generated_files = splitter.split_xml_file(input_path, output_dir, records_per_file, prefix or 'split')
        
        # 生成报告
        report_file = splitter.generate_split_report(input_path, output_dir, generated_files, records_per_file)
        
        print(f"\n{get_message_fallback('splitting_completed')}")
        print(get_message_fallback("generated_files_count", count=len(generated_files)))
        print(get_message_fallback("output_directory_label", dir=output_dir))
        print(get_message_fallback("split_report_label", report=report_file))
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n{get_message_fallback('user_interrupted_operation')}")
        return 1
    except Exception as e:
        print(get_message_fallback("error_occurred", error=str(e)))
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())