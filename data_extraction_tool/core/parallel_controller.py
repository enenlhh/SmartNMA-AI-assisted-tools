#!/usr/bin/env python3
"""
并行数据提取控制器
Parallel Data Extraction Controller

负责协调多个工作器并行提取数据
Coordinates multiple workers for parallel data extraction
"""

import os
import json
import time
import psutil
import multiprocessing as mp
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    from i18n.i18n_manager import get_message
except ImportError:
    def get_message(key, **kwargs):
        return key.format(**kwargs) if kwargs else key

try:
    from .progress_monitor import ProgressMonitor
    from .result_merger import ResultMerger
    from .resource_detector import ResourceDetector
except ImportError:
    from progress_monitor import ProgressMonitor
    from result_merger import ResultMerger
    from resource_detector import ResourceDetector


def process_batch_worker(batch_id: int, document_batch: List[str], config_path: str, temp_dir: str) -> Dict[str, Any]:
    """独立的批次处理工作函数，避免pickling问题"""
    try:
        from src.main import DataExtractor
        
        # 为每个批次创建独立的提取器
        extractor = DataExtractor(config_path)
        
        # 处理批次中的所有文档
        results = []
        for doc_path in document_batch:
            try:
                result = extractor.process_single_document(doc_path)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Error processing {doc_path}: {e}")
        
        # 保存批次结果
        if results:
            batch_output_path = os.path.join(temp_dir, f"batch_{batch_id}_results.xlsx")
            extractor.save_batch_results(results, batch_output_path)
        
        return {
            "success": True,
            "batch_id": batch_id,
            "processed_count": len(results),
            "total_count": len(document_batch)
        }
        
    except Exception as e:
        return {
            "success": False,
            "batch_id": batch_id,
            "error": str(e)
        }


