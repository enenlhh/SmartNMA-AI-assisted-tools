#!/usr/bin/env python3
"""
并行筛选主控制器
负责系统检测、智能分配、进程管理和断点续传
"""

import os
import sys
import json
import time
import psutil
import multiprocessing as mp
from datetime import datetime
from pathlib import Path
import traceback
import shutil

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'tools', 'xml_splitter'))
sys.path.insert(0, os.path.join(project_root, 'i18n'))

# 确保能够正确导入 i18n_manager
i18n_path = os.path.join(project_root, 'i18n')
if i18n_path not in sys.path:
    sys.path.append(i18n_path)

# 导入国际化管理器
try:
    from i18n.i18n_manager import get_message
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    print("Warning: i18n module not available, using fallback messages")

# 简化的XMLSplitter类（避免导入问题）
class XMLSplitter:
    def count_records(self, xml_path):
        import xml.etree.ElementTree as ET
        tree = ET.parse(xml_path)
        root = tree.getroot()
        records = root.findall('.//record')
        return len(records)

from src.utils import load_config

# 国际化消息处理函数（优先使用i18n系统）
def get_message_fallback(key, **kwargs):
    """
    获取本地化消息
    优先使用i18n系统，如果不可用则使用回退消息
    """
    if I18N_AVAILABLE:
        try:
            # 使用hasattr和globals安全检查函数是否存在
            import sys
            current_module = sys.modules[__name__]
            if hasattr(current_module, 'get_message') and callable(getattr(current_module, 'get_message', None)):
                return current_module.get_message(key, **kwargs)
        except Exception:
            pass
    
    # 回退消息映射（英文）
    fallback_messages = {
        "config_loaded": "✓ Configuration file loaded successfully",
        "temp_prepared": "✓ Temporary directory prepared: {temp_dir}",
        "system_detection": "🖥️  System Resource Detection",
        "cpu_cores": "CPU Cores: {cores}",
        "total_memory": "Total Memory: {memory:.1f}GB",
        "available_memory": "Available Memory: {memory:.1f}GB",
        "available_disk": "Available Disk Space: {space:.1f}GB",
        "recommended_screeners": "Recommended Screeners: {count}",
        "max_safe_screeners": "Max Safe Screeners: {count}",
        "config_warning": "⚠️  Configuration Warning:",
        "suggestion": "💡 Suggestion:",
        "adjust_to_recommended": "Adjust to recommended configuration ({count} screeners)? [y/N]: ",
        "adjusted_to": "✓ Adjusted to {count} screeners",
        "continue_anyway": "Continue with current configuration anyway? [y/N]: ",
        "execution_cancelled": "Execution cancelled",
        "exceed_cpu_cores": "Requested screeners ({requested}) exceed safe CPU cores ({safe})",
        "recommend_cpu_screeners": "Recommend setting to {count} screeners (based on CPU cores)",
        "exceed_memory": "Estimated memory usage ({estimated:.1f}GB) may exceed available memory ({available:.1f}GB)",
        "recommend_memory_screeners": "Based on memory limit, recommend setting to {count} screeners",
        "insufficient_disk": "Disk space less than 2GB, may affect temporary file storage",
        "debug_screener_count": "🔍 Debug: Using {count} screeners (from configuration file)",
        "screener_modified_warning": "⚠️  Warning: Screener count was unexpectedly modified!",
        "screener_reset_success": "✓ Reset to configuration value: {count}",
        "all_batches_completed_status": "✅ All batches processing completed",
        "wait_process_error": "⚠️  Error waiting for processes to complete: {error}",
        "reload_state_file": "📋 Reloading state file: {file}",
        "state_file_not_exist": "⚠️  State file does not exist, using passed state",
        "cannot_get_state": "Unable to get state information",
        "batch_status_stats": "📊 Batch status: {completed}/{total} completed",
        "save_state_failed": "⚠️  Failed to save state: {error}",
        "temp_cleanup_success": "✓ Temporary files cleaned",
        "temp_cleanup_error": "⚠️  Error cleaning temporary files: {error}",
        "parallel_screening_system": "🎯 SmartEBM Parallel Screening System",
        "parallel_screening_completed": "✅ Parallel screening completed",
        "parallel_screening_failed": "❌ Parallel screening failed",
        "user_interrupted": "⚠️  User interrupted operation",
        "detected_incomplete_task": "🔄 Detected incomplete screening task",
        "task_id": "Task ID: {id}",
        "total_records_label": "Total Records: {count}",
        "screener_count_label": "Screener Count: {count}",
        "current_progress": "Current Progress: {completed}/{total} ({percent:.1f}%)",
        "pending_batches_label": "Pending Batches:",
        "options_label": "Options:",
        "auto_continue_batches": "1. Auto continue incomplete batches",
        "restart_all_tasks": "2. Restart all tasks",
        "cancel_operation": "3. Cancel",
        "please_select_option": "Please select [1/2/3]: ",
        "please_enter_valid_option": "Please enter a valid option (1/2/3)",
        "auto_continue_selected": "✓ Auto continue incomplete tasks",
        "restart_selected": "✓ Restart tasks",
        "cancelled_selected": "Cancelled",
        "startup_failed": "❌ Startup failed: {error}",
        "new_task_startup_failed": "❌ New task startup failed: {error}",
        "parallel_execution_starting": "🔄 Starting parallel screening execution...",
        "parallel_execution_failed": "❌ Parallel screening execution failed: {error}",
        "resume_screening_failed": "❌ Resume screening failed: {error}",
        "execution_cancelled_user": "Execution cancelled",
        "starting_new_parallel": "🚀 Starting parallel screening system"
    }
    
    message = fallback_messages.get(key, key)
    if message and kwargs:
        try:
            return message.format(**kwargs)
        except (KeyError, ValueError):
            return message
    return message or key


