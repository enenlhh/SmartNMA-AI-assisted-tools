# ==============================================================================
# PDF Filter Tool for Included Studies
# ==============================================================================
# 
# Description:
# This script automates the extraction of PDF files based on "Include" status from an Excel spreadsheet.
# It identifies studies marked as "Include" in the "Conflict Status" column and copies their corresponding
# PDF files from a source directory to a dedicated output folder. Useful for streamlining literature review workflows.
#
# Features:
# - Reads Excel tables to identify included studies
# - Automatically copies matching PDF files
# - Creates output folder if it doesn't exist
# - Provides detailed operation feedback
# - Reports missing files for manual follow-up
# - Preserves original file metadata
#
# Requirements:
# - Python 3.6+
# - Required packages: pandas, openpyxl
# ==============================================================================

import os           # For interacting with the file system
import shutil       # For copying files
import pandas as pd # For reading and processing Excel files

# ---------------------- USER CONFIGURATION - MODIFY THESE PATHS ----------------------
# Full path to your Excel file containing the study metadata
excel_file_path = "path/to/your/table.xlsx"

# Folder where all your original PDF files are stored
pdf_source_folder = "path/to/your/pdf/folder"

# Folder where you want the filtered "Include" PDFs to be copied (will be created if it doesn't exist)
output_folder = "path/to/output/include_pdfs"
# --------------------------------------------------------------------------------------

def copy_included_pdfs():
    """
    Main function to process the Excel file, identify included studies,
    and copy their corresponding PDF files to the output folder.
    """
    try:
        # Read the Excel file into a pandas DataFrame
        print("Reading Excel file...")
        df = pd.read_excel(excel_file_path)
        
        # Check if the required columns exist in the Excel file
        required_columns = ['Filename', 'Conflict Status']
        for col in required_columns:
            if col not in df.columns:
                # Raise an error if any required column is missing
                raise ValueError(f"Excel file is missing required column: {col}")
        
        # Filter the DataFrame to get only rows where Conflict Status is 'Include',
        # then extract the list of filenames from these rows
        included_files = df[df['Conflict Status'] == 'Include']['Filename'].tolist()
        print(f"Found {len(included_files)} files to extract")
        
        # Create the output folder if it doesn't already exist
        # exist_ok=True ensures no error is thrown if the folder already exists
        os.makedirs(output_folder, exist_ok=True)
        print(f"Output folder prepared: {output_folder}")
        
        # Initialize counters and lists for tracking results
        copied_count = 0          # Number of successfully copied files
        missing_files = []        # List of files that couldn't be found
        
        # Iterate through each included filename to copy the corresponding PDF
        for filename in included_files:
            # Create the full path to the source PDF file
            source_path = os.path.join(pdf_source_folder, filename)
            
            # Check if the source file exists and is a valid file (not a folder)
            if os.path.exists(source_path) and os.path.isfile(source_path):
                # Create the full path to the target location in the output folder
                target_path = os.path.join(output_folder, filename)
                
                # Copy the file from source to target, preserving metadata (using copy2)
                shutil.copy2(source_path, target_path)
                copied_count += 1
                print(f"Copied: {filename}")
            else:
                # If file not found, add to missing files list
                missing_files.append(filename)
                print(f"File not found: {filename}")
        
        # Print a summary of the operation results
        print("\nProcessing complete!")
        print(f"Successfully copied {copied_count} files to output folder")
        
        # If there are missing files, list them for the user
        if missing_files:
            print(f"Note: {len(missing_files)} files were not found:")
            for file in missing_files:
                print(f"  - {file}")
    
    # Catch and display any errors that occur during processing
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Run the main function if the script is executed directly (not imported as a module)
if __name__ == "__main__":
    copy_included_pdfs()
    # Pause to allow the user to review the output before the window closes
    input("Press Enter to exit...")