import os
import json
import pandas as pd
import numpy as np
from src.grade_evaluator import GradeEvaluator
import traceback

def list_available_outcomes(base_dir: str) -> list:
    """Lists all available outcomes for evaluation."""
    available_outcomes = []
    if not os.path.exists(base_dir):
        print(f"Warning: Base directory '{base_dir}' does not exist.")
        return []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            has_random = os.path.exists(os.path.join(item_path, "Results of Random Effect Model"))
            has_fixed = os.path.exists(os.path.join(item_path, "Results of Common Effect Model"))
            models = []
            if has_random: models.append("random")
            if has_fixed: models.append("fixed")
            if models: available_outcomes.append({"outcome": item, "models": models})
    return available_outcomes

def main():
    """Main function to run GRADE and generate a single, fully self-contained, interactive HTML report."""
    print("--- Starting GRADE Evaluation Project ---")

    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("Configuration loaded successfully.")
    except Exception as e:
        print(f"Error loading config.json: {e}")
        return

    base_dir = config['data_settings']['base_dir']
    output_dir = config['data_settings']['output_dir']
    os.makedirs(output_dir, exist_ok=True)

    available_outcomes = list_available_outcomes(base_dir)
    if not available_outcomes:
        print("No valid outcomes found. Exiting.")
        return
    
    print(f"Found {len(available_outcomes)} outcomes to process.")
    
    all_report_data = {}

    for outcome_info in available_outcomes:
        outcome_name = outcome_info["outcome"]
        print(f"\nProcessing outcome: {outcome_name}")
        for model_type in outcome_info["models"]:
            print(f"  - Model: {model_type.capitalize()}")
            try:
                evaluator = GradeEvaluator(
                    base_dir=base_dir, outcome_name=outcome_name, model_type=model_type,
                    ask_for_mid=False, mid_params=config.get('mid_params'),
                    rob_params=config.get('rob_params'), inconsistency_params=config.get('inconsistency_params')
                )
                grade_results = evaluator.evaluate_grade()
                
                model_dir_name = "Results of Random Effect Model" if model_type == "random" else "Results of Common Effect Model"
                final_output_path = os.path.join(output_dir, outcome_name, model_dir_name)
                os.makedirs(final_output_path, exist_ok=True)
                excel_filename = f"{outcome_name}-GRADE_Evaluation_Results.xlsx"
                excel_filepath = os.path.join(final_output_path, excel_filename)
                grade_results.to_excel(excel_filepath, index=False)
                print(f"    ✓ Excel results saved to: {excel_filepath}")

                report_key = f"{outcome_name} ({model_type.capitalize()} Model)"
                grade_results_json = grade_results.replace({pd.NA: None, np.nan: None})
                all_report_data[report_key] = {
                    "data": grade_results_json.to_dict(orient='records'),
                    "excel_path": os.path.join(outcome_name, model_dir_name, excel_filename).replace("\\", "/")
                }
            except Exception as e:
                print(f"    ✗ Error processing {outcome_name} ({model_type}): {e}")
                traceback.print_exc()

    if not all_report_data:
        print("\nNo data generated. HTML report will not be created.")
        return
        
    try:
        print("\nCreating fully self-contained, interactive HTML report...")
        with open('template.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        with open('static/css/style.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
        with open('static/js/calculation_logic.js', 'r', encoding='utf-8') as f:
            calc_js_content = f.read()
        with open('static/js/main.js', 'r', encoding='utf-8') as f:
            main_js_content = f.read()

        final_html = template_content.replace('/* __CSS_PLACEHOLDER__ */', css_content)
        data_as_json_string = f"window.EMBEDDED_DATA = {json.dumps(all_report_data, indent=2)};"
        final_html = final_html.replace('// __DATA_PLACEHOLDER__', data_as_json_string)
        final_html = final_html.replace('// __CALCULATION_LOGIC_JS_PLACEHOLDER__', calc_js_content)
        final_html = final_html.replace('// __MAIN_JS_PLACEHOLDER__', main_js_content)
        
        report_filepath = os.path.join(output_dir, 'report.html')
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(final_html)
        
        print(f"✓ Success! Fully self-contained, live-updating report created at: {report_filepath}")
        print("You can now double-click this file to open it.")

    except Exception as e:
        print(f"\nAn error occurred while creating the final HTML report: {e}")

    print("\n--- GRADE Evaluation Project Finished ---")

if __name__ == "__main__":
    main()
