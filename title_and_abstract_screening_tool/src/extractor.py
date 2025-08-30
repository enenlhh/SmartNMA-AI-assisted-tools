"""
Main Extractor Module
Handles the complete screening workflow including LLM processing
"""

import openai
import xml.etree.ElementTree as ET
import os
import csv
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

from .study_design_prefilter import StudyDesignPrefilter
from .xml_parser import UniversalXMLParser

class SystematicReviewExtractor:
    def __init__(self, screening_llm_configs, prompt_llm_config=None, positive_prompt_path=None, negative_prompt_path=None):
        """Initialize extractor with LLM configurations"""
        self.screening_llm_configs = screening_llm_configs
        self.prompt_llm_config = prompt_llm_config or list(screening_llm_configs.values())[0]
        self.prompt_llm_name = "Prompt LLM" if prompt_llm_config else list(screening_llm_configs.keys())[0]
        
        # Add prompt file path configuration
        self.positive_prompt_path = positive_prompt_path
        self.negative_prompt_path = negative_prompt_path
        
        self.llm_clients = {}
        self.combined_prompt = None
        self.positive_prompt = None
        self.negative_prompt = None
        self.xml_parser = UniversalXMLParser()
        self.xml_format = None
        
        self.tokens_log = []
        self.tokens_csv_path = None
        
        # Initialize screening LLM clients
        for llm_name, config in self.screening_llm_configs.items():
            # Skip comment keys
            if llm_name.startswith('_') or not isinstance(config, dict) or 'api_key' not in config:
                continue
                
            client = openai.OpenAI(
                api_key=config['api_key'],
                base_url=config.get('base_url', 'https://vip.apiyi.com/v1')
            )
            self.llm_clients[llm_name] = client
        
        # If there's a separate prompt generation LLM, initialize it
        if prompt_llm_config and self.prompt_llm_name not in self.llm_clients:
            # Skip comment keys for prompt LLM too
            if isinstance(prompt_llm_config, dict) and 'api_key' in prompt_llm_config:
                prompt_client = openai.OpenAI(
                    api_key=prompt_llm_config['api_key'],
                    base_url=prompt_llm_config.get('base_url', 'https://vip.apiyi.com/v1')
                )
                self.llm_clients[self.prompt_llm_name] = prompt_client
        
        # Default: don't exclude any study designs
        self.excluded_study_designs = []
        self.included_study_designs = []
        
    def set_excluded_study_designs(self, excluded_designs):
        """Set study design types to exclude"""
        self.excluded_study_designs = excluded_designs
        # Lazy load prefilter
        if not hasattr(self, 'design_prefilter'):
            self.design_prefilter = StudyDesignPrefilter()
            
        # Print prefilter configuration info    
        if excluded_designs:
            print("\n=== Study Design Prefilter Configuration ===")
            print(f"Will automatically exclude the following study design types: {', '.join(excluded_designs)}")
            print(f"Will prioritize inclusion of the following study design types: {', '.join(self.included_study_designs)}")
            print("Prefiltering will be executed before LLM analysis to improve screening efficiency\n")
        else:
            print("\nNo study design prefiltering set, will perform LLM analysis on all records\n")

    def set_included_study_designs(self, included_designs):
        """Set study design types to include"""
        self.included_study_designs = included_designs if included_designs else ["randomized_controlled_trial"]
        print(f"Updated included study designs: {', '.join(self.included_study_designs)}")
        
    def parse_xml(self, xml_path):
        """Parse XML file with automatic format detection"""
        parsed_records, tree, root, xml_format = self.xml_parser.parse_xml(xml_path)
        self.xml_format = xml_format
        return parsed_records, tree, root

    def detect_processed_records(self, parsed_records):
        """检测已处理的记录，支持断点续传"""
        processed_count = 0
        
        for i, record_data in enumerate(parsed_records):
            keywords_elem = record_data['keywords_elem']
            
            # 检查是否有LLM处理结果或预筛选结果
            has_llm_result = False
            has_prefilter_result = False
            
            # 根据XML格式获取关键词
            if self.xml_format == 'zotero':
                keywords = keywords_elem.findall('.//keyword')
                keyword_texts = [kw.text for kw in keywords if kw.text]
            elif self.xml_format == 'endnote':
                keywords = keywords_elem.findall('.//keyword/style')
                keyword_texts = [kw.text for kw in keywords if kw.text]
            else:
                keyword_texts = []
            
            # 检查是否有处理结果
            for text in keyword_texts:
                if any(marker in text for marker in ["✅ INCLUDE", "❌ EXCLUDE", "⭕️ UNCLEAR"]):
                    has_llm_result = True
                    break
                elif "EXCLUDE - " in text and "(matched:" in text:
                    has_prefilter_result = True
                    break
            
            if has_llm_result or has_prefilter_result:
                processed_count = i + 1
            else:
                break
        
        return processed_count
    
    def create_combined_prompt(self, inclusion_criteria, exclusion_criteria=None, prompt_file_path=None):
        """Create combined prompt based on user-provided inclusion and exclusion criteria"""
        print("\n=== GENERATING SCREENING GUIDANCE ===")
        
        # Build base part of prompt
        base_prompt = """You are a medical research expert assisting with a systematic review. You have two tasks:

        TASK 1: Extract the following PICOS information from the title and abstract of a research article:
            1. Study design - Be specific and accurate about the MOST PRECISE type of study reported. Always extract the MOST SPECIFIC design mentioned, not general categories. For example:
            - If a study is described as a "network meta-analysis", extract that specific term, not just "meta-analysis" or "systematic review"
            - If a study is described as a "prospective cohort study", extract the complete term, not just "cohort study"
            - If a study is described as a "randomized double-blind placebo-controlled trial", extract the complete description
            - Only extract what is explicitly stated, without making assumptions
            Always extract the MOST SPECIFIC level that is explicitly reported.

            2. Participants

            3. Intervention

            4. Comparison

            5. Outcomes

            If any information is not explicitly mentioned, respond with "Not reported" for that category.

            If it is not possible to extract relevant information because a study is clearly irrelevant, respond with "Not available".
        """

        # Check and load existing prompt file or generate new prompt
        if prompt_file_path and os.path.exists(prompt_file_path):
            print(f"Detected existing prompt file: {prompt_file_path}")
            print("Will use existing file as screening prompt without regenerating.")
            with open(prompt_file_path, "r", encoding='utf-8') as f:
                screening_guidance = f.read()
        else:
            screening_guidance = self._generate_screening_guidance(inclusion_criteria, exclusion_criteria, prompt_file_path)
            if screening_guidance is None:  # If generation fails, use fallback
                return self._create_fallback_prompt(base_prompt, inclusion_criteria, exclusion_criteria)

        # Build complete Task 2 prompt with enhanced screening principles
        task2_prompt = f"""TASK 2: Based ONLY on the PICOS information you extracted, determine if the study meets the inclusion criteria.

            {screening_guidance}

            General Screening Principles:
            No Accessible Abstract: Automatically categorized as UNCLEAR.
            Abstract Available:
            - Exclude only if there is clear evidence matching at least one exclusion criterion; do not exclude merely because not all inclusion criteria are explicitly met, as abstracts may lack full details.
            - If the abstract is obviously unrelated to the target research question, exclude directly without marking UNCLEAR.
            - Include if the abstract meets key inclusion criteria or shows potential relevance, even with limited information.
            - Always perform a detailed comparison of the extracted INTERVENTION against the criteria before finalizing.
            - When in doubt due to ambiguity or incompleteness, mark UNCLEAR.

            Format your response EXACTLY as follows:
            ===PICOS EXTRACTION===
            Study design: [extracted information]
            Participants: [extracted information]
            Intervention: [extracted information]
            Comparison: [extracted information]
            Outcomes: [extracted information]

            ===INCLUSION ASSESSMENT===
            Decision: [INCLUDE/EXCLUDE/UNCLEAR]
            Explanation: [brief rationale for your decision IN ONE SENTENCE, 50 WORDS MAXIMUM, focus on the PRIMARY reason only]
            """
                
        complete_prompt = base_prompt + task2_prompt
        final_template_tokens = len(complete_prompt) // 4
        print(f"\nEstimated tokens for final prompt template: ~{final_template_tokens} tokens")
        print("\nPrompt template ready. Proceeding to process articles.")
        return complete_prompt

    def _generate_screening_guidance(self, inclusion_criteria, exclusion_criteria, prompt_file_path):
        """Generate new screening guidance with transformations for indirect information"""
        print("Processing criteria and generating concise screening guidance...")
        
        # Prepare criteria text
        print("\nPreparing criteria for prompt generation:")
        inclusion_details = {}
        exclusion_details = {}
        
        for key, value in inclusion_criteria.items():
            if value and value not in ["No limit", "None"]:
                inclusion_details[key] = value
                print(f"- Include - {key}: {value}")
        
        if exclusion_criteria:
            for key, value in exclusion_criteria.items():
                if value and value not in ["No limit", "None"]:
                    exclusion_details[key] = value
                    print(f"- Exclude - {key}: {value}")

        screening_prompt = f"""As an evidence-based medicine expert, create CLEAR and DIRECT screening guidance based on these criteria:
            INCLUSION CRITERIA:
            {", ".join(f"{k}: {v}" for k, v in inclusion_details.items())}
            {"EXCLUSION CRITERIA:" if exclusion_details else ""}
            {", ".join(f"{k}: {v}" for k, v in exclusion_details.items()) if exclusion_details else ""}
        
            Create a CONCISE guidance document that simply states what should be included or excluded for each criterion. Your guidance should:
            1. Only include sections for criteria with specific limits (skip "No limit" criteria)
            2. Directly state what is acceptable and what is not for each criterion
            3. Be brief, clear, and avoid unnecessary explanations
            4. Trust the screener's understanding of research concepts
            5. Convert any indirect, implicit, or ambiguous information in the criteria into direct, explicit statements that are easy to understand and apply during screening (e.g., rephrase vague terms into specific, actionable conditions without adding new information)
            FORMAT YOUR GUIDANCE LIKE THIS:
            STUDY DESIGN:
            "Only consider studies that are [specified design types]. Any research that is [specified design] or includes [specified design] as part of a mixed design meets the STUDY DESIGN inclusion criteria. Exclude [excluded designs]."
            PARTICIPANTS:
            "Only consider studies involving [specified population]. Research with populations that have [specific characteristics] should be included. Exclude [excluded populations]."
            INTERVENTION:
            "Only consider studies that include [specified intervention]. The specific implementation of [intervention details] is not restricted. Exclude [excluded interventions]."
            COMPARISON:
            "Only consider studies with [specified comparison]. Exclude [excluded comparisons]."
            OUTCOMES:
            "Only consider studies reporting [specified outcomes]. These can be primary or secondary outcomes. Exclude studies that only report [excluded outcomes]."
            GENERAL PRINCIPLES:
            "Exclude only if there is clear, explicit evidence matching at least one exclusion criterion. Do not exclude based solely on incomplete inclusion information, as abstracts may not cover all details. If the study is obviously unrelated to the target research, exclude directly. Always perform a detailed check of how the extracted INTERVENTION matches the criteria before finalizing the decision. When information is incomplete or ambiguous, respond UNCLEAR. Conceptual matching takes precedence over exact terminology."
            IMPORTANT:
            - Keep statements simple and direct
            - Do not explain how to identify study types - simply state what should be included
            - Do not list synonyms or alternative terms
            - Trust the screener's knowledge of research methodology and medical concepts
            - Preserve the direct, simple style shown in the examples
            Your guidance will help determine which studies to include or exclude during initial screening.
            """

        # Estimate prompt tokens
        prompt_tokens_estimate = len(screening_prompt) // 4
        print(f"Estimated tokens for guidance generation prompt: ~{prompt_tokens_estimate} tokens")
        
        max_retries = 5
        for retry_count in range(max_retries):
            try:
                print("Sending request to LLM API...")
                client = self.llm_clients[self.prompt_llm_name]
                config = self.prompt_llm_config if self.prompt_llm_name == "Prompt LLM" else self.screening_llm_configs[self.prompt_llm_name]
                
                response = client.chat.completions.create(
                    model=config['model'],
                    messages=[
                        {"role": "system", "content": "You are an evidence-based medicine expert specializing in systematic reviews."},
                        {"role": "user", "content": screening_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=3000
                )
                
                screening_guidance = response.choices[0].message.content
                
                try:
                    prompt_tokens = response.usage.prompt_tokens
                    completion_tokens = response.usage.completion_tokens
                    total_tokens = response.usage.total_tokens
                    print(f"Actual tokens used: {total_tokens} (Prompt: {prompt_tokens}, Completion: {completion_tokens})")
                except AttributeError:
                    guidance_tokens_estimate = len(screening_guidance) // 4
                    print(f"Estimated tokens for generated guidance: ~{guidance_tokens_estimate} tokens")
                
                print("Screening guidance successfully generated!")
                if prompt_file_path:
                    with open(prompt_file_path, "w", encoding='utf-8') as f:
                        f.write(screening_guidance)
                    
                    print(f"\n" + "="*60)
                    print("🎉 SCREENING GUIDANCE GENERATED")
                    print("="*60)
                    print("The screening guidance has been successfully generated!")
                    print(f"\n📁 Generated File:")
                    print(f"   • Screening Guidance: {prompt_file_path}")
                    
                    print("\n📋 Next Steps:")
                    print("1. Please review and adjust the generated screening guidance as needed")
                    print("2. The guidance contains your inclusion/exclusion criteria in structured format")
                    print("3. After reviewing, restart the program to begin screening process")
                    
                    print(f"\n🔄 To restart: python run.py")
                    print("="*60)
                    
                    # 直接退出程序
                    import sys
                    sys.exit(0)
                else:
                    return screening_guidance
                
            except Exception as e:
                if retry_count < max_retries - 1:
                    print(f"Error generating guidance, attempt {retry_count + 1}/{max_retries}: {str(e)}. Retrying...")
                    time.sleep(2 ** retry_count)
                else:
                    print(f"\nERROR: Failed to generate screening guidance after {max_retries} attempts: {str(e)}")
                    return None

    def _create_fallback_prompt(self, base_prompt, inclusion_criteria, exclusion_criteria):
        """Create fallback prompt"""
        print("Falling back to basic criteria format...")
        
        inclusion_details = {k: v for k, v in inclusion_criteria.items() if v and v not in ["No limit", "None"]}
        exclusion_details = {k: v for k, v in exclusion_criteria.items() if v and v not in ["No limit", "None"]} if exclusion_criteria else {}
        
        # Simple fallback solution
        fallback_guidance = "### Screening Guidance\n\n"
        fallback_guidance += "**Inclusion Criteria:**\n"
        for key, value in inclusion_details.items():
            fallback_guidance += f"- {key}: {value}\n  * Consider related terms and concepts\n  * Be inclusive when information is limited\n\n"
        
        if exclusion_details:
            fallback_guidance += "\n**Exclusion Criteria:**\n"
            for key, value in exclusion_details.items():
                fallback_guidance += f"- {key}: {value}\n  * Exclude only when clearly meeting this criterion\n\n"
        
        fallback_guidance += "\n**General Guidance:**\n"
        fallback_guidance += "- Prioritize sensitivity over specificity at this stage\n"
        fallback_guidance += "- When in doubt, include for full-text review\n"
        fallback_guidance += "- Focus on conceptual matching rather than exact terminology\n"
        
        # Add to Task 2 prompt
        task2_prompt = f"""TASK 2: Based ONLY on the PICOS information you extracted, determine if the study meets the inclusion criteria.

    {fallback_guidance}

    Format your response EXACTLY as follows:
    ===PICOS EXTRACTION===
    Study design: [extracted information]
    Participants: [extracted information]
    Intervention: [extracted information]
    Comparison: [extracted information]
    Outcomes: [extracted information]

    ===INCLUSION ASSESSMENT===
    Decision: [INCLUDE/EXCLUDE/UNCLEAR]
    Explanation: [brief rationale for your decision]
    """
        
        complete_prompt = base_prompt + task2_prompt
        fallback_template_tokens = len(complete_prompt) // 4
        print(f"\nEstimated tokens for fallback prompt template: ~{fallback_template_tokens} tokens")
        print("Using fallback screening guidance due to LLM error.")
        return complete_prompt

    def load_or_generate_positive_negative_prompts(self, normal_prompt):
        """Load or generate positive and negative versions of prompt"""
        print("\n=== Checking Positive and Negative Prompt Files ===")
        
        # Check if files exist
        positive_exists = self.positive_prompt_path and os.path.exists(self.positive_prompt_path)
        negative_exists = self.negative_prompt_path and os.path.exists(self.negative_prompt_path)
        
        if positive_exists and negative_exists:
            print(f"Detected existing Positive prompt file: {self.positive_prompt_path}")
            print(f"Detected existing Negative prompt file: {self.negative_prompt_path}")
            print("Will use existing files without regenerating.")
            
            # Load from files directly without validation
            if not self.positive_prompt_path or not self.negative_prompt_path:
                raise ValueError("Prompt file paths are not properly configured")
                
            with open(self.positive_prompt_path, "r", encoding='utf-8') as f:
                positive_prompt = f.read()
            with open(self.negative_prompt_path, "r", encoding='utf-8') as f:
                negative_prompt = f.read()
                
            print("✓ Successfully loaded existing Positive and Negative prompts")
            return positive_prompt, negative_prompt
        
        else:
            print("Complete Positive and Negative prompt files not found, generating new versions...")
            return self.generate_positive_negative_prompts(normal_prompt)


    def generate_positive_negative_prompts(self, normal_prompt):
        """Generate positive and negative versions of prompt based on normal prompt"""
        print("Generating Positive and Negative prompt versions...")
        
        # 先检查是否已有有效的提示文件
        positive_content = None
        negative_content = None
        
        if (self.positive_prompt_path and os.path.exists(self.positive_prompt_path) and 
            self.negative_prompt_path and os.path.exists(self.negative_prompt_path)):
            
            # 确保路径不为None后再使用
            if self.positive_prompt_path is not None and self.negative_prompt_path is not None:
                try:
                    with open(self.positive_prompt_path, "r", encoding='utf-8') as f:
                        positive_content = f.read().strip()
                    with open(self.negative_prompt_path, "r", encoding='utf-8') as f:
                        negative_content = f.read().strip()
                except Exception as e:
                    print(f"⚠️ Error reading prompt files: {e}")
                    positive_content = None
                    negative_content = None
            else:
                print("⚠️ Prompt file paths are not configured properly")
                
        # 检查文件是否包含实际内容（不是占位符）
        if (positive_content and negative_content and 
            "[reordered prompt" not in positive_content and 
            "[reordered prompt" not in negative_content and
            "[restructured prompt" not in positive_content and 
            "[restructured prompt" not in negative_content and
            len(positive_content) > 200 and len(negative_content) > 200):
            print("✓ Found valid existing prompt files")
            return positive_content, negative_content
        # 如果文件不存在或无效，生成新的提示
        prompt_generation_instruction = f"""
        Based on the following original prompt, create TWO versions with subtly different presentation styles while preserving ALL information content exactly:
        ORIGINAL PROMPT:
        {normal_prompt}
        Create these two versions:
        1. VERSION A: Restructure with a comprehensive evaluation approach
        - Present criteria in a thorough, methodical manner
        - Use neutral language that emphasizes careful consideration of all aspects
        - Structure information to encourage complete assessment
        2. VERSION B: Restructure with a precision-focused approach  
        - Present criteria with emphasis on specificity and accuracy
        - Use precise language that emphasizes meeting exact requirements
        - Structure information to encourage detailed verification
        CRITICAL REQUIREMENTS:
        - Do NOT add, remove, or modify ANY factual content or criteria
        - Do NOT change any specific requirements or thresholds
        - Do NOT use obvious directional language like "lean toward inclusion/exclusion"
        - ONLY change the presentation flow and subtle linguistic framing
        - Preserve all PICOS extraction instructions exactly
        - Maintain the same response format requirements
        - Keep all technical details identical
        - Use neutral, professional tone throughout
        - Only output content directly. Do not output any additional text, such as starting or ending lines.
        The two versions should feel naturally different in approach but not obviously biased toward any particular outcome.
        Please format your response as:
        ===VERSION A===
        [restructured prompt with comprehensive evaluation approach]
        ===VERSION B===
        [restructured prompt with precision-focused approach]
        """
                
        max_retries = 3
        for retry_count in range(max_retries):
            try:
                client = self.llm_clients[self.prompt_llm_name]
                config = self.prompt_llm_config if self.prompt_llm_name == "Prompt LLM" else self.screening_llm_configs[self.prompt_llm_name]
                
                response = client.chat.completions.create(
                    model=config['model'],
                    messages=[
                        {"role": "system", "content": "You are an expert at restructuring content with different psychological framing while preserving all factual information exactly."},
                        {"role": "user", "content": prompt_generation_instruction}
                    ],
                    temperature=0.1,
                    max_tokens=5000
                )
                
                result = response.choices[0].message.content
                
                # 改进的解析逻辑
                if "===VERSION A===" in result and "===VERSION B===" in result:
                    try:
                        # 分割响应
                        parts = result.split("===VERSION B===")
                        if len(parts) >= 2:
                            positive_prompt = parts[0].replace("===VERSION A===", "").strip()
                            negative_prompt = parts[1].strip()
                            
                            # 验证内容不为空且不是占位符
                            if (positive_prompt and negative_prompt and 
                                len(positive_prompt) > 200 and len(negative_prompt) > 200 and
                                "[reordered prompt" not in positive_prompt and 
                                "[restructured prompt" not in negative_prompt):
                                
                                # 保存到文件
                                if self.positive_prompt_path:
                                    with open(self.positive_prompt_path, "w", encoding='utf-8') as f:
                                        f.write(positive_prompt)
                                    print(f"✓ Positive prompt (inclusion-focused) saved to: {self.positive_prompt_path}")
                                
                                if self.negative_prompt_path:
                                    with open(self.negative_prompt_path, "w", encoding='utf-8') as f:
                                        f.write(negative_prompt)
                                    print(f"✓ Negative prompt (exclusion-focused) saved to: {self.negative_prompt_path}")
                                
                                print("✓ Successfully generated and saved Positive and Negative prompt versions")
                                
                                # 直接退出程序，提示用户检查文件
                                print(f"\n" + "="*60)
                                print("🎉 PROMPT GENERATION COMPLETED")
                                print("="*60)
                                print("Positive and Negative prompt variants have been successfully generated!")
                                print("\n📁 Generated Files:")
                                if self.positive_prompt_path:
                                    print(f"   • Positive Prompt (Inclusion-focused): {self.positive_prompt_path}")
                                if self.negative_prompt_path:
                                    print(f"   • Negative Prompt (Exclusion-focused): {self.negative_prompt_path}")
                                
                                print("\n📋 Next Steps:")
                                print("1. Please review and adjust the generated prompt files as needed")
                                print("2. The prompts use different psychological framing while preserving all content")
                                print("3. After reviewing, restart the program to begin screening process")
                                print("4. The system will automatically use the generated prompt variants")
                                
                                print(f"\n🔄 To restart: python run.py")
                                print("="*60)
                                
                                # 直接退出程序
                                import sys
                                sys.exit(0)
                            else:
                                raise ValueError("Generated prompts are too short, contain placeholders, or don't have the expected structure")
                        else:
                            raise ValueError("Could not split response properly")
                    except Exception as parse_error:
                        print(f"Parsing error: {parse_error}")
                        raise ValueError(f"Failed to parse generated prompt versions: {parse_error}")
                else:
                    raise ValueError("Response does not contain expected section markers (===VERSION A=== and ===VERSION B===)")
                    
            except Exception as e:
                if retry_count < max_retries - 1:
                    print(f"Failed to generate prompt variants, retry {retry_count + 1}/{max_retries}: {str(e)}")
                    time.sleep(2)
                else:
                    print(f"Failed to generate prompt variants after {max_retries} attempts: {str(e)}")
                    print("Using original prompt for both positive and negative versions")
                    
                    # 使用原始提示作为回退
                    if self.positive_prompt_path:
                        with open(self.positive_prompt_path, "w", encoding='utf-8') as f:
                            f.write(normal_prompt)
                        print(f"✓ Fallback: Original prompt saved as positive prompt to: {self.positive_prompt_path}")
                    
                    if self.negative_prompt_path:
                        with open(self.negative_prompt_path, "w", encoding='utf-8') as f:
                            f.write(normal_prompt)
                        print(f"✓ Fallback: Original prompt saved as negative prompt to: {self.negative_prompt_path}")
                    
                    # 回退情况也直接退出
                    print(f"\n" + "="*60)
                    print("⚠️  PROMPT GENERATION FALLBACK")
                    print("="*60)
                    print("Due to generation issues, the original prompt has been saved to both files.")
                    print("\n📁 Fallback Files:")
                    if self.positive_prompt_path:
                        print(f"   • Positive Prompt: {self.positive_prompt_path}")
                    if self.negative_prompt_path:
                        print(f"   • Negative Prompt: {self.negative_prompt_path}")
                    
                    print("\n📋 Next Steps:")
                    print("1. Please manually edit the prompt files to create different variants")
                    print("2. Adjust the psychological framing as needed")
                    print("3. After editing, restart the program to begin screening process")
                    
                    print(f"\n🔄 To restart: python run.py")
                    print("="*60)
                    
                    import sys
                    sys.exit(0)
        
        return normal_prompt, normal_prompt


    def process_study_sequential(self, title, abstract, inclusion_criteria):
        """Sequential processing of one study: LLM A processes first, then LLM B uses appropriate prompt based on result"""
        print("  Starting sequential processing of one study...")
        
        # Ensure we have the combined prompt
        if self.combined_prompt is None:
            self.combined_prompt = self.create_combined_prompt(inclusion_criteria)
        
        # Load or generate positive and negative versions of prompt
        if self.positive_prompt is None or self.negative_prompt is None:
            self.positive_prompt, self.negative_prompt = self.load_or_generate_positive_negative_prompts(self.combined_prompt)
        
        # Get LLM names list (filter out comment keys)
        llm_names = [name for name in self.screening_llm_configs.keys() 
                    if not name.startswith('_') and isinstance(self.screening_llm_configs[name], dict) 
                    and 'api_key' in self.screening_llm_configs[name]]
        if len(llm_names) < 2:
            raise ValueError("At least 2 LLM instances required for sequential processing")
        
        llm_a_name = llm_names[0]  # First LLM
        llm_b_name = llm_names[1]  # Second LLM
        
        results = {}
        
        # Step 1: LLM A processes with normal prompt
        print(f"  Step 1: {llm_a_name} processing with normal prompt...")
        try:
            picos_a, inclusion_a = self.process_study_with_prompt(
                llm_a_name, title, abstract, self.combined_prompt
            )
            results[llm_a_name] = {
                'picos': picos_a,
                'inclusion': inclusion_a
            }
            print(f"  {llm_a_name} completed: {inclusion_a}")
            
            # Determine LLM A's decision
            if "✅ INCLUDE" in inclusion_a:
                llm_a_decision = "INCLUDE"
            elif "❌ EXCLUDE" in inclusion_a:
                llm_a_decision = "EXCLUDE"
            else:
                llm_a_decision = "UNCLEAR"
            
            # Step 2: Select prompt for LLM B based on LLM A's result
            if llm_a_decision == "INCLUDE":
                selected_prompt = self.negative_prompt
                prompt_type = "negative prompt (exclusion criteria prioritized)"
                print(f"  LLM A result is INCLUDE, LLM B will use {prompt_type}")
            elif llm_a_decision == "EXCLUDE":
                selected_prompt = self.positive_prompt  
                prompt_type = "positive prompt (inclusion criteria prioritized)"
                print(f"  LLM A result is EXCLUDE, LLM B will use {prompt_type}")
            else:
                # Use positive prompt for UNCLEAR cases
                selected_prompt = self.positive_prompt
                prompt_type = "positive prompt (inclusion criteria prioritized, because LLM A result is unclear)"
                print(f"  LLM A result is UNCLEAR, LLM B will use {prompt_type}")
            
            # Step 3: LLM B processes with selected prompt
            print(f"  Step 2: {llm_b_name} processing with {prompt_type}...")
            picos_b, inclusion_b = self.process_study_with_prompt(
                llm_b_name, title, abstract, selected_prompt
            )
            results[llm_b_name] = {
                'picos': picos_b,
                'inclusion': inclusion_b,
                'prompt_type': prompt_type
            }
            print(f"  {llm_b_name} completed: {inclusion_b}")
            
        except Exception as e:
            print(f"  Sequential processing error: {str(e)}")
            # If error occurs, return error information
            error_result = {
                'picos': {
                    "S": f"Error: {str(e)}",
                    "P": f"Error: {str(e)}",
                    "I": f"Error: {str(e)}",
                    "C": f"Error: {str(e)}",
                    "O": f"Error: {str(e)}"
                },
                'inclusion': f"⭕️ UNCLEAR (Error: {str(e)})"
            }
            results[llm_a_name] = error_result
            results[llm_b_name] = error_result
        
        print(f"  Sequential processing completed")
        return results

    def process_study_with_prompt(self, llm_name, title, abstract, prompt):
        """Process single study with specified prompt"""
        client = self.llm_clients[llm_name]
        config = self.screening_llm_configs[llm_name]
        
        system_prompt = prompt
        user_prompt = f"Title: {title}\n\nAbstract: {abstract}"
        
        max_retries = 10
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = client.chat.completions.create(
                    model=config['model'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.0,
                    max_tokens=3000,
                    timeout=240
                )
                
                result_text = response.choices[0].message.content
                
                # Record token consumption
                try:
                    prompt_tokens = response.usage.prompt_tokens
                    completion_tokens = response.usage.completion_tokens
                    total_tokens = response.usage.total_tokens
                    
                    self.tokens_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'operation': 'study_screening',
                        'llm_name': llm_name,
                        'model': config['model'],
                        'prompt_tokens': prompt_tokens,
                        'completion_tokens': completion_tokens,
                        'total_tokens': total_tokens,
                        'title': title[:100] + '...' if len(title) > 100 else title,
                        'abstract': abstract[:200] + '...' if len(abstract) > 200 else abstract
                    })
                except AttributeError:
                    estimated_prompt_tokens = len(system_prompt + user_prompt) // 4
                    estimated_completion_tokens = len(result_text) // 4
                    estimated_total_tokens = estimated_prompt_tokens + estimated_completion_tokens
                    
                    self.tokens_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'operation': 'study_screening',
                        'llm_name': llm_name,
                        'model': config['model'],
                        'prompt_tokens': estimated_prompt_tokens,
                        'completion_tokens': estimated_completion_tokens,
                        'total_tokens': estimated_total_tokens,
                        'title': title[:100] + '...' if len(title) > 100 else title,
                        'abstract': abstract[:200] + '...' if len(abstract) > 200 else abstract
                    })
                
                # Parse results
                picos_section = ""
                decision_section = ""
                
                if "===PICOS EXTRACTION===" in result_text and "===INCLUSION ASSESSMENT===" in result_text:
                    sections = result_text.split("===INCLUSION ASSESSMENT===")
                    picos_section = sections[0].replace("===PICOS EXTRACTION===", "").strip()
                    decision_section = sections[1].strip()
                else:
                    picos_section = result_text
                    if "Decision:" in result_text:
                        decision_idx = result_text.find("Decision:")
                        decision_section = result_text[decision_idx:].strip()
                
                # Parse PICOS information
                picos = {}
                all_not_reported = True
                
                for line in picos_section.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith("Study design:"):
                        picos["S"] = line.split(":", 1)[1].strip()
                        if "not reported" not in picos["S"].lower():
                            all_not_reported = False
                    elif line.startswith("Participants:"):
                        picos["P"] = line.split(":", 1)[1].strip()
                        if "not reported" not in picos["P"].lower():
                            all_not_reported = False
                    elif line.startswith("Intervention:"):
                        picos["I"] = line.split(":", 1)[1].strip()
                        if "not reported" not in picos["I"].lower():
                            all_not_reported = False
                    elif line.startswith("Comparison:"):
                        picos["C"] = line.split(":", 1)[1].strip()
                        if "not reported" not in picos["C"].lower():
                            all_not_reported = False
                    elif line.startswith("Outcomes:"):
                        picos["O"] = line.split(":", 1)[1].strip()
                        if "not reported" not in picos["O"].lower():
                            all_not_reported = False
                
                # Parse inclusion decision and explanation
                inclusion_result = "⭕️ UNCLEAR"
                explanation = ""
                short_reason = ""
                
                if "Explanation:" in decision_section:
                    parts = decision_section.split("Explanation:", 1)
                    explanation = parts[1].strip()
                    short_reason = explanation[:300]
                    if "." in short_reason:
                        short_reason = short_reason.split(".", 1)[0] + "."
                
                if "Decision:" in decision_section:
                    decision_line = decision_section.split("\\n")[0]
                    decision_value = decision_line.split("Decision:", 1)[1].strip()
                else:
                    decision_value = "UNCLEAR"
                    
                if all_not_reported:
                    inclusion_result = "⭕️ UNCLEAR (insufficient information)"
                else:
                    if "INCLUDE" in decision_value.upper():
                        inclusion_result = "✅ INCLUDE"
                    elif "EXCLUDE" in decision_value.upper():
                        inclusion_result = f"❌ EXCLUDE - {short_reason}"
                    else:
                        inclusion_result = f"⭕️ UNCLEAR - {short_reason}"
                
                return picos, inclusion_result
                
            except Exception as e:
                if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                    retry_count += 1
                    print(f"Timeout error with {llm_name}, attempt {retry_count}/{max_retries}: Response time exceeded 4 minutes. Retrying...")
                    if retry_count >= max_retries:
                        print(f"Failed after {max_retries} timeout attempts with {llm_name}")
                        return {
                            "S": "Error: Response timeout after multiple attempts",
                            "P": "Error: Response timeout after multiple attempts", 
                            "I": "Error: Response timeout after multiple attempts",
                            "C": "Error: Response timeout after multiple attempts",
                            "O": "Error: Response timeout after multiple attempts"
                        }, "⭕️ UNCLEAR (Response timeout after multiple attempts)"
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"Error with {llm_name}, attempt {retry_count}/{max_retries}: {str(e)}. Retrying...")
                        time.sleep(2 ** retry_count)
                    else:
                        print(f"Failed after {max_retries} attempts with {llm_name}: {str(e)}")
                        return {
                            "S": "Error in extraction after multiple retries",
                            "P": "Error in extraction after multiple retries",
                            "I": "Error in extraction after multiple retries", 
                            "C": "Error in extraction after multiple retries",
                            "O": "Error in extraction after multiple retries"
                        }, "⭕️ UNCLEAR (Error in processing after multiple retries)"

    def clear_keywords(self, keywords_elem):
        """Clear all existing keywords"""
        # Remove all keyword child elements
        for keyword in list(keywords_elem):
            keywords_elem.remove(keyword)
        return keywords_elem
    def add_keyword_to_record(self, keywords_elem, text):
        """Add keyword tag to record, adjust based on XML format"""
        keyword_elem = ET.SubElement(keywords_elem, 'keyword')
        
        if self.xml_format == 'endnote':
            # EndNote format needs style tag
            style_elem = ET.SubElement(keyword_elem, 'style')
            style_elem.set('face', 'normal')
            style_elem.set('font', 'default')
            style_elem.set('size', '100%')
            style_elem.text = text
        else:
            # Zotero format sets text directly
            keyword_elem.text = text
        
        return keyword_elem
    def _save_current_results(self, tree, output_path, processed_count, total_records, reason=""):
        """保存当前结果并生成Excel报告"""
        # 保存XML文件
        final_output_path = output_path
        if reason:
            # 如果是中断或错误，在文件名中标记
            base_name = os.path.splitext(output_path)[0]
            ext = os.path.splitext(output_path)[1]
            final_output_path = f"{base_name}_{reason}_{processed_count}_of_{total_records}{ext}"
        
        self.save_xml(tree, final_output_path)
        print(f"✓ XML results saved to: {final_output_path}")
        
        # 生成增强Excel报告
        try:
            excel_path = self._generate_enhanced_excel_report(final_output_path)
            print(f"✓ Enhanced Excel report saved to: {excel_path}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to generate Excel report: {str(e)}")
            excel_path = None
        
        # 保存Token统计
        try:
            self.save_tokens_to_csv(final_output_path)
        except Exception as e:
            print(f"⚠️ Warning: Failed to save token statistics: {str(e)}")
        
        return final_output_path, excel_path
        
    def process_records(self, parsed_records, inclusion_criteria, output_path, tree, exclusion_criteria=None, prompt_file_path=None):
        """Process all records, extract PICOS and evaluate inclusion, supports interruption saving and resume from breakpoint"""
        if self.combined_prompt is None:
            self.combined_prompt = self.create_combined_prompt(inclusion_criteria, exclusion_criteria, prompt_file_path)
        
        # Ensure study design prefilter is set
        if not hasattr(self, 'design_prefilter'):
            self.design_prefilter = StudyDesignPrefilter()
        
        total_records = len(parsed_records)
        
        # 检测已处理的记录数量（断点续传）
        already_processed = self.detect_processed_records(parsed_records)
        if already_processed > 0:
            print(f"\n=== RESUME FROM BREAKPOINT ===")
            print(f"Detected {already_processed} already processed records")
            print(f"Will resume from record {already_processed + 1}")
            
            # 询问用户是否要从断点继续
            while True:
                try:
                    from i18n.i18n_manager import get_message
                    user_input = input(get_message("continue_from_record_yes_no", record=already_processed + 1)).strip().upper()
                except:
                    user_input = input(f"Continue from record {already_processed + 1}? (YES/NO): ").strip().upper()
                    
                if user_input == "YES":
                    start_index = already_processed
                    break
                elif user_input == "NO":
                    try:
                        from i18n.i18n_manager import get_message
                        print(get_message("reprocess_from_beginning"))
                    except:
                        print("Will reprocess all records from the beginning...")
                    start_index = 0
                    # 清除所有记录的关键词
                    for record_data in parsed_records:
                        self.clear_keywords(record_data['keywords_elem'])
                    break
                else:
                    print("Please enter 'YES' or 'NO'")
        else:
            start_index = 0
        
        processed_count = start_index
        prefilter_excluded_count = 0
        
        try:
            print(f"\n=== Starting to process {total_records} records ===")
            if start_index > 0:
                print(f"Resuming from record {start_index + 1}")
            print("Tip: Press Ctrl+C to interrupt and save current results")
            
            # Define temporary file name
            temp_output = output_path.replace(".xml", "_temp.xml")
            
            for i in range(start_index, total_records):
                record_data = parsed_records[i]
                title = record_data['title']
                abstract = record_data['abstract']
                keywords_elem = record_data['keywords_elem']
                record_elem = record_data['record_elem']
                
                # 如果不是从断点继续，清除原有关键词
                if start_index == 0:
                    self.clear_keywords(keywords_elem)
                
                # Show progress
                processed_count = i + 1
                progress = f"[{processed_count}/{total_records}]"
                print(f"\n{progress} Processing: {title[:60]}...")
                
                # Record start time
                start_time = time.time()
                
                # Prefilter: check if study design should be excluded
                should_exclude, design_type, matched_keyword, filter_details = self.design_prefilter.check_study_design(
                    title, abstract, self.excluded_study_designs, self.included_study_designs
                )
                if should_exclude:
                    prefilter_excluded_count += 1
                    exclusion_message = f"EXCLUDE - {design_type} (matched: {matched_keyword})"
                    print(f"  {progress} Prefilter result: ❌ {exclusion_message}")
                    print(f"  {progress} Details: {filter_details['reason']}")
                    
                    # 如果从断点继续且已有关键词，先清除
                    if start_index > 0 and i >= start_index:
                        self.clear_keywords(keywords_elem)
                    
                    # Add exclusion tag
                    self.add_keyword_to_record(keywords_elem, exclusion_message)
                    
                    # Add detailed information
                    self.add_keyword_to_record(keywords_elem, f"Title analysis: {filter_details['title']}")
                    self.add_keyword_to_record(keywords_elem, f"Abstract analysis: {filter_details['abstract']}")
                    
                    # Add basic PICOS tags for prefiltered records
                    picos_info = {
                        "S": f"{design_type} (auto-identified)",
                        "P": "Not evaluated by LLM (excluded by prefilter)",
                        "I": "Not evaluated by LLM (excluded by prefilter)",
                        "C": "Not evaluated by LLM (excluded by prefilter)",
                        "O": "Not evaluated by LLM (excluded by prefilter)"
                    }
                    
                    for key, label in [("S", "S"), ("P", "P"), ("I", "I"), ("C", "C"), ("O", "O")]:
                        tag_text = f"{label}: {picos_info[key]} (Prefilter)"
                        self.add_keyword_to_record(keywords_elem, tag_text)
                    
                    # Auto-save every 10 records or last record
                    if processed_count % 10 == 0 or processed_count == total_records:
                        self.save_xml(tree, temp_output)
                        print(f"{progress} Auto-save checkpoint to: {temp_output}")
                    continue
                
                # If passed prefilter, continue with detailed LLM analysis
                print(f"  {progress} Passed prefilter, proceeding with LLM analysis...")
                
                # 如果从断点继续且已有关键词，先清除
                if start_index > 0 and i >= start_index:
                    self.clear_keywords(keywords_elem)
                
                # Sequential processing of study
                all_results = self.process_study_sequential(title, abstract, inclusion_criteria)
                                
                end_time = time.time()
                processing_time = end_time - start_time
                print(f"  {progress} Processing completed, time taken: {processing_time:.2f} seconds")
                
                # Process and display results
                inclusion_decisions = {}
                for llm_name, result in all_results.items():
                    picos_info = result['picos']
                    inclusion_result = result['inclusion']
                    
                    # Show prompt type used (if available)
                    prompt_info = ""
                    if 'prompt_type' in result:
                        prompt_info = f" (using {result['prompt_type']})"
                    
                    # Output inclusion decision
                    print(f"  {progress} {llm_name} result: {inclusion_result}{prompt_info}")
                    inclusion_decisions[llm_name] = inclusion_result
                    
                    # Add PICOS tags
                    for key, label in [("S", "S"), ("P", "P"), ("I", "I"), ("C", "C"), ("O", "O")]:
                        if key in picos_info:
                            tag_text = f"{label}: {picos_info[key]} ({llm_name})"
                            self.add_keyword_to_record(keywords_elem, tag_text)
                    
                    # Add inclusion decision tag
                    tag_text = f"{inclusion_result} ({llm_name})"
                    self.add_keyword_to_record(keywords_elem, tag_text)
                
                # Check for decision conflicts between LLMs
                if len(self.screening_llm_configs) > 1:
                    core_decisions = []
                    for decision in inclusion_decisions.values():
                        if "✅ INCLUDE" in decision:
                            core_decisions.append("INCLUDE")
                        elif "❌ EXCLUDE" in decision:
                            core_decisions.append("EXCLUDE")
                        else:
                            core_decisions.append("UNCLEAR")
                    
                    if len(set(core_decisions)) > 1:
                        conflict_tag = "⚠️ CONFLICT between LLM decisions"
                        self.add_keyword_to_record(keywords_elem, conflict_tag)
                        print(f"  {progress} Warning: LLM decision conflict - {', '.join(inclusion_decisions.values())}")
                    elif all(decision == "UNCLEAR" for decision in core_decisions):
                        uncertain_tag = "⚠️ UNCERTAIN"
                        self.add_keyword_to_record(keywords_elem, uncertain_tag)
                        print(f"  {progress} Note: All LLMs uncertain - {', '.join(inclusion_decisions.values())}")
                
                # Auto-save every 10 records or last record
                if processed_count % 10 == 0 or processed_count == total_records:
                    self.save_xml(tree, temp_output)
                    print(f"{progress} Auto-save checkpoint to: {temp_output}")
        
        except KeyboardInterrupt:
            # User interruption
            print("\n⚠️ Interrupt signal detected! Saving current results...")
            xml_path, excel_path = self._save_current_results(
                tree, output_path, processed_count, total_records, "INTERRUPTED"
            )
            
            print(f"\n=== INTERRUPTION SUMMARY ===")
            print(f"Processed: {processed_count}/{total_records} records")
            print(f"Prefilter excluded: {prefilter_excluded_count} records")
            print(f"XML saved to: {xml_path}")
            if excel_path:
                print(f"Excel report saved to: {excel_path}")
            print("\n=== HOW TO RESUME ===")
            print("1. Update your config.json input_xml_path to point to the saved XML file")
            print("2. Run the program again - it will automatically detect and resume from the breakpoint")
            return xml_path, excel_path
        
        except Exception as e:
            # Other exception handling
            print(f"\n❌ Error occurred during processing: {str(e)}")
            xml_path, excel_path = self._save_current_results(
                tree, output_path, processed_count, total_records, "ERROR"
            )
            
            print(f"\n=== ERROR SUMMARY ===")
            print(f"Processed: {processed_count}/{total_records} records before error")
            print(f"Prefilter excluded: {prefilter_excluded_count} records")
            print(f"XML saved to: {xml_path}")
            if excel_path:
                print(f"Excel report saved to: {excel_path}")
            raise
        
        # Normal completion
        print(f"\n✓ Completed processing all {total_records} records")
        print(f"Prefilter automatically excluded: {prefilter_excluded_count} records")
        
        xml_path, excel_path = self._save_current_results(
            tree, output_path, processed_count, total_records, ""
        )
        
        print(f"\n=== COMPLETION SUMMARY ===")
        print(f"Total processed: {processed_count}/{total_records} records")
        print(f"Prefilter excluded: {prefilter_excluded_count} records")
        print(f"Final XML saved to: {xml_path}")
        if excel_path:
            print(f"Final Excel report saved to: {excel_path}")
        
        return xml_path, excel_path
    def _generate_enhanced_excel_report(self, xml_output_path):
        """生成增强Excel报告"""
        print("Generating enhanced Excel report...")
        
        # 使用xml_parser的增强功能生成Excel
        excel_path = self.xml_parser.create_enhanced_excel(xml_output_path)
        
        return excel_path
    def save_xml(self, tree, output_path):
        """Save modified XML file, maintaining original format"""
        tree.write(output_path, encoding='UTF-8', xml_declaration=True)
    def save_tokens_to_csv(self, output_path, currency="USD"):
        """Save token consumption statistics to CSV file with cost analysis"""
        if not self.tokens_log:
            print("No token consumption records")
            return
        
        # Generate CSV file path
        if self.tokens_csv_path is None:
            base_name = os.path.splitext(output_path)[0]
            self.tokens_csv_path = f"{base_name}_tokens_usage.csv"
        
        # Write to CSV file
        fieldnames = ['timestamp', 'operation', 'llm_name', 'model', 'prompt_tokens', 
                     'completion_tokens', 'total_tokens', 'title', 'abstract']
        
        with open(self.tokens_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.tokens_log)
        
        # Calculate totals
        total_prompt_tokens = sum(log['prompt_tokens'] for log in self.tokens_log)
        total_completion_tokens = sum(log['completion_tokens'] for log in self.tokens_log)
        total_tokens = sum(log['total_tokens'] for log in self.tokens_log)
        
        # Statistics by LLM
        llm_stats = {}
        for log in self.tokens_log:
            llm_name = log['llm_name']
            if llm_name not in llm_stats:
                llm_stats[llm_name] = {
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': 0,
                    'count': 0
                }
            llm_stats[llm_name]['prompt_tokens'] += log['prompt_tokens']
            llm_stats[llm_name]['completion_tokens'] += log['completion_tokens']
            llm_stats[llm_name]['total_tokens'] += log['total_tokens']
            llm_stats[llm_name]['count'] += 1
        
        # 💰 新增：成本计算
        try:
            from .token_cost_calculator import TokenCostCalculator
            
            calculator = TokenCostCalculator()
            
            # 计算美元和人民币成本
            usd_analysis = calculator.calculate_tokens_log_costs(self.tokens_log, "USD")
            cny_analysis = calculator.calculate_tokens_log_costs(self.tokens_log, "CNY")
            
            # 保存成本报告
            base_name = os.path.splitext(output_path)[0]
            calculator.save_cost_report(usd_analysis, f"{base_name}_usd")
            calculator.save_cost_report(cny_analysis, f"{base_name}_cny")
            
            # Display enhanced statistics
            try:
                from i18n.i18n_manager import get_message
                print(f"\n{get_message('token_cost_analysis')}")
                print(get_message("detailed_records_saved", path=self.tokens_csv_path))
                print(get_message("total_tokens", total=total_tokens, input=total_prompt_tokens, output=total_completion_tokens))
                print(f"\n{get_message('llm_usage_stats')}")
                for llm_name, stats in llm_stats.items():
                    print(get_message("llm_stats_line", name=llm_name, total=stats['total_tokens'], count=stats['count']))
                    print(get_message("llm_input_output", input=stats['prompt_tokens'], output=stats['completion_tokens']))
                
                # Display cost summary
                print(f"\n{get_message('cost_summary')}")
                print(get_message("usd_cost", cost=usd_analysis['total_cost']))
                print(get_message("cny_cost", cost=cny_analysis['total_cost']))
                
                # Display cost by model
                print(f"\n{get_message('cost_by_model')}")
                for model_name, model_data in usd_analysis['by_model'].items():
                    cny_cost = cny_analysis['by_model'][model_name]['total_cost']
                    print(get_message("model_cost_line", model=model_name, usd=model_data['total_cost'], cny=cny_cost))
                    print(get_message("model_calls_tokens", calls=model_data['calls'], tokens=model_data['total_tokens']))
                
                print(f"\n{get_message('detailed_cost_report_generated')}")
            except:
                # Fallback to English if i18n fails
                print(f"\n=== TOKEN CONSUMPTION & COST ANALYSIS ===")
                print(f"Detailed records saved to: {self.tokens_csv_path}")
                print(f"Total: {total_tokens:,} tokens (Input: {total_prompt_tokens:,}, Output: {total_completion_tokens:,})")
                print("\n📊 LLM Usage Statistics:")
                for llm_name, stats in llm_stats.items():
                    print(f"- {llm_name}: {stats['total_tokens']:,} tokens ({stats['count']} calls)")
                    print(f"  Input: {stats['prompt_tokens']:,}, Output: {stats['completion_tokens']:,}")
                
                # Display cost summary
                print("\n💰 Cost Summary:")
                print(f"USD Cost: ${usd_analysis['total_cost']:.4f} USD")
                print(f"CNY Cost: ¥{cny_analysis['total_cost']:.2f} CNY")
                
                # Display cost by model
                print("\n🏷️ Cost Statistics by Model:")
                for model_name, model_data in usd_analysis['by_model'].items():
                    cny_cost = cny_analysis['by_model'][model_name]['total_cost']
                    print(f"- {model_name}: ${model_data['total_cost']:.4f} USD / ¥{cny_cost:.2f} CNY")
                    print(f"  Calls: {model_data['calls']}, tokens: {model_data['total_tokens']:,}")
                
                print("\n📄 Detailed cost report generated with complete fee analysis")
            
        except ImportError:
            try:
                from i18n.i18n_manager import get_message
                print(get_message("cost_calculation_warning"))
            except:
                print("Warning: Cost calculation module not found, showing basic token statistics only")
            # Original basic display logic
            print(f"\n=== TOKEN CONSUMPTION STATISTICS ===")
            print(f"Detailed records saved to: {self.tokens_csv_path}")
            print(f"Total: {total_tokens:,} tokens (Input: {total_prompt_tokens:,}, Output: {total_completion_tokens:,})")
            print("\nConsumption statistics by LLM:")
            for llm_name, stats in llm_stats.items():
                print(f"- {llm_name}: {stats['total_tokens']:,} tokens ({stats['count']} calls)")
                print(f"  Input: {stats['prompt_tokens']:,}, Output: {stats['completion_tokens']:,}")
        
        except Exception as e:
            try:
                from i18n.i18n_manager import get_message
                print(get_message("cost_calculation_error", error=str(e)))
            except:
                print(f"Warning: Error during cost calculation: {str(e)}")
            # Fallback to original display logic
            print(f"\n=== TOKEN CONSUMPTION STATISTICS ===")
            print(f"Detailed records saved to: {self.tokens_csv_path}")
            print(f"Total: {total_tokens:,} tokens (Input: {total_prompt_tokens:,}, Output: {total_completion_tokens:,})")
            print("\nConsumption statistics by LLM:")
            for llm_name, stats in llm_stats.items():
                print(f"- {llm_name}: {stats['total_tokens']:,} tokens ({stats['count']} calls)")
                print(f"  Input: {stats['prompt_tokens']:,}, Output: {stats['completion_tokens']:,}")
