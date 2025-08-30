#!/usr/bin/env python3
"""
并行全文筛选系统主入口
SmartEBM 并行全文筛选工具

用法:
    python parallel_run.py                    # 使用默认配置
    python parallel_run.py --config custom.json  # 使用自定义配置
    python parallel_run.py --resume           # 恢复中断的任务
    python parallel_run.py --monitor          # 仅监控模式
"""

import os
import sys
import argparse
import time
import threading
from pathlib import Path

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
# 添加全文筛选工具路径
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(project_root, 'i18n'))
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'tools'))
# 添加标题摘要筛选工具的核心模块路径（parallel_controller等模块在此目录）
smartebm_root = os.path.dirname(project_root)  # 到达SmartEBM根目录
title_abstract_root = os.path.join(smartebm_root, 'title_and_abstract_screening_tool')
title_abstract_core = os.path.join(title_abstract_root, 'core')
sys.path.insert(0, title_abstract_core)
# 也需要添加title_and_abstract_screening_tool的src路径，因为parallel_controller依赖它
sys.path.insert(0, os.path.join(title_abstract_root, 'src'))
sys.path.insert(0, os.path.join(title_abstract_root, 'i18n'))

# 创建fallback类和函数
class MockLanguageManager:
    def set_language(self, lang): 
        pass

def fallback_get_language_manager():
    return MockLanguageManager()

def fallback_get_message(key, **kwargs):
    # 简单的英文消息映射
    messages = {
        "system_title_fulltext": "SmartEBM Full-Text Screening Tool",
        "operation_selection": "Please select an operation:",
        "operation_1": "Start new full-text screening task",
        "operation_2": "Resume interrupted task",
        "operation_3": "Monitor running task",
        "operation_4": "Merge results only",
        "operation_5": "Clean temporary files",
        "operation_6": "Exit",
        "operation_prompt": "Enter your choice (1-6): ",
        "invalid_option": "Invalid option. Please enter 1-6."
    }
    message = messages.get(key, key)
    if kwargs and message:
        try:
            return message.format(**kwargs)
        except (KeyError, ValueError):
            return message
    return message

def fallback_select_language():
    return 'en'

# 导入本地模块
try:
    from i18n.i18n_manager import get_language_manager, get_message, select_language
except ImportError:
    # 使用fallback函数
    get_language_manager = fallback_get_language_manager
    get_message = fallback_get_message
    select_language = fallback_select_language

# 并行处理模块（将在需要时动态导入或使用单线程fallback）
ParallelScreeningManager = None
monitor_screening_progress = None
merge_results_from_state = None


def setup_parallel_module_paths():
    """设置并行处理模块路径"""
    try:
        # 计算到达SmartEBM根目录的路径
        smartebm_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        title_abstract_root = os.path.join(smartebm_root, 'title_and_abstract_screening_tool')
        title_abstract_core = os.path.join(title_abstract_root, 'core')
        title_abstract_src = os.path.join(title_abstract_root, 'src')
        title_abstract_i18n = os.path.join(title_abstract_root, 'i18n')
        
        # 添加必要的路径到sys.path
        paths_to_add = [title_abstract_core, title_abstract_src, title_abstract_i18n]
        for path in paths_to_add:
            if os.path.exists(path) and path not in sys.path:
                sys.path.insert(0, path)
        
        return True
    except Exception as e:
        print(f"⚠️ 无法设置并行模块路径: {str(e)}")
        return False


def import_parallel_controller():
    """动态导入并行控制器"""
    global ParallelScreeningManager
    if ParallelScreeningManager is not None:
        return ParallelScreeningManager
    
    try:
        # 设置路径
        if not setup_parallel_module_paths():
            return None
        
        # 动态导入
        import importlib
        parallel_controller_module = importlib.import_module('parallel_controller')
        ParallelScreeningManager = parallel_controller_module.ParallelScreeningManager
        return ParallelScreeningManager
    except ImportError as e:
        print(f"⚠️ 无法导入并行控制器: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 导入并行控制器时发生错误: {str(e)}")
        return None


def import_progress_monitor():
    """动态导入进度监控器"""
    global monitor_screening_progress
    if monitor_screening_progress is not None:
        return monitor_screening_progress
    
    try:
        # 设置路径
        if not setup_parallel_module_paths():
            return None
        
        # 动态导入
        import importlib
        progress_monitor_module = importlib.import_module('progress_monitor')
        monitor_screening_progress = progress_monitor_module.monitor_screening_progress
        return monitor_screening_progress
    except ImportError as e:
        print(f"⚠️ 无法导入进度监控器: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 导入进度监控器时发生错误: {str(e)}")
        return None


