#!/usr/bin/env python3
"""
SmartEBM 数据提取工具 - 主入口
SmartEBM Data Extraction Tool - Main Entry Point

这是系统的主入口文件，提供完整的双语交互界面和多线程并行处理功能
This is the main entry point providing complete bilingual interactive interface and multi-threaded parallel processing

使用方法 / Usage:
    python3 main.py                    # 交互式界面 / Interactive interface
    python3 main.py --config custom.json  # 使用自定义配置 / Use custom config  
    python3 main.py --lang en          # 英文界面 / English interface
    python3 main.py --lang zh          # 中文界面 / Chinese interface
    python3 main.py --resume           # 恢复中断的任务 / Resume interrupted task
    python3 main.py --monitor state.json  # 监控现有任务 / Monitor existing task
    python3 main.py --merge-only state.json  # 仅合并结果 / Merge results only
    python3 main.py --cleanup          # 清理临时文件 / Clean temporary files
"""

import os
import sys
import argparse
import time
import threading
from pathlib import Path

# 添加项目路径到Python路径
current_dir = Path(__file__).parent.absolute()
i18n_dir = current_dir / "i18n"
src_dir = current_dir / "src"
core_dir = current_dir / "core"

# 将所有必要的目录添加到Python路径
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(i18n_dir))
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(core_dir))

# 确保当前目录是工作目录
os.chdir(current_dir)

from i18n.i18n_manager import get_language_manager, get_message, select_language
from core.parallel_controller import ParallelExtractionManager
from core.progress_monitor import ProgressMonitor, monitor_extraction_progress
from core.result_merger import ResultMerger
from core.resource_detector import ResourceDetector


