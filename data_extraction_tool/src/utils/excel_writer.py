"""
Excel output utilities
"""
import pandas as pd
import os
import time
import json
import shutil

def save_results_to_excel(all_data, output_file, create_process_files=True):
    """Save extracted data to Excel with multiple sheets"""
    try:
        # Fix: Extract directory from output_file
        output_folder = os.path.dirname(output_file)
        process_folder = os.path.join(output_folder, "process_files")

        # Create process_files folder to store intermediate xlsx files
        process_folder = os.path.join(output_folder, "process_files")
        os.makedirs(process_folder, exist_ok=True)

        # Save a copy to the process folder
        process_file = os.path.join(process_folder, f"process_{os.path.basename(output_file)}")

        # Define the preferred sheet order
        preferred_order = [
            "Study_Info", 
            "Groups", 
            "Participant_Characteristics",
            "Outcomes", 
            "Results", 
            "Comparisons"
        ]
      
        # Backup existing file in case writing fails
        if os.path.exists(output_file):
            backup_file = os.path.join(process_folder, f'{os.path.basename(output_file).replace(".xlsx", "")}_backup_{int(time.time())}.xlsx')
            try:
                import shutil
                shutil.copy2(output_file, backup_file)
                print(f"Backup created: {backup_file}")
            except Exception as e:
                print(f"Failed to create backup: {e}")
      
        # Check the number of rows in each table
        for table_name, data in all_data.items():
            if len(data) > 1000000:  # Excel limit
                print(f"Warning: Table {table_name} contains {len(data)} rows, exceeding Excel limit (1,048,576), will be truncated")
      
        # Print the number of entries in each table for data validation
        print("\nData statistics to be saved:")
        for table_name in preferred_order:
            if table_name in all_data:
                print(f"  {table_name}: {len(all_data[table_name])} rows")
            else:
                print(f"  {table_name}: Does not exist")
      
        # Create a temporary file to write first, then replace the original file after success to avoid file corruption due to interruption
        temp_file = output_file.replace('.xlsx', f'_temp_{int(time.time())}.xlsx')
      
        # Create a Pandas Excel writer using XlsxWriter as the engine
        with pd.ExcelWriter(temp_file, engine='xlsxwriter') as writer:
            # Write each table to a different worksheet in the preferred order
            for table_name in preferred_order:
                if table_name in all_data and all_data[table_name]:  # Only create sheet if there's data
                    print(f"  Writing {table_name}...")
                    df = pd.DataFrame(all_data[table_name])
                  
                    # Check if the DataFrame is empty
                    if df.empty:
                        print(f"  Warning: {table_name} data is empty, skipping")
                        continue
                  
                    # Handle column order for specific tables
                    if table_name == "Groups":
                        # For Groups table, ensure Study_ID comes after File_Name and Group_Name comes right after Study_ID
                        if all(col in df.columns for col in ["File_Name", "Study_ID", "Group_Name"]):
                            cols = ["File_Name", "Study_ID", "Group_Name"] + [col for col in df.columns if col not in ["File_Name", "Study_ID", "Group_Name"]]
                            df = df[cols]
                    elif table_name == "Outcomes":
                        # For Outcomes table, ensure Study_ID comes after File_Name and Outcome_Name comes right after Study_ID
                        if all(col in df.columns for col in ["File_Name", "Study_ID", "Outcome_Name"]):
                            cols = ["File_Name", "Study_ID", "Outcome_Name"] + [col for col in df.columns if col not in ["File_Name", "Study_ID", "Outcome_Name"]]
                            df = df[cols]
                    else:
                        # For other tables, just ensure File_Name is at the front
                        if "File_Name" in df.columns:
                            cols = ["File_Name"] + [col for col in df.columns if col != "File_Name"]
                            df = df[cols]
                  
                    # Try to fix special characters and illegal column names
                    df.columns = [str(col).replace('/', '_').replace('\\', '_') for col in df.columns]
                  
                    # Ensure all values are strings to avoid type errors
                    for col in df.columns:
                        df[col] = df[col].astype(str)
                  
                    # Write to Excel
                    df.to_excel(writer, sheet_name=table_name, index=False)
                
                    # Auto-adjust columns' width
                    worksheet = writer.sheets[table_name]
                    for i, col in enumerate(df.columns):
                        # Find the maximum length of any cell in this column
                        max_len = max(
                            df[col].astype(str).map(len).max(),  # max length of column values
                            len(str(col))  # length of column name
                        ) + 1  # adding a little extra space
                        worksheet.set_column(i, i, min(max_len, 50))  # max width of 50 to avoid too wide columns
      
        # After successfully writing to the temporary file, replace the original file
        if os.path.exists(temp_file):
            if os.path.exists(output_file):
                os.remove(output_file)
            os.rename(temp_file, output_file)
            
            # Also save a copy to the process_folder
            import shutil
            shutil.copy2(output_file, process_file)
            print(f"Results successfully saved to: {output_file}")
            print(f"Process file saved to: {process_file}")
        else:
            print("Error: Failed to write temporary file")
        
    except Exception as e:
        print(f"Error saving Excel: {e}")
        import traceback
        traceback.print_exc()
        
        # If Excel save fails, try saving to JSON
        json_file = os.path.join(process_folder, f'emergency_backup_{os.path.basename(output_file).replace(".xlsx", "")}_{int(time.time())}.json')
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            print(f"Emergency backup saved as JSON: {json_file}")
        except Exception as json_error:
            print(f"Emergency JSON backup also failed: {json_error}")