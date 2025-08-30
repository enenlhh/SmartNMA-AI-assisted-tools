#!/usr/bin/env python3
"""
进度监控模块
Progress Monitoring Module

实时监控数据提取进度和状态
Real-time monitoring of data extraction progress and status
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class ProgressMonitor:
    """进度监控器 / Progress Monitor"""
    
    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.start_time = None
        self.total_batches = 0
        self.completed_batches = 0
        self.failed_batches = 0
        self.current_status = "Initializing"
        self.lock = threading.Lock()
    
    def start_monitoring(self, total_batches: int):
        """开始监控"""
        with self.lock:
            self.is_monitoring = True
            self.start_time = datetime.now()
            self.total_batches = total_batches
            self.completed_batches = 0
            self.failed_batches = 0
            self.current_status = "Running"
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        with self.lock:
            self.is_monitoring = False
            self.current_status = "Completed"
    
    def update_progress(self, completed: int, failed: int = 0):
        """更新进度"""
        with self.lock:
            self.completed_batches = completed
            self.failed_batches = failed
    
    def get_progress_info(self) -> Dict[str, Any]:
        """获取进度信息"""
        with self.lock:
            if not self.start_time:
                return {}
            
            elapsed_time = datetime.now() - self.start_time
            total_processed = self.completed_batches + self.failed_batches
            
            # 计算进度百分比
            progress_percentage = (total_processed / self.total_batches * 100) if self.total_batches > 0 else 0
            
            # 估算剩余时间
            estimated_total_time = None
            estimated_remaining_time = None
            
            if total_processed > 0:
                avg_time_per_batch = elapsed_time.total_seconds() / total_processed
                estimated_total_time = timedelta(seconds=avg_time_per_batch * self.total_batches)
                remaining_batches = self.total_batches - total_processed
                estimated_remaining_time = timedelta(seconds=avg_time_per_batch * remaining_batches)
            
            return {
                "status": self.current_status,
                "total_batches": self.total_batches,
                "completed_batches": self.completed_batches,
                "failed_batches": self.failed_batches,
                "progress_percentage": progress_percentage,
                "elapsed_time": elapsed_time,
                "estimated_total_time": estimated_total_time,
                "estimated_remaining_time": estimated_remaining_time,
                "start_time": self.start_time
            }
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                time.sleep(5)  # 每5秒更新一次
                
                # 这里可以添加更详细的监控逻辑
                # 比如检查系统资源使用情况、API调用状态等
                
            except Exception as e:
                print(f"Warning: Error in progress monitoring: {e}")
    
    def format_time_delta(self, td: timedelta) -> str:
        """格式化时间差"""
        if not td:
            return "Unknown"
        
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def print_progress_summary(self):
        """打印进度摘要"""
        info = self.get_progress_info()
        if not info:
            return
        
        try:
            from i18n.i18n_manager import get_message
        except ImportError:
            def get_message(key, **kwargs):
                fallback_messages = {
                    "progress_summary_title": "📊 Progress Summary",
                    "status": "Status: {status}",
                    "progress": "Progress: {completed}/{total} ({percentage:.1f}%)",
                    "failed": "Failed: {count}",
                    "elapsed_time": "Elapsed Time: {time}",
                    "estimated_remaining": "Estimated Remaining: {time}",
                    "estimated_total": "Estimated Total: {time}"
                }
                message = fallback_messages.get(key, key)
                return message.format(**kwargs) if kwargs and isinstance(message, str) else message
        
        print("\n" + "=" * 60)
        print(get_message("progress_summary_title"))
        print("=" * 60)
        print(get_message("status", status=info['status']))
        print(get_message("progress", completed=info['completed_batches'], 
                         total=info['total_batches'], percentage=info['progress_percentage']))
        
        if info['failed_batches'] > 0:
            print(get_message("failed", count=info['failed_batches']))
        
        print(get_message("elapsed_time", time=self.format_time_delta(info['elapsed_time'])))
        
        if info['estimated_remaining_time']:
            print(get_message("estimated_remaining", time=self.format_time_delta(info['estimated_remaining_time'])))
        
        if info['estimated_total_time']:
            print(get_message("estimated_total", time=self.format_time_delta(info['estimated_total_time'])))
        
        print("=" * 60)


def monitor_extraction_progress(state_file: str, update_interval: int = 5):
    """独立的进度监控函数"""
    import json
    import os
    
    print("🔍 Starting progress monitoring...")
    print(f"Monitoring state file: {state_file}")
    print(f"Update interval: {update_interval} seconds")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            if os.path.exists(state_file):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    
                    # 显示当前状态
                    status = state.get("status", "Unknown")
                    completed = state.get("completed_batches", 0)
                    total = state.get("total_batches", 0)
                    failed = len(state.get("failed_batches", []))
                    
                    progress_percentage = (completed / total * 100) if total > 0 else 0
                    
                    print(f"\r📊 Status: {status} | Progress: {completed}/{total} " +
                          f"({progress_percentage:.1f}%) | Failed: {failed}", end="")
                    
                    if status in ["completed", "completed_with_errors", "failed"]:
                        print("\n✅ Monitoring completed.")
                        break
                        
                except Exception as e:
                    print(f"\n❌ Error reading state file: {e}")
                    break
            else:
                print(f"\n❌ State file not found: {state_file}")
                break
            
            time.sleep(update_interval)
            
    except KeyboardInterrupt:
        print("\n⚠️ Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitoring error: {e}")