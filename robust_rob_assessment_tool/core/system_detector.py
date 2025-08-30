"""
System resource detection and capacity planning.

This module provides system resource detection, capacity planning,
and configuration validation for optimal parallel processing.
"""

import os
import psutil
import platform
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass


@dataclass
class SystemCapacity:
    """Represents system capacity information."""
    cpu_cores: int
    cpu_logical: int
    memory_total_gb: float
    memory_available_gb: float
    disk_free_gb: float
    platform: str
    python_version: str


class SystemCapacityDetector:
    """
    System resource detection and capacity planning utilities.
    
    This class provides methods for detecting system resources,
    recommending optimal parallel worker configurations, and
    validating configurations against system capabilities.
    """
    
    @staticmethod
    def detect_system_capacity() -> Dict[str, Any]:
        """
        Detect available system resources and capacity.
        
        Returns:
            Dict[str, Any]: System capacity information
        """
        try:
            # CPU information
            cpu_cores = psutil.cpu_count(logical=False) or 1
            cpu_logical = psutil.cpu_count(logical=True) or 1
            
            # Memory information
            memory = psutil.virtual_memory()
            memory_total_gb = memory.total / (1024**3)
            memory_available_gb = memory.available / (1024**3)
            
            # Disk information
            disk = psutil.disk_usage('.')
            disk_free_gb = disk.free / (1024**3)
            
            # Platform information
            platform_info = platform.platform()
            python_version = platform.python_version()
            
            capacity = SystemCapacity(
                cpu_cores=cpu_cores,
                cpu_logical=cpu_logical,
                memory_total_gb=memory_total_gb,
                memory_available_gb=memory_available_gb,
                disk_free_gb=disk_free_gb,
                platform=platform_info,
                python_version=python_version
            )
            
            return {
                "cpu_cores": capacity.cpu_cores,
                "cpu_logical": capacity.cpu_logical,
                "memory_total_gb": round(capacity.memory_total_gb, 2),
                "memory_available_gb": round(capacity.memory_available_gb, 2),
                "disk_free_gb": round(capacity.disk_free_gb, 2),
                "platform": capacity.platform,
                "python_version": capacity.python_version
            }
            
        except Exception as e:
            # Fallback to conservative estimates
            return {
                "cpu_cores": 2,
                "cpu_logical": 4,
                "memory_total_gb": 8.0,
                "memory_available_gb": 4.0,
                "disk_free_gb": 10.0,
                "platform": "Unknown",
                "python_version": platform.python_version(),
                "detection_error": str(e)
            }
    
    @staticmethod
    def recommend_parallel_workers(config: Dict[str, Any]) -> int:
        """
        Recommend optimal number of parallel workers based on system capacity.
        
        Args:
            config: Current configuration dictionary
            
        Returns:
            int: Recommended number of parallel workers
        """
        capacity = SystemCapacityDetector.detect_system_capacity()
        
        # Conservative approach: use 75% of logical CPUs
        max_workers_cpu = max(1, int(capacity["cpu_logical"] * 0.75))
        
        # Memory-based limit: assume 1GB per worker minimum
        max_workers_memory = max(1, int(capacity["memory_available_gb"]))
        
        # Take the minimum to be safe
        recommended = min(max_workers_cpu, max_workers_memory)
        
        # Cap at 8 workers for stability
        recommended = min(recommended, 8)
        
        # Ensure at least 1 worker
        return max(1, recommended)
    
    @staticmethod
    def validate_configuration(config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration against system capabilities.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List[str]: List of validation warnings/errors
        """
        warnings = []
        capacity = SystemCapacityDetector.detect_system_capacity()
        
        # Check parallel workers
        parallel_workers = config.get("parallel_workers", 1)
        recommended_workers = SystemCapacityDetector.recommend_parallel_workers(config)
        
        if parallel_workers > capacity["cpu_logical"]:
            warnings.append(
                f"Parallel workers ({parallel_workers}) exceeds logical CPU count "
                f"({capacity['cpu_logical']}). This may cause performance issues."
            )
        
        if parallel_workers > recommended_workers * 1.5:
            warnings.append(
                f"Parallel workers ({parallel_workers}) significantly exceeds "
                f"recommended count ({recommended_workers}). Consider reducing for optimal performance."
            )
        
        # Check memory requirements
        estimated_memory_per_worker = 1.0  # GB
        total_memory_needed = parallel_workers * estimated_memory_per_worker
        
        if total_memory_needed > capacity["memory_available_gb"]:
            warnings.append(
                f"Estimated memory usage ({total_memory_needed:.1f}GB) may exceed "
                f"available memory ({capacity['memory_available_gb']:.1f}GB)."
            )
        
        # Check disk space
        if capacity["disk_free_gb"] < 5.0:
            warnings.append(
                f"Low disk space ({capacity['disk_free_gb']:.1f}GB). "
                "Ensure sufficient space for temporary files and outputs."
            )
        
        return warnings
    
    @staticmethod
    def get_system_info_summary() -> str:
        """
        Get a formatted summary of system information.
        
        Returns:
            str: Formatted system information summary
        """
        capacity = SystemCapacityDetector.detect_system_capacity()
        
        summary = f"""System Information:
  Platform: {capacity['platform']}
  Python: {capacity['python_version']}
  CPU Cores: {capacity['cpu_cores']} physical, {capacity['cpu_logical']} logical
  Memory: {capacity['memory_available_gb']:.1f}GB available / {capacity['memory_total_gb']:.1f}GB total
  Disk Space: {capacity['disk_free_gb']:.1f}GB free
  Recommended Workers: {SystemCapacityDetector.recommend_parallel_workers({})}"""
        
        return summary
    
    @staticmethod
    def validate_resource_usage_with_warnings(config: Dict[str, Any], 
                                            interactive: bool = True,
                                            confirmation_callback: Optional[Callable[[str], bool]] = None) -> bool:
        """
        Validate resource usage and provide interactive warnings.
        
        Args:
            config: Configuration to validate
            interactive: Whether to show interactive prompts
            confirmation_callback: Optional callback for confirmation prompts
            
        Returns:
            bool: True if user confirms to proceed, False otherwise
        """
        warnings = SystemCapacityDetector.validate_configuration(config)
        
        if not warnings:
            return True
        
        if not interactive:
            # Non-interactive mode: log warnings and proceed
            for warning in warnings:
                print(f"WARNING: {warning}")
            return True
        
        # Interactive mode: show warnings and ask for confirmation
        print("\n⚠️  Resource Usage Warnings:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
        
        print(f"\nRecommended configuration:")
        recommended_workers = SystemCapacityDetector.recommend_parallel_workers(config)
        print(f"  - Parallel workers: {recommended_workers}")
        
        capacity = SystemCapacityDetector.detect_system_capacity()
        print(f"  - Available memory: {capacity['memory_available_gb']:.1f}GB")
        print(f"  - CPU cores: {capacity['cpu_logical']} logical")
        
        # Use callback if provided, otherwise use input
        if confirmation_callback:
            return confirmation_callback("Do you want to proceed with the current configuration?")
        else:
            while True:
                response = input("\nDo you want to proceed with the current configuration? (y/n/r for recommend): ").lower().strip()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                elif response in ['r', 'recommend']:
                    print(f"\nRecommended configuration changes:")
                    print(f"  - Set parallel_workers to {recommended_workers}")
                    return False
                else:
                    print("Please enter 'y' for yes, 'n' for no, or 'r' for recommendations.")
    
    @staticmethod
    def get_resource_recommendations(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get resource optimization recommendations.
        
        Args:
            config: Current configuration
            
        Returns:
            Dict[str, Any]: Recommended configuration changes
        """
        capacity = SystemCapacityDetector.detect_system_capacity()
        recommendations = {}
        
        # Parallel workers recommendation
        recommended_workers = SystemCapacityDetector.recommend_parallel_workers(config)
        current_workers = config.get("parallel_workers", 1)
        
        if current_workers != recommended_workers:
            recommendations["parallel_workers"] = {
                "current": current_workers,
                "recommended": recommended_workers,
                "reason": f"Optimized for {capacity['cpu_logical']} logical CPUs and {capacity['memory_available_gb']:.1f}GB available memory"
            }
        
        # Memory optimization
        if capacity["memory_available_gb"] < 4.0:
            recommendations["memory_optimization"] = {
                "suggestion": "Consider reducing parallel workers or closing other applications",
                "current_available": f"{capacity['memory_available_gb']:.1f}GB",
                "recommended_minimum": "4.0GB"
            }
        
        # Disk space optimization
        if capacity["disk_free_gb"] < 10.0:
            recommendations["disk_optimization"] = {
                "suggestion": "Free up disk space or change output directory",
                "current_free": f"{capacity['disk_free_gb']:.1f}GB",
                "recommended_minimum": "10.0GB"
            }
        
        return recommendations
    
    @staticmethod
    def monitor_resource_usage(duration_seconds: int = 60, 
                             interval_seconds: int = 5) -> Dict[str, List[float]]:
        """
        Monitor system resource usage over time.
        
        Args:
            duration_seconds: How long to monitor
            interval_seconds: Sampling interval
            
        Returns:
            Dict[str, List[float]]: Resource usage data over time
        """
        monitoring_data = {
            "timestamps": [],
            "cpu_percent": [],
            "memory_percent": [],
            "memory_available_gb": [],
            "disk_usage_percent": []
        }
        
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            current_time = time.time() - start_time
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('.')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            monitoring_data["timestamps"].append(current_time)
            monitoring_data["cpu_percent"].append(cpu_percent)
            monitoring_data["memory_percent"].append(memory_percent)
            monitoring_data["memory_available_gb"].append(memory_available_gb)
            monitoring_data["disk_usage_percent"].append(disk_usage_percent)
            
            time.sleep(interval_seconds)
        
        return monitoring_data
    
    @staticmethod
    def check_resource_thresholds(thresholds: Optional[Dict[str, float]] = None) -> Dict[str, bool]:
        """
        Check if current resource usage exceeds specified thresholds.
        
        Args:
            thresholds: Resource thresholds to check against
            
        Returns:
            Dict[str, bool]: Threshold violation status
        """
        if thresholds is None:
            thresholds = {
                "cpu_percent": 80.0,
                "memory_percent": 85.0,
                "disk_usage_percent": 90.0
            }
        
        violations = {}
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        violations["cpu_exceeded"] = cpu_percent > thresholds.get("cpu_percent", 80.0)
        
        # Check memory usage
        memory = psutil.virtual_memory()
        violations["memory_exceeded"] = memory.percent > thresholds.get("memory_percent", 85.0)
        
        # Check disk usage
        disk = psutil.disk_usage('.')
        disk_usage_percent = (disk.used / disk.total) * 100
        violations["disk_exceeded"] = disk_usage_percent > thresholds.get("disk_usage_percent", 90.0)
        
        violations["any_exceeded"] = any([
            violations["cpu_exceeded"],
            violations["memory_exceeded"], 
            violations["disk_exceeded"]
        ])
        
        return violations