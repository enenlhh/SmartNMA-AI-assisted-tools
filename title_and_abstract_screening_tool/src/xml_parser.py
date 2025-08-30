"""
XML Parser Module
Supports both Zotero and EndNote XML formats with enhanced parsing capabilities
"""

import xml.etree.ElementTree as ET
import pandas as pd
import os
import re
from datetime import datetime

class XMLFormatDetector:
    """XML format detector for identifying Zotero or EndNote formats"""
    
    @staticmethod
    def detect_format(xml_path):
        """Detect XML file format
        
        Returns:
            str: 'zotero', 'endnote', or 'unknown'
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Check first record
            first_record = root.find('.//record')
            if first_record is None:
                return 'unknown'
            
            # Check source-app attribute
            source_app = root.find('.//source-app')
            if source_app is not None:
                app_name = source_app.get('name', '').lower()
                if 'zotero' in app_name:
                    return 'zotero'
                elif 'endnote' in app_name:
                    return 'endnote'
            
            # Check title structure for further confirmation
            title_elem = first_record.find('.//titles/title')
            if title_elem is not None:
                # Check for style tags (EndNote feature)
                style_elem = title_elem.find('.//style')
                if style_elem is not None:
                    return 'endnote'
                elif title_elem.text is not None:
                    return 'zotero'
            
            return 'unknown'
            
        except Exception as e:
            print(f"Error detecting XML format: {str(e)}")
            return 'unknown'

class UniversalXMLParser:
    """Universal XML parser supporting both Zotero and EndNote formats with enhanced data extraction"""
    
    def __init__(self):
        self.format_detector = XMLFormatDetector()
        self.llm_names = set()  # Store LLM names for column generation
        self.xml_format = None
    
    def parse_xml(self, xml_path):
        """Parse XML file with automatic format detection and basic record extraction"""
        # Detect format
        self.xml_format = self.format_detector.detect_format(xml_path)
        print(f"Detected XML format: {self.xml_format.upper()}")
        
        if self.xml_format == 'zotero':
            return self._parse_zotero_xml(xml_path)
        elif self.xml_format == 'endnote':
            return self._parse_endnote_xml(xml_path)
        else:
            raise ValueError(f"Unsupported XML format or unable to identify format")
    
    def parse_xml_enhanced(self, xml_path):
        """Parse XML file with enhanced data extraction for screening results"""
        # Detect format first
        self.xml_format = self.format_detector.detect_format(xml_path)
        print(f"Detected XML format: {self.xml_format.upper()}")
        
        if self.xml_format not in ['zotero', 'endnote']:
            raise ValueError(f"Unsupported XML format or unable to identify format")
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Get all record elements
            records = root.findall('.//record')
            print(f"Found {len(records)} records")
            
            # Parse each record with enhanced extraction
            all_records_data = []
            for i, record in enumerate(records):
                print(f"Processing record {i + 1}/{len(records)}...")
                record_data = self._extract_enhanced_record_data(record)
                if record_data:
                    all_records_data.append(record_data)
            
            return all_records_data, tree, root, self.xml_format
            
        except Exception as e:
            print(f"Error parsing XML file: {str(e)}")
            raise
    
    def _parse_zotero_xml(self, xml_path):
        """Parse Zotero format XML"""
        print("Using Zotero parsing scheme...")
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        records = root.findall('.//record')
        parsed_records = []
        
        for record in records:
            rec_data = {}
            
            # Extract title - Zotero format contains text directly
            title_elem = record.find('.//titles/title')
            if title_elem is not None and title_elem.text:
                rec_data['title'] = title_elem.text
            else:
                rec_data['title'] = "No title found"
            
            # Extract abstract - Zotero format contains text directly
            abstract_elem = record.find('.//abstract')
            if abstract_elem is not None and abstract_elem.text:
                rec_data['abstract'] = abstract_elem.text
            else:
                rec_data['abstract'] = "No abstract found"
            
            # Get keywords element, create if doesn't exist
            keywords_elem = record.find('.//keywords')
            if keywords_elem is None:
                keywords_elem = ET.SubElement(record, 'keywords')
            
            rec_data['record_elem'] = record
            rec_data['keywords_elem'] = keywords_elem
            rec_data['xml_format'] = 'zotero'
            
            parsed_records.append(rec_data)
        
        return parsed_records, tree, root, 'zotero'
    
    def _parse_endnote_xml(self, xml_path):
        """Parse EndNote format XML"""
        print("Using EndNote parsing scheme...")
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        records = root.findall('.//record')
        parsed_records = []
        
        for record in records:
            rec_data = {}
            
            # Extract title - EndNote format needs extraction from style tags
            title_elem = record.find('.//titles/title')
            if title_elem is not None:
                # Try to get text from style tag
                style_elem = title_elem.find('.//style')
                if style_elem is not None and style_elem.text:
                    rec_data['title'] = style_elem.text
                elif title_elem.text:
                    rec_data['title'] = title_elem.text
                else:
                    rec_data['title'] = "No title found"
            else:
                rec_data['title'] = "No title found"
            
            # Extract abstract - EndNote format needs extraction from style tags
            abstract_elem = record.find('.//abstract')
            if abstract_elem is not None:
                # Try to get text from style tag
                style_elem = abstract_elem.find('.//style')
                if style_elem is not None and style_elem.text:
                    rec_data['abstract'] = style_elem.text
                elif abstract_elem.text:
                    rec_data['abstract'] = abstract_elem.text
                else:
                    rec_data['abstract'] = "No abstract found"
            else:
                rec_data['abstract'] = "No abstract found"
            
            # Get keywords element, create if doesn't exist
            keywords_elem = record.find('.//keywords')
            if keywords_elem is None:
                keywords_elem = ET.SubElement(record, 'keywords')
            
            rec_data['record_elem'] = record
            rec_data['keywords_elem'] = keywords_elem
            rec_data['xml_format'] = 'endnote'
            
            parsed_records.append(rec_data)
        
        return parsed_records, tree, root, 'endnote'
    
    def _extract_enhanced_record_data(self, record):
        """Extract comprehensive data from a single record including screening results
        
        Args:
            record: XML record element
            
        Returns:
            dict: Comprehensive record data
        """
        record_data = {}
        
        # Extract basic bibliographic information
        record_data.update(self._extract_basic_info(record))
        
        # Extract screening results from keywords
        record_data.update(self._extract_screening_results(record))
        
        return record_data
    
    def _extract_basic_info(self, record):
        """Extract basic bibliographic information"""
        data = {}
        
        # Extract title based on format
        if self.xml_format == 'zotero':
            title_elem = record.find('.//titles/title')
            if title_elem is not None and title_elem.text:
                data['Title'] = title_elem.text
            else:
                data['Title'] = "No title found"
        elif self.xml_format == 'endnote':
            title_elem = record.find('.//titles/title/style')
            if title_elem is not None and title_elem.text:
                data['Title'] = title_elem.text
            else:
                # Fallback to non-style title
                title_elem = record.find('.//titles/title')
                if title_elem is not None and title_elem.text:
                    data['Title'] = title_elem.text
                else:
                    data['Title'] = "No title found"
        
        # Extract abstract based on format
        if self.xml_format == 'zotero':
            abstract_elem = record.find('.//abstract')
            if abstract_elem is not None and abstract_elem.text:
                data['Abstract'] = abstract_elem.text
            else:
                data['Abstract'] = "No abstract found"
        elif self.xml_format == 'endnote':
            abstract_elem = record.find('.//abstract/style')
            if abstract_elem is not None and abstract_elem.text:
                data['Abstract'] = abstract_elem.text
            else:
                # Fallback to non-style abstract
                abstract_elem = record.find('.//abstract')
                if abstract_elem is not None and abstract_elem.text:
                    data['Abstract'] = abstract_elem.text
                else:
                    data['Abstract'] = "No abstract found"
        
        # Extract authors
        authors = []
        if self.xml_format == 'zotero':
            authors_elem = record.findall('.//contributors/authors/author')
            for author in authors_elem:
                author_text = ""
                if author.find('style') is not None and author.find('style').text:
                    author_text = author.find('style').text
                elif author.find('lastname') is not None:
                    last_name = author.find('lastname').text or ""
                    first_name = ""
                    if author.find('firstname') is not None and author.find('firstname').text:
                        first_name = author.find('firstname').text
                    author_text = f"{last_name}, {first_name}".strip(", ")
                
                if author_text:
                    authors.append(author_text)
        elif self.xml_format == 'endnote':
            authors_elem = record.findall('.//contributors/authors/author/style')
            for author in authors_elem:
                if author.text:
                    authors.append(author.text)
        
        data['Authors'] = "; ".join(authors) if authors else "No authors found"
        
        # Extract publication year
        if self.xml_format == 'zotero':
            year_elem = record.find('.//dates/year')
            if year_elem is not None and year_elem.text:
                data['Year'] = year_elem.text
            else:
                data['Year'] = "No year found"
        elif self.xml_format == 'endnote':
            year_elem = record.find('.//dates/year/style')
            if year_elem is not None and year_elem.text:
                data['Year'] = year_elem.text
            else:
                # Fallback to non-style year
                year_elem = record.find('.//dates/year')
                if year_elem is not None and year_elem.text:
                    data['Year'] = year_elem.text
                else:
                    data['Year'] = "No year found"
        
        return data
    
    def _extract_screening_results(self, record):
        """Extract screening results from keywords"""
        data = {}
        
        # Get keywords based on format
        if self.xml_format == 'zotero':
            keywords = record.findall('.//keywords/keyword')
        elif self.xml_format == 'endnote':
            keywords = record.findall('.//keywords/keyword/style')
        else:
            keywords = []
        
        # Initialize fields with default values
        data['Prefilter_Result'] = "Not Available"
        data['Decision_Status'] = ""
        
        # Storage for LLM decisions and PICOS data
        llm_decisions = {}
        picos_data = {}
        has_prefilter_exclusion = False
        
        # Process all keywords to extract screening results
        for keyword in keywords:
            keyword_text = keyword.text if keyword.text else ""
            
            # Extract prefilter results
            if "EXCLUDE - " in keyword_text and "(matched:" in keyword_text:
                data['Prefilter_Result'] = keyword_text
                has_prefilter_exclusion = True
                continue
            
            # Extract LLM decisions
            decision_match = re.match(r'(✅ INCLUDE|❌ EXCLUDE|⭕️ UNCLEAR)(.*)\((.*?)\)$', keyword_text)
            if decision_match:
                decision = decision_match.group(1).strip()
                explanation = decision_match.group(2).strip()
                llm_name = decision_match.group(3).strip()
                
                # Record LLM name for column generation
                self.llm_names.add(llm_name)
                
                # Store decision and explanation
                llm_decisions[llm_name] = {
                    'decision': decision,
                    'explanation': explanation
                }
                
                # Create decision result column
                data[f"{llm_name}_Decision"] = f"{decision}{' - ' + explanation if explanation else ''}"
                continue
            
            # Check for conflict or uncertainty markers
            if "⚠️ CONFLICT" in keyword_text:
                data['Decision_Status'] = "⚠️ Conflict"
                continue
            
            if "⚠️ UNCERTAIN" in keyword_text:
                data['Decision_Status'] = "⚠️ Uncertain"
                continue
            
            # Extract PICOS data
            picos_match = re.match(r'([SPICO]): (.*) \((.*?)\)$', keyword_text)
            if picos_match:
                picos_type = picos_match.group(1)
                picos_content = picos_match.group(2)
                llm_name = picos_match.group(3)
                
                # Record LLM name
                self.llm_names.add(llm_name)
                
                # Initialize PICOS data structure if not exists
                if llm_name not in picos_data:
                    picos_data[llm_name] = {}
                
                # Store PICOS data
                picos_data[llm_name][picos_type] = picos_content
        
        # Process results based on prefilter status
        if has_prefilter_exclusion:
            # Set all LLM columns to "Not Available" for prefiltered records
            for llm in self.llm_names:
                data[f"{llm}_Decision"] = "Not Available"
                for picos_type, label in [("P", "Participants"), ("I", "Intervention"),
                                        ("C", "Comparison"), ("O", "Outcomes"), ("S", "Study design")]:
                    data[f"{label} ({llm})"] = "Not Available"
            
            data['Decision_Status'] = "❌ Recommended Exclusion"
        else:
            # Process LLM decisions for non-prefiltered records
            if not data['Decision_Status'] and len(llm_decisions) > 0:
                data['Decision_Status'] = self._determine_decision_status(llm_decisions)
            
            # Process PICOS data
            for llm_name, picos in picos_data.items():
                for picos_type, content in picos.items():
                    column_name = self._get_picos_column_name(picos_type, llm_name)
                    if column_name:
                        data[column_name] = content
        
        # Ensure default Decision_Status if still empty
        if not data['Decision_Status']:
            if len(llm_decisions) == 1:
                decision = list(llm_decisions.values())[0]['decision']
                if "✅ INCLUDE" in decision:
                    data['Decision_Status'] = "✅ Recommended Inclusion"
                elif "❌ EXCLUDE" in decision:
                    data['Decision_Status'] = "❌ Recommended Exclusion"
                else:
                    data['Decision_Status'] = "⚠️ Uncertain"
            else:
                data['Decision_Status'] = "⚠️ Uncertain"
        
        # Ensure all LLM columns have values for consistency
        self._ensure_column_consistency(data, has_prefilter_exclusion)
        
        return data
    
    def _determine_decision_status(self, llm_decisions):
        """Determine overall decision status based on LLM decisions"""
        core_decisions = []
        for llm_name, decision_info in llm_decisions.items():
            decision = decision_info['decision']
            if "✅ INCLUDE" in decision:
                core_decisions.append("INCLUDE")
            elif "❌ EXCLUDE" in decision:
                core_decisions.append("EXCLUDE")
            else:
                core_decisions.append("UNCLEAR")
        
        # Determine status based on decision combinations
        if len(set(core_decisions)) > 1:
            return "⚠️ Conflict"
        elif len(core_decisions) > 0:
            if all(d == "UNCLEAR" for d in core_decisions):
                return "⚠️ Uncertain"
            elif all(d == "INCLUDE" for d in core_decisions):
                return "✅ Recommended Inclusion"
            elif all(d == "EXCLUDE" for d in core_decisions):
                return "❌ Recommended Exclusion"
        
        return "⚠️ Uncertain"
    
    def _get_picos_column_name(self, picos_type, llm_name):
        """Get column name for PICOS data"""
        picos_mapping = {
            "P": f"Participants ({llm_name})",
            "I": f"Intervention ({llm_name})",
            "C": f"Comparison ({llm_name})",
            "O": f"Outcomes ({llm_name})",
            "S": f"Study design ({llm_name})"
        }
        return picos_mapping.get(picos_type, "")
    
    def _ensure_column_consistency(self, data, has_prefilter_exclusion):
        """Ensure all LLM columns have values for consistent table format"""
        for llm in self.llm_names:
            # Decision columns
            if f"{llm}_Decision" not in data and not has_prefilter_exclusion:
                data[f"{llm}_Decision"] = "No decision data found"
            
            # PICOS columns
            for picos_type, label in [("P", "Participants"), ("I", "Intervention"),
                                    ("C", "Comparison"), ("O", "Outcomes"), ("S", "Study design")]:
                column_name = f"{label} ({llm})"
                if column_name not in data and not has_prefilter_exclusion:
                    data[column_name] = "No data found"
    
    def create_enhanced_excel(self, xml_path, output_dir=None):
        """Parse XML and create enhanced Excel with screening results"""
        # Parse XML data with enhanced extraction
        records_data, tree, root, xml_format = self.parse_xml_enhanced(xml_path)
        
        if not records_data:
            print("No valid records found, cannot create Excel file")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(records_data)
        
        # Optimize column order
        desired_columns = ['Title', 'Authors', 'Year', 'Abstract', 'Prefilter_Result', 'Decision_Status']
        
        # Add LLM decision columns
        for llm in sorted(self.llm_names):
            desired_columns.append(f"{llm}_Decision")
        
        # Add PICOS columns for each LLM
        for llm in sorted(self.llm_names):
            desired_columns.extend([
                f"Study design ({llm})",
                f"Participants ({llm})",
                f"Intervention ({llm})",
                f"Comparison ({llm})",
                f"Outcomes ({llm})"
            ])
        
        # Reorder columns (only include existing columns)
        actual_columns = [col for col in desired_columns if col in df.columns]
        remaining_columns = [col for col in df.columns if col not in actual_columns]
        df = df[actual_columns + remaining_columns]
        
        # Generate summary
        summary_data = self._generate_summary(records_data, xml_path)
        summary_df = pd.DataFrame([summary_data])
        
        # Generate output filename
        if output_dir is None:
            output_dir = os.path.dirname(xml_path)
        
        base_filename = os.path.splitext(os.path.basename(xml_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_excel = os.path.join(output_dir, f"{base_filename}_parsed_{timestamp}.xlsx")
        
        # Create Excel file with multiple sheets
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            # Write main data sheet
            df.to_excel(writer, sheet_name='Screening Results', index=False)
            
            # Write summary sheet
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"Enhanced Excel file created: {output_excel}")
        return output_excel
    
    def _generate_summary(self, records_data, xml_path):
        """Generate screening results summary"""
        summary = {
            "Total records": len(records_data),
            "Date of analysis": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "XML file": os.path.basename(xml_path)
        }
        
        # Prefilter statistics
        prefiltered = sum(1 for r in records_data if r.get('Prefilter_Result', '') != "Not Available")
        summary["Excluded by prefilter"] = prefiltered
        summary["Evaluated by LLMs"] = summary["Total records"] - prefiltered
        
        # Decision status statistics
        status_counts = {
            "✅ Recommended Inclusion": 0,
            "❌ Recommended Exclusion": 0,
            "⚠️ Conflict": 0,
            "⚠️ Uncertain": 0
        }
        
        for record in records_data:
            status = record.get('Decision_Status', '')
            if status in status_counts:
                status_counts[status] += 1
        
        # Add to summary
        summary.update(status_counts)
        summary["Recommended for inclusion"] = status_counts["✅ Recommended Inclusion"]
        summary["Recommended for exclusion"] = status_counts["❌ Recommended Exclusion"]
        summary["Conflict between LLMs"] = status_counts["⚠️ Conflict"]
        summary["Uncertain decisions"] = status_counts["⚠️ Uncertain"]
        
        # Calculate percentages
        total_count = summary["Total records"]
        if total_count > 0:
            for key in ["Recommended for inclusion", "Recommended for exclusion", 
                       "Conflict between LLMs", "Uncertain decisions"]:
                summary[f"% {key.lower()}"] = round(summary[key] / total_count * 100, 1)
        
        # LLM agreement rate
        evaluated_count = summary["Evaluated by LLMs"]
        if evaluated_count > 0:
            non_conflict_count = evaluated_count - summary["Conflict between LLMs"]
            summary["LLM agreement rate"] = round(non_conflict_count / evaluated_count * 100, 1)
        
        # Individual LLM statistics
        for llm in sorted(self.llm_names):
            include_count = exclude_count = unclear_count = 0
            
            for record in records_data:
                if record.get('Prefilter_Result', '') != "Not Available":
                    continue
                
                decision_col = f"{llm}_Decision"
                if decision_col in record:
                    decision = record[decision_col]
                    if "✅ INCLUDE" in decision:
                        include_count += 1
                    elif "❌ EXCLUDE" in decision:
                        exclude_count += 1
                    elif "⭕️ UNCLEAR" in decision:
                        unclear_count += 1
            
            summary[f"{llm} - INCLUDE"] = include_count
            summary[f"{llm} - EXCLUDE"] = exclude_count
            summary[f"{llm} - UNCLEAR"] = unclear_count
            
            if evaluated_count > 0:
                summary[f"{llm} - % INCLUDE"] = round(include_count / evaluated_count * 100, 1)
                summary[f"{llm} - % EXCLUDE"] = round(exclude_count / evaluated_count * 100, 1)
                summary[f"{llm} - % UNCLEAR"] = round(unclear_count / evaluated_count * 100, 1)
        
        return summary
