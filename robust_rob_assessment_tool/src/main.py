import json
import logging
import time
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from rob_evaluator import ROBEvaluator
from visualizer import ROBVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> dict:
    """Load configuration file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration file: {e}")
        raise

def run_assessment(config_path: str = "config/config.json"):
    """Run ROB assessment with parallel processing support"""
    # Load configuration
    config = load_config(config_path)
    
    # Log configuration details
    logger.info("=== ROB Assessment Program Started ===")
    logger.info(f"Input folder: {config['paths']['input_folder']}")
    logger.info(f"Output path: {config['paths']['output_folder']}")
    logger.info(f"Evaluate optional items: {config['processing']['eval_optional_items']}")
    logger.info(f"Max text truncation length: {config['processing']['max_text_length']} characters")
    logger.info(f"Start processing index: {config['processing']['start_index']}")
    
    thresholds = config['domain6']['thresholds']
    logger.info(f"Domain 6 Thresholds: <{thresholds['definitely_low']}% = Definitely low, "
               f"<{thresholds['probably_low']}% = Probably low, "
               f"<{thresholds['probably_high']}% = Probably high, "
               f"≥{thresholds['probably_high']}% = Definitely high")
    logger.info(f"Domain 6 Default Assessment (when not reported): {config['domain6']['default_assessment']}")
    
    logger.info(f"Configured {len(config['llm_models'])} LLM models for assessment")
    for idx, model_config in enumerate(config['llm_models']):
        logger.info(f"Model {idx+1}: {model_config['name']} (API model: {model_config['model_name']})")

    # Check if parallel processing is enabled
    parallel_enabled = config.get('parallel', {}).get('enabled', False)
    max_workers = config.get('parallel', {}).get('max_workers', 1)
    
    logger.info(f"Parallel processing: {'Enabled' if parallel_enabled else 'Disabled'}")
    if parallel_enabled:
        logger.info(f"Max workers: {max_workers}")

    # Record start time
    start_time = time.time()
    
    # Use the ROBEvaluator which now handles parallel processing internally
    logger.info(f"Starting ROB assessment with {'parallel' if parallel_enabled and max_workers > 1 else 'sequential'} processing")
    run_sequential_assessment(config)
    
    output_folder = config['paths']['output_folder']
    
    # Generate traffic light visualization
    excel_file_path = os.path.join(output_folder, "rob_results.xlsx")
    if os.path.exists(excel_file_path):
        logger.info("Generating traffic light plot visualization...")
        try:
            visualizer = ROBVisualizer(config)
            html_output_path = os.path.join(output_folder, "rob_visualization.html")
            visualizer.generate_visualization(excel_file_path, html_output_path)
        except Exception as e:
            logger.error(f"An error occurred during visualization generation: {e}")
    else:
        logger.warning(f"Could not find results file at {excel_file_path}. Skipping visualization.")

    # Record total time
    elapsed_time = time.time() - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    logger.info(f"Assessment completed! Total time: {int(hours)} hours {int(minutes)} minutes {seconds:.2f} seconds")


def run_sequential_assessment(config: dict):
    """Run assessment using sequential or parallel processing based on config"""
    evaluator = ROBEvaluator(config)
    evaluator.process_folder(config['paths']['input_folder'], config['paths']['output_folder'])

if __name__ == "__main__":
    run_assessment()