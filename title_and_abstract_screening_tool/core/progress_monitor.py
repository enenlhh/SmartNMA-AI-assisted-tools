#!/usr/bin/env python3
"""
Progress Monitor
Real-time monitoring of parallel screener processing progress
"""

import os
import time
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path


class ProgressMonitor:
    """Progress Monitor"""
    
    def __init__(self, state_file_path, update_interval=5):
        self.state_file_path = state_file_path
        self.update_interval = update_interval
        self.is_monitoring = False
        self.monitor_thread = None
        self.start_time = None
        self.last_update_time = None
        
    def start_monitoring(self):
        """Start monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.start_time = datetime.now()
        self.last_update_time = self.start_time
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("📊 Progress monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        print("📊 Progress monitoring stopped")
    
    def _monitor_loop(self):
        """Monitoring loop"""
        while self.is_monitoring:
            try:
                self._update_progress_display()
                time.sleep(self.update_interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️  Monitor update error: {str(e)}")
                time.sleep(self.update_interval)
    
    def _load_current_state(self):
        """Load current state"""
        try:
            if not os.path.exists(self.state_file_path):
                return None
            
            with open(self.state_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to read state file: {str(e)}")
            return None
    
    def _update_progress_display(self):
        """Update progress display"""
        state = self._load_current_state()
        if not state:
            return
        
        current_time = datetime.now()
        
        # Only clear screen if we're in monitoring mode (not mixed with other outputs)
        # Use a more gentle update approach
        print("\n" + "="*80)
        print("📊 Progress Update - " + current_time.strftime('%H:%M:%S'))
        print("="*80)
        
        self._display_batch_progress_summary(state['batches'])
        self._display_overall_progress(state, current_time)
        
        self.last_update_time = current_time
    
    def _display_header(self, state, current_time):
        """Display header information"""
        print("=" * 80)
        print("🎯 SmartEBM Parallel Screening Progress Monitor")
        print("=" * 80)
        print(f"Session ID: {state.get('session_id', 'unknown')}")
        if self.start_time:
            print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"Start Time: Unknown")
        print(f"Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.start_time:
            elapsed = current_time - self.start_time
            print(f"Runtime: {self._format_duration(elapsed)}")
        else:
            print(f"Runtime: Unknown")
        print("=" * 80)
    
    def _display_batch_progress_summary(self, batches):
        """Display simplified batch progress summary"""
        print("📋 Batch Status Summary:")
        
        # Count by status
        status_counts = {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0}
        running_batches = []
        
        for batch in batches:
            status = batch['status']
            if status in status_counts:
                status_counts[status] += 1
            
            if status == 'running':
                progress = self._calculate_accurate_progress(batch)
                running_batches.append(f"Batch {batch['batch_id']}: {progress}")
        
        # Display status summary
        print(f"  ✅ Completed: {status_counts['completed']}")
        print(f"  🔄 Running: {status_counts['running']}")
        print(f"  ⏳ Pending: {status_counts['pending']}")
        print(f"  ❌ Failed: {status_counts['failed']}")
        
        # Show running batch details
        if running_batches:
            print("  Running Details:")
            for batch_info in running_batches:
                print(f"    {batch_info}")
    
    def _display_batch_progress(self, batches):
        """Display detailed batch progress (for full screen mode only)"""
        print("\n📋 Batch Progress Details")
        print("-" * 80)
        
        # Table header
        header = (f"{'Batch':<6} {'Record Range':<15} {'Status':<12} {'Progress':<8} "
                 f"{'Start Time':<12} {'Duration':<10}")
        print(header)
        print("-" * 80)
        
        for batch in batches:
            batch_id = batch['batch_id']
            record_range = f"{batch['start_record']}-{batch['end_record']}"
            status = batch['status']
            
            # Status icons
            status_icons = {
                'pending': '⏳',
                'running': '🔄',
                'completed': '✅',
                'failed': '❌',
                'error': '💥'
            }
            status_display = f"{status_icons.get(status, '❓')} {status}"
            
            # Progress calculation
            if status == 'completed':
                progress = "100%"
            elif status == 'running':
                progress = self._calculate_accurate_progress(batch)
            else:
                progress = "0%"
            
            # Time information
            start_time = batch.get('started_at', '')
            if start_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    start_display = start_dt.strftime('%H:%M:%S')
                    
                    if status in ['completed', 'failed']:
                        end_time = batch.get('completed_at', batch.get('failed_at', ''))
                        if end_time:
                            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                            duration = self._format_duration(end_dt - start_dt)
                        else:
                            duration = "Unknown"
                    elif status == 'running':
                        duration = self._format_duration(datetime.now() - start_dt)
                    else:
                        duration = "-"
                except:
                    start_display = start_time[:8] if len(start_time) > 8 else start_time
                    duration = "-"
            else:
                start_display = "-"
                duration = "-"
            
            # Display row
            row = (f"{batch_id:<6} {record_range:<15} {status_display:<12} "
                  f"{progress:<8} {start_display:<12} {duration:<10}")
            print(row)
        
        print("-" * 80)
    
    def _display_overall_progress(self, state, current_time):
        """Display overall progress"""
        batches = state['batches']
        total_batches = len(batches)
        
        completed_batches = sum(1 for b in batches if b['status'] == 'completed')
        running_batches = sum(1 for b in batches if b['status'] == 'running')
        failed_batches = sum(1 for b in batches if b['status'] == 'failed')
        pending_batches = sum(1 for b in batches if b['status'] == 'pending')
        
        # Calculate record progress
        total_records = state.get('total_records', 0)
        completed_records = sum(b.get('record_count', 0) for b in batches 
                              if b['status'] == 'completed')
        
        batch_progress = (completed_batches / total_batches) * 100 if total_batches > 0 else 0
        record_progress = (completed_records / total_records) * 100 if total_records > 0 else 0
        
        try:
            from i18n.i18n_manager import get_message
            print(f"\n{get_message('overall_progress')}")
            print("-" * 40)
            print(get_message("total_batches", count=total_batches))
            print(get_message("completed_batches", count=completed_batches, percent=batch_progress))
            print(get_message("running_batches", count=running_batches))
            print(get_message("failed_batches", count=failed_batches))
            print(get_message("pending_batches", count=pending_batches))
            print()
            print(get_message("total_records", count=total_records))
            print(get_message("processed_records", count=completed_records, percent=record_progress))
        except:
            print(f"\n📊 Overall Progress")
            print("-" * 40)
            print(f"Total Batches: {total_batches}")
            print(f"Completed: {completed_batches} ({batch_progress:.1f}%)")
            print(f"Running: {running_batches}")
            print(f"Failed: {failed_batches}")
            print(f"Pending: {pending_batches}")
            print()
            print(f"Total Records: {total_records}")
            print(f"Processed Records: {completed_records} ({record_progress:.1f}%)")
        
        # Progress bar
        self._display_progress_bar(record_progress)
        
        # Estimate remaining time
        if running_batches > 0 or pending_batches > 0:
            eta = self._estimate_remaining_time(state, current_time)
            if eta:
                print(f"Estimated Remaining Time: {eta}")
    
    def _display_performance_stats(self, state, current_time):
        """Display performance statistics"""
        batches = state['batches']
        completed_batches = [b for b in batches if b['status'] == 'completed']
        
        if not completed_batches:
            return
        
        print(f"\n⚡ Performance Statistics")
        print("-" * 40)
        
        # Calculate average processing time
        total_duration = timedelta(0)
        total_records = 0
        
        for batch in completed_batches:
            start_time = batch.get('started_at')
            end_time = batch.get('completed_at')
            
            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    duration = end_dt - start_dt
                    total_duration += duration
                    total_records += batch.get('record_count', 0)
                except:
                    continue
        
        if total_records > 0:
            avg_time_per_record = total_duration.total_seconds() / total_records
            records_per_minute = 60 / avg_time_per_record if avg_time_per_record > 0 else 0
            
            print(f"Average Processing Time: {avg_time_per_record:.2f} sec/record")
            print(f"Processing Speed: {records_per_minute:.1f} records/min")
        
        # API使用统计（如果有的话）
        api_calls = sum(batch.get('api_calls', 0) for batch in completed_batches)
        if api_calls > 0:
            elapsed_minutes = (current_time - self.start_time).total_seconds() / 60
            api_rate = api_calls / elapsed_minutes if elapsed_minutes > 0 else 0
            print(f"Total API Calls: {api_calls}")
            try:
                from i18n.i18n_manager import get_message
                print(get_message("api_call_rate", rate=api_rate))
            except:
                print(f"API Call Rate: {api_rate:.1f} calls/minute")
    
    def _display_progress_bar(self, percentage, width=50):
        """显示进度条"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        try:
            from i18n.i18n_manager import get_message
            print(f"\n{get_message('progress_bar', bar=bar, percent=percentage)}")
        except:
            print(f"\nProgress: [{bar}] {percentage:.1f}%")
    
    def _calculate_accurate_progress(self, batch):
        """计算更准确的批次进度"""
        # 优先使用实际记录进度
        if 'current_record' in batch and 'record_count' in batch:
            current = batch.get('current_record', 0)
            total = batch.get('record_count', 1)
            progress = (current / total) * 100 if total > 0 else 0
            return f"{progress:.1f}%"
        
        # 检查是否有处理进度信息
        if 'processed_count' in batch and 'record_count' in batch:
            processed = batch.get('processed_count', 0)
            total = batch.get('record_count', 1)
            progress = (processed / total) * 100 if total > 0 else 0
            return f"{progress:.1f}%"
        
        # 基于时间的保守估算（改进版）
        start_time = batch.get('started_at')
        if not start_time:
            return "0%"
        
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            elapsed = datetime.now() - start_dt
            elapsed_minutes = elapsed.total_seconds() / 60
            
            # 基于记录数量的动态估算（每条记录0.5-2分钟）
            record_count = batch.get('record_count', 1)
            if record_count <= 10:
                avg_time_per_record = 1.0  # 小批次处理较快
            elif record_count <= 50:
                avg_time_per_record = 1.5
            else:
                avg_time_per_record = 2.0  # 大批次可能较慢
            
            estimated_total_minutes = record_count * avg_time_per_record
            progress = min(95, (elapsed_minutes / estimated_total_minutes) * 100)  # 最多显示95%
            
            return f"~{progress:.0f}%"
        except Exception as e:
            return "运行中"
    
    def _estimate_batch_progress(self, batch):
        """估算单个批次的进度（保持向后兼容）"""
        return self._calculate_accurate_progress(batch)
    
    def _estimate_remaining_time(self, state, current_time):
        """估算剩余时间"""
        try:
            batches = state['batches']
            completed_batches = [b for b in batches if b['status'] == 'completed']
            
            if len(completed_batches) < 2:
                return None
            
            # 计算平均批次处理时间
            total_duration = timedelta(0)
            for batch in completed_batches:
                start_time = batch.get('started_at')
                end_time = batch.get('completed_at')
                
                if start_time and end_time:
                    try:
                        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        total_duration += (end_dt - start_dt)
                    except:
                        continue
            
            if len(completed_batches) == 0:
                return None
            
            avg_batch_time = total_duration / len(completed_batches)
            
            # 计算剩余批次
            remaining_batches = sum(1 for b in batches 
                                  if b['status'] in ['pending', 'running'])
            
            # 估算剩余时间
            estimated_remaining = avg_batch_time * remaining_batches
            
            return self._format_duration(estimated_remaining)
            
        except Exception as e:
            return None
    
    def _format_duration(self, duration):
        """格式化时间间隔"""
        if isinstance(duration, timedelta):
            total_seconds = int(duration.total_seconds())
        else:
            total_seconds = int(duration)
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def get_summary_report(self):
        """获取摘要报告"""
        state = self._load_current_state()
        if not state:
            return None
        
        batches = state['batches']
        total_batches = len(batches)
        completed = sum(1 for b in batches if b['status'] == 'completed')
        failed = sum(1 for b in batches if b['status'] == 'failed')
        running = sum(1 for b in batches if b['status'] == 'running')
        pending = sum(1 for b in batches if b['status'] == 'pending')
        
        total_records = state.get('total_records', 0)
        completed_records = sum(b.get('record_count', 0) for b in batches 
                              if b['status'] == 'completed')
        
        return {
            'session_id': state.get('session_id'),
            'total_batches': total_batches,
            'completed_batches': completed,
            'failed_batches': failed,
            'running_batches': running,
            'pending_batches': pending,
            'total_records': total_records,
            'completed_records': completed_records,
            'progress_percentage': (completed / total_batches * 100) if total_batches > 0 else 0,
            'start_time': self.start_time,
            'current_time': datetime.now()
        }


