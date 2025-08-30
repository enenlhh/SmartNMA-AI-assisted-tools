"""
Enhanced error handling and recovery mechanisms for ROB assessment
"""

import logging
import time
import json
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Categories of errors that can occur during ROB assessment"""
    CONFIGURATION_ERROR = "configuration"
    SYSTEM_RESOURCE_ERROR = "system_resource"
    DOCUMENT_PROCESSING_ERROR = "document_processing"
    LLM_API_ERROR = "llm_api"
    PARALLEL_PROCESSING_ERROR = "parallel_processing"
    DATA_PARSING_ERROR = "data_parsing"
    FILE_IO_ERROR = "file_io"
    UNKNOWN_ERROR = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for errors"""
    LOW = "low"          # Non-critical, can continue processing
    MEDIUM = "medium"    # Important but recoverable
    HIGH = "high"        # Critical, may affect results quality
    CRITICAL = "critical"  # Fatal, must stop processing


class ROBError(Exception):
    """Custom exception class for ROB assessment errors"""
    
    def __init__(self, message: str, category: ErrorCategory, severity: ErrorSeverity, 
                 context: Optional[Dict[str, Any]] = None, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization"""
        return {
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.value,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'original_exception': str(self.original_exception) if self.original_exception else None,
            'traceback': traceback.format_exc() if self.original_exception else None
        }


class ErrorHandler:
    """Comprehensive error handling and recovery system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.retry_attempts = config.get('retry_attempts', 3)
        self.base_delay = config.get('base_delay', 2)
        self.max_delay = config.get('max_delay', 60)
        self.error_log = []
        self.recovery_strategies = self._initialize_recovery_strategies()
        
    def _initialize_recovery_strategies(self) -> Dict[ErrorCategory, Callable]:
        """Initialize recovery strategies for different error categories"""
        return {
            ErrorCategory.LLM_API_ERROR: self._handle_llm_api_error,
            ErrorCategory.DOCUMENT_PROCESSING_ERROR: self._handle_document_processing_error,
            ErrorCategory.DATA_PARSING_ERROR: self._handle_data_parsing_error,
            ErrorCategory.FILE_IO_ERROR: self._handle_file_io_error,
            ErrorCategory.SYSTEM_RESOURCE_ERROR: self._handle_system_resource_error,
            ErrorCategory.PARALLEL_PROCESSING_ERROR: self._handle_parallel_processing_error,
            ErrorCategory.CONFIGURATION_ERROR: self._handle_configuration_error,
            ErrorCategory.UNKNOWN_ERROR: self._handle_unknown_error
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main error handling entry point
        
        Args:
            error: The exception that occurred
            context: Context information about where the error occurred
            
        Returns:
            Dictionary containing error handling result and recommendations
        """
        # Categorize the error
        rob_error = self._categorize_error(error, context)
        
        # Log the error
        self._log_error(rob_error)
        
        # Attempt recovery
        recovery_result = self._attempt_recovery(rob_error)
        
        return {
            'error': rob_error.to_dict(),
            'recovery_attempted': recovery_result['attempted'],
            'recovery_successful': recovery_result['successful'],
            'recovery_action': recovery_result['action'],
            'should_retry': recovery_result['should_retry'],
            'should_continue': recovery_result['should_continue']
        }
    
    def _categorize_error(self, error: Exception, context: Dict[str, Any]) -> ROBError:
        """Categorize an error based on its type and context"""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # LLM API errors
        if any(keyword in error_str for keyword in ['api', 'rate limit', 'quota', 'authentication', 'network', 'timeout']):
            severity = ErrorSeverity.MEDIUM if 'rate limit' in error_str else ErrorSeverity.HIGH
            return ROBError(
                message=str(error),
                category=ErrorCategory.LLM_API_ERROR,
                severity=severity,
                context=context,
                original_exception=error
            )
        
        # Document processing errors
        if any(keyword in error_str for keyword in ['extract', 'parse', 'document', 'pdf', 'text']):
            return ROBError(
                message=str(error),
                category=ErrorCategory.DOCUMENT_PROCESSING_ERROR,
                severity=ErrorSeverity.MEDIUM,
                context=context,
                original_exception=error
            )
        
        # Data parsing errors
        if any(keyword in error_str for keyword in ['json', 'parse', 'format', 'schema', 'validation']):
            return ROBError(
                message=str(error),
                category=ErrorCategory.DATA_PARSING_ERROR,
                severity=ErrorSeverity.MEDIUM,
                context=context,
                original_exception=error
            )
        
        # File I/O errors
        if error_type in ['FileNotFoundError', 'PermissionError', 'IOError'] or 'file' in error_str:
            return ROBError(
                message=str(error),
                category=ErrorCategory.FILE_IO_ERROR,
                severity=ErrorSeverity.HIGH,
                context=context,
                original_exception=error
            )
        
        # System resource errors
        if any(keyword in error_str for keyword in ['memory', 'disk', 'resource', 'space']):
            return ROBError(
                message=str(error),
                category=ErrorCategory.SYSTEM_RESOURCE_ERROR,
                severity=ErrorSeverity.CRITICAL,
                context=context,
                original_exception=error
            )
        
        # Configuration errors
        if any(keyword in error_str for keyword in ['config', 'setting', 'parameter', 'key']):
            return ROBError(
                message=str(error),
                category=ErrorCategory.CONFIGURATION_ERROR,
                severity=ErrorSeverity.HIGH,
                context=context,
                original_exception=error
            )
        
        # Default to unknown error
        return ROBError(
            message=str(error),
            category=ErrorCategory.UNKNOWN_ERROR,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            original_exception=error
        )
    
    def _log_error(self, error: ROBError) -> None:
        """Log error with appropriate level"""
        self.error_log.append(error)
        
        log_message = f"[{error.category.value.upper()}] {error.message}"
        if error.context:
            log_message += f" | Context: {error.context}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def _attempt_recovery(self, error: ROBError) -> Dict[str, Any]:
        """Attempt to recover from an error"""
        recovery_strategy = self.recovery_strategies.get(error.category, self._handle_unknown_error)
        
        try:
            return recovery_strategy(error)
        except Exception as e:
            logger.error(f"Recovery strategy failed for {error.category.value}: {e}")
            return {
                'attempted': True,
                'successful': False,
                'action': 'Recovery strategy failed',
                'should_retry': False,
                'should_continue': error.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]
            }
    
    def _handle_llm_api_error(self, error: ROBError) -> Dict[str, Any]:
        """Handle LLM API errors with exponential backoff"""
        error_str = error.message.lower()
        
        if 'rate limit' in error_str:
            return {
                'attempted': True,
                'successful': False,
                'action': 'Rate limit detected, implementing exponential backoff',
                'should_retry': True,
                'should_continue': True,
                'retry_delay': min(self.base_delay * 4, self.max_delay)  # Longer delay for rate limits
            }
        elif 'quota' in error_str:
            return {
                'attempted': True,
                'successful': False,
                'action': 'API quota exceeded, cannot retry',
                'should_retry': False,
                'should_continue': False
            }
        elif any(keyword in error_str for keyword in ['network', 'timeout', 'connection']):
            return {
                'attempted': True,
                'successful': False,
                'action': 'Network error detected, will retry with backoff',
                'should_retry': True,
                'should_continue': True,
                'retry_delay': self.base_delay
            }
        else:
            return {
                'attempted': True,
                'successful': False,
                'action': 'Generic API error, will retry',
                'should_retry': True,
                'should_continue': True,
                'retry_delay': self.base_delay
            }
    
    def _handle_document_processing_error(self, error: ROBError) -> Dict[str, Any]:
        """Handle document processing errors"""
        return {
            'attempted': True,
            'successful': False,
            'action': 'Document processing failed, skipping document',
            'should_retry': False,
            'should_continue': True
        }
    
    def _handle_data_parsing_error(self, error: ROBError) -> Dict[str, Any]:
        """Handle data parsing errors"""
        return {
            'attempted': True,
            'successful': False,
            'action': 'Data parsing failed, will retry with different approach',
            'should_retry': True,
            'should_continue': True,
            'retry_delay': self.base_delay
        }
    
    def _handle_file_io_error(self, error: ROBError) -> Dict[str, Any]:
        """Handle file I/O errors"""
        error_str = error.message.lower()
        
        if 'permission' in error_str:
            return {
                'attempted': True,
                'successful': False,
                'action': 'Permission denied, cannot recover',
                'should_retry': False,
                'should_continue': False
            }
        elif 'not found' in error_str:
            return {
                'attempted': True,
                'successful': False,
                'action': 'File not found, skipping',
                'should_retry': False,
                'should_continue': True
            }
        else:
            return {
                'attempted': True,
                'successful': False,
                'action': 'File I/O error, will retry',
                'should_retry': True,
                'should_continue': True,
                'retry_delay': self.base_delay
            }
    
    def _handle_system_resource_error(self, error: ROBError) -> Dict[str, Any]:
        """Handle system resource errors"""
        return {
            'attempted': True,
            'successful': False,
            'action': 'System resource exhausted, reducing parallel workers',
            'should_retry': False,
            'should_continue': True,
            'recommendation': 'Reduce parallel_workers in configuration'
        }
    
    def _handle_parallel_processing_error(self, error: ROBError) -> Dict[str, Any]:
        """Handle parallel processing errors"""
        return {
            'attempted': True,
            'successful': False,
            'action': 'Parallel processing error, falling back to sequential',
            'should_retry': False,
            'should_continue': True,
            'recommendation': 'Consider reducing parallel workers or switching to sequential processing'
        }
    
    def _handle_configuration_error(self, error: ROBError) -> Dict[str, Any]:
        """Handle configuration errors"""
        return {
            'attempted': True,
            'successful': False,
            'action': 'Configuration error detected, cannot recover',
            'should_retry': False,
            'should_continue': False,
            'recommendation': 'Check configuration file and fix errors'
        }
    
    def _handle_unknown_error(self, error: ROBError) -> Dict[str, Any]:
        """Handle unknown errors"""
        return {
            'attempted': True,
            'successful': False,
            'action': 'Unknown error, will attempt retry',
            'should_retry': True,
            'should_continue': True,
            'retry_delay': self.base_delay
        }
    
    def execute_with_retry(self, func: Callable, context: Dict[str, Any], 
                          max_retries: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a function with retry logic and error handling
        
        Args:
            func: Function to execute
            context: Context information
            max_retries: Maximum number of retries (uses config default if None)
            
        Returns:
            Dictionary containing execution result
        """
        max_retries = max_retries or self.retry_attempts
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                result = func()
                return {
                    'success': True,
                    'result': result,
                    'attempts': attempt + 1,
                    'errors': []
                }
            except Exception as e:
                last_error = e
                error_result = self.handle_error(e, {**context, 'attempt': attempt + 1})
                
                if not error_result['should_retry'] or attempt >= max_retries:
                    return {
                        'success': False,
                        'result': None,
                        'attempts': attempt + 1,
                        'errors': [error_result],
                        'final_error': error_result
                    }
                
                # Calculate delay with exponential backoff
                delay = min(
                    error_result.get('retry_delay', self.base_delay) * (2 ** attempt),
                    self.max_delay
                )
                
                logger.info(f"Retrying in {delay} seconds (attempt {attempt + 1}/{max_retries})...")
                time.sleep(delay)
        
        # Should not reach here, but just in case
        return {
            'success': False,
            'result': None,
            'attempts': max_retries + 1,
            'errors': [],
            'final_error': {'error': {'message': str(last_error)}}
        }
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors encountered"""
        if not self.error_log:
            return {'total_errors': 0, 'categories': {}, 'severities': {}}
        
        categories = {}
        severities = {}
        
        for error in self.error_log:
            # Count by category
            cat = error.category.value
            categories[cat] = categories.get(cat, 0) + 1
            
            # Count by severity
            sev = error.severity.value
            severities[sev] = severities.get(sev, 0) + 1
        
        return {
            'total_errors': len(self.error_log),
            'categories': categories,
            'severities': severities,
            'recent_errors': [error.to_dict() for error in self.error_log[-5:]]  # Last 5 errors
        }
    
    def save_error_log(self, output_path: str) -> None:
        """Save error log to file"""
        try:
            error_data = {
                'summary': self.get_error_summary(),
                'errors': [error.to_dict() for error in self.error_log]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(error_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Error log saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save error log: {e}")