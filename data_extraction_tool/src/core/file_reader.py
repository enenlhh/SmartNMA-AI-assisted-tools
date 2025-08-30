"""
File reading utilities for PDF and Word documents
"""
import os
import docx2txt
import fitz  # PyMuPDF

def read_file(file_path):
    """Read content from PDF or Word document"""
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.pdf':
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        elif ext in ['.docx', '.doc']:
            return docx2txt.process(file_path)
        else:
            print(f"Unsupported file format: {file_path}")
            return None
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None