def monitor_screening_progress(state_file_path, update_interval=5):
    """
    监控筛选进度的便捷函数
    
    Args:
        state_file_path (str): 状态文件路径
        update_interval (int): 更新间隔（秒）
    """
    monitor = ProgressMonitor(state_file_path, update_interval)
    
    try:
        monitor.start_monitoring()
        
        # 保持监控直到用户中断
        while True:
            time.sleep(1)
            
            # 检查是否所有任务完成
            summary = monitor.get_summary_report()
            if summary:
                if (summary['running_batches'] == 0 and 
                    summary['pending_batches'] == 0):
                    try:
                        from i18n.i18n_manager import get_message
                        print(f"\n{get_message('all_batches_completed')}")
                    except:
                        print("\n✅ All batches processing completed!")
                    break
    
    except KeyboardInterrupt:
        try:
            from i18n.i18n_manager import get_message
            print(f"\n{get_message('monitoring_interrupted')}")
        except:
            print("\n⚠️  Monitoring interrupted by user")
    
    finally:
        monitor.stop_monitoring()
        
        # 显示最终摘要
        summary = monitor.get_summary_report()
        if summary:
            try:
                from i18n.i18n_manager import get_message
                print(f"\n{get_message('final_summary')}")
                print(get_message("total_batches", count=summary['total_batches']))
                print(get_message("completed_batches", count=summary['completed_batches'], percent=0))
                print(get_message("failed_batches", count=summary['failed_batches']))
                print(get_message("progress_percent", percent=summary['progress_percentage']))
            except:
                print(f"\n📊 Final Summary:")
                print(f"Total Batches: {summary['total_batches']}")
                print(f"Completed: {summary['completed_batches']}")
                print(f"Failed: {summary['failed_batches']}")
                print(f"Progress: {summary['progress_percentage']:.1f}%")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        try:
            from i18n.i18n_manager import get_message
            print(get_message("monitor_usage"))
        except:
            print("Usage: python progress_monitor.py <state_file_path> [update_interval]")
        sys.exit(1)
    
    state_file = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    try:
        from i18n.i18n_manager import get_message
        print(get_message("start_monitoring", file=state_file))
    except:
        print(f"🔍 Starting monitoring: {state_file}")
    monitor_screening_progress(state_file, interval)