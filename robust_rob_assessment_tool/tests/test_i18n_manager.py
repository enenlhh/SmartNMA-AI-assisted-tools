#!/usr/bin/env python3
"""
Unit tests for LanguageManager and internationalization functionality.

Tests bilingual interface support, message formatting, language switching,
and fallback mechanisms.
"""

import unittest
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import patch, Mock
import sys
import io

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from i18n.i18n_manager import LanguageManager


class TestLanguageManager(unittest.TestCase):
    """Test the LanguageManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_i18n_config.json"
        
        # Create test message configuration
        self.test_messages = {
            "en": {
                "welcome": "Welcome to ROB Assessment Tool",
                "language_selection": "Please select your language:",
                "operation_menu": "Select operation:",
                "processing": "Processing...",
                "error": "Error occurred: {error}",
                "confirm": "Do you want to continue? (y/n): ",
                "system_detection": {
                    "detecting_resources": "Detecting system resources...",
                    "recommended_workers": "Recommended parallel workers: {workers}"
                },
                "progress_monitoring": {
                    "overall_progress": "Overall progress: {percent}% ({completed}/{total})",
                    "elapsed_time": "Elapsed time: {time}",
                    "processing_rate": "Processing rate: {rate} docs/min"
                }
            },
            "zh": {
                "welcome": "欢迎使用ROB评估工具",
                "language_selection": "请选择您的语言：",
                "operation_menu": "选择操作：",
                "processing": "处理中...",
                "error": "发生错误：{error}",
                "confirm": "是否继续？(y/n)：",
                "system_detection": {
                    "detecting_resources": "检测系统资源中...",
                    "recommended_workers": "推荐并行工作进程数：{workers}"
                },
                "progress_monitoring": {
                    "overall_progress": "总体进度：{percent}% ({completed}/{total})",
                    "elapsed_time": "已用时间：{time}",
                    "processing_rate": "处理速度：{rate} 文档/分钟"
                }
            }
        }
        
        # Save test configuration
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_messages, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization_with_existing_config(self):
        """Test initialization with existing configuration file."""
        manager = LanguageManager(str(self.config_file), default_lang="en")
        
        self.assertEqual(manager.current_lang, "en")
        self.assertEqual(manager.default_lang, "en")
        self.assertIn("en", manager.messages)
        self.assertIn("zh", manager.messages)
    
    def test_initialization_without_config(self):
        """Test initialization without existing configuration file."""
        non_existent_file = Path(self.temp_dir) / "non_existent.json"
        manager = LanguageManager(str(non_existent_file))
        
        # Should create default messages
        self.assertIn("en", manager.messages)
        self.assertIn("zh", manager.messages)
        self.assertTrue(non_existent_file.exists())
    
    def test_basic_message_retrieval(self):
        """Test basic message retrieval."""
        manager = LanguageManager(str(self.config_file))
        
        # Test English messages
        manager.set_language("en")
        welcome_msg = manager.get_message("welcome")
        self.assertEqual(welcome_msg, "Welcome to ROB Assessment Tool")
        
        # Test Chinese messages
        manager.set_language("zh")
        welcome_msg = manager.get_message("welcome")
        self.assertEqual(welcome_msg, "欢迎使用ROB评估工具")
    
    def test_nested_message_retrieval(self):
        """Test nested message retrieval using dot notation."""
        manager = LanguageManager(str(self.config_file))
        
        # Test nested English message
        manager.set_language("en")
        nested_msg = manager.get_message("system_detection.detecting_resources")
        self.assertEqual(nested_msg, "Detecting system resources...")
        
        # Test nested Chinese message
        manager.set_language("zh")
        nested_msg = manager.get_message("system_detection.detecting_resources")
        self.assertEqual(nested_msg, "检测系统资源中...")
    
    def test_message_formatting_with_parameters(self):
        """Test message formatting with parameter substitution."""
        manager = LanguageManager(str(self.config_file))
        
        # Test English formatting
        manager.set_language("en")
        error_msg = manager.get_message("error", error="Connection failed")
        self.assertEqual(error_msg, "Error occurred: Connection failed")
        
        # Test nested message with parameters
        workers_msg = manager.get_message("system_detection.recommended_workers", workers=4)
        self.assertEqual(workers_msg, "Recommended parallel workers: 4")
        
        # Test Chinese formatting
        manager.set_language("zh")
        error_msg = manager.get_message("error", error="连接失败")
        self.assertEqual(error_msg, "发生错误：连接失败")
    
    def test_fallback_mechanism(self):
        """Test fallback to default language for missing translations."""
        manager = LanguageManager(str(self.config_file), default_lang="en")
        
        # Remove a message from Chinese
        del manager.messages["zh"]["processing"]
        
        # Set to Chinese and try to get missing message
        manager.set_language("zh")
        processing_msg = manager.get_message("processing")
        
        # Should fallback to English
        self.assertEqual(processing_msg, "Processing...")
    
    def test_missing_message_handling(self):
        """Test handling of completely missing messages."""
        manager = LanguageManager(str(self.config_file))
        
        # Try to get non-existent message
        missing_msg = manager.get_message("non_existent_key")
        self.assertEqual(missing_msg, "non_existent_key")
        
        # Try to get non-existent nested message
        missing_nested = manager.get_message("non_existent.nested.key")
        self.assertEqual(missing_nested, "non_existent.nested.key")
    
    def test_language_switching(self):
        """Test runtime language switching."""
        manager = LanguageManager(str(self.config_file))
        
        # Start with English
        manager.set_language("en")
        self.assertEqual(manager.get_current_language(), "en")
        
        # Switch to Chinese
        manager.set_language("zh")
        self.assertEqual(manager.get_current_language(), "zh")
        
        # Try to switch to unsupported language
        manager.set_language("fr")
        # Should remain on default language
        self.assertEqual(manager.get_current_language(), "en")
    
    @patch('builtins.input')
    def test_interactive_language_selection(self, mock_input):
        """Test interactive language selection."""
        manager = LanguageManager(str(self.config_file))
        
        # Test selecting English
        mock_input.return_value = "1"
        selected_lang = manager.select_language()
        self.assertEqual(selected_lang, "en")
        self.assertEqual(manager.get_current_language(), "en")
        
        # Test selecting Chinese
        mock_input.return_value = "2"
        selected_lang = manager.select_language()
        self.assertEqual(selected_lang, "zh")
        self.assertEqual(manager.get_current_language(), "zh")
    
    @patch('builtins.input')
    def test_interactive_language_selection_invalid_input(self, mock_input):
        """Test interactive language selection with invalid input."""
        manager = LanguageManager(str(self.config_file))
        
        # Simulate invalid input followed by valid input
        mock_input.side_effect = ["3", "invalid", "1"]
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            selected_lang = manager.select_language()
        
        self.assertEqual(selected_lang, "en")
        # Should have shown error messages for invalid inputs
        output = mock_stdout.getvalue()
        self.assertIn("Invalid input", output)
    
    @patch('builtins.input')
    def test_keyboard_interrupt_handling(self, mock_input):
        """Test handling of keyboard interrupt during language selection."""
        manager = LanguageManager(str(self.config_file))
        
        # Simulate keyboard interrupt
        mock_input.side_effect = KeyboardInterrupt()
        
        selected_lang = manager.select_language()
        # Should return current language
        self.assertEqual(selected_lang, manager.current_lang)
    
    def test_message_existence_checking(self):
        """Test checking if messages exist."""
        manager = LanguageManager(str(self.config_file))
        
        # Test existing message
        self.assertTrue(manager.has_message("welcome"))
        self.assertTrue(manager.has_message("welcome", "en"))
        self.assertTrue(manager.has_message("welcome", "zh"))
        
        # Test nested message
        self.assertTrue(manager.has_message("system_detection.detecting_resources"))
        
        # Test non-existent message
        self.assertFalse(manager.has_message("non_existent"))
        self.assertFalse(manager.has_message("system_detection.non_existent"))
    
    def test_available_languages(self):
        """Test getting available languages."""
        manager = LanguageManager(str(self.config_file))
        
        languages = manager.get_available_languages()
        self.assertIn("en", languages)
        self.assertIn("zh", languages)
        self.assertEqual(len(languages), 2)
    
    def test_message_addition(self):
        """Test adding new messages."""
        manager = LanguageManager(str(self.config_file))
        
        # Add new message
        manager.add_message("new_message", "New English message", "新的中文消息")
        
        # Test retrieval
        manager.set_language("en")
        self.assertEqual(manager.get_message("new_message"), "New English message")
        
        manager.set_language("zh")
        self.assertEqual(manager.get_message("new_message"), "新的中文消息")
        
        # Check that it was saved to file
        self.assertTrue(manager.has_message("new_message"))
    
    def test_error_formatting_helpers(self):
        """Test error formatting helper methods."""
        manager = LanguageManager(str(self.config_file))
        
        # Test error formatting
        error_msg = manager.format_error("error", "Test error details")
        self.assertIn("Test error details", error_msg)
        
        # Test success formatting (using existing message)
        success_msg = manager.format_success("processing")
        self.assertEqual(success_msg, "Processing...")
        
        # Test warning formatting (using error message as example)
        warning_msg = manager.format_warning("error", error="Warning details")
        self.assertIn("Warning details", warning_msg)
    
    def test_complex_parameter_substitution(self):
        """Test complex parameter substitution scenarios."""
        manager = LanguageManager(str(self.config_file))
        
        # Test multiple parameters
        progress_msg = manager.get_message(
            "progress_monitoring.overall_progress",
            percent="75.5",
            completed=151,
            total=200
        )
        
        expected = "Overall progress: 75.5% (151/200)"
        self.assertEqual(progress_msg, expected)
        
        # Test with missing parameters (should not crash)
        partial_msg = manager.get_message(
            "progress_monitoring.overall_progress",
            percent="50"
        )
        # Should return the original template since not all params provided
        self.assertIn("{completed}", partial_msg)
    
    def test_unicode_handling(self):
        """Test proper Unicode handling for Chinese text."""
        manager = LanguageManager(str(self.config_file))
        
        manager.set_language("zh")
        
        # Test Chinese message retrieval
        welcome_msg = manager.get_message("welcome")
        self.assertEqual(welcome_msg, "欢迎使用ROB评估工具")
        
        # Test Chinese message with parameters
        error_msg = manager.get_message("error", error="测试错误")
        self.assertEqual(error_msg, "发生错误：测试错误")
    
    def test_config_file_corruption_handling(self):
        """Test handling of corrupted configuration files."""
        # Create corrupted JSON file
        corrupted_file = Path(self.temp_dir) / "corrupted.json"
        with open(corrupted_file, 'w') as f:
            f.write("{ invalid json content")
        
        # Should handle gracefully and create default messages
        manager = LanguageManager(str(corrupted_file))
        
        self.assertIn("en", manager.messages)
        self.assertIn("zh", manager.messages)
        # Should have basic messages
        self.assertTrue(manager.has_message("welcome"))


if __name__ == '__main__':
    unittest.main()