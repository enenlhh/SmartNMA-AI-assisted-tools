"""
JSON format extractor (v8 approach)
Uses OpenAI's structured output with JSON schema
"""
import os
import time
import json
from openai import AzureOpenAI
from .base_extractor import BaseExtractor
from ..parsers.json_parser import JsonParser
from ..core.schema import EXTRACTION_SCHEMA, create_structured_schemas
from ..core.file_reader import read_file
from ..core.data_processor import post_process_data

class JsonExtractor(BaseExtractor):
    """Extractor that uses JSON structured output"""
    
    def __init__(self, llm_config, repair_llm_config=None, debug_folder=None):
        super().__init__(llm_config, repair_llm_config, debug_folder)
        self.parser = JsonParser()
        self.schemas = create_structured_schemas()
    
    def create_prompts(self):
        """Create extraction prompts for JSON format output"""
        prompts = {}

        # 通用系统提示
        system_prompt = (
            "You are a research assistant tasked with extracting specific information from academic papers for a systematic review. "
            "Extract information accurately and precisely according to the provided schema. "
            "If information is not available or not reported, respond with 'Not reported'. "
            "Format your response as a valid JSON object. "
            "Make sure to preserve the hierarchical relationship between different data elements. "
            "Only respond in English."
        )

        # 为每个表创建提取提示
        for table_name, fields in EXTRACTION_SCHEMA.items():
            field_descriptions = "\n".join([f"- {field['name']}: {field['description']}" for field in fields])

            # 为Study_Info表
            if table_name == "Study_Info":
                user_prompt = f"""
    Extract information for the {table_name.replace('_', ' ')} table according to the following schema:

    {field_descriptions}

    Format your response as a JSON object with a 'studies' array containing the extracted data.

    Example JSON structure:
    {{
    "studies": [
        {{
        "Study_ID": "Smith, 2020",
        "Publication_Type": "Full report",
        "Study_Design": "Randomized Controlled Trial",
        "Aim": "To evaluate the effectiveness of...",
        "Unit_of_Allocation": "Individuals",
        "Country": "United States",
        "Setting": "Three urban community health centers",
        "Method_of_Recruitment": "Physician referrals and community advertisements",
        "Start_Date": "January 2018",
        "End_Date": "December 2019",
        "Duration": "8 months",
        "Ethical_Approval": "Yes, university ethics committee approval #ERB2017-234",
        "Ethical_Approval_Sentence": "The study protocol was approved by the University Research Ethics Board",
        "Informed_Consent": "Written informed consent obtained from all participants",
        "Funding_Sources": "National Institute for Health Research, Grant #NH-2017-45621",
        "Conflicts_of_Interest": "Dr. Smith received speaking fees from PharmaCo",
        "Key_Conclusions": "A 12-week structured exercise program significantly reduced pain intensity",
        "Adverse_Events": "Structured exercise: Muscle soreness: 12 (16%)",
        "Notes": "Study was stopped early due to significant benefit"
        }}
    ]
    }}

    Document content:
    {{paper_content}}
    """

            # 为Groups表
            elif table_name == "Groups":
                user_prompt = f"""
    Extract information for the intervention and control groups according to the following schema:

    {field_descriptions}

    FOCUS ONLY ON IDENTIFYING DISTINCT GROUPS AND THEIR INTERVENTION DETAILS. Do not extract participant numbers or demographic information - that will be extracted separately.

    Format your response as a JSON object with a 'groups' array containing the extracted data.

    Example JSON structure:
    {{
    "groups": [
        {{
        "Group_Name": "Structured exercise program",
        "Study_ID": "Smith, 2020",
        "Group_Type": "Intervention",
        "Sample_Size": "75 participants",
        "Assessed_for_Eligibility": "98 participants",
        "Excluded_Before_Randomization": "23 (10 did not meet inclusion criteria)",
        "Randomized": "75 participants",
        "Lost_to_Followup": "3 (2 withdrew due to time constraints)",
        "Excluded_from_Analysis": "2 (protocol violations)",
        "Cluster_Unit_and_Size": "Not applicable",
        "Description": "60-minute sessions including aerobic warm-up, strengthening exercises",
        "Duration": "12 weeks",
        "Timing": "3 sessions per week, 60 minutes per session",
        "Setting_Delivery_Location": "Hospital outpatient rehabilitation gymnasium",
        "Delivery": "In-person, supervised by trained physiotherapists",
        "Providers": "Certified physiotherapists with ≥3 years experience",
        "Recruitment_Method": "Referrals from primary care physicians",
        "Co_Interventions": "Educational booklet on back pain self-management",
        "Compliance": "Mean attendance: 30.2 of 36 sessions (84%)"
        }},
        {{
        "Group_Name": "Usual care",
        "Study_ID": "Smith, 2020",
        "Group_Type": "Control",
        "Sample_Size": "75 participants",
        "Assessed_for_Eligibility": "98 participants",
        "Excluded_Before_Randomization": "23 (10 did not meet inclusion criteria)",
        "Randomized": "75 participants",
        "Lost_to_Followup": "2 (1 withdrew, 1 moved away)",
        "Excluded_from_Analysis": "1 (protocol violation)",
        "Cluster_Unit_and_Size": "Not applicable",
        "Description": "Participants received standard medical care",
        "Duration": "12 weeks",
        "Timing": "Routine doctor visits as needed",
        "Setting_Delivery_Location": "Primary care clinics",
        "Delivery": "Standard care by primary care physicians",
        "Providers": "Primary care physicians",
        "Recruitment_Method": "Same as intervention group",
        "Co_Interventions": "None specified",
        "Compliance": "Not reported"
        }}
    ]
    }}

    Document content:
    {{paper_content}}
    """

            # 为Participant_Characteristics表
            elif table_name == "Participant_Characteristics":
                user_prompt = f"""
    Extract participant characteristics according to the following schema:

    {field_descriptions}

    IMPORTANT: Check if participant characteristics are reported overall (for all participants combined) or separately for each group.
    If reported overall, create ONE entry with Group set to "Overall" and report all characteristics for the entire sample.
    If reported by groups, create SEPARATE entries for EACH intervention or control group. Do NOT combine data from different groups in the same field.

    For each group, extract both the participant numbers (Sample_Size, Randomized, etc.) AND demographic characteristics (Age, Sex, etc.).

    Format your response as a JSON object with a 'characteristics' array containing the extracted data.

    Example JSON structure for group-specific reporting:
    {{
    "characteristics": [
        {{
        "Group": "Structured exercise program",
        "Total_Sample_Size": "225",
        "Population_Description": "Community-dwelling adults with chronic low back pain",
        "Baseline_Reporting": "By group",
        "Baseline_Imbalances": "Significant between-group differences in baseline pain severity",
        "Inclusion_Criteria": "Adults aged 18-65 years with chronic lower back pain",
        "Exclusion_Criteria": "Specific pathologies, recent surgery, pending litigation",
        "Subgroups_Measured": "Age (<50 vs ≥50 years), Sex (male vs female)",
        "Subgroups_Reported": "Age and sex subgroups reported",
        "Age": "Mean 48.2 years (SD 10.9), range 22-65 years",
        "Sex": "Female: 42 (56%), Male: 33 (44%)",
        "Race_Ethnicity": "White: 45 (60%), Black: 20 (27%)",
        "BMI": "Mean 27.8 kg/m² (SD 4.4)",
        "Height_Weight": "Height: mean 172.5 cm; Weight: mean 82.3 kg",
        "Smoking": "Current smokers: 15 (20%), Former: 25 (33%)",
        "Alcohol": "Non-drinkers: 15 (20%), Moderate: 45 (60%)",
        "Physical_Activity": "Sedentary: 42 (56%), Moderate: 20 (27%)",
        "Education": "High school or less: 25 (33%), College: 30 (40%)",
        "Employment": "Employed full-time: 50 (67%), Part-time: 15 (20%)",
        "Income": "<$30,000: 20 (27%), $30,000-60,000: 30 (40%)",
        "Marital_Status": "Married/partnered: 50 (67%), Single: 18 (24%)",
        "Duration_of_Condition": "Median duration of pain: 4.0 years",
        "Severity_of_Illness": "Pain intensity: mean 6.7 (SD 1.3)",
        "Comorbidities": "Hypertension: 15 (20%), Diabetes: 8 (11%)",
        "Medication_Use": "NSAIDs: 55 (73%), Acetaminophen: 45 (60%)",
        "Previous_Treatments": "Physical therapy: 35 (47%), Chiropractic: 20 (27%)"
        }},
        {{
        "Group": "Usual care",
        "Total_Sample_Size": "225",
        "Population_Description": "Community-dwelling adults with chronic low back pain",
        "Baseline_Reporting": "By group",
        "Baseline_Imbalances": "Significant between-group differences in baseline pain severity",
        "Inclusion_Criteria": "Adults aged 18-65 years with chronic lower back pain",
        "Exclusion_Criteria": "Specific pathologies, recent surgery, pending litigation",
        "Subgroups_Measured": "Age (<50 vs ≥50 years), Sex (male vs female)",
        "Subgroups_Reported": "Age and sex subgroups reported",
        "Age": "Mean 47.8 years (SD 11.2), range 20-64 years",
        "Sex": "Female: 39 (52%), Male: 36 (48%)",
        "Race_Ethnicity": "White: 48 (64%), Black: 18 (24%)",
        "BMI": "Mean 28.1 kg/m² (SD 4.2)",
        "Height_Weight": "Height: mean 171.8 cm; Weight: mean 83.1 kg",
        "Smoking": "Current smokers: 18 (24%), Former: 22 (29%)",
        "Alcohol": "Non-drinkers: 18 (24%), Moderate: 42 (56%)",
        "Physical_Activity": "Sedentary: 45 (60%), Moderate: 18 (24%)",
        "Education": "High school or less: 28 (37%), College: 25 (33%)",
        "Employment": "Employed full-time: 48 (64%), Part-time: 12 (16%)",
        "Income": "<$30,000: 22 (29%), $30,000-60,000: 28 (37%)",
        "Marital_Status": "Married/partnered: 48 (64%), Single: 20 (27%)",
        "Duration_of_Condition": "Median duration of pain: 3.8 years",
        "Severity_of_Illness": "Pain intensity: mean 6.5 (SD 1.4)",
        "Comorbidities": "Hypertension: 18 (24%), Diabetes: 10 (13%)",
        "Medication_Use": "NSAIDs: 52 (69%), Acetaminophen: 48 (64%)",
        "Previous_Treatments": "Physical therapy: 32 (43%), Chiropractic: 22 (29%)"
        }}
    ]
    }}

    Example for overall reporting:
    {{
    "characteristics": [
        {{
        "Group": "Overall",
        "Total_Sample_Size": "150",
        "Population_Description": "Community-dwelling adults with chronic low back pain",
        "Age": "Mean 48.0 years (SD 11.0)",
        "Sex": "Female: 81 (54%), Male: 69 (46%)",
        // ... other fields for overall sample
        }}
    ]
    }}

    Document content:
    {{paper_content}}
    """

            # 为Outcomes表
            elif table_name == "Outcomes":
                user_prompt = f"""
    Extract information for all outcome measures according to the following schema:

    {field_descriptions}

    FOCUS ONLY ON IDENTIFYING AND DESCRIBING THE OUTCOME MEASURES. The actual results will be extracted separately.

    Be comprehensive and extract ALL outcomes mentioned in the paper, including primary, secondary, and any additional outcomes reported.

    Format your response as a JSON object with an 'outcomes' array containing the extracted data.

    Example JSON structure:
    {{
    "outcomes": [
        {{
        "Outcome_Name": "Pain intensity",
        "Study_ID": "Smith, 2020",
        "Outcome_Type": "Primary",
        "Time_Points": "Baseline, 6 weeks, 12 weeks, 24 weeks",
        "Definition": "Self-reported pain intensity during the past week",
        "Outcome_Definition": "Average pain intensity over the past 7 days",
        "Measurement_Tool": "Visual Analog Scale (VAS)",
        "Unit_of_Measurement": "0-10 scale",
        "Range_of_Measurement": "0-10 scale; categorized as mild (0-3), moderate (4-6), severe (7-10)",
        "Scales": "0 (no pain) to 10 (worst pain imaginable); lower scores indicate better outcomes",
        "Validation": "Yes, validated in chronic pain populations",
        "Evaluation_Type": "Quantitative",
        "Power": "Sample size calculated to detect 1.5-point difference with 90% power",
        "Analysis_Method": "Intention-to-treat analysis with multiple imputation"
        }},
        {{
        "Outcome_Name": "Functional disability",
        "Study_ID": "Smith, 2020",
        "Outcome_Type": "Secondary",
        "Time_Points": "Baseline, 12 weeks, 24 weeks",
        "Definition": "Ability to perform daily activities",
        "Outcome_Definition": "Self-reported functional limitations in daily activities",
        "Measurement_Tool": "Oswestry Disability Index (ODI)",
        "Unit_of_Measurement": "0-100 scale",
        "Range_of_Measurement": "0-100 scale; higher scores indicate greater disability",
        "Scales": "0 (no disability) to 100 (maximum disability); lower scores are better",
        "Validation": "Yes, validated disability measure",
        "Evaluation_Type": "Quantitative",
        "Power": "Powered for primary outcome",
        "Analysis_Method": "Intention-to-treat analysis"
        }}
    ]
    }}

    Document content:
    {{paper_content}}
    """

            # 为Results表
            elif table_name == "Results":
                user_prompt = f"""
    Extract results for each outcome by group according to the following schema:

    {field_descriptions}

    IMPORTANT: Create SEPARATE entries for EACH combination of outcome, group, and time point. Do NOT combine results from different groups in the same entry.

    Format your response as a JSON object with a 'results' array containing the extracted data.

    Example JSON structure:
    {{
    "results": [
        {{
        "Result_ID": "Smith2020_Pain_Exercise_12wk",
        "Outcome_Name": "Pain intensity",
        "Group_Name": "Structured exercise program",
        "Time_Point": "12 weeks",
        "Sample_Size": "72",
        "Data_Complete": "72 of 75 randomized (96%)",
        "Result_Value": "Mean 3.5 (SD 1.8); Mean change from baseline: -3.3 (SD 1.5)",
        "Subgroup_Results": "Age <50 years: Mean 3.0 (SD 1.6); Age ≥50 years: Mean 4.1 (SD 1.9)",
        "Missing_Data": "3 (2 withdrew due to time constraints, 1 lost to follow-up)"
        }},
        {{
        "Result_ID": "Smith2020_Pain_Control_12wk",
        "Outcome_Name": "Pain intensity",
        "Group_Name": "Usual care",
        "Time_Point": "12 weeks",
        "Sample_Size": "70",
        "Data_Complete": "70 of 75 randomized (93%)",
        "Result_Value": "Mean 6.0 (SD 1.7); Mean change from baseline: -0.8 (SD 1.2)",
        "Subgroup_Results": "Age <50 years: Mean 5.8 (SD 1.5); Age ≥50 years: Mean 6.2 (SD 1.8)",
        "Missing_Data": "5 (3 withdrew, 2 lost to follow-up)"
        }}
    ]
    }}

    Document content:
    {{paper_content}}
    """

            # 为Comparisons表
            elif table_name == "Comparisons":
                user_prompt = f"""
    Extract comparisons between groups for each outcome according to the following schema:

    {field_descriptions}

    IMPORTANT: Create one entry for each comparison between groups for each outcome at each time point. Focus on extracting the statistical comparisons, effect sizes, and p-values.

    Format your response as a JSON object with a 'comparisons' array containing the extracted data.

    Example JSON structure:
    {{
    "comparisons": [
        {{
        "Comparison_ID": "Smith2020_Pain_Ex_vs_UC_12wk",
        "Outcome_Name": "Pain intensity",
        "Group1_Name": "Structured exercise program",
        "Group2_Name": "Usual care",
        "Intervention_and_Comparison": "Structured exercise program vs. usual care",
        "Time_Point": "12 weeks",
        "Effect_Estimate": "Mean difference: -2.5 (95% CI: -3.1 to -1.9); p<0.001",
        "Adjusted_Effect": "Adjusted mean difference: -2.3 (95% CI: -2.9 to -1.7); adjusted for baseline pain, age, and sex",
        "Subgroup_Analyses": "Age subgroups: Significant treatment effect in patients <50 years but not ≥50 years",
        "Statistical_Methods": "ANCOVA adjusting for baseline pain scores; intention-to-treat analysis"
        }},
        {{
        "Comparison_ID": "Smith2020_Function_Ex_vs_UC_12wk",
        "Outcome_Name": "Functional disability",
        "Group1_Name": "Structured exercise program",
        "Group2_Name": "Usual care",
        "Intervention_and_Comparison": "Structured exercise program vs. usual care",
        "Time_Point": "12 weeks",
        "Effect_Estimate": "Mean difference: -5.2 (95% CI: -7.8 to -2.6); p=0.002",
        "Adjusted_Effect": "Adjusted mean difference: -4.8 (95% CI: -7.2 to -2.4); adjusted for baseline disability",
        "Subgroup_Analyses": "No significant subgroup interactions detected",
        "Statistical_Methods": "ANCOVA adjusting for baseline disability scores"
        }}
    ]
    }}

    Document content:
    {{paper_content}}
    """

            prompts[table_name] = (system_prompt, user_prompt)

        return prompts

    def call_llm(self, system_prompt, user_prompt, schema=None, **kwargs):
        """Call LLM API with structured JSON output"""
        import json
        import time

        model = kwargs.get('model', self.llm_config['model'])
        temperature = kwargs.get('temperature', 0.0)
        max_tokens = kwargs.get('max_tokens', 4000)
        timeout = kwargs.get('timeout', 300)
        max_retries = kwargs.get('max_retries', 5)

        for attempt in range(max_retries):
            try:
                # 使用更简单的结构化输出方式
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout,
                    response_format={"type": "json_object"} 
                )
            
                # 直接解析JSON
                result = json.loads(response.choices[0].message.content)
                return result
                            
            except Exception as e:
                print(f"LLM call failed (attempt {attempt+1}): {e}")
                if attempt < max_retries-1:
                    wait_time = 2 ** attempt
                    print(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    print("Failed after multiple retries, skipping this one.")
                    return None

    def process_file(self, file_path, split_length=100000):
        """Process file using JSON structured approach"""
        file_name = os.path.basename(file_path)
        print(f"\nProcessing file: {file_name}")

        # 记录开始时间
        overall_start_time = time.time()

        # Read file content
        content = read_file(file_path)
        if content is None:
            print(f"Failed to read, skipping {file_name}")
            return None

        print(f"Number of characters in the file: {len(content)}")

        # 创建提示
        prompts = self.create_prompts()

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
            schema=self.schemas["Study_Info"],
            model=self.llm_config["model"],
            temperature=self.llm_config.get("temperature", 0.0)
        )
    
        if llm_response is None:
            all_extracted_data["Study_Info"] = []
            study_id = file_name.replace(".pdf", "").replace(".docx", "")
        else:
            extracted_data = llm_response.get("studies", [])
            for item in extracted_data:
                item["File_Name"] = file_name
            all_extracted_data["Study_Info"] = extracted_data
        
            # Get study ID for future use
            study_id = extracted_data[0].get("Study_ID", file_name.replace(".pdf", "").replace(".docx", "")) if extracted_data else file_name.replace(".pdf", "").replace(".docx", "")
    
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"  Study_Info completed - Time taken: {elapsed_str} - {len(all_extracted_data.get('Study_Info', []))} records retrieved")
    
        # Step 2: Extract Groups (including original Groups and Interventions information)
        print(f"  Extracting Groups data...")
        start_time = time.time()
    
        system_prompt, prompt_template = prompts["Groups"]
        # Modify the prompt to use Group_Name instead of Group_ID
        modified_prompt = prompt_template.replace("Group_ID", "Group_Name").replace("{paper_content}", content[:split_length])
        # Add instruction to put Study_ID after File_Name and before Group_Name
        modified_prompt = modified_prompt.replace("Format your response as a JSON array of objects",
                                                "Format your response as a JSON object with a 'groups' array. Make sure to place the Study_ID column after File_Name and before Group_Name. Use this Study_ID: " + study_id)
    
        llm_response = self.call_llm(
            system_prompt,
            modified_prompt,
            schema=self.schemas["Groups"],
            model=self.llm_config["model"],
            temperature=self.llm_config.get("temperature", 0.0)
        )
    
        if llm_response is None:
            all_extracted_data["Groups"] = []
            group_names = []
        else:
            extracted_data = llm_response.get("groups", [])
            for item in extracted_data:
                item["File_Name"] = file_name
                item["Study_ID"] = study_id  # Use consistent Study_ID
            all_extracted_data["Groups"] = extracted_data
        
            # Get group names for future use
            group_names = [item.get("Group_Name", "") for item in extracted_data if "Group_Name" in item and item["Group_Name"]]
    
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"  Groups completed - Time taken: {elapsed_str} - {len(all_extracted_data.get('Groups', []))} records retrieved")
    
        # Step 3: Extract Participant_Characteristics with group names
        print(f"  Extracting Participant_Characteristics data...")
        start_time = time.time()
    
        system_prompt, prompt_template = prompts["Participant_Characteristics"]
        # Modify the prompt to use Group_Name instead of Group_ID and provide group names
        modified_prompt = prompt_template.replace("Group_ID", "Group_Name").replace("{paper_content}", content[:split_length])
    
        # Add instruction to use specific group names
        if group_names:
            group_names_str = ", ".join([f'"{name}"' for name in group_names])
            modified_prompt = modified_prompt.replace("Format your response as a JSON array of objects",
                                                    f"Format your response as a JSON object with a 'characteristics' array. Create one entry for each of these exact group names: {group_names_str}. Use the Study_ID: {study_id}")
        else:
            modified_prompt = modified_prompt.replace("Format your response as a JSON array of objects",
                                                    f"Format your response as a JSON object with a 'characteristics' array. Use the Study_ID: {study_id}")
    
        llm_response = self.call_llm(
            system_prompt,
            modified_prompt,
            schema=self.schemas["Participant_Characteristics"],
            model=self.llm_config["model"],
            temperature=self.llm_config.get("temperature", 0.0)
        )
    
        if llm_response is None:
            all_extracted_data["Participant_Characteristics"] = []
        else:
            extracted_data = llm_response.get("characteristics", [])
            for item in extracted_data:
                item["File_Name"] = file_name
                # Ensure group name matches one from the Groups table
                if "Group_Name" in item and item["Group_Name"] and item["Group_Name"] not in group_names:
                    closest_match = next((name for name in group_names if name.lower() in item["Group_Name"].lower() or item["Group_Name"].lower() in name.lower()), None)
                    if closest_match:
                        item["Group_Name"] = closest_match
            all_extracted_data["Participant_Characteristics"] = extracted_data
    
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"  Participant_Characteristics completed - Time taken: {elapsed_str} - {len(all_extracted_data.get('Participant_Characteristics', []))} records obtained")
    
        # Step 4: Extract Outcomes to get Outcome_Names (Interventions step removed)
        print(f"  Extracting Outcomes data...")
        start_time = time.time()
    
        system_prompt, prompt_template = prompts["Outcomes"]
        # Modify the prompt to use Outcome_Name instead of Outcome_ID
        modified_prompt = prompt_template.replace("Outcome_ID", "Outcome_Name").replace("{paper_content}", content[:split_length])
        # Add instruction to put Study_ID after File_Name and before Outcome_Name
        modified_prompt = modified_prompt.replace("Format your response as a JSON array of objects",
                                                "Format your response as a JSON object with an 'outcomes' array. Make sure to place the Study_ID column after File_Name and before Outcome_Name. Use this Study_ID: " + study_id)
    
        llm_response = self.call_llm(
            system_prompt,
            modified_prompt,
            schema=self.schemas["Outcomes"],
            model=self.llm_config["model"],
            temperature=self.llm_config.get("temperature", 0.0)
        )
    
        if llm_response is None:
            all_extracted_data["Outcomes"] = []
            outcome_names = []
        else:
            extracted_data = llm_response.get("outcomes", [])
            for item in extracted_data:
                item["File_Name"] = file_name
                item["Study_ID"] = study_id  # Use consistent Study_ID
            all_extracted_data["Outcomes"] = extracted_data
        
            # Get outcome names for future use
            outcome_names = [item.get("Outcome_Name", "") for item in extracted_data if "Outcome_Name" in item and item["Outcome_Name"]]
    
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"  Outcomes completed - Time taken: {elapsed_str} - {len(all_extracted_data.get('Outcomes', []))} data entries retrieved")
    
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
            outcome_instruction = f"Extract results for these specific outcomes: {outcome_names_str}. "
    
        group_instruction = ""
        if group_names:
            group_names_str = ", ".join([f'"{name}"' for name in group_names])
            group_instruction = f"For each outcome, extract results for these specific groups: {group_names_str}. "
    
        modified_prompt = modified_prompt.replace("Format your response as a JSON array of objects",
                                                f"Format your response as a JSON object with a 'results' array. {outcome_instruction}{group_instruction}Use the Study_ID: {study_id}")
    
        llm_response = self.call_llm(
            system_prompt,
            modified_prompt,
            schema=self.schemas["Results"],
            model=self.llm_config["model"],
            temperature=self.llm_config.get("temperature", 0.0)
        )
    
        if llm_response is None:
            all_extracted_data["Results"] = []
        else:
            extracted_data = llm_response.get("results", [])
            for item in extracted_data:
                item["File_Name"] = file_name
            
                # Ensure outcome name matches one from the Outcomes table
                if "Outcome_Name" in item and item["Outcome_Name"] and item["Outcome_Name"] not in outcome_names:
                    closest_match = next((name for name in outcome_names if name.lower() in item["Outcome_Name"].lower() or item["Outcome_Name"].lower() in name.lower()), None)
                    if closest_match:
                        item["Outcome_Name"] = closest_match
            
                # Ensure group name matches one from the Groups table
                if "Group_Name" in item and item["Group_Name"] and item["Group_Name"] not in group_names:
                    closest_match = next((name for name in group_names if name.lower() in item["Group_Name"].lower() or item["Group_Name"].lower() in name.lower()), None)
                    if closest_match:
                        item["Group_Name"] = closest_match
        
            all_extracted_data["Results"] = extracted_data
    
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"  Results completed - Time taken: {elapsed_str} - {len(all_extracted_data.get('Results', []))} records retrieved")
    
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
            outcome_instruction = f"Extract comparisons for these specific outcomes: {outcome_names_str}. "
    
        group_instruction = ""
        if group_names:
            group_names_str = ", ".join([f'"{name}"' for name in group_names])
            group_instruction = f"Compare between these specific groups: {group_names_str}. "
    
        modified_prompt = modified_prompt.replace("Format your response as a JSON array of objects",
                                                f"Format your response as a JSON object with a 'comparisons' array. {outcome_instruction}{group_instruction}Use the Study_ID: {study_id}")
    
        llm_response = self.call_llm(
            system_prompt,
            modified_prompt,
            schema=self.schemas["Comparisons"],
            model=self.llm_config["model"],
            temperature=self.llm_config.get("temperature", 0.0)
        )
    
        if llm_response is None:
            all_extracted_data["Comparisons"] = []
        else:
            extracted_data = llm_response.get("comparisons", [])
            for item in extracted_data:
                item["File_Name"] = file_name
            
                # Ensure outcome name matches one from the Outcomes table
                if "Outcome_Name" in item and item["Outcome_Name"] and item["Outcome_Name"] not in outcome_names:
                    closest_match = next((name for name in outcome_names if name.lower() in item["Outcome_Name"].lower() or item["Outcome_Name"].lower() in name.lower()), None)
                    if closest_match:
                        item["Outcome_Name"] = closest_match
            
                # Ensure group names match ones from the Groups table
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
        print(f"  Comparisons completed - Time taken: {elapsed_str} - {len(all_extracted_data.get('Comparisons', []))} records retrieved")
        
        # 后处理数据，格式化字典并处理缺失值
        all_extracted_data = post_process_data(all_extracted_data)
    
        # Calculate the total processing time
        overall_elapsed_time = time.time() - overall_start_time
        overall_elapsed_str = time.strftime("%H:%M:%S", time.gmtime(overall_elapsed_time))
        print(f"\nTotal processing time for file {file_name}: {overall_elapsed_str}")
        
        # Record the study processing time to the log file
        try:
            with open("extraction_timing.csv", "a") as f:
                f.write(f"{file_name},{study_id},{overall_elapsed_time:.1f},{overall_elapsed_str}\n")
        except Exception as e:
            print(f"Error recording time log: {e}")
    
        return all_extracted_data