def import_result_merger():
    """动态导入结果合并器"""
    global merge_results_from_state
    if merge_results_from_state is not None:
        return merge_results_from_state
    
    try:
        # 设置路径
        if not setup_parallel_module_paths():
            return None
        
        # 动态导入
        import importlib
        result_merger_module = importlib.import_module('result_merger')
        merge_results_from_state = result_merger_module.merge_results_from_state
        return merge_results_from_state
    except ImportError as e:
        print(f"⚠️ 无法导入结果合并器: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 导入结果合并器时发生错误: {str(e)}")
        return None


def create_argument_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="SmartEBM Parallel Full-Text Screening System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
  python parallel_run.py                           # Start new task with default config
  python parallel_run.py --config custom.json     # Use custom config file
  python parallel_run.py --resume                  # Resume interrupted task
  python parallel_run.py --monitor state.json     # Monitor existing task
  python parallel_run.py --merge-only state.json  # Merge results only
  python parallel_run.py --cleanup                 # Clean temporary files

Configuration Guide:
  Users only need to set parallel_screeners count in config.json,
  the system will automatically detect hardware capacity and intelligently distribute documents.
        """
    )
    
    parser.add_argument(
        '--config', '-c', 
        default='config/config.json',
        help='Unified configuration file path (default: config/config.json)'
    )
    
    parser.add_argument(
        '--resume', '-r',
        action='store_true',
        help='Resume interrupted parallel screening task'
    )
    
    parser.add_argument(
        '--monitor', '-m',
        metavar='STATE_FILE',
        help='Monitor screening progress of specified state file'
    )
    
    parser.add_argument(
        '--merge-only',
        metavar='STATE_FILE',
        help='Merge results of specified state file only'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean temporary files and state files'
    )
    
    parser.add_argument(
        '--update-interval',
        type=int,
        default=5,
        help='Monitor update interval in seconds (default: 5 seconds)'
    )
    
    parser.add_argument(
        '--lang', '-l',
        choices=['en', 'zh', 'auto'],
        default='auto',
        help='Interface language: en (English), zh (Chinese), auto (interactive selection)'
    )
    
    return parser


def find_state_file():
    """Find the latest state file"""
    state_files = list(Path('.').glob('parallel_fulltext_state*.json'))
    
    if not state_files:
        return None
    
    # Return the latest state file
    return max(state_files, key=lambda p: p.stat().st_mtime)


def interactive_mode(lang_override=None):
    """Interactive mode"""
    try:
        # 首先让用户选择语言（除非已预设）
        if lang_override and lang_override in ['en', 'zh']:
            get_language_manager().set_language(lang_override)
            selected_lang = lang_override
        else:
            selected_lang = select_language()
        
        print("=" * 60)
        print(get_message("system_title_fulltext"))
        print("=" * 60)
        
        print(f"\n{get_message('operation_selection')}")
        print(f"1. {get_message('operation_1')}")
        print(f"2. {get_message('operation_2')}")
        print(f"3. {get_message('operation_3')}")
        print(f"4. {get_message('operation_4')}")
        print(f"5. {get_message('operation_5')}")
        print(f"6. {get_message('operation_6')}")
        
        while True:
            choice = input(f"\n{get_message('operation_prompt')}").strip()
            
            if choice == '1':
                return 'new'
            elif choice == '2':
                return 'resume'
            elif choice == '3':
                return 'monitor'
            elif choice == '4':
                return 'merge'
            elif choice == '5':
                return 'cleanup'
            elif choice == '6':
                return 'exit'
            else:
                print(get_message('invalid_option'))
    except:
        # Fallback for when i18n is not available yet
        print("=" * 60)
        print("SmartEBM Full-Text Screening Tool")
        print("=" * 60)
        
        print("\nPlease select an operation:")
        print("1. Start new full-text screening task")
        print("2. Resume interrupted task")
        print("3. Monitor running task")
        print("4. Merge results only")
        print("5. Clean temporary files")
        print("6. Exit")
        
        while True:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                return 'new'
            elif choice == '2':
                return 'resume'
            elif choice == '3':
                return 'monitor'
            elif choice == '4':
                return 'merge'
            elif choice == '5':
                return 'cleanup'
            elif choice == '6':
                return 'exit'
            else:
                print("Invalid option. Please enter 1-6.")


def run_new_task(config_path):
    """Run new task"""
    try:
        print("🚀 Starting new full-text screening task...")
        
        # 尝试动态导入并行处理模块
        PSM = import_parallel_controller()
        if PSM is not None:
            try:
                manager = PSM(config_path)
                success = manager.start_parallel_screening()
                return success
            except Exception as e:
                print(f"❌ 并行处理执行错误: {str(e)}")
                # Fallback到单线程处理
                print("⚠️  Falling back to single-threaded mode...")
        else:
            print("⚠️  Parallel processing not available, using single-threaded mode...")
        
        # Fallback到单线程处理
        try:
            from run_fulltext import main as single_main
            return single_main() == 0
        except ImportError:
            print("❌ 单线程处理模块也不可用")
            return False
        
    except Exception as e:
        print(f"❌ System error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_resume_task(config_path):
    """Resume task"""
    try:
        print("🔄 Resuming interrupted parallel full-text screening task...")
        
        # Find state file
        state_file = find_state_file()
        if not state_file:
            print("❌ No state file found, cannot resume task")
            return False
        
        print(f"✓ Found state file: {state_file}")
        
        # 尝试动态导入并行处理模块
        PSM = import_parallel_controller()
        if PSM is not None:
            try:
                manager = PSM(config_path)
                success = manager.resume_parallel_screening(state_file)
                return success
            except Exception as e:
                print(f"❌ 并行处理恢复错误: {str(e)}")
                return False
        else:
            print("❌ Parallel processing not available for resume operation")
            return False
        
    except Exception as e:
        print(f"❌ Task resume failed: {str(e)}")
        return False


def run_monitor_only(state_file_path, update_interval):
    """Monitor only mode"""
    try:
        if not os.path.exists(state_file_path):
            print(f"❌ State file does not exist: {state_file_path}")
            return False
        
        print(f"📊 Starting task progress monitoring: {state_file_path}")
        
        # 尝试动态导入监控模块
        monitor_func = import_progress_monitor()
        if monitor_func is not None:
            try:
                monitor_func(state_file_path, update_interval)
                return True
            except Exception as e:
                print(f"❌ 监控执行错误: {str(e)}")
                # Fallback到简单监控
                pass
        
        # 简单的监控fallback
        print("⚠️ Progress monitoring not available, using simple file monitoring...")
        print(f"📊 Monitoring state file: {state_file_path}")
        print("Press Ctrl+C to stop monitoring...")
        try:
            while True:
                if os.path.exists(state_file_path):
                    stat = os.stat(state_file_path)
                    print(f"State file last modified: {time.ctime(stat.st_mtime)}")
                else:
                    print("State file no longer exists")
                    break
                time.sleep(update_interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
        return True
        
    except Exception as e:
        print(f"❌ Monitoring failed: {str(e)}")
        return False


def run_merge_only(state_file_path):
    """Merge results only"""
    try:
        if not os.path.exists(state_file_path):
            print(f"❌ State file does not exist: {state_file_path}")
            return False
        
        print(f"🔗 Merging results from state file: {state_file_path}")
        
        # 尝试动态导入结果合并模块
        merge_func = import_result_merger()
        if merge_func is not None:
            try:
                success = merge_func(state_file_path)
                
                if success:
                    print("✅ Results merged successfully")
                else:
                    print("❌ Failed to merge results")
                
                return success
            except Exception as e:
                print(f"❌ 合并执行错误: {str(e)}")
                return False
        else:
            print("❌ Result merging not available yet")
            print("ℹ️ Please use the title_and_abstract_screening_tool for result merging")
            return False
        
    except Exception as e:
        print(f"❌ Merge failed: {str(e)}")
        return False


def run_cleanup():
    """Clean temporary files"""
    try:
        print("🧹 Cleaning temporary files...")
        
        # Clean temp directories
        temp_dirs = ['temp_parallel', 'temp_fulltext']
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
                print(f"✓ Cleaned directory: {temp_dir}")
        
        # Clean state files
        state_files = list(Path('.').glob('parallel_fulltext_state*.json'))
        for state_file in state_files:
            state_file.unlink()
            print(f"✓ Cleaned state file: {state_file}")
        
        print("✅ Cleanup completed")
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")
        return False


def main():
    """Main function"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Handle different operation modes
    if args.cleanup:
        return 0 if run_cleanup() else 1
    
    if args.monitor:
        return 0 if run_monitor_only(args.monitor, args.update_interval) else 1
    
    if args.merge_only:
        return 0 if run_merge_only(args.merge_only) else 1
    
    # Interactive or direct mode
    if len(sys.argv) == 1 or (len(sys.argv) == 3 and args.lang):
        # Interactive mode
        operation = interactive_mode(args.lang)
        
        if operation == 'exit':
            print("👋 Goodbye!")
            return 0
        elif operation == 'new':
            return 0 if run_new_task(args.config) else 1
        elif operation == 'resume':
            return 0 if run_resume_task(args.config) else 1
        elif operation == 'monitor':
            state_file = find_state_file()
            if state_file:
                return 0 if run_monitor_only(str(state_file), args.update_interval) else 1
            else:
                print("❌ No state file found for monitoring")
                return 1
        elif operation == 'merge':
            state_file = find_state_file()
            if state_file:
                return 0 if run_merge_only(str(state_file)) else 1
            else:
                print("❌ No state file found for merging")
                return 1
        elif operation == 'cleanup':
            return 0 if run_cleanup() else 1
    else:
        # Direct mode based on arguments
        if args.resume:
            return 0 if run_resume_task(args.config) else 1
        else:
            return 0 if run_new_task(args.config) else 1


if __name__ == "__main__":
    sys.exit(main())