class ParallelExtractionManager:
    """并行提取管理器 / Parallel Extraction Manager"""
    
    def __init__(self, config_path: str):
        """初始化管理器"""
        self.config_path = config_path
        self.config = self.load_config()
        self.resource_detector = ResourceDetector()
        self.progress_monitor = ProgressMonitor()
        self.result_merger = ResultMerger()
        self.state_file = None
        self.temp_dir = None
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(get_message("config_error", error=str(e)))
    
    def validate_and_optimize_config(self) -> Tuple[bool, List[str]]:
        """验证并优化配置"""
        warnings = []
        
        # 检测系统资源
        cpu_cores = self.resource_detector.get_cpu_cores()
        available_memory = self.resource_detector.get_available_memory()
        
        # 获取配置的工作器数量
        requested_workers = self.config.get("parallel_settings", {}).get("parallel_workers", 1)
        safe_cpu_cores = max(1, cpu_cores - 2)  # 保留2个核心给系统
        
        # CPU核心检查
        if requested_workers > safe_cpu_cores:
            warnings.append(get_message("cpu_warning", 
                                      requested=requested_workers, 
                                      safe=safe_cpu_cores))
            warnings.append(get_message("cpu_suggestion", 
                                      recommended=safe_cpu_cores))
        
        # 内存使用估算
        memory_per_worker = self.config.get("resource_management", {}).get("memory_limit_mb", 2048) / 1024
        estimated_memory = requested_workers * memory_per_worker
        
        if estimated_memory > available_memory * 0.8:  # 使用80%内存阈值
            recommended_workers = max(1, int(available_memory * 0.8 / memory_per_worker))
            warnings.append(get_message("memory_warning",
                                      estimated=estimated_memory,
                                      available=available_memory))
            warnings.append(get_message("memory_suggestion",
                                      recommended=recommended_workers))
        
        return len(warnings) == 0, warnings
    
    def setup_extraction_environment(self) -> str:
        """设置提取环境"""
        # 创建临时目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_dir = self.config.get("parallel_settings", {}).get("temp_dir", "temp_parallel")
        self.temp_dir = f"{self.temp_dir}_{timestamp}"
        
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
        
        # 创建状态文件
        self.state_file = f"extraction_state_{timestamp}.json"
        
        return self.temp_dir
    
    def scan_input_documents(self) -> List[str]:
        """扫描输入文档"""
        input_folder = self.config["paths"]["input_folder"]
        if not os.path.exists(input_folder):
            raise Exception(get_message("file_not_found", file=input_folder))
        
        # 支持的文档格式
        supported_extensions = ['.pdf', '.docx', '.doc', '.txt']
        documents = []
        
        for ext in supported_extensions:
            # 使用递归扫描，这样会包含当前目录和子目录的所有文件
            documents.extend(Path(input_folder).glob(f"**/*{ext}"))
        
        # 去重并转换为字符串路径
        unique_documents = list(set(str(doc) for doc in documents))
        return sorted(unique_documents)
    
    def distribute_documents(self, documents: List[str], num_workers: int) -> List[List[str]]:
        """分发文档到各个工作器"""
        if not documents:
            return []
        
        # 平均分配文档
        docs_per_worker = len(documents) // num_workers
        remainder = len(documents) % num_workers
        
        batches = []
        start_idx = 0
        
        for i in range(num_workers):
            # 如果有余数，前几个工作器多分配一个文档
            batch_size = docs_per_worker + (1 if i < remainder else 0)
            end_idx = start_idx + batch_size
            
            if start_idx < len(documents):
                batches.append(documents[start_idx:end_idx])
                start_idx = end_idx
        
        return [batch for batch in batches if batch]  # 过滤空批次
    
    def save_state(self, state_data: Dict[str, Any]):
        """保存状态"""
        if self.state_file:
            try:
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    json.dump(state_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Warning: Failed to save state: {e}")
    
    def start_parallel_extraction(self) -> bool:
        """启动并行提取"""
        try:
            print(get_message("starting_new_task"))
            
            # 验证配置
            is_valid, warnings = self.validate_and_optimize_config()
            if warnings:
                print(get_message("resource_warning"))
                for warning in warnings:
                    print(warning)
                print()
                
                # 询问是否继续
                choice = input("Continue with current settings? (y/n): ").lower().strip()
                if choice != 'y':
                    return False
            
            # 设置环境
            temp_dir = self.setup_extraction_environment()
            print(get_message("temp_prepared", temp_dir=temp_dir))
            
            # 扫描文档
            documents = self.scan_input_documents()
            if not documents:
                print(get_message("no_documents"))
                return False
            
            print(get_message("documents_found", count=len(documents)))
            
            # 获取工作器数量
            num_workers = self.config.get("parallel_settings", {}).get("parallel_workers", 1)
            print(get_message("parallel_setup", workers=num_workers))
            
            # 分发文档
            document_batches = self.distribute_documents(documents, num_workers)
            
            # 初始化状态
            state_data = {
                "timestamp": datetime.now().isoformat(),
                "total_documents": len(documents),
                "total_batches": len(document_batches),
                "completed_batches": 0,
                "failed_batches": [],
                "temp_dir": temp_dir,
                "status": "running"
            }
            self.save_state(state_data)
            
            # 启动并行处理
            return self._execute_parallel_extraction(document_batches, state_data)
            
        except Exception as e:
            print(get_message("system_error", error=str(e)))
            return False
    
    def _execute_parallel_extraction(self, document_batches: List[List[str]], state_data: Dict[str, Any]) -> bool:
        """执行并行提取"""
        try:
            from src.main import DataExtractor
            
            # 启动进度监控
            self.progress_monitor.start_monitoring(len(document_batches))
            
            completed_batches = 0
            failed_batches = []
            
            # 使用进程池执行并行提取
            max_workers = min(len(document_batches), self.config.get("parallel_settings", {}).get("parallel_workers", 1))
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有批次任务
                future_to_batch = {}
                for i, batch in enumerate(document_batches):
                    future = executor.submit(process_batch_worker, i, batch, self.config_path, self.temp_dir)
                    future_to_batch[future] = i
                
                # 处理完成的任务
                for future in as_completed(future_to_batch):
                    batch_id = future_to_batch[future]
                    try:
                        result = future.result()
                        if result["success"]:
                            completed_batches += 1
                            print(get_message("batch_completed", batch=batch_id + 1))
                        else:
                            failed_batches.append(batch_id)
                            print(get_message("batch_failed", 
                                            batch=batch_id + 1, 
                                            error=result.get("error", "Unknown error")))
                        
                        # 更新进度
                        progress = (completed_batches + len(failed_batches)) / len(document_batches) * 100
                        print(get_message("extraction_progress",
                                        processed=completed_batches + len(failed_batches),
                                        total=len(document_batches),
                                        percentage=progress))
                        
                    except Exception as e:
                        failed_batches.append(batch_id)
                        print(get_message("batch_failed", 
                                        batch=batch_id + 1, 
                                        error=str(e)))
            
            # 停止进度监控
            self.progress_monitor.stop_monitoring()
            
            # 合并结果
            if completed_batches > 0:
                print(get_message("merging_results"))
                output_path = self.result_merger.merge_batch_results(self.temp_dir, self.config)
                print(get_message("saving_results", path=output_path))
            
            # 清理临时文件
            if self.config.get("parallel_settings", {}).get("cleanup_temp_files", True):
                print(get_message("cleanup_temp"))
                self._cleanup_temp_files()
            
            # 更新最终状态
            state_data.update({
                "completed_batches": completed_batches,
                "failed_batches": failed_batches,
                "status": "completed" if not failed_batches else "completed_with_errors"
            })
            self.save_state(state_data)
            
            return completed_batches > 0
            
        except Exception as e:
            print(get_message("system_error", error=str(e)))
            return False
    
    def _process_batch(self, batch_id: int, document_batch: List[str]) -> Dict[str, Any]:
        """处理单个批次"""
        # 这个方法现在需要作为独立函数来避免pickling问题
        return process_batch_worker(batch_id, document_batch, self.config_path, self.temp_dir)
    
    def resume_from_state(self, state_file_path: str) -> bool:
        """从状态文件恢复任务 / Resume task from state file"""
        try:
            print(f"🔄 Loading state from: {state_file_path}")
            
            # 读取状态文件
            with open(state_file_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # 检查状态
            if state_data.get("status") == "completed":
                print("✅ Task already completed")
                return True
            
            # 恢复配置
            self.temp_dir = state_data.get("temp_dir")
            completed_batches = state_data.get("completed_batches", 0)
            failed_batches = state_data.get("failed_batches", [])
            total_batches = state_data.get("total_batches", 0)
            
            print(f"📊 Resume status: {completed_batches}/{total_batches} batches completed")
            
            if failed_batches:
                print(f"🔄 Retrying {len(failed_batches)} failed batches")
                # 重新处理失败的批次
                # 这里需要重新构建文档批次并处理
                return self._retry_failed_batches(failed_batches, state_data)
            else:
                print("✅ All batches completed successfully")
                return True
                
        except Exception as e:
            print(get_message("system_error", error=str(e)))
            return False
    
    def _retry_failed_batches(self, failed_batch_ids: List[int], state_data: Dict[str, Any]) -> bool:
        """重试失败的批次 / Retry failed batches"""
        try:
            # 这里需要重新构建失败批次的文档列表
            # 由于原始文档分配信息可能丢失，我们重新扫描并分配
            documents = self.scan_input_documents()
            num_workers = self.config.get("parallel_settings", {}).get("parallel_workers", 1)
            document_batches = self.distribute_documents(documents, num_workers)
            
            # 只处理失败的批次
            failed_batches = [document_batches[i] for i in failed_batch_ids if i < len(document_batches)]
            
            if not failed_batches:
                print("✅ No failed batches to retry")
                return True
            
            # 执行重试
            return self._execute_parallel_extraction(failed_batches, state_data)
            
        except Exception as e:
            print(get_message("system_error", error=str(e)))
            return False
    
    def _cleanup_temp_files(self):
        """清理临时文件 / Cleanup temporary files"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                print(f"✓ Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            print(f"Warning: Failed to cleanup temp files: {e}")