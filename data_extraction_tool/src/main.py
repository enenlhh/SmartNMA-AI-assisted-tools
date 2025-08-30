"""
升级版数据提取协调器
Enhanced Data Extraction Orchestrator

支持并行处理的数据提取主模块
Main module for data extraction with parallel processing support
"""
import os
import json
import time
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm import tqdm

from .extractors.table_extractor import TableExtractor
from .extractors.json_extractor import JsonExtractor
from .core.file_reader import read_file
from .core.data_processor import merge_results, post_process_data
from .utils.excel_writer import save_results_to_excel
from .utils.validation import validate_data_consistency


class DataExtractor:
    """升级版数据提取协调器 / Enhanced Data Extraction Coordinator"""
    
    def __init__(self, config_path="config/config.json"):
        """初始化提取器"""
        self.config_path = config_path
        self.config = self.load_config()
        self.setup_directories()
        self.initialize_extractor()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 向后兼容性处理
            if "paths" not in config:
                raise ValueError("Missing 'paths' section in config")
            
            # 设置默认值
            if "parallel_settings" not in config:
                config["parallel_settings"] = {
                    "parallel_workers": 1,
                    "auto_distribute": True,
                    "temp_dir": "temp_parallel",
                    "cleanup_temp_files": True,
                    "retry_failed_batches": True,
                    "max_retries": 3
                }
            
            if "resource_management" not in config:
                config["resource_management"] = {
                    "api_calls_per_minute_limit": 100,
                    "memory_limit_mb": 2048,
                    "delay_between_workers": 2,
                    "progress_update_interval": 5
                }
            
            return config
            
        except Exception as e:
            raise Exception(f"Failed to load config: {str(e)}")
    
    def setup_directories(self):
        """设置目录结构"""
        # 创建输出目录
        output_folder = self.config["paths"]["output_folder"]
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        
        # 创建调试和处理文件目录
        if self.config.get("processing", {}).get("create_debug_files", False):
            Path(output_folder, "debug_files").mkdir(exist_ok=True)
        
        if self.config.get("processing", {}).get("create_process_files", False):
            Path(output_folder, "process_files").mkdir(exist_ok=True)
    
    def initialize_extractor(self):
        """初始化提取器"""
        debug_folder = None
        if self.config.get("processing", {}).get("create_debug_files", False):
            debug_folder = os.path.join(self.config["paths"]["output_folder"], "debug_files")
        
        extraction_mode = self.config.get("mode", {}).get("extraction_mode", 
                                                         self.config.get("extraction_mode", "table"))
        
        primary_llm = self.config["llm_configs"]["primary"]
        repair_llm = self.config["llm_configs"].get("repair", primary_llm)
        
        if extraction_mode == "table":
            self.extractor = TableExtractor(primary_llm, repair_llm, debug_folder)
        elif extraction_mode == "json":
            self.extractor = JsonExtractor(primary_llm, repair_llm, debug_folder)
        else:
            raise ValueError(f"Unsupported extraction mode: {extraction_mode}")
    
    def extract_from_files(self) -> Optional[Dict[str, Any]]:
        """主提取函数（兼容原有接口）"""
        return self.process_all_documents()
    
    def process_all_documents(self) -> Optional[Dict[str, Any]]:
        """处理所有文档"""
        input_folder = self.config["paths"]["input_folder"]
        output_file = os.path.join(
            self.config["paths"]["output_folder"], 
            self.config["paths"]["output_filename"]
        )
        
        # 获取文件列表
        all_files = self.scan_documents(input_folder)
        if not all_files:
            print("No supported files found")
            return None
        
        # 检查现有结果并过滤已处理的文件
        existing_data = self.load_existing_data(output_file)
        remaining_files = self.filter_processed_files(all_files, existing_data)
        
        if not remaining_files:
            print("All files have been processed")
            return existing_data
        
        # 处理文件
        all_data = existing_data.copy()
        processed_count = 0
        
        print(f"Processing {len(remaining_files)} documents...")
        
        for file_idx, file_path in enumerate(tqdm(remaining_files, desc="Processing files")):
            print(f"\nProcessing: {os.path.basename(file_path)} ({file_idx+1}/{len(remaining_files)})")
            
            try:
                file_data = self.process_single_document(file_path)
                
                if file_data:
                    all_data = merge_results(all_data, file_data)
                    processed_count += 1
                    
                    # 保存中间结果
                    save_interval = self.config.get("processing", {}).get("save_interval", 1)
                    if processed_count % save_interval == 0:
                        print(f"\nSaving intermediate results ({processed_count} files processed)...")
                        self.save_results(all_data, output_file)
                        
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # 保存最终结果
        if processed_count > 0:
            print("\nSaving final results...")
            self.save_results(all_data, output_file)
            
            # 数据一致性验证
            try:
                validate_data_consistency(all_data)
                print("✅ Data consistency validation passed")
            except Exception as e:
                print(f"⚠️ Data consistency warning: {e}")
        
        print(f"\n✅ Extraction completed! Processed {processed_count} documents.")
        return all_data
    
    def process_single_document(self, file_path: str) -> Optional[Dict[str, Any]]:
        """处理单个文档"""
        try:
            split_length = self.config.get("processing", {}).get("split_length", 100000)
            return self.extractor.process_file(file_path, split_length)
        except Exception as e:
            print(f"Error processing document {file_path}: {e}")
            return None
    
    def save_batch_results(self, results: List[Dict[str, Any]], output_path: str):
        """保存批次结果"""
        try:
            # 合并批次中的所有结果
            batch_data = {}
            for result in results:
                if result:
                    batch_data = merge_results(batch_data, result)
            
            # 保存到Excel文件
            if batch_data:
                create_process_files = self.config.get("processing", {}).get("create_process_files", False)
                save_results_to_excel(batch_data, output_path, create_process_files)
                
        except Exception as e:
            print(f"Error saving batch results: {e}")
    
    def scan_documents(self, input_folder: str) -> List[str]:
        """扫描文档文件"""
        if not os.path.exists(input_folder):
            raise Exception(f"Input folder not found: {input_folder}")
        
        supported_extensions = ['.pdf', '.docx', '.doc', '.txt']
        documents = []
        
        for ext in supported_extensions:
            # 扫描当前目录
            documents.extend(Path(input_folder).glob(f"*{ext}"))
            # 扫描子目录
            documents.extend(Path(input_folder).glob(f"**/*{ext}"))
        
        # 转换为字符串路径并排序
        file_paths = [str(doc) for doc in documents]
        return sorted(file_paths)
    
    def load_existing_data(self, output_file: str) -> Dict[str, Any]:
        """加载现有的提取结果"""
        existing_data = {}
        if os.path.exists(output_file):
            try:
                import pandas as pd
                existing_sheets = pd.read_excel(output_file, sheet_name=None)
                for sheet_name, df in existing_sheets.items():
                    existing_data[sheet_name] = df.to_dict('records')
                print(f"✓ Loaded existing results with {len(existing_sheets)} tables")
            except Exception as e:
                print(f"Warning: Error reading existing results: {e}")
        return existing_data
    
    def filter_processed_files(self, all_files: List[str], existing_data: Dict[str, Any]) -> List[str]:
        """过滤已处理的文件"""
        processed_files = set()
        
        # 从Study_Info表中获取已处理的文件名
        if "Study_Info" in existing_data and existing_data["Study_Info"]:
            for study in existing_data["Study_Info"]:
                if "File_Name" in study and study["File_Name"]:
                    processed_files.add(study["File_Name"])
        
        # 过滤文件列表
        filtered_files = []
        for file_path in all_files:
            file_name = os.path.basename(file_path)
            if file_name not in processed_files:
                filtered_files.append(file_path)
        
        skipped_count = len(all_files) - len(filtered_files)
        if skipped_count > 0:
            print(f"⏭️ Skipping {skipped_count} already processed files")
        
        return filtered_files
    
    def save_results(self, data: Dict[str, Any], output_file: str):
        """保存结果"""
        try:
            create_process_files = self.config.get("processing", {}).get("create_process_files", False)
            save_results_to_excel(data, output_file, create_process_files)
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def get_extraction_stats(self, data: Dict[str, Any]) -> Dict[str, int]:
        """获取提取统计信息"""
        stats = {}
        for table_name, records in data.items():
            stats[table_name] = len(records) if records else 0
        return stats
    
    def estimate_processing_time(self, file_count: int, avg_time_per_file: float = 30.0) -> str:
        """估算处理时间"""
        total_seconds = file_count * avg_time_per_file
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        if hours > 0:
            return f"约 {hours} 小时 {minutes} 分钟"
        else:
            return f"约 {minutes} 分钟"