#!/usr/bin/env python3
"""
错误处理和重试机制模块
Error Handling and Retry Mechanism Module

提供本地化错误消息、容错机制和自动重试功能
Provides localized error messages, fault tolerance, and automatic retry functionality
"""

import time
import traceback
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple
from functools import wraps
from enum import Enum

try:
    from i18n.i18n_manager import get_message
except ImportError:
    def get_message(key, **kwargs):
        return key.format(**kwargs) if kwargs else key


class ErrorType(Enum):
    """错误类型枚举"""
    API_ERROR = "api_error"
    FILE_ERROR = "file_error"
    CONFIG_ERROR = "config_error"
    NETWORK_ERROR = "network_error"
    PARSING_ERROR = "parsing_error"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"
    UNKNOWN_ERROR = "unknown_error"


class ExtractionError(Exception):
    """数据提取专用异常类"""
    
    def __init__(self, message: str, error_type: ErrorType = ErrorType.UNKNOWN_ERROR, 
                 details: Optional[Dict[str, Any]] = None, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}
        self.original_error = original_error
        self.timestamp = time.time()


class ErrorHandler:
    """错误处理器 / Error Handler"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.error_counts = {}
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志记录"""
        log_level = self.config.get("logging", {}).get("level", "INFO")
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("extraction_errors.log", encoding="utf-8")
            ]
        )
        self.logger = logging.getLogger("DataExtraction")
    
    def handle_error(self, error: Exception, context: str = "", file_path: str = "") -> ExtractionError:
        """处理错误并返回标准化的异常"""
        # 确定错误类型
        error_type = self._classify_error(error)
        
        # 生成本地化错误消息
        localized_message = self._get_localized_error_message(error, error_type, context)
        
        # 创建详细信息
        details = {
            "context": context,
            "file_path": file_path,
            "original_type": type(error).__name__,
            "original_message": str(error)
        }
        
        # 记录错误
        self._log_error(error, error_type, context, file_path)
        
        # 更新错误计数
        self._update_error_count(error_type)
        
        return ExtractionError(localized_message, error_type, details, error)
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """分类错误类型"""
        error_name = type(error).__name__.lower()
        error_message = str(error).lower()
        
        # API相关错误
        if any(keyword in error_name for keyword in ["api", "openai", "http"]):
            return ErrorType.API_ERROR
        if any(keyword in error_message for keyword in ["api", "rate limit", "unauthorized", "forbidden"]):
            return ErrorType.API_ERROR
        
        # 网络相关错误
        if any(keyword in error_name for keyword in ["connection", "timeout", "network"]):
            return ErrorType.NETWORK_ERROR
        if any(keyword in error_message for keyword in ["connection", "timeout", "network", "unreachable"]):
            return ErrorType.NETWORK_ERROR
        
        # 文件相关错误
        if any(keyword in error_name for keyword in ["file", "io", "permission"]):
            return ErrorType.FILE_ERROR
        if any(keyword in error_message for keyword in ["file not found", "permission denied", "no such file"]):
            return ErrorType.FILE_ERROR
        
        # 解析相关错误
        if any(keyword in error_name for keyword in ["json", "parse", "decode"]):
            return ErrorType.PARSING_ERROR
        if any(keyword in error_message for keyword in ["json", "parse", "decode", "invalid format"]):
            return ErrorType.PARSING_ERROR
        
        # 验证相关错误
        if any(keyword in error_name for keyword in ["validation", "value"]):
            return ErrorType.VALIDATION_ERROR
        
        # 配置相关错误
        if any(keyword in error_message for keyword in ["config", "configuration", "missing key"]):
            return ErrorType.CONFIG_ERROR
        
        return ErrorType.UNKNOWN_ERROR
    
    def _get_localized_error_message(self, error: Exception, error_type: ErrorType, context: str) -> str:
        """获取本地化错误消息"""
        try:
            if error_type == ErrorType.API_ERROR:
                return get_message("api_error", error=str(error), context=context)
            elif error_type == ErrorType.FILE_ERROR:
                return get_message("file_error", error=str(error), context=context)
            elif error_type == ErrorType.NETWORK_ERROR:
                return get_message("network_error", error=str(error), context=context)
            elif error_type == ErrorType.PARSING_ERROR:
                return get_message("parsing_error", error=str(error), context=context)
            elif error_type == ErrorType.VALIDATION_ERROR:
                return get_message("validation_error", error=str(error), context=context)
            elif error_type == ErrorType.CONFIG_ERROR:
                return get_message("config_error", error=str(error))
            else:
                return get_message("system_error", error=str(error))
        except:
            # 如果本地化失败，返回默认英文消息
            return f"Error in {context}: {str(error)}"
    
    def _log_error(self, error: Exception, error_type: ErrorType, context: str, file_path: str):
        """记录错误日志"""
        self.logger.error(
            f"Error Type: {error_type.value} | Context: {context} | File: {file_path} | "
            f"Error: {type(error).__name__}: {str(error)}"
        )
        
        # 记录详细堆栈跟踪（调试级别）
        self.logger.debug(f"Detailed traceback:\n{traceback.format_exc()}")
    
    def _update_error_count(self, error_type: ErrorType):
        """更新错误计数"""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
    
    def get_error_summary(self) -> Dict[str, int]:
        """获取错误摘要"""
        return dict(self.error_counts)
    
    def print_error_summary(self):
        """打印错误摘要"""
        if not self.error_counts:
            try:
                from i18n.i18n_manager import get_message
                print(get_message("no_errors"))
            except ImportError:
                print("✅ No errors encountered during processing")
            return
        
        try:
            from i18n.i18n_manager import get_message
        except ImportError:
            def get_message(key, **kwargs):
                fallback_messages = {
                    "error_summary_title": "⚠️ Error Summary",
                    "total_errors": "Total Errors: {count}"
                }
                message = fallback_messages.get(key, key)
                return message.format(**kwargs) if kwargs and isinstance(message, str) else message
        
        print("\n" + "=" * 50)
        print(get_message("error_summary_title"))
        print("=" * 50)
        
        total_errors = sum(self.error_counts.values())
        print(get_message("total_errors", count=total_errors))
        
        for error_type, count in self.error_counts.items():
            print(f"  {error_type.value}: {count}")
        
        print("=" * 50)


