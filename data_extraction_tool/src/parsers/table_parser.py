"""
Parser for table format responses
Handles tab-separated, space-separated, markdown tables, etc.
"""
import re
import time
import os
import json

class TableParser:
    """Parser for table format LLM responses"""
    
    def __init__(self, repair_client=None, repair_llm_config=None, debug_folder=None):
        self.repair_client = repair_client
        self.repair_llm_config = repair_llm_config
        self.debug_folder = debug_folder
    
    def parse_response(self, response_text):
        """Parse table format response into structured data"""
        if not response_text:
            print("Warning: Received an empty response")
            return []
        
        if self.debug_folder:
            os.makedirs(self.debug_folder, exist_ok=True)
            debug_file = os.path.join(self.debug_folder, f"debug_raw_response_{int(time.time())}.txt")
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(response_text)
        # 创建debug文件夹
        if self.debug_folder:
            os.makedirs(self.debug_folder, exist_ok=True)
        
        # 保存原始响应用于调试
        with open(os.path.join(self.debug_folder, f"debug_raw_response_{int(time.time())}.txt"), "w", encoding="utf-8") as f:
            f.write(response_text)
        
        # 尝试多种表格格式解析方法
        entries = []
        
        # 1. 首先尝试解析制表符分隔的表格
        if '\t' in response_text:
            try:
                lines = [line.strip() for line in response_text.split('\n') if line.strip()]
                if len(lines) >= 2:
                    headers = [h.strip() for h in lines[0].split('\t')]
                    headers_count = len(headers)
                    
                    for i, line in enumerate(lines[1:], 1):
                        values = line.split('\t')
                        
                        # 确保与表头数量匹配
                        if len(values) < headers_count:
                            print(f"Warning: The number of columns in row {i} ({len(values)}) is less than the number of headers ({headers_count}). Automatically filling in empty values.")
                            values.extend(['Not reported'] * (headers_count - len(values)))
                        elif len(values) > headers_count:
                            print(f"Warning: The number of columns in row {i} ({len(values)}) is more than the number of headers ({headers_count}). Truncating excess values.")
                            values = values[:headers_count]
                        
                        # 创建字典并添加
                        entry = {headers[j]: values[j].strip() for j in range(headers_count)}
                        entries.append(entry)
                    
                    if entries:
                        print(f"Successfully parsed tab-separated table, extracted {len(entries)} records")
                        return entries
            except Exception as e:
                print(f"Failed to parse tab-separated table: {e}")
        
        # 2. 尝试解析空格分隔的表格
        try:
            # 首先检测是否有连续多个空格的行，这通常表示是空格分隔的表格
            space_separated_pattern = re.compile(r'(\S+(?:\s{2,}\S+)+)')
            if any(space_separated_pattern.search(line) for line in response_text.split('\n')):
                lines = [line.strip() for line in response_text.split('\n') if line.strip() and space_separated_pattern.search(line)]
                
                if len(lines) >= 2:
                    # 分析第一行作为表头，识别每列的起始位置
                    headers_line = lines[0]
                    column_positions = []
                    header_names = []
                    
                    # 找出表头中每列的起始位置
                    for match in re.finditer(r'\S+', headers_line):
                        column_positions.append(match.start())
                        header_names.append(match.group())
                    
                    # 处理每一行数据
                    for i, line in enumerate(lines[1:], 1):
                        if len(line) < max(column_positions):
                            continue  # 行太短，跳过
                        
                        entry = {}
                        for j in range(len(column_positions)):
                            start = column_positions[j]
                            end = column_positions[j+1] if j+1 < len(column_positions) else None
                            
                            value = line[start:end].strip() if end else line[start:].strip()
                            entry[header_names[j]] = value
                        
                        entries.append(entry)
                    
                    if entries:
                        print(f"Successfully parsed space-separated table, extracted {len(entries)} records")
                        return entries
        except Exception as e:
            print(f"Failed to parse space-separated table: {e}")
        
        # 3. 尝试解析Markdown表格
        try:
            md_table_pattern = r'(\|[^\n]+\|\n\|[-:| ]+\|\n(?:\|[^\n]+\|\n)+)'
            table_matches = re.findall(md_table_pattern, response_text, re.MULTILINE)
            
            if table_matches:
                for table_match in table_matches:
                    lines = table_match.strip().split('\n')
                    headers = [h.strip() for h in lines[0].strip('|').split('|')]
                    data_lines = lines[2:]
                    
                    for line in data_lines:
                        if '|' not in line:
                            continue
                        values = [v.strip() for v in line.strip('|').split('|')]
                        if len(values) > 0:

                            if len(values) < len(headers):
                                values.extend(['Not reported'] * (len(headers) - len(values)))
                            elif len(values) > len(headers):
                                values = values[:len(headers)]
                            
                            entry = {headers[i]: values[i] for i in range(len(headers))}
                            entries.append(entry)
                
                if entries:
                    print(f"Successfully parsed Markdown table, extracted {len(entries)} records")
                    return entries
        except Exception as e:
            print(f"Failed to parse Markdown table: {e}")
        
        # 4. Try to parse the field:value format (Key: Value)
        try:
            # Identify the following patterns:
            # Group: Group A
            # Age: Mean 65.2 years
            # Sex: Male 60%, Female 40%
            
            field_pattern = r'([A-Za-z_]+):\s*(.*?)(?=\n[A-Za-z_]+:|$)'
            matches = re.findall(field_pattern, response_text, re.DOTALL)
            
            if matches:
                fields = [m[0] for m in matches]
                field_counts = {f: fields.count(f) for f in set(fields)}
                
                separator_field = max(field_counts, key=field_counts.get)
                
                if field_counts[separator_field] > 1:
                    current_entry = {}
                    for field, value in matches:
                        if field == separator_field and current_entry:
                            entries.append(current_entry.copy())
                            current_entry = {}
                        current_entry[field] = value.strip()
                    
                    if current_entry:
                        entries.append(current_entry)
                else:
                    entry = {field: value.strip() for field, value in matches}
                    entries.append(entry)
                
                if entries:
                    print(f"Successfully parsed field:value format, extracted {len(entries)} records")
                    return entries
        except Exception as e:
            print(f"Failed to parse field:value format: {e}")
        
        # If all standard parsing methods fail, use LLM to repair format
        if self.repair_client and self.repair_llm_config:
            print("All parsing methods failed, attempting to repair format with LLM...")
            return self._repair_with_llm(response_text)

        # Log failure reason and save problematic response
        print("Warning: Unable to parse structured data from response")
        with open(f"parsing_failed_{int(time.time())}.txt", "w", encoding="utf-8") as f:
            f.write("===== FAILED TO PARSE THE FOLLOWING RESPONSE =====\n\n")
            f.write(response_text)
        
        return []

    def _repair_with_llm(self, response_text, max_retries=3):
        """Use LLM to repair malformed table format"""
        if self.debug_folder:
            os.makedirs(self.debug_folder, exist_ok=True)

        system_prompt = (
            "You are a data formatting assistant specialized in converting unstructured or poorly formatted data into "
            "clean tab-separated tables. Your job is to take the text and produce ONLY a tab-separated table with the "
            "following characteristics:\n"
            "1. First line should contain all column headers separated by tabs\n"
            "2. Each subsequent line should contain values for one entry, with fields separated by tabs\n"
            "3. All lines should have exactly the same number of tab-separated fields\n"
            "4. Do not include any markdown formatting, explanations, or other text\n"
            "5. If data appears to be missing, use 'Not reported' as the value\n"
            "6. Preserve all field names exactly as they appear in the input"
        )
        
        user_prompt = (
            "The following text contains participant characteristics data that needs to be converted to a proper tab-separated table. "
            "The data appears to be about study participants, possibly including fields like Group, Age, Sex, etc. "
            "Please convert it to a clean tab-separated table format.\n\n"
            "Create a table with appropriate column headers, and make sure every row has the same number of tab-separated values. "
            "Identify all relevant fields and ensure they're consistently represented across all entries. "
            "Only output the formatted table, nothing else.\n\n"
            f"{response_text}"
        )
        
        for attempt in range(max_retries):
            try:
                repair_response = self.repair_client.chat.completions.create(
                    model=self.repair_llm_config["model"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.0,
                    timeout=120
                )
                
                repaired_text = repair_response.choices[0].message.content
                
                if self.debug_folder:
                    with open(os.path.join(self.debug_folder, f"repaired_text_{int(time.time())}.txt"), "w", encoding="utf-8") as f:
                        f.write(repaired_text)
                
                if '\t' in repaired_text:
                    lines = [line.strip() for line in repaired_text.split('\n') if line.strip()]
                    if len(lines) >= 2:
                        headers = [h.strip() for h in lines[0].split('\t')]
                        entries = []
                        
                        for line in lines[1:]:
                            if not line.strip():
                                continue
                            values = [v.strip() for v in line.split('\t')]
                            
                            if len(values) < len(headers):
                                values.extend(["Not reported"] * (len(headers) - len(values)))
                            elif len(values) > len(headers):
                                values = values[:len(headers)]
                            
                            entry = {headers[i]: values[i] for i in range(len(headers))}
                            entries.append(entry)
                        
                        if entries:
                            print(f"LLM successfully fixed the table format and extracted {len(entries)} records")
                            return entries
                
                print(f"No tab characters found in the LLM-repaired data (attempt {attempt+1}/{max_retries})")
                
                if '|' in repaired_text and '-|' in repaired_text:
                    md_table_pattern = r'(\|[^\n]+\|\n\|[-:| ]+\|\n(?:\|[^\n]+\|\n)+)'
                    table_matches = re.findall(md_table_pattern, repaired_text, re.MULTILINE)
                    
                    if table_matches:
                        print("Markdown table format detected, attempting to parse...")
                        entries = []
                        for table_match in table_matches:
                            lines = table_match.strip().split('\n')
                            headers = [h.strip() for h in lines[0].strip('|').split('|')]
                            data_lines = lines[2:]  # 跳过表头和分隔线
                            
                            for line in data_lines:
                                if '|' not in line:
                                    continue
                                values = [v.strip() for v in line.strip('|').split('|')]
                                if len(values) < len(headers):
                                    values.extend(["Not reported"] * (len(headers) - len(values)))
                                elif len(values) > len(headers):
                                    values = values[:len(headers)]
                                
                                entry = {headers[i]: values[i] for i in range(len(headers))}
                                entries.append(entry)
                        
                        if entries:
                            print(f"Successfully parsed {len(entries)} records from Markdown table")
                            return entries

                if attempt < max_retries - 1:
                    user_prompt = (
                        "The previous response wasn't in the correct format. Please convert the data to a STRICT tab-separated table. "
                        "Use actual tab characters to separate fields, not spaces or other characters. "
                        "First line should be column headers, separated by tabs. Each subsequent line should be values, separated by tabs. "
                        "Here is the original data again:\n\n"
                        f"{response_text}"
                    )
                else:
                    print("Maximum retries reached, failed to fix table format")
                    return []
            
            except Exception as e:
                print(f"LLM format repair failed (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    print("Maximum retries reached, failed to fix table format")
                    return []
        
        return []