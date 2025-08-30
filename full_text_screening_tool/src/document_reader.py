"""
Document Reader Module
Supports PDF, DOCX, DOC, and TXT file formats
"""

import os
import docx2txt
import fitz  # PyMuPDF
import pdfplumber

class DocumentReader:
    """Document reader supporting multiple file formats"""
    
    @staticmethod
    def read_file(file_path):
        """Read file content based on file extension"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                return DocumentReader._read_pdf(file_path)
            elif file_extension == '.docx':
                return docx2txt.process(file_path)
            elif file_extension == '.doc':
                print(f"  Warning: {file_path} is in DOC format, consider converting to DOCX")
                return docx2txt.process(file_path)
            elif file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
            else:
                print(f"  Warning: Unsupported file format: {file_extension}")
                return None
        except Exception as e:
            print(f"  Error reading file {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def _read_pdf(file_path):
        """Read PDF file using multiple methods"""
        text = ""
        try:
            # Try pdfplumber first
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            
            # If limited text, try PyMuPDF
            if len(text) < 1000:
                print(f"  Warning: Limited text extracted, trying PyMuPDF for {os.path.basename(file_path)}")
                backup_text = ""
                with fitz.open(file_path) as doc:
                    for page in doc:
                        backup_text += page.get_text() + "\n\n"
                
                if len(backup_text) > len(text) * 1.5:
                    text = backup_text
        except Exception as e:
            print(f"  Error with pdfplumber: {str(e)}, trying PyMuPDF")
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text() + "\n\n"
        
        return text