import time
import logging
from typing import Dict, Tuple, Optional, Union
from openai import OpenAI

logger = logging.getLogger(__name__)

class LLMConfig:
    def __init__(self, name: str, api_key: str, base_url: str, model_name: str, use_streaming: bool = True):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.temperature = 0
        self.max_tokens = 8000
        self.use_streaming = use_streaming
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate_response(self, prompt: str, track_usage: bool = False) -> str:
        """Call LLM to generate regular response"""
        if track_usage:
            response_text, usage_info = self.generate_response_with_usage(prompt)
            return response_text
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Error generating response with {self.model_name}: {e}")
            # 重试逻辑
            logger.info(f"Retrying after 5 seconds...")
            time.sleep(5)
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.error(f"Retry failed with {self.model_name}: {e}")
                return ""
    
    def generate_response_with_usage(self, prompt: str) -> Tuple[str, Optional[Dict]]:
        """Call LLM to generate regular response and return usage statistics"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            usage_info = None
            if hasattr(response, 'usage') and response.usage:
                usage_info = {
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            
            return response.choices[0].message.content or "", usage_info
            
        except Exception as e:
            logger.error(f"Error generating response with {self.model_name}: {e}")
            # 重试逻辑
            logger.info(f"Retrying after 5 seconds...")
            time.sleep(5)
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                usage_info = None
                if hasattr(response, 'usage') and response.usage:
                    usage_info = {
                        'input_tokens': response.usage.prompt_tokens,
                        'output_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }
                
                return response.choices[0].message.content or "", usage_info
                
            except Exception as e:
                logger.error(f"Retry failed with {self.model_name}: {e}")
                return "", None

    def generate_structured_response(self, prompt: str, response_format=None, track_usage: bool = False) -> str:
        """Call LLM to generate structured response"""
        if track_usage:
            response_text, usage_info = self.generate_structured_response_with_usage(prompt, response_format)
            return response_text
        
        try:
            if response_format:
                # 使用结构化输出
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format=response_format
                )
                return response.choices[0].message.content or ""
            else:
                # 原有的非结构化方法
                return self.generate_response(prompt)
        except Exception as e:
            logger.error(f"Error generating structured response with {self.model_name}: {e}")
            # 重试逻辑
            logger.info(f"Retrying after 5 seconds...")
            time.sleep(5)
            try:
                if response_format:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        response_format=response_format
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                        max_tokens=self.max_tokens
                    )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.error(f"Retry failed with {self.model_name}: {e}")
                return ""
    
    def generate_structured_response_with_usage(self, prompt: str, response_format=None) -> Tuple[str, Optional[Dict]]:
        """Call LLM to generate structured response and return usage statistics"""
        try:
            if response_format:
                # 使用结构化输出
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format=response_format
                )
            else:
                # 原有的非结构化方法
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            
            usage_info = None
            if hasattr(response, 'usage') and response.usage:
                usage_info = {
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            
            return response.choices[0].message.content or "", usage_info
            
        except Exception as e:
            logger.error(f"Error generating structured response with {self.model_name}: {e}")
            # 重试逻辑
            logger.info(f"Retrying after 5 seconds...")
            time.sleep(5)
            try:
                if response_format:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        response_format=response_format
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                        max_tokens=self.max_tokens
                    )
                
                usage_info = None
                if hasattr(response, 'usage') and response.usage:
                    usage_info = {
                        'input_tokens': response.usage.prompt_tokens,
                        'output_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }
                
                return response.choices[0].message.content or "", usage_info
                
            except Exception as e:
                logger.error(f"Retry failed with {self.model_name}: {e}")
                return "", None