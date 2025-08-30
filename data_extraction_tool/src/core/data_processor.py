"""
Core data processing functions
Handles post-processing, merging, and validation
"""
import re
import copy

def format_dictionary_value(value):
    """Format dictionary values to a readable string with semicolons between items"""
    if isinstance(value, dict):
        formatted_items = [f"{key}: {val}" for key, val in value.items()]
        return "; ".join(formatted_items)
    return value

def post_process_data(data):
    """Post-process extracted data to format dictionaries and handle missing values"""
    processed_data = {}
  
    for table_name, table_data in data.items():
        processed_table = []
        if table_name == "Participant_Characteristics" and table_data:
            table_data = split_mixed_characteristics(table_data)
      
        for item in table_data:
            processed_item = {}
          
            for key, value in item.items():
                # Format dictionary values
                if isinstance(value, dict):
                    processed_item[key] = format_dictionary_value(value)
                # Handle empty or None values
                elif value is None or value == "" or value == "null":
                    processed_item[key] = "Not reported"
                else:
                    processed_item[key] = value
          
            processed_table.append(processed_item)
      
        processed_data[table_name] = processed_table
  
    return processed_data

def merge_results(existing_data, new_data):
    """Merge new extracted data with existing data"""
    if not existing_data:
        return new_data
    
    import copy
    merged_data = copy.deepcopy(existing_data)
    
    merge_stats = {}
    
    for table_name, table_data in new_data.items():
        if table_name not in merged_data:
            merged_data[table_name] = copy.deepcopy(table_data)
            merge_stats[table_name] = len(table_data)
            continue

        if not table_data:
            merge_stats[table_name] = 0
            continue
            
        if merged_data[table_name] and table_data and "File_Name" in table_data[0]:
            for item in merged_data[table_name]:
                if "File_Name" not in item:
                    item["File_Name"] = "Unknown"
        
        added_count = 0
        for item in table_data:
            item_copy = copy.deepcopy(item)
            merged_data[table_name].append(item_copy)
            added_count += 1
        
        merge_stats[table_name] = f"Added: {added_count}"

    print("Data Merge Statistics:")
    for table, stats in merge_stats.items():
        print(f"  {table}: {stats}")
    
    return merged_data


def split_mixed_characteristics(participant_chars):
    """Parse mixed participant characteristics data"""
    if not participant_chars:
        return participant_chars
  
    characteristic_fields = ["Age", "Sex", "Race_Ethnicity", "BMI", "Height_Weight", 
                             "Smoking", "Alcohol", "Physical_Activity", "Education", 
                             "Employment", "Income", "Marital_Status", "Duration_of_Condition", 
                             "Severity_of_Illness", "Comorbidities", "Medication_Use", 
                             "Previous_Treatments"]
  
    new_participant_chars = []
    for char in participant_chars:
        group = char.get("Group", "")
        if not group:
            new_participant_chars.append(char)
            continue
      
        # 检查是否需要处理混合数据
        needs_processing = False
        for field in characteristic_fields:
            if field in char and char[field] != "Not reported":
                # 检查是否包含其他组的数据
                for other_char in participant_chars:
                    other_group = other_char.get("Group", "")
                    if other_group and other_group != group:
                        if other_group in char[field]:
                            needs_processing = True
                            break
            if needs_processing:
                break
      
        if not needs_processing:
            new_participant_chars.append(char)
            continue
      
        processed_char = char.copy()
        for field in characteristic_fields:
            if field in char and char[field] != "Not reported":

                group_specific_data = extract_group_specific_data(char[field], group)
                if group_specific_data:
                    processed_char[field] = group_specific_data
      
        new_participant_chars.append(processed_char)
  
    return new_participant_chars


def extract_group_specific_data(mixed_data, group_name):
    """Extract group-specific data from mixed strings"""
    if not isinstance(mixed_data, str):
        return mixed_data
      
    # 尝试一些常见的匹配模式
    patterns = [
        rf"{group_name}\s*[:]\s*([^;]+)",  # 组名: 数据;
        rf"{group_name}\s*[,]\s*([^;]+)",  # 组名, 数据;
        rf"{group_name}\s*group\s*[:]\s*([^;]+)",  # 组名 group: 数据;
        rf"{group_name}\s*arm\s*[:]\s*([^;]+)",  # 组名 arm: 数据;
        rf"{group_name}\s*[(]n\s*=\s*\d+[)]\s*[:]\s*([^;]+)"  # 组名 (n=X): 数据;
    ]
  
    for pattern in patterns:
        match = re.search(pattern, mixed_data, re.IGNORECASE)
        if match:
            return match.group(1).strip()
  
    blocks = re.split(r';\s*', mixed_data)
    for block in blocks:
        if group_name.lower() in block.lower():
            clean_block = re.sub(rf"{group_name}\s*[:]\s*", "", block, flags=re.IGNORECASE)
            return clean_block.strip()
  
    return mixed_data
