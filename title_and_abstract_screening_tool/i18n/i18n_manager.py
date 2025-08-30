#!/usr/bin/env python3
"""
国际化语言管理器
支持中英文切换的多语言界面
"""

import json
import os
from typing import Dict, Any, Optional


class LanguageManager:
    """语言管理器"""
    
    def __init__(self, config_file="i18n/i18n_config.json", default_lang="en"):
        self.config_file = config_file
        self.default_lang = default_lang
        self.current_lang = default_lang
        self.messages = {}
        self.load_languages()
    
    def load_languages(self):
        """加载语言配置"""
        try:
            # 如果是相对路径，调整为绝对路径
            if not os.path.isabs(self.config_file):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)
                self.config_file = os.path.join(project_root, self.config_file)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.messages = config.get('languages', {})
            else:
                # 如果配置文件不存在，使用英文默认消息
                self.messages = {
                    "en": {
                        "messages": {
                            "system_title": "🎯 SmartEBM Parallel Screening System - Interactive Mode",
                            "operation_completed": "✅ Operation completed!",
                            "operation_failed": "❌ Operation failed!"
                        }
                    }
                }
        except Exception as e:
            print(f"Warning: Failed to load language config: {e}")
            self.messages = {}
    
    def select_language(self) -> str:
        """交互式语言选择"""
        # 显示双语言选择提示
        print("=" * 60)
        print("🌐 Language Selection / 语言选择")
        print("=" * 60)
        
        if "en" in self.messages and "zh" in self.messages:
            print(self.messages["en"]["messages"].get("language_selection", 
                  "Please select your preferred language / 请选择您的首选语言:"))
            print()
            print(self.messages["en"]["messages"].get("language_options",
                  "1. English\n2. 中文"))
            print()
            
            while True:
                try:
                    choice = input(self.messages["en"]["messages"].get("language_prompt",
                                   "Please enter your choice [1-2] / 请输入您的选择 [1-2]: ")).strip()
                    
                    if choice == '1':
                        self.current_lang = "en"
                        return "en"
                    elif choice == '2':
                        self.current_lang = "zh"
                        return "zh"
                    else:
                        print(self.messages["en"]["messages"].get("invalid_language",
                              "Invalid option, defaulting to English / 选项无效，默认使用英文"))
                        self.current_lang = "en"
                        return "en"
                except (KeyboardInterrupt, EOFError):
                    print("\n" + self.messages["en"]["messages"].get("invalid_language",
                          "Invalid option, defaulting to English / 选项无效，默认使用英文"))
                    self.current_lang = "en"
                    return "en"
        else:
            # 如果语言配置不完整，默认使用英文
            self.current_lang = "en"
            return "en"
    
    def get_message(self, key: str, **kwargs) -> str:
        """获取本地化消息"""
        try:
            if self.current_lang in self.messages:
                message = self.messages[self.current_lang]["messages"].get(key)
                if message:
                    # 支持格式化参数
                    return message.format(**kwargs) if kwargs else message
            
            # 回退到英文
            if "en" in self.messages:
                message = self.messages["en"]["messages"].get(key)
                if message:
                    return message.format(**kwargs) if kwargs else message
            
            # 如果都找不到，返回key本身
            return key
            
        except Exception as e:
            print(f"Warning: Error getting message for key '{key}': {e}")
            return key
    
    def get_current_language(self) -> str:
        """获取当前语言"""
        return self.current_lang
    
    def set_language(self, lang_code: str):
        """设置语言"""
        if lang_code in self.messages:
            self.current_lang = lang_code
        else:
            print(f"Warning: Language '{lang_code}' not available, using {self.default_lang}")
            self.current_lang = self.default_lang


# 全局语言管理器实例
_language_manager = None


def get_language_manager() -> LanguageManager:
    """获取全局语言管理器实例"""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager


def init_language_manager(config_file="i18n/i18n_config.json", default_lang="en") -> LanguageManager:
    """初始化语言管理器"""
    global _language_manager
    _language_manager = LanguageManager(config_file, default_lang)
    return _language_manager


def get_message(key: str, **kwargs) -> str:
    """便捷函数：获取本地化消息"""
    return get_language_manager().get_message(key, **kwargs)


def select_language() -> str:
    """便捷函数：选择语言"""
    return get_language_manager().select_language()


# 导出主要函数
__all__ = [
    'LanguageManager',
    'get_language_manager', 
    'init_language_manager',
    'get_message',
    'select_language'
]