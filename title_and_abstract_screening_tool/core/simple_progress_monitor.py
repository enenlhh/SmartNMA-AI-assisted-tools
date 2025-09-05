#!/usr/bin/env python3
"""
Simple Progress Monitor
Simplified progress monitoring for parallel screening with minimal output
"""

import os
import json
import time
import threading
from datetime import datetime


class SimpleProgressMonitor:
    """简化的进度监控器"""
    
    def __init__(self, state_file_path, update_interval=10):
        self.state_file_path = state_file_path
        self.update_interval = update_interval
        self.is_monitoring = False
        self.monitor_thread = None
        self.start_time = None
        self.last_status = None
        
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.start_time = datetime.now()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("📊 Progress monitoring started (simplified mode)")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=3)
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                self._update_progress_simple()
                time.sleep(self.update_interval)
            except KeyboardInterrupt:
                break
            except Exception:
                # 静默处理错误，避免干扰主进程
                time.sleep(self.update_interval)
    
    def _load_current_state(self):
        """加载当前状态"""
        try:
            if not os.path.exists(self.state_file_path):
                return None
            
            with open(self.state_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _update_progress_simple(self):
        """简化的进度更新"""
        state = self._load_current_state()
        if not state:
            return
        
        batches = state.get('batches', [])
        total_batches = len(batches)
        
        # 统计各状态的批次数
        completed = sum(1 for b in batches if b.get('status') == 'completed')
        running = sum(1 for b in batches if b.get('status') == 'running')
        failed = sum(1 for b in batches if b.get('status') == 'failed')
        pending = sum(1 for b in batches if b.get('status') == 'pending')
        
        # 计算总体进度
        progress_percent = (completed / total_batches * 100) if total_batches > 0 else 0
        
        # 构建状态字符串
        current_status = f"Progress: {completed}/{total_batches} ({progress_percent:.1f}%)"
        if running > 0:
            current_status += f" | Running: {running}"
        if failed > 0:
            current_status += f" | Failed: {failed}"
        
        # 只在状态变化时输出
        if current_status != self.last_status:
            current_time = datetime.now()
            elapsed = current_time - self.start_time if self.start_time else None
            elapsed_str = self._format_duration(elapsed) if elapsed else "Unknown"
            
            print(f"📊 {current_time.strftime('%H:%M:%S')} | {current_status} | Runtime: {elapsed_str}")
            self.last_status = current_status
        
        # 检查是否完成
        if completed + failed == total_batches and running == 0:
            if completed == total_batches:
                print("✅ All batches completed successfully!")
            else:
                print(f"⚠️  Processing completed with {failed} failed batches")
            self.stop_monitoring()
    
    def _format_duration(self, duration):
        """格式化时间间隔"""
        if not duration:
            return "Unknown"
        
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def get_final_summary(self):
        """获取最终摘要"""
        state = self._load_current_state()
        if not state:
            return None
        
        batches = state.get('batches', [])
        total_batches = len(batches)
        completed = sum(1 for b in batches if b.get('status') == 'completed')
        failed = sum(1 for b in batches if b.get('status') == 'failed')
        
        return {
            'total_batches': total_batches,
            'completed_batches': completed,
            'failed_batches': failed,
            'success_rate': (completed / total_batches * 100) if total_batches > 0 else 0,
            'start_time': self.start_time,
            'end_time': datetime.now()
        }


def start_simple_monitoring(state_file_path, update_interval=10):
    """启动简化监控"""
    monitor = SimpleProgressMonitor(state_file_path, update_interval)
    monitor.start_monitoring()
    return monitor