#!/usr/bin/env python3
"""
系统资源检测模块
System Resource Detection Module

检测系统硬件资源并提供优化建议
Detect system hardware resources and provide optimization suggestions
"""

import psutil
import platform
from typing import Dict, Any, Tuple, List


class ResourceDetector:
    """系统资源检测器 / System Resource Detector"""
    
    def __init__(self):
        self.system_info = self._collect_system_info()
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """收集系统信息"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
    
    def get_cpu_cores(self) -> int:
        """获取CPU核心数"""
        return psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True) or 1
    
    def get_logical_cores(self) -> int:
        """获取逻辑核心数"""
        return psutil.cpu_count(logical=True) or 1
    
    def get_available_memory(self) -> float:
        """获取可用内存 (GB)"""
        memory = psutil.virtual_memory()
        return memory.available / (1024 ** 3)  # 转换为GB
    
    def get_total_memory(self) -> float:
        """获取总内存 (GB)"""
        memory = psutil.virtual_memory()
        return memory.total / (1024 ** 3)  # 转换为GB
    
    def get_memory_usage_percent(self) -> float:
        """获取内存使用百分比"""
        memory = psutil.virtual_memory()
        return memory.percent
    
    def get_cpu_usage_percent(self, interval: float = 1.0) -> float:
        """获取CPU使用百分比"""
        return psutil.cpu_percent(interval=interval)
    
    def get_disk_usage(self, path: str = ".") -> Dict[str, float]:
        """获取磁盘使用情况"""
        try:
            disk = psutil.disk_usage(path)
            return {
                "total_gb": disk.total / (1024 ** 3),
                "used_gb": disk.used / (1024 ** 3),
                "free_gb": disk.free / (1024 ** 3),
                "percent": (disk.used / disk.total) * 100
            }
        except Exception:
            return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "percent": 0}
    
    def get_optimal_worker_count(self, memory_per_worker_mb: int = 2048) -> Tuple[int, str]:
        """获取最优工作器数量"""
        cpu_cores = self.get_cpu_cores()
        available_memory_gb = self.get_available_memory()
        
        # 基于CPU核心的建议（保留1-2个核心给系统）
        cpu_based_workers = max(1, cpu_cores - 2)
        
        # 基于内存的建议
        memory_per_worker_gb = memory_per_worker_mb / 1024
        memory_based_workers = max(1, int(available_memory_gb * 0.8 / memory_per_worker_gb))
        
        # 取较小值作为保守建议
        recommended_workers = min(cpu_based_workers, memory_based_workers)
        
        # 生成建议说明
        if cpu_based_workers < memory_based_workers:
            reason = f"CPU limited (safe cores: {cpu_based_workers})"
        elif memory_based_workers < cpu_based_workers:
            reason = f"Memory limited (available: {available_memory_gb:.1f}GB)"
        else:
            reason = "Balanced configuration"
        
        return recommended_workers, reason
    
    def check_system_requirements(self, min_memory_gb: float = 4.0, min_cores: int = 2) -> Tuple[bool, List[str]]:
        """检查系统要求"""
        issues = []
        
        # 检查内存
        total_memory = self.get_total_memory()
        if total_memory < min_memory_gb:
            issues.append(f"Insufficient memory: {total_memory:.1f}GB < {min_memory_gb}GB required")
        
        # 检查CPU核心
        cpu_cores = self.get_cpu_cores()
        if cpu_cores < min_cores:
            issues.append(f"Insufficient CPU cores: {cpu_cores} < {min_cores} required")
        
        # 检查磁盘空间
        disk_info = self.get_disk_usage()
        if disk_info["free_gb"] < 1.0:  # 至少1GB可用空间
            issues.append(f"Insufficient disk space: {disk_info['free_gb']:.1f}GB available")
        
        return len(issues) == 0, issues
    
    def get_performance_recommendations(self) -> Dict[str, Any]:
        """获取性能优化建议"""
        cpu_cores = self.get_cpu_cores()
        logical_cores = self.get_logical_cores()
        total_memory = self.get_total_memory()
        available_memory = self.get_available_memory()
        memory_usage = self.get_memory_usage_percent()
        
        recommendations = {
            "system_info": {
                "cpu_cores": cpu_cores,
                "logical_cores": logical_cores,
                "total_memory_gb": total_memory,
                "available_memory_gb": available_memory,
                "memory_usage_percent": memory_usage
            },
            "recommendations": []
        }
        
        # CPU相关建议
        if cpu_cores <= 2:
            recommendations["recommendations"].append({
                "type": "CPU",
                "level": "warning",
                "message": "Low CPU core count detected. Consider using single-threaded mode for stability."
            })
        elif cpu_cores >= 8:
            recommendations["recommendations"].append({
                "type": "CPU", 
                "level": "info",
                "message": f"High-performance CPU detected ({cpu_cores} cores). You can use up to {cpu_cores - 2} parallel workers."
            })
        
        # 内存相关建议
        if memory_usage > 80:
            recommendations["recommendations"].append({
                "type": "Memory",
                "level": "warning", 
                "message": f"High memory usage detected ({memory_usage:.1f}%). Consider reducing parallel workers or closing other applications."
            })
        elif available_memory < 2.0:
            recommendations["recommendations"].append({
                "type": "Memory",
                "level": "warning",
                "message": f"Low available memory ({available_memory:.1f}GB). Recommend using single-threaded mode."
            })
        
        # 性能优化建议
        optimal_workers, reason = self.get_optimal_worker_count()
        recommendations["recommendations"].append({
            "type": "Performance",
            "level": "info",
            "message": f"Recommended worker count: {optimal_workers} ({reason})"
        })
        
        return recommendations
    
    def print_system_summary(self):
        """打印系统摘要"""
        try:
            from i18n.i18n_manager import get_message
        except ImportError:
            def get_message(key, **kwargs):
                fallback_messages = {
                    "system_info_title": "🖥️ System Information",
                    "platform": "Platform: {platform} {arch}",
                    "cpu_cores": "CPU Cores: {physical} physical, {logical} logical",
                    "total_memory": "Total Memory: {memory:.1f} GB",
                    "available_memory": "Available Memory: {memory:.1f} GB",
                    "memory_usage": "Memory Usage: {usage:.1f}%",
                    "disk_space": "Disk Space: {free:.1f} GB free of {total:.1f} GB",
                    "recommended_workers": "Recommended Workers: {workers} ({reason})"
                }
                message = fallback_messages.get(key, key)
                return message.format(**kwargs) if kwargs and isinstance(message, str) else message
        
        print("\n" + "=" * 50)
        print(get_message("system_info_title"))
        print("=" * 50)
        print(get_message("platform", platform=self.system_info['platform'], arch=self.system_info['architecture']))
        print(get_message("cpu_cores", physical=self.get_cpu_cores(), logical=self.get_logical_cores()))
        print(get_message("total_memory", memory=self.get_total_memory()))
        print(get_message("available_memory", memory=self.get_available_memory()))
        print(get_message("memory_usage", usage=self.get_memory_usage_percent()))
        
        disk_info = self.get_disk_usage()
        print(get_message("disk_space", free=disk_info['free_gb'], total=disk_info['total_gb']))
        
        # 显示建议
        optimal_workers, reason = self.get_optimal_worker_count()
        print(get_message("recommended_workers", workers=optimal_workers, reason=reason))
        print("=" * 50)