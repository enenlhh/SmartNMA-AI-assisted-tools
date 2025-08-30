#!/usr/bin/env python3
"""
全文筛选进度监控器
实时监控全文筛选任务的进度和状态
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class FullTextProgressMonitor:
    """全文筛选进度监控器"""
    
    def __init__(self, state_file_path: str, update_interval: int = 5):
        self.state_file_path = state_file_path
        self.update_interval = update_interval
        self.start_time = None
        self.last_update = None
        
    def monitor_progress(self):
        """监控筛选进度"""
        # Import i18n functions
        try:
            from i18n.i18n_manager import get_message
        except ImportError:
            def get_message(key, **kwargs):
                return key.format(**kwargs) if kwargs else key
        
        print(get_message("progress_monitoring_start", file_name=os.path.basename(self.state_file_path)))
        print(get_message("progress_update_interval", interval=self.update_interval))
        print(get_message("progress_stop_instruction"))
        print()
        
        self.start_time = time.time()
        
        try:
            while True:
                if os.path.exists(self.state_file_path):
                    self._display_progress()
                else:
                    print(get_message("progress_state_not_found", file_path=self.state_file_path))
                    break
                
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print(f"\n{get_message('operation_interrupted')}")
        except Exception as e:
            print(f"\n{get_message('progress_monitoring_error', error=e)}")
    
    def _display_progress(self):
        """显示当前进度"""
        # Import i18n functions
        try:
            from i18n.i18n_manager import get_message
        except ImportError:
            def get_message(key, **kwargs):
                return key.format(**kwargs) if kwargs else key
                
        try:
            with open(self.state_file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            current_time = time.time()
            
            # 清屏并显示标题
            os.system('clear' if os.name == 'posix' else 'cls')
            print("=" * 80)
            print(get_message("progress_monitor_title"))
            print("=" * 80)
            
            # 显示基本信息
            task_name = state.get('task_name', 'Full-Text Screening')
            start_time_str = state.get('start_time', 'Unknown')
            print(get_message("progress_task", task_name=task_name))
            print(get_message("progress_started", start_time=start_time_str))
            print(get_message("progress_state_file", file_name=os.path.basename(self.state_file_path)))
            
            # 显示总体进度
            total_documents = state.get('total_documents', 0)
            completed_documents = state.get('completed_documents', 0)
            failed_documents = state.get('failed_documents', 0)
            
            if total_documents > 0:
                progress_percent = (completed_documents / total_documents) * 100
                print(f"\n{get_message('progress_overall', completed=completed_documents, total=total_documents, percent=progress_percent)}")
                
                # 进度条
                bar_length = 50
                filled_length = int(bar_length * completed_documents / total_documents)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                print(f"[{bar}] {progress_percent:.1f}%")
            
            # 显示处理统计
            print(f"\n{get_message('progress_statistics')}")
            print(f"  {get_message('progress_completed', count=completed_documents)}")
            print(f"  {get_message('progress_failed', count=failed_documents)}")
            print(f"  {get_message('progress_remaining', count=total_documents - completed_documents - failed_documents)}")
            
            # 显示速度和时间估算
            if self.start_time and completed_documents > 0:
                elapsed_time = current_time - self.start_time
                speed = completed_documents / (elapsed_time / 60)  # docs per minute
                
                remaining_docs = total_documents - completed_documents - failed_documents
                if speed > 0 and remaining_docs > 0:
                    estimated_remaining = (remaining_docs / speed) * 60  # seconds
                    eta = datetime.now() + timedelta(seconds=estimated_remaining)
                    
                    print(f"\n{get_message('progress_speed', speed=speed)}")
                    print(get_message('progress_eta', eta=eta.strftime('%H:%M:%S')))
                    print(get_message('progress_remaining_time', time=self._format_duration(estimated_remaining)))
            
            # 显示LLM统计
            llm_stats = state.get('llm_statistics', {})
            if llm_stats:
                print(f"\n{get_message('progress_llm_stats')}")
                for llm_name, stats in llm_stats.items():
                    if not llm_name.startswith('_'):
                        total_tokens = stats.get('total_tokens', 0)
                        avg_tokens = stats.get('average_tokens_per_doc', 0)
                        print(f"  • {llm_name}: {total_tokens:,} tokens (avg: {avg_tokens:.0f}/doc)")
            
            # 显示筛选结果统计
            results_stats = state.get('results_statistics', {})
            if results_stats:
                included = results_stats.get('included', 0)
                excluded = results_stats.get('excluded', 0)
                unclear = results_stats.get('unclear', 0)
                
                print(f"\n{get_message('progress_screening_results')}")
                print(f"  ✅ {get_message('documents_included_short', count=included)}")
                print(f"  ❌ {get_message('documents_excluded_short', count=excluded)}")
                print(f"  ❓ {get_message('documents_unclear_short', count=unclear)}")
                
                total_screened = included + excluded + unclear
                if total_screened > 0:
                    print(f"  {get_message('progress_inclusion_rate', rate=included/total_screened*100)}")
            
            # 显示最近处理的文档
            recent_documents = state.get('recent_documents', [])
            if recent_documents:
                print(f"\n{get_message('progress_recently_processed')}")
                for doc in recent_documents[-5:]:  # 显示最近5个
                    filename = doc.get('filename', 'Unknown')
                    status = doc.get('status', 'Unknown')
                    timestamp = doc.get('timestamp', '')
                    
                    status_icon = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"
                    print(f"  {status_icon} {filename} ({timestamp})")
            
            # 显示系统资源使用
            system_stats = state.get('system_statistics', {})
            if system_stats:
                cpu_usage = system_stats.get('cpu_usage', 0)
                memory_usage = system_stats.get('memory_usage', 0)
                print(f"\n{get_message('progress_system_resources')}")
                print(f"  {get_message('progress_cpu_usage', usage=cpu_usage)}")
                print(f"  {get_message('progress_memory_usage', usage=memory_usage)}")
            
            print(f"\n{get_message('progress_last_updated', time=datetime.now().strftime('%H:%M:%S'))}")
            print(get_message('progress_stop_instruction'))
            
        except json.JSONDecodeError:
            print(get_message('progress_invalid_state'))
        except Exception as e:
            print(get_message('progress_read_error', error=e))
    
    def _format_duration(self, seconds: float) -> str:
        """格式化时间长度"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = int(seconds / 3600)
            remaining_minutes = int((seconds % 3600) / 60)
            return f"{hours}h {remaining_minutes}m"


def monitor_fulltext_screening_progress(state_file_path: str, update_interval: int = 5):
    """监控全文筛选进度的便捷函数"""
    monitor = FullTextProgressMonitor(state_file_path, update_interval)
    monitor.monitor_progress()


# 导出主要函数
__all__ = [
    'FullTextProgressMonitor',
    'monitor_fulltext_screening_progress'
]