class RetryManager:
    """重试管理器 / Retry Manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_retries = config.get("parallel_settings", {}).get("max_retries", 3)
        self.base_delay = 1.0  # 基础延迟时间（秒）
        self.max_delay = 60.0  # 最大延迟时间（秒）
        self.backoff_factor = 2.0  # 指数退避因子
    
    def with_retry(self, max_retries: Optional[int] = None):
        """重试装饰器"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self.execute_with_retry(
                    func, 
                    *args, 
                    max_retries=max_retries, 
                    **kwargs
                )
            return wrapper
        return decorator
    
    def execute_with_retry(self, func: Callable, *args, max_retries: Optional[int] = None, **kwargs) -> Any:
        """执行函数并在失败时重试"""
        retries = max_retries if max_retries is not None else self.max_retries
        last_error = None
        
        for attempt in range(retries + 1):
            try:
                return func(*args, **kwargs)
            
            except Exception as error:
                last_error = error
                
                if attempt == retries:
                    # 最后一次尝试失败
                    raise error
                
                # 检查是否应该重试
                if not self._should_retry(error):
                    raise error
                
                # 计算延迟时间
                delay = self._calculate_delay(attempt)
                
                # 打印重试信息
                func_name = getattr(func, '__name__', 'unknown_function')
                print(get_message("batch_retrying", 
                                batch=func_name, 
                                attempt=attempt + 1, 
                                max_attempts=retries + 1))
                
                # 等待后重试
                time.sleep(delay)
        
        # 如果所有重试都失败了
        if last_error:
            raise last_error
    
    def _should_retry(self, error: Exception) -> bool:
        """判断是否应该重试"""
        error_message = str(error).lower()
        
        # 不应重试的错误类型
        non_retryable_errors = [
            "authentication",
            "unauthorized", 
            "forbidden",
            "invalid_request_error",
            "file not found",
            "permission denied",
            "configuration error"
        ]
        
        for non_retryable in non_retryable_errors:
            if non_retryable in error_message:
                return False
        
        # 应该重试的错误类型
        retryable_errors = [
            "rate limit",
            "timeout",
            "connection",
            "internal server error",
            "service unavailable",
            "temporary",
            "network"
        ]
        
        for retryable in retryable_errors:
            if retryable in error_message:
                return True
        
        # 默认对未知错误进行重试
        return True
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算延迟时间（指数退避）"""
        delay = self.base_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)


def with_error_handling(error_handler: ErrorHandler, context: str = ""):
    """错误处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ExtractionError:
                # 如果已经是ExtractionError，直接重新抛出
                raise
            except Exception as error:
                # 包装其他异常
                extraction_error = error_handler.handle_error(error, context)
                raise extraction_error
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default_return=None, error_handler: Optional[ErrorHandler] = None, **kwargs) -> Tuple[Any, Optional[ExtractionError]]:
    """安全执行函数，返回结果和错误"""
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as error:
        if error_handler:
            extraction_error = error_handler.handle_error(error, func.__name__)
            return default_return, extraction_error
        else:
            return default_return, ExtractionError(str(error), original_error=error)