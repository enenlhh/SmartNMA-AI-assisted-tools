import os
import time
from openai import OpenAI
from .base_extractor import BaseExtractor
from ..parsers.table_parser import TableParser
from ..core.schema import EXTRACTION_SCHEMA
class TableExtractor(BaseExtractor):
    """Extractor that uses table format output and parsing"""
    
    def __init__(self, llm_config, repair_llm_config=None, debug_folder=None):
        super().__init__(llm_config, repair_llm_config, debug_folder)
        self.parser = TableParser(self.repair_client, repair_llm_config, debug_folder)
    
    def create_prompts(self):
        prompts = {}
        # Enhanced system prompt with stronger emphasis on table format
        system_prompt = (
            "You are a research assistant tasked with extracting specific information from academic papers for a systematic review. "
            "Extract information accurately and precisely according to the provided schema. "
            "If information is not available or not reported, respond with 'Not reported'. "
            "CRITICAL FORMATTING REQUIREMENT: You must return data in a proper tab-separated table format. "
            "First line should contain ALL column headers, separated by tabs. "
            "Each subsequent line should contain values for each column, separated by tabs. "
            "EVERY row must have exactly the same number of tab-separated values as there are headers. "
            "If a field has no value, still include a tab and write 'Not reported'. "
            "DO NOT include any explanations, markdown formatting, or additional text - ONLY the tab-separated table."
        )
        # Create extraction prompts for each table
        for table_name, fields in EXTRACTION_SCHEMA.items():
            field_descriptions = "\n".join([f"- {field['name']}: {field['description']}" for field in fields])
            field_examples = "\n".join([f"  {field['name']}: {field['example']}" for field in fields])
            # Special prompt for Groups table
            if table_name == "Groups":
                user_prompt = f"""
    Extract information for the intervention and control groups according to the following schema:
    {field_descriptions}
    FOCUS ONLY ON IDENTIFYING DISTINCT GROUPS AND THEIR INTERVENTION DETAILS. Do not extract participant numbers or demographic information - that will be extracted separately.
    Format your response as a tab-separated table. First line should contain all the column headers, and each subsequent line should contain values for one intervention or control group.
    Example format:
    Group_Name\tStudy_ID\tDescription\tDuration\tTiming\t[other headers...]
    Structured exercise program\tSmith, 2020\t60-minute sessions including aerobic warm-up...\t12 weeks\t3 sessions per week...\t[other values...]
    Usual care\tSmith, 2020\tParticipants received standard medical care...\t12 weeks\tRoutine doctor visits...\t[other values...]
    Document content:
    {{paper_content}}
    """
            # Special prompt for Participant_Characteristics table
            elif table_name == "Participant_Characteristics":
                user_prompt = f"""
    Extract participant characteristics according to the following schema:
    {field_descriptions}
    IMPORTANT: Check if participant characteristics are reported overall (for all participants combined) or separately for each group.
    If reported overall, create ONE entry with Group set to "Overall" and report all characteristics for the entire sample.
    If reported by groups, create SEPARATE entries for EACH intervention or control group. Do NOT combine data from different groups in the same field.
    For each group, extract both the participant numbers (Sample_Size, Randomized, etc.) AND demographic characteristics (Age, Sex, etc.).
    Format your response as a tab-separated table with these exact column headers:
    Group\tSample_Size\tAssessed_for_Eligibility\tExcluded_Before_Randomization\tRandomized\tLost_to_Followup\tExcluded_from_Analysis\tPopulation_Description\tAge\tSex\t[other demographic fields...]
    Example format for group-specific reporting:
    Group\tSample_Size\tAssessed_for_Eligibility\t[other participant number fields...]\tAge\tSex\t[other demographic fields...]
    Structured exercise program\t75 participants\t98 participants\t[other values...]\tMean 65.2 years (SD 9.8)\tMale: 42 (56%)\t[other values...]
    Usual care\t75 participants\t98 participants\t[other values...]\tMean 64.8 years (SD 10.1)\tMale: 39 (52%)\t[other values...]
    Document content:
    {{paper_content}}
    """
            # Special prompt for Outcomes table focusing on identifying all outcome measures
            elif table_name == "Outcomes":
                user_prompt = f"""
    Extract information for all outcome measures according to the following schema:
    {field_descriptions}
    FOCUS ONLY ON IDENTIFYING AND DESCRIBING THE OUTCOME MEASURES. The actual results will be extracted separately.
    Be comprehensive and extract ALL outcomes mentioned in the paper, including primary, secondary, and any additional outcomes reported.
    Format your response as a tab-separated table. First line should contain all the column headers, and each subsequent line should contain values for one outcome measure.
    Example format:
    Outcome_Name\tStudy_ID\tOutcome_Type\tTime_Points\tDefinition\t[other headers...]
    Pain intensity\tSmith, 2020\tPrimary\tBaseline, 6 weeks, 12 weeks\tSelf-reported pain intensity during the past week\t[other values...]
    Functional disability\tSmith, 2020\tSecondary\tBaseline, 12 weeks\tAbility to perform daily activities\t[other values...]
    Document content:
    {{paper_content}}
    """
            # Special prompt for Results table explicitly requiring extraction by group
            elif table_name == "Results":
                user_prompt = f"""
    Extract results for each outcome by group according to the following schema:
    {field_descriptions}
    IMPORTANT: Create SEPARATE entries for EACH combination of outcome, group, and time point. Do NOT combine results from different groups in the same entry.
    Format your response as a tab-separated table. First line should contain all the column headers, and each subsequent line should contain values for one specific result.
    Example format:
    Result_ID\tOutcome_Name\tGroup_Name\tTime_Point\tSample_Size\tResult_Value\t[other headers...]
    Smith2020_Pain_Exercise_12wk\tPain intensity\tStructured exercise program\t12 weeks\t72\tMean 3.5 (SD 1.8)\t[other values...]
    Smith2020_Pain_Control_12wk\tPain intensity\tUsual care\t12 weeks\t70\tMean 6.0 (SD 1.7)\t[other values...]
    Document content:
    {{paper_content}}
    """
            # Special prompt for Comparisons table
            elif table_name == "Comparisons":
                user_prompt = f"""
    Extract comparisons between groups for each outcome according to the following schema:
    {field_descriptions}
    IMPORTANT: Create one entry for each comparison between groups for each outcome at each time point. Focus on extracting the statistical comparisons, effect sizes, and p-values.
    Format your response as a tab-separated table. First line should contain all the column headers, and each subsequent line should contain values for one specific comparison.
    Example format:
    Comparison_ID\tOutcome_Name\tGroup1_Name\tGroup2_Name\tTime_Point\tEffect_Estimate\t[other headers...]
    Smith2020_Pain_Ex_vs_UC_12wk\tPain intensity\tStructured exercise program\tUsual care\t12 weeks\tMean difference: -2.5 (95% CI: -3.1 to -1.9); p<0.001\t[other values...]
    Smith2020_Function_Ex_vs_UC_12wk\tFunctional disability\tStructured exercise program\tUsual care\t12 weeks\tMean difference: -5.2 (95% CI: -7.8 to -2.6); p=0.002\t[other values...]
    Document content:
    {{paper_content}}
    """
            # Default prompt for Study_Info
            else:
                user_prompt = f"""
    Extract information for the {table_name.replace('_', ' ')} table according to the following schema:
    {field_descriptions}
    Format your response as a tab-separated table. First line should contain all the column headers, and each subsequent line should contain values for one entry.
    Example field values:
    {field_examples}
    Document content:
    {{paper_content}}
    """
            prompts[table_name] = (system_prompt, user_prompt)
        return prompts
    
    def call_llm(self, system_prompt, user_prompt, **kwargs):
        """Call LLM API for table format output"""
        model = kwargs.get('model', self.llm_config['model'])
        temperature = kwargs.get('temperature', 0.0)
        max_tokens = kwargs.get('max_tokens', 4000)
        timeout = kwargs.get('timeout', 300)
        max_retries = kwargs.get('max_retries', 5)
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"LLM call failed (attempt {attempt+1}): {e}")
                if attempt < max_retries-1:
                    wait_time = 2 ** attempt
                    print(f"Waiting {wait_time}s before retrying...")
                    time.sleep(wait_time)
                else:
                    print("Failed after multiple retries, skipping.")
                    return None
            
    def process_file(self, file_path, split_length=100000):
        from ..core.file_reader import read_file
        from ..core.data_processor import post_process_data
        import time
        prompts = self.create_prompts()
        file_name = os.path.basename(file_path)
        print(f"\nProcessing file: {file_name}")
        # Record start time
        overall_start_time = time.time()
        # Read file content
        content = read_file(file_path)
        if content is None:
            print(f"Read failed, skipping {file_name}")
            return None
        print(f"File character count: {len(content)}")
        # Extract data table by table in specific order to maintain consistency
        all_extracted_data = {}
        
        # Step 1: First extract Study_Info to get Study_ID
        print(f"  Extracting Study_Info data...")
        start_time = time.time()
        
        system_prompt, prompt_template = prompts["Study_Info"]
        user_prompt = prompt_template.replace("{paper_content}", content[:split_length])
        
        llm_response = self.call_llm(
            system_prompt,
            user_prompt,
            model=self.llm_config["model"],
            temperature=self.llm_config.get("temperature", 0.0)
        )
        
        if llm_response is None:
            all_extracted_data["Study_Info"] = []
            study_id = file_name.replace(".pdf", "").replace(".docx", "")
        else:
            extracted_data = self.parser.parse_response(llm_response)
            for item in extracted_data:
                item["File_Name"] = file_name
            all_extracted_data["Study_Info"] = extracted_data
            
            # Get study ID for future use
            study_id = extracted_data[0].get("Study_ID", file_name.replace(".pdf", "").replace(".docx", "")) if extracted_data else file_name.replace(".pdf", "").replace(".docx", "")
        
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"  Study_Info completed - Duration: {elapsed_str} - Extracted {len(all_extracted_data.get('Study_Info', []))} records")
        
        # Step 2: Extract Groups to get Group_Names - Focus only on intervention information
        print(f"  Extracting Groups data...")
        start_time = time.time()
        
        system_prompt, prompt_template = prompts["Groups"]
        # Modify prompt to emphasize extracting only intervention information
        modified_prompt = prompt_template.replace("{paper_content}", content[:split_length])
        # Add instruction to use specific Study_ID
        modified_prompt = modified_prompt.replace("Format your response as a tab-separated table",
                                                f"Format your response as a tab-separated table. FOCUS ONLY ON IDENTIFYING DISTINCT GROUPS AND THEIR INTERVENTION DETAILS. Use this Study_ID: {study_id}")
        
        llm_response = self.call_llm(
            system_prompt,
            modified_prompt,
            model=self.llm_config["model"],
            temperature=self.llm_config.get("temperature", 0.0)
        )
        
        if llm_response is None:
            all_extracted_data["Groups"] = []
            group_names = []
        else:
            extracted_data = self.parser.parse_response(llm_response)
            for item in extracted_data:
                item["File_Name"] = file_name
                item["Study_ID"] = study_id  # Use consistent Study_ID
            all_extracted_data["Groups"] = extracted_data
            
            # Get group names for future use
            group_names = [item.get("Group_Name", "") for item in extracted_data if "Group_Name" in item and item["Group_Name"]]
        
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"  Groups completed - Duration: {elapsed_str} - Extracted {len(all_extracted_data.get('Groups', []))} records")
        
        # Step 3: Extract Participant_Characteristics with group names
        print(f"  Extracting Participant_Characteristics data...")
        start_time = time.time()
        system_prompt, prompt_template = prompts["Participant_Characteristics"]
        # Enhance system prompt emphasizing format requirements
        enhanced_system_prompt = system_prompt + "\n\nIMPORTANT: Your response MUST follow proper tab-separated table format. First line should contain ALL column headers separated by tabs. Each subsequent line should contain values separated by tabs. Every row must have exactly the same number of fields as there are headers."
        # Modify prompt to use Group instead of Group_Name
        modified_prompt = prompt_template.replace("{paper_content}", content[:split_length])
        # Add explicit format example
        format_example = """
        Example of proper format with tabs:
        Group[TAB]Total_Sample_Size[TAB]Population_Description[TAB]Age[TAB]Sex
        Group A[TAB]75[TAB]Patients with condition X[TAB]Mean 65.2 years (SD 9.8)[TAB]Male: 42 (56%)
        Group B[TAB]75[TAB]Patients with condition X[TAB]Mean 64.8 years (SD 10.1)[TAB]Male: 39 (52%)
        Or for overall reporting:
        Group[TAB]Total_Sample_Size[TAB]Population_Description[TAB]Age[TAB]Sex
        Overall[TAB]150[TAB]Patients with condition X[TAB]Mean 65.0 years (SD 9.9)[TAB]Male: 81 (54%)
        DO NOT include any explanations, markdown formatting, or additional text - ONLY the tab-separated table.
        """
        # Add instruction to use specific group names
        if group_names:
            group_names_str = ", ".join([f'"{name}"' for name in group_names])
            modified_prompt = modified_prompt.replace("Format your response as a tab-separated table",
                                                    f"Format your response as a tab-separated table. IMPORTANT: If characteristics are reported by group, create one entry for EACH of these exact group names: {group_names_str}. If characteristics are reported only for the overall sample, create a single entry with Group set to 'Overall'. Use the Study_ID: {study_id}\n\n{format_example}")
        
        llm_response = self.call_llm(
            enhanced_system_prompt,
            modified_prompt,
            model=self.llm_config["model"],
            temperature=self.llm_config.get("temperature", 0.0)
        )
        
        # Save raw response for debugging
        if llm_response and self.debug_folder:
            debug_file = os.path.join(self.debug_folder, f"debug_{int(time.time())}_participant_chars.txt")
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write("=== PROMPT ===\n")
                f.write(modified_prompt[:1000] + "...\n\n")  # Save first 1000 characters of prompt
                f.write("=== RESPONSE ===\n")
                f.write(llm_response)
            print(f"  Saved raw response to: {debug_file}")
        
        if llm_response is None:
            all_extracted_data["Participant_Characteristics"] = []
        else:
            extracted_data = self.parser.parse_response(llm_response)
            
            # Save more debug info if parsing fails
            if not extracted_data and self.debug_folder:
                print("  Warning: Failed to parse Participant_Characteristics table data")
                debug_file = os.path.join(self.debug_folder, f"failed_parsing_{int(time.time())}.txt")
                with open(debug_file, "w", encoding="utf-8") as f:
                    f.write("=== FAILED PARSING FOR PARTICIPANT CHARACTERISTICS ===\n")
                    f.write("=== RESPONSE ===\n")
                    f.write(llm_response)
                print(f"  Saved failed parsing response to: {debug_file}")
            for item in extracted_data:
                item["File_Name"] = file_name
                # Ensure group name matches one from Groups table unless "Overall"
                if "Group" in item and item["Group"] and item["Group"] != "Overall" and item["Group"] not in group_names:
                    closest_match = next((name for name in group_names if name.lower() in item["Group"].lower() or item["Group"].lower() in name.lower()), None)
                    if closest_match:
                        item["Group"] = closest_match
            all_extracted_data["Participant_Characteristics"] = extracted_data
        
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"  Participant_Characteristics completed - Duration: {elapsed_str} - Extracted {len(all_extracted_data.get('Participant_Characteristics', []))} records")
        
        # Step 4: Extract Outcomes to get Outcome_Names
        print(f"  Extracting Outcomes data...")
        start_time = time.time()
        
        system_prompt, prompt_template = prompts["Outcomes"]
        enhanced_system_prompt = system_prompt + "\n\nEnsure you extract ALL outcomes mentioned in the paper, as these will be used to extract result data in subsequent steps. Be comprehensive and thorough in identifying all relevant outcomes."
        # Modify the prompt to use Outcome_Name instead of Outcome_ID
        modified_prompt = prompt_template.replace("Outcome_ID", "Outcome_Name").replace("{paper_content}", content[:split_length])
        # Add instruction to put Study_ID after File_Name and before Outcome_Name
        modified_prompt = modified_prompt.replace("Format your response as a tab-separated table",
                                                "Format your response as a tab-separated table. Be comprehensive and extract ALL outcomes mentioned in the paper. Make sure to place the Study_ID column after File_Name and before Outcome_Name. Use this Study_ID: " + study_id)
        llm_response = self.call_llm(
            enhanced_system_prompt,
            modified_prompt,
            model=self.llm_config["model"],
            temperature=self.llm_config.get("temperature", 0.0)
        )
        
        if llm_response is None:
            all_extracted_data["Outcomes"] = []
            outcome_names = []
        else:
            extracted_data = self.parser.parse_response(llm_response)
            for item in extracted_data:
                item["File_Name"] = file_name
                item["Study_ID"] = study_id  # Use consistent Study_ID
            all_extracted_data["Outcomes"] = extracted_data
            
            # Get outcome names for future use
            outcome_names = [item.get("Outcome_Name", "") for item in extracted_data if "Outcome_Name" in item and item["Outcome_Name"]]
        
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"  Outcomes completed - Duration: {elapsed_str} - Extracted {len(all_extracted_data.get('Outcomes', []))} records")
        
        # Step 5: Extract Results with outcome names and group names
        print(f"  Extracting Results data...")
        start_time = time.time()
        
        system_prompt, prompt_template = prompts["Results"]
        # Modify the prompt to use Outcome_Name and Group_Name instead of IDs
        modified_prompt = prompt_template.replace("Outcome_ID", "Outcome_Name").replace("Group_ID", "Group_Name").replace("{paper_content}", content[:split_length])
        
        # Add instruction to use specific outcome names and group names
        outcome_instruction = ""
        if outcome_names:
            outcome_names_str = ", ".join([f'"{name}"' for name in outcome_names])
            outcome_instruction = f"IMPORTANT: Extract results ONLY for these specific outcomes: {outcome_names_str}. Do not extract results for any other outcomes. For each outcome, make sure to use the exact outcome name as listed. "
        group_instruction = ""
        if group_names:
            group_names_str = ", ".join([f'"{name}"' for name in group_names])
            group_instruction = f"For each outcome, extract results for these specific groups: {group_names_str}. "
        
        modified_prompt = modified_prompt.replace("Format your response as a tab-separated table",
                                                f"Format your response as a tab-separated table. {outcome_instruction}{group_instruction}Use the Study_ID: {study_id}")
        
        llm_response = self.call_llm(
            system_prompt,
            modified_prompt,
            model=self.llm_config["model"],
            temperature=self.llm_config.get("temperature", 0.0)
        )
        
        if llm_response is None:
            all_extracted_data["Results"] = []
        else:
            extracted_data = self.parser.parse_response(llm_response)
            for item in extracted_data:
                item["File_Name"] = file_name
                
                # Ensure outcome name matches one from Outcomes table
                if "Outcome_Name" in item and item["Outcome_Name"] and item["Outcome_Name"] not in outcome_names:
                    closest_match = next((name for name in outcome_names if name.lower() in item["Outcome_Name"].lower() or item["Outcome_Name"].lower() in name.lower()), None)
                    if closest_match:
                        item["Outcome_Name"] = closest_match
                
                # Ensure group name matches one from Groups table
                if "Group_Name" in item and item["Group_Name"] and item["Group_Name"] not in group_names:
                    closest_match = next((name for name in group_names if name.lower() in item["Group_Name"].lower() or item["Group_Name"].lower() in name.lower()), None)
                    if closest_match:
                        item["Group_Name"] = closest_match
            
            all_extracted_data["Results"] = extracted_data
        
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"  Results completed - Duration: {elapsed_str} - Extracted {len(all_extracted_data.get('Results', []))} records")
        
        # Step 6: Extract Comparisons with outcome names and group names
        print(f"  Extracting Comparisons data...")
        start_time = time.time()
        
        system_prompt, prompt_template = prompts["Comparisons"]
        # Modify the prompt to use Outcome_Name and Group_Name instead of IDs
        modified_prompt = prompt_template.replace("Outcome_ID", "Outcome_Name").replace("Group1_ID", "Group1_Name").replace("Group2_ID", "Group2_Name").replace("{paper_content}", content[:split_length])
        
        # Add instruction to use specific outcome names and group names
        outcome_instruction = ""
        if outcome_names:
            outcome_names_str = ", ".join([f'"{name}"' for name in outcome_names])
            outcome_instruction = f"IMPORTANT: Extract comparisons ONLY for these specific outcomes: {outcome_names_str}. Do not extract comparisons for any other outcomes. For each outcome, make sure to use the exact outcome name as listed. "
        group_instruction = ""
        if group_names:
            group_names_str = ", ".join([f'"{name}"' for name in group_names])
            group_instruction = f"Compare between these specific groups: {group_names_str}. "
        
        modified_prompt = modified_prompt.replace("Format your response as a tab-separated table",
                                                f"Format your response as a tab-separated table. {outcome_instruction}{group_instruction}Use the Study_ID: {study_id}")
        
        llm_response = self.call_llm(
            system_prompt,
            modified_prompt,
            model=self.llm_config["model"],
            temperature=self.llm_config.get("temperature", 0.0)
        )
        
        if llm_response is None:
            all_extracted_data["Comparisons"] = []
        else:
            extracted_data = self.parser.parse_response(llm_response)
            for item in extracted_data:
                item["File_Name"] = file_name
                
                # Ensure outcome name matches one from Outcomes table
                if "Outcome_Name" in item and item["Outcome_Name"] and item["Outcome_Name"] not in outcome_names:
                    closest_match = next((name for name in outcome_names if name.lower() in item["Outcome_Name"].lower() or item["Outcome_Name"].lower() in name.lower()), None)
                    if closest_match:
                        item["Outcome_Name"] = closest_match
                
                # Ensure group names match ones from Groups table
                if "Group1_Name" in item and item["Group1_Name"] and item["Group1_Name"] not in group_names:
                    closest_match = next((name for name in group_names if name.lower() in item["Group1_Name"].lower() or item["Group1_Name"].lower() in name.lower()), None)
                    if closest_match:
                        item["Group1_Name"] = closest_match
                
                if "Group2_Name" in item and item["Group2_Name"] and item["Group2_Name"] not in group_names:
                    closest_match = next((name for name in group_names if name.lower() in item["Group2_Name"].lower() or item["Group2_Name"].lower() in name.lower()), None)
                    if closest_match:
                        item["Group2_Name"] = closest_match
            
            all_extracted_data["Comparisons"] = extracted_data
        
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"  Comparisons completed - Duration: {elapsed_str} - Extracted {len(all_extracted_data.get('Comparisons', []))} records")
        
        # Post-process data to format dictionaries and handle missing values
        all_extracted_data = post_process_data(all_extracted_data)
        # Calculate total processing time
        overall_elapsed_time = time.time() - overall_start_time
        overall_elapsed_str = time.strftime("%H:%M:%S", time.gmtime(overall_elapsed_time))
        print(f"\nTotal processing time for file {file_name}: {overall_elapsed_str}")
        
        # Log study processing time to file
        try:
            with open("extraction_timing.csv", "a") as f:
                f.write(f"{file_name},{study_id},{overall_elapsed_time:.1f},{overall_elapsed_str}\n")
        except Exception as e:
            print(f"Error logging timing: {e}")
        return all_extracted_data