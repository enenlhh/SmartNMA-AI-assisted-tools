"""
Language management and internationalization support.

This module provides bilingual interface support with interactive language
selection, message formatting, and runtime language switching.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


class LanguageManager:
    """
    Bilingual interface support with dynamic language switching.
    
    This class manages language selection, message formatting with parameter
    substitution, and provides fallback mechanisms for missing translations.
    """
    
    def __init__(self, config_file: str, default_lang: str = "en"):
        """
        Initialize the language manager.
        
        Args:
            config_file: Path to the i18n configuration file
            default_lang: Default language code (en/zh)
        """
        self.config_file = Path(config_file)
        self.default_lang = default_lang
        self.current_lang = default_lang
        self.messages = {}
        self._load_messages()
    
    def _load_messages(self) -> None:
        """Load message configurations from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
            else:
                # Create default message structure
                self.messages = self._create_default_messages()
                self._save_messages()
        except Exception as e:
            print(f"Warning: Could not load i18n config: {e}")
            self.messages = self._create_default_messages()
    
    def _create_default_messages(self) -> Dict[str, Dict[str, Any]]:
        """Create default message structure with basic messages."""
        return {
            "en": {
                "welcome": "Welcome to ROB Assessment Tool",
                "language_selection": "Please select your language:",
                "language_english": "English",
                "language_chinese": "中文",
                "operation_menu": "Select operation:",
                "operation_start": "Start new assessment",
                "operation_resume": "Resume assessment",
                "operation_monitor": "Monitor progress",
                "operation_exit": "Exit",
                "invalid_input": "Invalid input. Please try again.",
                "processing": "Processing...",
                "completed": "Completed successfully",
                "error": "Error occurred: {error}",
                "confirm": "Do you want to continue? (y/n): ",
                "system_detection": {
                    "detecting_resources": "Detecting system resources...",
                    "recommended_workers": "Recommended parallel workers: {workers}"
                },
                "errors": {
                    "critical_error": "Critical error occurred: {error}",
                    "unexpected_error": "Unexpected error: {error}"
                }
            },
            "zh": {
                "welcome": "欢迎使用ROB评估工具",
                "language_selection": "请选择您的语言：",
                "language_english": "English",
                "language_chinese": "中文",
                "operation_menu": "选择操作：",
                "operation_start": "开始新评估",
                "operation_resume": "恢复评估",
                "operation_monitor": "监控进度",
                "operation_exit": "退出",
                "invalid_input": "输入无效，请重试。",
                "processing": "处理中...",
                "completed": "成功完成",
                "error": "发生错误：{error}",
                "confirm": "是否继续？(y/n)：",
                "system_detection": {
                    "detecting_resources": "检测系统资源中...",
                    "recommended_workers": "推荐并行工作进程数：{workers}"
                },
                "errors": {
                    "critical_error": "发生严重错误：{error}",
                    "unexpected_error": "意外错误：{error}"
                }
            }
        }
    
    def _save_messages(self) -> None:
        """Save messages to configuration file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save i18n config: {e}")
    
    def select_language(self) -> str:
        """
        Interactive language selection interface.
        
        Returns:
            str: Selected language code
        """
        print("\n" + "="*50)
        print("ROB Assessment Tool")
        print("="*50)
        
        # Show language options
        print(f"\n{self.get_message('language_selection')}")
        print(f"1. {self.get_message('language_english')}")
        print(f"2. {self.get_message('language_chinese')}")
        
        while True:
            try:
                choice = input("\nChoice (1/2): ").strip()
                if choice == "1":
                    self.set_language("en")
                    return "en"
                elif choice == "2":
                    self.set_language("zh")
                    return "zh"
                else:
                    print(self.get_message('invalid_input'))
            except KeyboardInterrupt:
                print("\nExiting...")
                return self.current_lang
            except Exception:
                print(self.get_message('invalid_input'))
    
    def get_message(self, key: str, **kwargs) -> str:
        """
        Get localized message with parameter substitution.
        Supports nested keys using dot notation (e.g., 'system_detection.cpu_cores').
        
        Args:
            key: Message key (supports dot notation for nested keys)
            **kwargs: Parameters for message formatting
            
        Returns:
            str: Localized message with parameters substituted
        """
        message = self._get_nested_message(key, self.current_lang)
        
        # Fallback to default language if not found
        if message is None:
            message = self._get_nested_message(key, self.default_lang)
        
        # Final fallback to key itself
        if message is None:
            message = key
        
        # Substitute parameters
        try:
            return message.format(**kwargs)
        except (KeyError, ValueError):
            return message
    
    def _get_nested_message(self, key: str, lang: str) -> Optional[str]:
        """
        Get message from nested dictionary structure using dot notation.
        
        Args:
            key: Message key (supports dot notation)
            lang: Language code
            
        Returns:
            str or None: Message if found, None otherwise
        """
        if lang not in self.messages:
            return None
            
        # Split key by dots for nested access
        keys = key.split('.')
        current = self.messages[lang]
        
        try:
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return None
            
            # Return only if it's a string (leaf node)
            return current if isinstance(current, str) else None
        except (KeyError, TypeError):
            return None
    
    def set_language(self, lang_code: str) -> None:
        """
        Set the current language.
        
        Args:
            lang_code: Language code (en/zh)
        """
        if lang_code in self.messages:
            self.current_lang = lang_code
        else:
            print(f"Warning: Language '{lang_code}' not supported, using '{self.default_lang}'")
            self.current_lang = self.default_lang
    
    def get_current_language(self) -> str:
        """
        Get the current language code.
        
        Returns:
            str: Current language code
        """
        return self.current_lang
    
    def add_message(self, key: str, en_text: str, zh_text: str) -> None:
        """
        Add a new message to both languages.
        
        Args:
            key: Message key
            en_text: English text
            zh_text: Chinese text
        """
        if "en" not in self.messages:
            self.messages["en"] = {}
        if "zh" not in self.messages:
            self.messages["zh"] = {}
            
        self.messages["en"][key] = en_text
        self.messages["zh"][key] = zh_text
        self._save_messages()
    
    def get_available_languages(self) -> list:
        """
        Get list of available language codes.
        
        Returns:
            list: List of available language codes
        """
        return list(self.messages.keys())
    
    def has_message(self, key: str, lang: str = None) -> bool:
        """
        Check if a message key exists.
        
        Args:
            key: Message key to check
            lang: Language code (uses current language if None)
            
        Returns:
            bool: True if message exists, False otherwise
        """
        if lang is None:
            lang = self.current_lang
            
        return self._get_nested_message(key, lang) is not None
    
    def format_error(self, error_key: str, error_details: str) -> str:
        """
        Format error message with consistent styling.
        
        Args:
            error_key: Error message key
            error_details: Error details to include
            
        Returns:
            str: Formatted error message
        """
        return self.get_message(error_key, error=error_details)
    
    def format_success(self, success_key: str, **kwargs) -> str:
        """
        Format success message with consistent styling.
        
        Args:
            success_key: Success message key
            **kwargs: Parameters for message formatting
            
        Returns:
            str: Formatted success message
        """
        return self.get_message(success_key, **kwargs)
    
    def format_warning(self, warning_key: str, **kwargs) -> str:
        """
        Format warning message with consistent styling.
        
        Args:
            warning_key: Warning message key
            **kwargs: Parameters for message formatting
            
        Returns:
            str: Formatted warning message
        """
        return self.get_message(warning_key, **kwargs)