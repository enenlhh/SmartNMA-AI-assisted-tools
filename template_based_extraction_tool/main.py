#!/usr/bin/env python3
"""
SmartEBM Template-Based Extraction Tool
A simple template-driven PDF data extraction tool using LLM
"""

import os
import sys
import json
import pandas as pd
import pdfplumber
import PyPDF2
from pathlib import Path
from tqdm import tqdm
from openai import OpenAI
import re
from typing import Dict, List, Tuple, Optional
import logging
from config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TemplateExtractor:
    def __init__(self, config: Dict):
        self.config = config
        self.client = OpenAI(
            api_key=config["llm"]["api_key"],
            base_url=config["llm"]["base_url"]
        )
        os.makedirs(config["runtime"]["debug_dir"], exist_ok=True)
        os.makedirs(os.path.dirname(config["paths"]["output_xlsx"]), exist_ok=True)
    
    def load_template(self, template_path: str) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Load 4-row template from Excel file"""
        try:
            df = pd.read_excel(template_path, header=None)
            if len(df) < 4:
                raise ValueError("Template must have at least 4 rows")
            
            field_names = [str(x) for x in df.iloc[0].dropna().tolist()]
            field_descriptions = [str(x) for x in df.iloc[1].dropna().tolist()]
            example1 = [str(x) for x in df.iloc[2].dropna().tolist()]
            example2 = [str(x) for x in df.iloc[3].dropna().tolist()]
            
            logger.info(f"Loaded template with {len(field_names)} fields")
            return field_names, field_descriptions, example1, example2
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            raise
    
    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber, fallback to PyPDF2"""
        try:
            # Try pdfplumber first
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                if text.strip():
                    return text[:self.config["runtime"]["max_chars_per_doc"]]
        except Exception as e:
            logger.warning(f"pdfplumber failed for {pdf_path}: {e}")
        
        try:
            # Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text[:self.config["runtime"]["max_chars_per_doc"]]
        except Exception as e:
            logger.error(f"Both PDF extractors failed for {pdf_path}: {e}")
            return ""
    
    def create_extraction_prompt(self, field_names: List[str], field_descriptions: List[str], 
                               example1: List[str], example2: List[str], text: str) -> str:
        """Create extraction prompt for LLM"""
        # Create field specification
        field_spec = []
        for i, (name, desc, ex1, ex2) in enumerate(zip(field_names, field_descriptions, example1, example2)):
            field_spec.append(f"{name}: {desc} (Examples: {ex1}, {ex2})")
        
        prompt = f"""Extract data from the following text and output ONLY a table format.

REQUIRED FIELDS:
{chr(10).join(field_spec)}

STRICT OUTPUT REQUIREMENTS:
1. Output ONLY the table - no explanations, no JSON, no markdown headers
2. First row must be the header with field names separated by tabs
3. Include a Row_ID column (starting from 1)
4. Use tab characters (\\t) to separate columns
5. Use "Not reported" for missing values
6. Each row must have the same number of columns as the header

TEXT TO EXTRACT FROM:
{text}

OUTPUT (table only):"""
        
        return prompt
    
    def parse_table_response(self, response: str) -> Optional[pd.DataFrame]:
        """Parse LLM response into DataFrame"""
        try:
            lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
            if not lines:
                return None
            
            # Try tab-separated first
            if '\t' in lines[0]:
                data = [line.split('\t') for line in lines]
            else:
                # Try space-separated or other formats
                data = [re.split(r'\s{2,}|\|', line) for line in lines]
                data = [[cell.strip() for cell in row if cell.strip()] for row in data]
            
            if not data or len(data) < 1:
                return None
            
            # Create DataFrame
            headers = data[0]
            rows = data[1:] if len(data) > 1 else []
            
            # Ensure all rows have same length as headers
            for i, row in enumerate(rows):
                while len(row) < len(headers):
                    row.append("Not reported")
                rows[i] = row[:len(headers)]
            
            df = pd.DataFrame(rows, columns=headers)
            return df
            
        except Exception as e:
            logger.warning(f"Failed to parse table response: {e}")
            return None
    
    def repair_response(self, original_response: str, field_names: List[str]) -> str:
        """Attempt to repair malformed LLM response"""
        repair_prompt = f"""The following text should be a table but has formatting issues. 
Please convert it to a proper tab-separated table format.

Required columns: Row_ID, {', '.join(field_names)}

Original text:
{original_response}

Output ONLY the corrected table (tab-separated, no explanations):"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config["llm"]["model"],
                messages=[{"role": "user", "content": repair_prompt}],
                temperature=self.config["llm"]["temperature"],
                max_tokens=self.config["llm"]["max_tokens"]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Repair call failed: {e}")
            return original_response
    
    def extract_from_pdf(self, pdf_path: str, field_names: List[str], 
                        field_descriptions: List[str], example1: List[str], 
                        example2: List[str]) -> pd.DataFrame:
        """Extract data from a single PDF"""
        logger.info(f"Processing: {os.path.basename(pdf_path)}")
        
        # Extract text
        text = self.extract_pdf_text(pdf_path)
        if not text:
            logger.warning(f"No text extracted from {pdf_path}")
            return pd.DataFrame()
        
        # Process in chunks if too many fields
        chunk_size = self.config["runtime"]["chunk_field_size"]
        all_results = []
        
        for i in range(0, len(field_names), chunk_size):
            chunk_fields = field_names[i:i+chunk_size]
            chunk_descriptions = field_descriptions[i:i+chunk_size]
            chunk_ex1 = example1[i:i+chunk_size]
            chunk_ex2 = example2[i:i+chunk_size]
            
            # Create prompt
            prompt = self.create_extraction_prompt(chunk_fields, chunk_descriptions, 
                                                 chunk_ex1, chunk_ex2, text)
            
            # Call LLM
            try:
                response = self.client.chat.completions.create(
                    model=self.config["llm"]["model"],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config["llm"]["temperature"],
                    max_tokens=self.config["llm"]["max_tokens"]
                )
                
                raw_response = response.choices[0].message.content.strip()
                
                # Save debug info
                debug_file = os.path.join(
                    self.config["runtime"]["debug_dir"], 
                    f"{os.path.basename(pdf_path)}_chunk_{i//chunk_size}.txt"
                )
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(f"PROMPT:\n{prompt}\n\nRESPONSE:\n{raw_response}")
                
                # Parse response
                df = self.parse_table_response(raw_response)
                
                # Try repair if parsing failed
                if df is None and self.config["runtime"]["use_repair_call"]:
                    logger.warning(f"Parsing failed, attempting repair for chunk {i//chunk_size}")
                    repaired_response = self.repair_response(raw_response, chunk_fields)
                    df = self.parse_table_response(repaired_response)
                    
                    # Save repaired version
                    with open(debug_file.replace('.txt', '_repaired.txt'), 'w', encoding='utf-8') as f:
                        f.write(f"ORIGINAL:\n{raw_response}\n\nREPAIRED:\n{repaired_response}")
                
                if df is not None:
                    all_results.append(df)
                else:
                    logger.error(f"Failed to parse response for chunk {i//chunk_size}")
                    
            except Exception as e:
                logger.error(f"LLM call failed for chunk {i//chunk_size}: {e}")
        
        # Merge results horizontally by Row_ID
        if all_results:
            final_df = all_results[0]
            for df in all_results[1:]:
                if 'Row_ID' in df.columns and 'Row_ID' in final_df.columns:
                    final_df = pd.merge(final_df, df, on='Row_ID', how='outer')
                else:
                    # Fallback: concatenate horizontally
                    final_df = pd.concat([final_df, df], axis=1)
            
            # Add filename and clean up
            final_df['File_Name'] = os.path.basename(pdf_path)
            if 'Row_ID' in final_df.columns:
                final_df = final_df.drop('Row_ID', axis=1)
            
            # Reorder columns: File_Name first, then template fields
            cols = ['File_Name'] + [col for col in final_df.columns if col != 'File_Name']
            final_df = final_df[cols]
            
            return final_df
        
        return pd.DataFrame()
    
    def run_extraction(self):
        """Main extraction workflow"""
        logger.info("Starting template-based extraction...")
        
        # Load template
        field_names, field_descriptions, example1, example2 = self.load_template(
            self.config["paths"]["template_xlsx"]
        )
        
        # Get PDF files
        pdf_folder = Path(self.config["paths"]["pdf_folder"])
        pdf_files = list(pdf_folder.glob("*.pdf"))
        
        if not pdf_files:
            logger.error(f"No PDF files found in {pdf_folder}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Process each PDF
        all_results = []
        for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
            try:
                result_df = self.extract_from_pdf(
                    str(pdf_file), field_names, field_descriptions, example1, example2
                )
                if not result_df.empty:
                    all_results.append(result_df)
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {e}")
        
        # Combine all results
        if all_results:
            final_df = pd.concat(all_results, ignore_index=True)
            
            # Save to Excel
            output_path = self.config["paths"]["output_xlsx"]
            final_df.to_excel(output_path, sheet_name='Results', index=False)
            logger.info(f"Results saved to: {output_path}")
            logger.info(f"Total records extracted: {len(final_df)}")
        else:
            logger.warning("No data extracted from any PDF files")

def main():
    """Main entry point"""
    try:
        # Get configuration
        config = get_config()
        
        # Validate configuration
        if not config["llm"]["api_key"]:
            logger.error("API key not configured. Please set OPENAI_API_KEY environment variable or update config.py.")
            return
        
        # Create extractor and run
        extractor = TemplateExtractor(config)
        extractor.run_extraction()
        
    except KeyboardInterrupt:
        logger.info("Extraction interrupted by user")
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise

if __name__ == "__main__":
    main()