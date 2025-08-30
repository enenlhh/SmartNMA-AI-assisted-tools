"""
Base extractor class with common functionality
"""
import os
import time
from abc import ABC, abstractmethod
from openai import OpenAI

class BaseExtractor(ABC):
    """Base class for data extractors"""
    
    def __init__(self, llm_config, repair_llm_config=None, debug_folder=None):
        """Initialize extractor with LLM configurations"""
        self.llm_config = llm_config
        self.repair_llm_config = repair_llm_config
        self.debug_folder = debug_folder
        self.client = OpenAI(api_key=llm_config["api_key"], base_url=llm_config["base_url"])
        
        if repair_llm_config:
            if (repair_llm_config.get("api_key") == llm_config.get("api_key") and 
                repair_llm_config.get("base_url") == llm_config.get("base_url")):
                self.repair_client = self.client
            else:
                self.repair_client = OpenAI(
                    api_key=repair_llm_config["api_key"], 
                    base_url=repair_llm_config["base_url"]
                )
        else:
            self.repair_client = None
    
    @abstractmethod
    def create_prompts(self):
        """Create extraction prompts for each data table"""
        pass
    
    @abstractmethod
    def call_llm(self, system_prompt, user_prompt, **kwargs):
        """Call LLM API with specific format requirements"""
        pass
    
    @abstractmethod
    def process_file(self, file_path, split_length=100000):
        """Process a single file and extract data"""
        pass
    
    def _save_debug_info(self, content, filename_prefix):
        """Save debug information to file"""
        if self.debug_folder:
            debug_file = os.path.join(self.debug_folder, f"{filename_prefix}_{int(time.time())}.txt")
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(content)
            return debug_file
        return None