class SystemCapacityDetector:
    """系统资源检测器"""
    
    @staticmethod
    def detect_system_capacity():
        """检测系统资源并推荐配置"""
        try:
            # CPU核心数
            cpu_cores = os.cpu_count() or 4  # 默认倄4核
            
            # 内存信息
            memory = psutil.virtual_memory()
            available_memory_gb = memory.available / (1024**3)
            total_memory_gb = memory.total / (1024**3)
            
            # 磁盘空间
            disk_usage = psutil.disk_usage('/')
            available_disk_gb = disk_usage.free / (1024**3)
            
            # 推荐配置（保守估算）
            # 每个筛选器大约需要512MB内存
            memory_based_limit = int(available_memory_gb // 0.5)
            cpu_based_limit = max(1, cpu_cores - 1)  # 保留一个核心给系统
            
            recommended_screeners = min(memory_based_limit, cpu_based_limit, 8)  # 最多8个
            
            return {
                'cpu_cores': cpu_cores,
                'total_memory_gb': round(total_memory_gb, 2),
                'available_memory_gb': round(available_memory_gb, 2),
                'available_disk_gb': round(available_disk_gb, 2),
                'recommended_screeners': max(1, recommended_screeners),
                'max_safe_screeners': cpu_based_limit,
                'memory_per_screener_mb': 512
            }
        except Exception as e:
            print(f"System detection error: {str(e)}")
            # 返回保守默认值
            return {
                'cpu_cores': 2,
                'total_memory_gb': 8.0,
                'available_memory_gb': 4.0,
                'available_disk_gb': 10.0,
                'recommended_screeners': 2,
                'max_safe_screeners': 2,
                'memory_per_screener_mb': 512
            }
    
    @staticmethod
    def validate_parallel_config(parallel_config, system_capacity):
        """验证并行配置是否合理"""
        requested_screeners = parallel_config.get('parallel_screeners', 1)
        
        warnings = []
        recommendations = []
        
        # CPU检查
        if requested_screeners > system_capacity['max_safe_screeners']:
            warnings.append(
                get_message_fallback("exceed_cpu_cores", 
                          requested=requested_screeners, 
                          safe=system_capacity['max_safe_screeners'])
            )
            recommendations.append(
                get_message_fallback("recommend_cpu_screeners", 
                          count=system_capacity['max_safe_screeners'])
            )
        
        # 内存检查
        estimated_memory = requested_screeners * system_capacity['memory_per_screener_mb'] / 1024
        if estimated_memory > system_capacity['available_memory_gb'] * 0.8:
            warnings.append(
                get_message_fallback("exceed_memory", 
                          estimated=estimated_memory, 
                          available=system_capacity['available_memory_gb'])
            )
            memory_safe_screeners = int(system_capacity['available_memory_gb'] * 0.8 * 1024 / 512)
            recommendations.append(
                get_message_fallback("recommend_memory_screeners", 
                          count=memory_safe_screeners)
            )
        
        # 磁盘空间检查
        if system_capacity['available_disk_gb'] < 2:
            warnings.append(get_message_fallback("insufficient_disk"))
        
        return {
            'is_safe': len(warnings) == 0,
            'warnings': warnings,
            'recommendations': recommendations,
            'adjusted_screeners': min(
                requested_screeners,
                system_capacity['recommended_screeners']
            )
        }


class RecordDistributor:
    """智能记录分配器"""
    
    @staticmethod
    def calculate_distribution(total_records, parallel_screeners):
        """计算记录分配方案"""
        if parallel_screeners <= 0:
            raise ValueError("Number of screeners must be greater than 0")
        
        if total_records <= 0:
            raise ValueError("Number of records must be greater than 0")
        
        # 基础分配量
        base_count = total_records // parallel_screeners
        remainder = total_records % parallel_screeners
        
        distributions = []
        current_start = 1
        
        for i in range(parallel_screeners):
            # 前remainder个筛选器多分配1条记录
            current_count = base_count + (1 if i < remainder else 0)
            current_end = current_start + current_count - 1
            
            distributions.append({
                'batch_id': i + 1,
                'start_record': current_start,
                'end_record': current_end,
                'record_count': current_count,
                'status': 'pending'
            })
            
            current_start = current_end + 1
        
        return distributions
    
    @staticmethod
    def print_distribution_table(distributions, total_records):
        """打印分配表格"""
        print("\n" + "="*70)
        print("📋 Record Distribution Plan")
        print("="*70)
        print(f"{'Batch':<6} {'Start Record':<12} {'End Record':<10} {'Record Count':<12} {'Percentage':<10}")
        print("-"*70)
        
        for dist in distributions:
            percentage = (dist['record_count'] / total_records) * 100
            print(f"{dist['batch_id']:<6} {dist['start_record']:<12} "
                  f"{dist['end_record']:<10} {dist['record_count']:<12} "
                  f"{percentage:.1f}%")
        
        print("-"*70)
        print(f"{'Total':<6} {'':<12} {'':<10} {total_records:<12} {'100.0%':<10}")
        print("="*70)


class ParallelScreeningManager:
    """并行筛选管理器"""
    
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config: dict = {}      # 统一配置
        self.state_file = ""
        self.temp_dir = ""
        self.processes = {}
        self.batch_status = {}
        
        # 加载配置
        self.load_configurations()
        
        # 初始化系统检测
        self.system_capacity = SystemCapacityDetector.detect_system_capacity()
        
        # 创建临时目录
        self.setup_temp_directory()
    
    def load_configurations(self):
        """加载统一配置文件"""
        try:
            # 加载统一配置文件
            self.config = load_config(self.config_path)
            
            # 检查是否包含并行配置
            if 'parallel_settings' not in self.config:
                raise Exception("Configuration file missing parallel_settings section")
            
            # 设置状态文件路径
            self.state_file = self.config['parallel_settings'].get('state_file', 'parallel_screening_state.json')
            
            print(get_message_fallback("config_loaded"))
            
        except Exception as e:
            raise Exception(f"Configuration file loading failed: {str(e)}")
    
    def setup_temp_directory(self):
        """设置临时目录"""
        if not self.config:
            raise Exception("Configuration file not loaded")
            
        self.temp_dir = self.config['parallel_settings']['temp_dir']
        
        # 创建临时目录
        os.makedirs(self.temp_dir, exist_ok=True)
        print(get_message_fallback("temp_prepared", temp_dir=self.temp_dir))
    
    def print_system_info(self):
        """打印系统信息"""
        capacity = self.system_capacity
        
        print("\n" + "="*60)
        print(get_message_fallback("system_detection"))
        print("="*60)
        print(get_message_fallback("cpu_cores", cores=capacity['cpu_cores']))
        print(get_message_fallback("total_memory", memory=capacity['total_memory_gb']))
        print(get_message_fallback("available_memory", memory=capacity['available_memory_gb']))
        print(get_message_fallback("available_disk", space=capacity['available_disk_gb']))
        print(get_message_fallback("recommended_screeners", count=capacity['recommended_screeners']))
        print(get_message_fallback("max_safe_screeners", count=capacity['max_safe_screeners']))
        print("="*60)
    
    def validate_configuration(self):
        """验证配置"""
        if not self.config:
            raise Exception("Configuration file not loaded")
            
        validation = SystemCapacityDetector.validate_parallel_config(
            self.config['parallel_settings'],
            self.system_capacity
        )
        
        if not validation['is_safe']:
            print(f"\n{get_message_fallback('config_warning')}")
            for warning in validation['warnings']:
                print(f"   - {warning}")
            
            print(f"\n{get_message_fallback('suggestion')}")
            for rec in validation['recommendations']:
                print(f"   - {rec}")
            
            # 询问用户是否继续
            choice = input(f"\n{get_message_fallback('adjust_to_recommended', count=validation['adjusted_screeners'])}")
            if choice.lower() == 'y':
                self.config['parallel_settings']['parallel_screeners'] = validation['adjusted_screeners']
                print(get_message_fallback('adjusted_to', count=validation['adjusted_screeners']))
            else:
                choice = input(get_message_fallback('continue_anyway'))
                if choice.lower() != 'y':
                    print(get_message_fallback('execution_cancelled'))
                    return False
        
        return True
    
    def count_xml_records(self, xml_path):
        """统计XML记录数量"""
        try:
            splitter = XMLSplitter()
            return splitter.count_records(xml_path)
        except Exception as e:
            raise Exception(f"XML record counting failed: {str(e)}")
    
    def check_existing_state(self):
        """检查是否存在未完成的任务"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                # 检查是否有未完成的批次
                pending_batches = [b for b in state['batches'] 
                                 if b['status'] in ['pending', 'failed', 'running']]
                
                if pending_batches:
                    return state, pending_batches
                    
            except Exception as e:
                print(f"State file read failed: {str(e)}")
        
        return None, []
    
    def interactive_recovery(self, state, pending_batches):
        """Interactive recovery selection"""
        print("\n" + "="*60)
        print(get_message_fallback("detected_incomplete_task"))
        print("="*60)
        print(get_message_fallback("task_id", id=state['session_id']))
        print(get_message_fallback("total_records_label", count=state['total_records']))
        print(get_message_fallback("screener_count_label", count=state['parallel_screeners']))
        
        completed = sum(1 for b in state['batches'] if b['status'] == 'completed')
        total = len(state['batches'])
        progress = (completed / total) * 100
        
        print(get_message_fallback("current_progress", completed=completed, total=total, percent=progress))
        
        print(f"\n{get_message_fallback('pending_batches_label')}")
        for batch in pending_batches:
            status_icon = {"pending": "⏳", "failed": "❌", "running": "🔄"}
            icon = status_icon.get(batch['status'], "❓")
            print(f"  {icon} Batch {batch['batch_id']}: Records {batch['start_record']}-{batch['end_record']} ({batch['status']})")
        
        print(f"\n{get_message_fallback('options_label')}")
        print(get_message_fallback("auto_continue_batches"))
        print(get_message_fallback("restart_all_tasks"))
        print(get_message_fallback("cancel_operation"))
        
        while True:
            choice = input(f"\n{get_message_fallback('please_select_option')}").strip()
            if choice in ['1', '2', '3']:
                return choice
            print(get_message_fallback('please_enter_valid_option'))
    
    def _ensure_config_loaded(self):
        """确保配置已加载"""
        if not self.config:
            raise Exception("Configuration file not loaded, please call load_configurations() first")
    
    def create_session_state(self, total_records, distributions):
        """创建新的会话状态"""
        self._ensure_config_loaded()
        
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        state = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'total_records': total_records,
            'parallel_screeners': self.config['parallel_settings']['parallel_screeners'],
            'input_xml_path': self.config['paths']['input_xml_path'],
            'batches': distributions,
            'temp_dir': self.temp_dir
        }
        
        # 保存状态文件
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Session state saved: {session_id}")
        return state
    
    def start_parallel_screening(self):
        """启动并行筛选"""
        try:
            print(f"\n{get_message_fallback('starting_new_parallel')}")
            
            # 1. 打印系统信息
            self.print_system_info()
            
            # 2. 验证配置
            if not self.validate_configuration():
                return False
            
            # 3. 检查现有状态
            existing_state, pending_batches = self.check_existing_state()
            
            if existing_state and pending_batches:
                choice = self.interactive_recovery(existing_state, pending_batches)
                
                if choice == '1':
                    # 继续未完成任务
                    print(get_message_fallback("auto_continue_selected"))
                    return self.resume_screening(existing_state, pending_batches)
                elif choice == '2':
                    # Restart task
                    print(get_message_fallback("restart_selected"))
                    self.cleanup_temp_files()
                elif choice == '3':
                    print(get_message_fallback("cancelled_selected"))
                    return False
            
            # 4. 开始新任务
            return self.start_new_screening()
            
        except Exception as e:
            print(f"❌ Startup failed: {str(e)}")
            traceback.print_exc()
            return False
    
    def start_new_screening(self):
        """开始新的筛选任务"""
        try:
            self._ensure_config_loaded()
            
            # 统计记录数量
            input_xml_path = self.config['paths']['input_xml_path']
            print(f"\n📖 Analyzing input file: {os.path.basename(input_xml_path)}")
            
            total_records = self.count_xml_records(input_xml_path)
            print(f"✓ Detected {total_records} records")
            
            # 计算分配方案
            parallel_screeners = self.config['parallel_settings']['parallel_screeners']
            
            # 强制检查：确保使用配置文件中的值，不允许基于记录数的自动调整
            print(get_message_fallback("debug_screener_count", count=parallel_screeners))
            if parallel_screeners != self.config['parallel_settings']['parallel_screeners']:
                print(get_message_fallback("screener_modified_warning"))
                parallel_screeners = self.config['parallel_settings']['parallel_screeners']
                print(get_message_fallback("screener_reset_success", count=parallel_screeners))
            
            distributions = RecordDistributor.calculate_distribution(total_records, parallel_screeners)
            
            # 显示分配表格
            RecordDistributor.print_distribution_table(distributions, total_records)
            
            # 确认执行
            choice = input(f"\nStart parallel screening? [y/N]: ")
            if choice.lower() != 'y':
                print(get_message_fallback("execution_cancelled_user"))
                return False
            
            # 创建会话状态
            state = self.create_session_state(total_records, distributions)
            
            # 执行分割和筛选
            return self.execute_parallel_screening(state)
            
        except Exception as e:
            print(f"❌ New task startup failed: {str(e)}")
            traceback.print_exc()
            return False
    
    def execute_parallel_screening(self, state):
        """执行并行筛选"""
        try:
            print(f"\n{get_message_fallback('parallel_execution_starting')}")
            
            # 1. 分割XML文件
            split_files = self.split_xml_file(state)
            if not split_files:
                return False
            
            # 2. 为每个批次创建配置文件
            batch_configs = self.create_batch_configs(state, split_files)
            
            # 3. Start parallel screening processes
            return self.start_parallel_processes(state, batch_configs)
            
        except Exception as e:
            print(f"❌ Parallel screening execution failed: {str(e)}")
            traceback.print_exc()
            return False
    
    def resume_screening(self, state, pending_batches):
        """恢复筛选"""
        try:
            print("\n🔄 Resuming screening processes...")
            
            # 为待处理批次创建配置
            batch_configs = []
            for batch in pending_batches:
                batch_id = batch['batch_id']
                config_path = os.path.join(self.temp_dir, f"config_batch_{batch_id}.json")
                
                if os.path.exists(config_path):
                    batch_configs.append({
                        'batch_info': batch,
                        'config_path': config_path,
                        'split_file': os.path.join(self.temp_dir, f"batch_{batch_id}.xml")
                    })
                else:
                    print(f"⚠️  Batch {batch_id} configuration file missing, recreating...")
                    # 重新创建配置文件
                    batch_config = self.create_single_batch_config(batch)
                    batch_configs.append(batch_config)
            
            # 启动恢复进程
            return self.start_parallel_processes(state, batch_configs)
            
        except Exception as e:
            print(f"❌ Resume screening failed: {str(e)}")
            traceback.print_exc()
            return False
    
    def split_xml_file(self, state):
        """分割XML文件"""
        try:
            self._ensure_config_loaded()
            
            print("\n📄 Starting XML file splitting...")
            
            input_xml_path = self.config['paths']['input_xml_path']
            splitter = XMLSplitter()
            
            # 生成分割文件名列表
            split_files = []
            for batch in state['batches']:
                batch_id = batch['batch_id']
                split_file = os.path.join(self.temp_dir, f"batch_{batch_id}.xml")
                split_files.append(split_file)
            
            # 使用自定义分割逻辑
            self.custom_split_xml(input_xml_path, state['batches'], split_files)
            
            print(f"✓ XML splitting completed, generated {len(split_files)} files")
            return split_files
            
        except Exception as e:
            print(f"❌ XML splitting failed: {str(e)}")
            return []
    
    def custom_split_xml(self, input_xml_path, batches, output_files):
        """自定义XML分割逻辑"""
        try:
            import xml.etree.ElementTree as ET
            
            # 解析原始XML
            tree = ET.parse(input_xml_path)
            root = tree.getroot()
            records = root.findall('.//record')
            
            print(f"Total records: {len(records)}")
            
            # 按批次分割
            for i, batch in enumerate(batches):
                start_idx = batch['start_record'] - 1  # 转换为0基索引
                end_idx = batch['end_record']  # end_record是包含的
                
                # 创建新的XML结构
                new_root = ET.Element(root.tag)
                
                # 复制根元素属性
                for key, value in root.attrib.items():
                    new_root.set(key, value)
                
                # 复制非records的子元素
                for child in root:
                    if child.tag != 'records':
                        new_root.append(child)
                
                # 创建records容器
                records_elem = ET.SubElement(new_root, 'records')
                
                # 添加该批次的记录
                batch_records = records[start_idx:end_idx]
                for record in batch_records:
                    records_elem.append(record)
                
                # 保存文件
                new_tree = ET.ElementTree(new_root)
                ET.indent(new_tree, space="  ", level=0)
                new_tree.write(output_files[i], encoding='utf-8', xml_declaration=True)
                
                print(f"  Batch {batch['batch_id']}: {len(batch_records)} records -> {os.path.basename(output_files[i])}")
            
        except Exception as e:
            raise Exception(f"Custom splitting failed: {str(e)}")
    
    def create_batch_configs(self, state, split_files):
        """为每个批次创建配置文件"""
        try:
            print("\n⚙️  Creating batch configuration files...")
            
            batch_configs = []
            
            for i, batch in enumerate(state['batches']):
                batch_id = batch['batch_id']
                split_file = split_files[i]
                
                # 创建批次特定的配置
                batch_config = self.create_single_batch_config(batch, split_file)
                batch_configs.append(batch_config)
                
                print(f"  ✓ Batch {batch_id} configuration created")
            
            return batch_configs
            
        except Exception as e:
            print(f"❌ Batch configuration creation failed: {str(e)}")
            return []
    
    def create_single_batch_config(self, batch, split_file=None):
        """创建单个批次的配置"""
        self._ensure_config_loaded()
        
        batch_id = batch['batch_id']
        
        if split_file is None:
            split_file = os.path.join(self.temp_dir, f"batch_{batch_id}.xml")
        
        # 复制统一配置（去除并行部分）
        if not self.config:
            raise Exception("Unified configuration not loaded")
            
        import copy
        batch_config = copy.deepcopy(self.config)
        
        # 设置为单线程模式
        batch_config['mode']['screening_mode'] = 'single'
        
        # 删除并行相关配置
        if 'parallel_settings' in batch_config:
            del batch_config['parallel_settings']
        if 'resource_management' in batch_config:
            del batch_config['resource_management']
        if 'output_settings' in batch_config:
            del batch_config['output_settings']
        
        # 修改路径配置
        batch_config['paths']['input_xml_path'] = os.path.abspath(split_file)
        batch_config['paths']['output_xml_path'] = os.path.abspath(
            os.path.join(self.temp_dir, f"batch_{batch_id}_results.xml")
        )
        
        # 设置跳过记录数为0（因为已经分割）
        batch_config['processing']['skip_records_count'] = 0
        
        # 保存批次配置文件
        config_path = os.path.join(self.temp_dir, f"config_batch_{batch_id}.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(batch_config, f, indent=2, ensure_ascii=False)
        
        return {
            'batch_info': batch,
            'config_path': config_path,
            'split_file': split_file
        }
    
    def start_parallel_processes(self, state, batch_configs):
        """启动并行筛选进程"""
        try:
            self._ensure_config_loaded()
            
            import threading
            from datetime import datetime
            
            print(f"\n🚀 Starting {len(batch_configs)} parallel screening processes...")
            
            # 更新状态文件
            for batch_config in batch_configs:
                batch_info = batch_config['batch_info']
                batch_info['status'] = 'running'
                batch_info['started_at'] = datetime.now().isoformat()
                batch_info['config_path'] = batch_config['config_path']
                batch_info['split_file'] = batch_config['split_file']
            
            self.save_state(state)
            
            # 启动线程池
            threads = []
            delay = self.config['resource_management'].get('delay_between_screeners', 2)
            
            for i, batch_config in enumerate(batch_configs):
                batch_id = batch_config['batch_info']['batch_id']
                config_path = batch_config['config_path']
                
                # 创建线程
                thread = threading.Thread(
                    target=self.run_single_batch,
                    args=(batch_id, config_path, state)
                )
                
                thread.start()
                threads.append(thread)
                
                print(f"  ✓ Batch {batch_id} thread started")
                
                # 延迟启动下一个线程
                if i < len(batch_configs) - 1:
                    time.sleep(delay)
            
            # 启动监控
            print("\n📊 Starting progress monitoring...")
            from progress_monitor import ProgressMonitor
            self.progress_monitor = ProgressMonitor(self.state_file, 5)
            self.progress_monitor.start_monitoring()
            
            # 等待所有线程完成
            print("\n⏳ Waiting for all batches to complete...")
            self.wait_for_completion_threads(threads, state)
            
            # 停止监控
            self.progress_monitor.stop_monitoring()
            
            # 合并结果
            print("\n🔄 Merging screening results...")  
            return self.merge_final_results(state)
            
        except Exception as e:
            print(f"❌ Parallel processes startup failed: {str(e)}")
            traceback.print_exc()
            return False
    
    def _execute_single_batch_screening(self, config_path):
        """直接执行单个批次的筛选逻辑"""
        try:
            from src.extractor import SystematicReviewExtractor
            from src.utils import load_config, validate_config, create_output_directory, check_file_exists
            
            # 加载批次配置
            config = load_config(config_path)
            validate_config(config)
            
            # 提取配置值
            paths = config['paths']
            processing = config.get('processing', {})
            
            # 处理研究设计配置
            if 'study_designs' in config:
                excluded_designs = config['study_designs'].get('excluded_study_designs', [])
                included_designs = config['study_designs'].get('included_study_designs', [])
            else:
                excluded_designs = config.get('excluded_study_designs', [])
                included_designs = config.get('included_study_designs', [])
            
            llm_configs = config['llm_configs']
            inclusion_criteria = config['inclusion_criteria']
            exclusion_criteria = config.get('exclusion_criteria', {})
            
            # 验证输入文件
            input_xml_path = paths['input_xml_path']
            check_file_exists(input_xml_path, "Input XML file")
            
            # 创建输出目录
            output_xml_path = paths['output_xml_path']
            create_output_directory(output_xml_path)
            
            # 初始化提取器
            extractor = SystematicReviewExtractor(
                screening_llm_configs=llm_configs['screening_llms'],
                prompt_llm_config=llm_configs.get('prompt_llm'),
                positive_prompt_path=paths.get('positive_prompt_file_path'),
                negative_prompt_path=paths.get('negative_prompt_file_path')
            )
            
            # 解析XML文件
            parsed_records, tree, root = extractor.parse_xml(input_xml_path)
            
            # 处理记录跳过
            skip_records_count = processing.get('skip_records_count', 0)
            if skip_records_count > 0:
                records_to_process = parsed_records[skip_records_count:]
            else:
                records_to_process = parsed_records
            
            # 设置研究设计过滤
            extractor.set_excluded_study_designs(excluded_designs)
            extractor.set_included_study_designs(included_designs)
            
            # 处理记录
            extractor.process_records(
                records_to_process, 
                inclusion_criteria, 
                output_xml_path, 
                tree,
                exclusion_criteria=exclusion_criteria,
                prompt_file_path=paths.get('prompt_file_path')
            )
            
            return True
            
        except Exception as e:
            print(f"批次筛选执行失败: {str(e)}")
            return False
    
    def run_single_batch(self, batch_id, config_path, state):
        """运行单个批次的筛选"""
        try:
            from datetime import datetime
            
            # 更新批次状态
            self.update_batch_status(state, batch_id, 'running', {
                'started_at': datetime.now().isoformat()
            })
            
            # 直接调用筛选逻辑
            success = self._execute_single_batch_screening(config_path)
            
            if success:
                # 成功完成
                # 找到实际生成的Excel文件
                excel_pattern = os.path.join(self.temp_dir, f"batch_{batch_id}_results*.xlsx")
                import glob
                excel_files = glob.glob(excel_pattern)
                excel_file = excel_files[0] if excel_files else os.path.join(self.temp_dir, f"batch_{batch_id}_results.xlsx")
                
                self.update_batch_status(state, batch_id, 'completed', {
                    'completed_at': datetime.now().isoformat(),
                    'output_files': {
                        'xml': os.path.join(self.temp_dir, f"batch_{batch_id}_results.xml"),
                        'excel': excel_file
                    }
                })
                print(f"✅ Batch {batch_id} completed")
            else:
                # 失败
                self.update_batch_status(state, batch_id, 'failed', {
                    'failed_at': datetime.now().isoformat(),
                    'error': 'Screening process execution failed'
                })
                print(f"❌ Batch {batch_id} failed")
                
        except Exception as e:
            # 错误
            from datetime import datetime
            self.update_batch_status(state, batch_id, 'error', {
                'failed_at': datetime.now().isoformat(),
                'error': str(e)
            })
            print(f"💥 Batch {batch_id} error: {str(e)}")
            traceback.print_exc()
    
    def update_batch_status(self, state, batch_id, status, extra_data=None):
        """更新批次状态"""
        try:
            # 加载最新状态
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    current_state = json.load(f)
            else:
                current_state = state
            
            # 更新指定批次
            for batch in current_state['batches']:
                if batch['batch_id'] == batch_id:
                    batch['status'] = status
                    if extra_data:
                        batch.update(extra_data)
                    break
            
            # 保存状态
            self.save_state(current_state)
            
        except Exception as e:
            print(f"⚠️  Failed to update batch status: {str(e)}")
    
    def wait_for_completion_threads(self, threads, state):
        """等待所有线程完成"""
        try:
            completed = 0
            total = len(threads)
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
                completed += 1
                print(f"Thread completed: {completed}/{total}")
            
            print(f"✅ All batches processing completed")
            
        except Exception as e:
            print(f"⚠️  Error waiting for threads to complete: {str(e)}")
    
    def wait_for_completion(self, processes, state):
        """等待所有进程完成"""
        try:
            completed = 0
            total = len(processes)
            
            while completed < total:
                time.sleep(5)
                
                # 检查进程状态
                for i, process in enumerate(processes):
                    if process and process.is_alive():
                        continue
                    elif process:
                        # 进程已结束
                        processes[i] = None
                        completed += 1
                        print(f"Process completed: {completed}/{total}")
            
            print(get_message_fallback("all_batches_completed_status"))
            
        except Exception as e:
            print(get_message_fallback("wait_process_error", error=str(e)))
    
    def merge_final_results(self, state=None):
        """合并最终结果"""
        try:
            self._ensure_config_loaded()
            
            # 重新加载最新的状态文件，确保获取到所有批次的最终状态
            if os.path.exists(self.state_file):
                print(get_message_fallback("reload_state_file", file=self.state_file))
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    latest_state = json.load(f)
            else:
                print(get_message_fallback("state_file_not_exist"))
                latest_state = state
            
            if not latest_state:
                raise ValueError(get_message_fallback("cannot_get_state"))
            
            # 显示批次状态统计
            completed_count = sum(1 for b in latest_state['batches'] if b['status'] == 'completed')
            total_count = len(latest_state['batches'])
            print(get_message_fallback("batch_status_stats", completed=completed_count, total=total_count))
            
            from result_merger import ResultMerger
            
            output_directory = self.config['paths'].get(
                'output_directory', 
                os.path.dirname(self.config['paths']['input_xml_path'])
            )
            
            merger = ResultMerger(output_directory)
            results = merger.merge_batch_results(latest_state, backup_individual=True)
            
            if results.get('xml_merge', {}).get('success') or results.get('excel_merge', {}).get('success'):
                print("✅ Result merge successful!")
                
                # 清理临时文件
                if self.config['parallel_settings'].get('cleanup_temp_files', True):
                    self.cleanup_temp_files()
                
                return True
            else:
                print("❌ Result merge failed")
                return False
                
        except Exception as e:
            print(f"❌ Final result merge failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_state(self, state):
        """保存状态到文件"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(get_message_fallback("save_state_failed", error=str(e)))
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
            print(get_message_fallback("temp_cleanup_success"))
        except Exception as e:
            print(get_message_fallback("temp_cleanup_error", error=str(e)))


def main():
    """主函数"""
    try:
        print("="*60)
        print(get_message_fallback("parallel_screening_system"))
        print("="*60)
        
        # 创建管理器
        manager = ParallelScreeningManager()
        
        # 启动并行筛选
        success = manager.start_parallel_screening()
        
        if success:
            print(f"\n{get_message_fallback('parallel_screening_completed')}")
            return 0
        else:
            print(f"\n{get_message_fallback('parallel_screening_failed')}")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n\n{get_message_fallback('user_interrupted')}")
        return 1
    except Exception as e:
        print(f"\n❌ System error: {str(e)}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())