def create_argument_parser():
    """创建命令行参数解析器 / Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="SmartEBM Parallel Data Extraction System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
  python main.py                           # Start interactive mode with language selection
  python main.py --config custom.json     # Use custom config file
  python main.py --resume                  # Resume interrupted task
  python main.py --monitor state.json     # Monitor existing task progress
  python main.py --merge-only state.json  # Merge results only
  python main.py --cleanup                 # Clean temporary files

Configuration Guide:
  Users only need to set parallel_workers count in config.json,
  the system will automatically detect hardware capacity and intelligently distribute documents.
  Configure your extraction settings and LLM credentials for optimal performance.
        """
    )
    
    parser.add_argument(
        '--config', '-c', 
        default='config/config.json',
        help='Configuration file path (default: config/config.json)'
    )
    
    parser.add_argument(
        '--resume', '-r',
        action='store_true',
        help='Resume interrupted data extraction task'
    )
    
    parser.add_argument(
        '--monitor', '-m',
        metavar='STATE_FILE',
        help='Monitor extraction progress of specified state file'
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
    """查找最新的状态文件"""
    state_files = list(Path('.').glob('extraction_state*.json'))
    
    if not state_files:
        return None
    
    # 返回最新的状态文件
    return max(state_files, key=lambda p: p.stat().st_mtime)


def interactive_mode(lang_override=None):
    """交互模式 / Interactive mode"""
    # 首先让用户选择语言（除非已预设）
    if lang_override and lang_override in ['en', 'zh']:
        get_language_manager().set_language(lang_override)
        selected_lang = lang_override
    else:
        selected_lang = select_language()
    
    print("=" * 60)
    print(get_message("system_title"))
    print("=" * 60)
    
    print(f"\n{get_message('operation_selection')}")
    print(f"1. {get_message('operation_1')}")
    print(f"2. {get_message('operation_2')}")
    print(f"3. {get_message('operation_3')}")
    print(f"4. {get_message('operation_4')}")
    print(f"5. {get_message('operation_5')}")
    print(f"6. {get_message('operation_6')}")
    
    # 显示系统资源信息
    try:
        detector = ResourceDetector()
        recommendations = detector.get_performance_recommendations()
        
        # 显示资源警告（如果有）
        if recommendations.get("recommendations"):
            print(f"\n{get_message('resource_warning')}")
            for rec in recommendations["recommendations"]:
                if rec.get("level") == "warning":
                    print(f"  {rec.get('message', '')}")
            print(f"{get_message('suggestion')}")
            for rec in recommendations["recommendations"]:
                if rec.get("level") == "suggestion":
                    print(f"  {rec.get('message', '')}")
    except Exception as e:
        # 如果资源检测失败，不影响主流程
        pass
    
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


def run_new_task(config_path):
    """运行新任务"""
    try:
        print(get_message("starting_new_task"))
        
        manager = ParallelExtractionManager(config_path)
        success = manager.start_parallel_extraction()
        
        return success
        
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        return False


def run_resume_task(config_path):
    """恢复任务 / Resume task"""
    try:
        print("🔄 Resuming interrupted data extraction task...")
        
        # 查找状态文件
        state_file = find_state_file()
        if not state_file:
            print(get_message("no_state_file"))
            return False
        
        print(f"✓ Found state file: {state_file}")
        
        manager = ParallelExtractionManager(config_path)
        # 实现恢复逻辑
        success = manager.resume_from_state(str(state_file))
        
        return success
        
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        return False


def run_monitor_only(state_file_path, update_interval):
    """仅监控模式 / Monitor only mode"""
    try:
        if not os.path.exists(state_file_path):
            print(get_message("file_not_found", file=state_file_path))
            return False
        
        print(f"📊 Starting task progress monitoring: {state_file_path}")
        monitor_extraction_progress(state_file_path, update_interval)
        
        return True
        
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        return False


def run_merge_only(state_file):
    """仅合并模式 / Merge only mode"""
    try:
        if not os.path.exists(state_file):
            print(get_message("file_not_found", file=state_file))
            return False
        
        print(get_message("merging_results"))
        
        # 读取状态文件获取输出目录配置
        import json
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # 使用配置文件中的输出目录，如果没有则使用output目录
        output_dir = "output"
        
        merger = ResultMerger()
        results = merger.merge_results_from_state(
            state_file, 
            output_dir,
            final_output_prefix="final_extraction_results",
            backup_individual=True
        )
        
        if results.get('excel_merge', {}).get('success'):
            print(get_message("saving_results", path=results['excel_merge']['output_path']))
            return True
        else:
            print("❌ Result merging failed")
            return False
            
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        return False


def run_with_monitor(task_func, state_file_pattern="extraction_state*.json", update_interval=5):
    """带监控运行任务 / Run task with monitoring"""
    
    def monitor_thread():
        """监控线程 / Monitor thread"""
        # 等待状态文件生成
        max_wait = 30  # 最多等待30秒
        wait_count = 0
        state_files = []
        latest_state_file = None
        
        while wait_count < max_wait:
            state_files = list(Path('.').glob(state_file_pattern))
            if state_files:
                # 使用最新的状态文件
                latest_state_file = max(state_files, key=lambda p: p.stat().st_mtime)
                break
            time.sleep(1)
            wait_count += 1
        
        if state_files and latest_state_file:
            try:
                monitor_extraction_progress(str(latest_state_file), update_interval)
            except:
                pass  # 监控失败不影响主任务
    
    # 启动监控线程
    monitor_t = threading.Thread(target=monitor_thread, daemon=True)
    monitor_t.start()
    
    # 执行主任务
    return task_func()


def run_cleanup():
    """清理模式 / Cleanup mode"""
    try:
        print(get_message("cleanup_temp"))
        
        # 清理临时文件夹
        import shutil
        temp_dirs = ['temp_parallel', 'temp_extraction']
        temp_pattern_dirs = list(Path('.').glob('temp_parallel_*'))
        state_files = list(Path('.').glob('extraction_state*.json'))
        
        cleaned_count = 0
        
        # 清理固定名称的临时目录
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                cleaned_count += 1
                print(f"✓ Removed: {temp_dir}")
        
        # 清理带时间戳的临时目录
        for temp_dir in temp_pattern_dirs:
            if temp_dir.is_dir():
                shutil.rmtree(temp_dir)
                cleaned_count += 1
                print(f"✓ Removed: {temp_dir}")
        
        # 清理状态文件
        for state_file in state_files:
            choice = input(get_message("delete_state_file", file=state_file) if hasattr(get_message, '__call__') else f"Delete state file {state_file}? (y/n): ")
            if choice.lower() == 'y':
                state_file.unlink()
                cleaned_count += 1
                print(f"✓ Removed: {state_file}")
        
        if cleaned_count > 0:
            print(f"✅ Cleaned {cleaned_count} items")
        else:
            print("ℹ️ No temporary files found")
            
        return True
        
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        return False


def main():
    """主函数"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # 调整配置文件路径（如果是相对路径）
    if not os.path.isabs(args.config):
        args.config = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.config)
    
    # 检查配置文件
    if not args.cleanup and not args.monitor and not args.merge_only:
        if not os.path.exists(args.config):
            print(get_message("file_not_found", file=args.config))
            print("Please create a configuration file first or use --config to specify the correct path")
            return 1
    
    try:
        # 设置语言
        if args.lang != 'auto':
            get_language_manager().set_language(args.lang)
        
        # 根据参数执行不同操作
        if args.monitor:
            # 仅监控模式
            success = run_monitor_only(args.monitor, args.update_interval)
            
        elif args.merge_only:
            # 仅合并模式
            success = run_merge_only(args.merge_only)
            
        elif args.cleanup:
            # 清理模式
            success = run_cleanup()
            
        elif args.resume:
            # 恢复模式
            success = run_resume_task(args.config)
            
        elif len(sys.argv) == 1 or (len(sys.argv) == 3 and '--lang' in sys.argv):
            # 交互模式
            mode = interactive_mode(args.lang if args.lang != 'auto' else None)
            
            if mode == 'new':
                success = run_with_monitor(
                    lambda: run_new_task(args.config),
                    update_interval=args.update_interval
                )
            elif mode == 'resume':
                success = run_with_monitor(
                    lambda: run_resume_task(args.config),
                    update_interval=args.update_interval
                )
            elif mode == 'monitor':
                state_file = find_state_file()
                if state_file:
                    success = run_monitor_only(str(state_file), args.update_interval)
                else:
                    print(get_message("no_state_file"))
                    success = False
            elif mode == 'merge':
                state_file = find_state_file()
                if state_file:
                    success = run_merge_only(str(state_file))
                else:
                    print(get_message("no_state_file"))
                    success = False
            elif mode == 'cleanup':
                success = run_cleanup()
            elif mode == 'exit':
                print(get_message("goodbye"))
                return 0
            else:
                success = False
                
        else:
            # 默认新任务模式
            success = run_with_monitor(
                lambda: run_new_task(args.config),
                update_interval=args.update_interval
            )
        
        if success:
            print(f"\n{get_message('operation_completed')}")
            return 0
        else:
            print(f"\n{get_message('operation_failed')}")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n\n{get_message('operation_interrupted')}")
        return 1
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())