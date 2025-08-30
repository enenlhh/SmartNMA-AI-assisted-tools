#!/usr/bin/env python3
"""
SmartEBM Literature Screening Tool - Main Entry Point

This is the main entry point of the system that automatically imports core modules and starts the system.

Usage:
    python3 main.py                    # Use default config
    python3 main.py --config custom.json  # Use custom config  
    python3 main.py --lang en          # English interface
    python3 main.py --lang zh          # Chinese interface
    python3 main.py --resume           # Resume interrupted task
    python3 main.py --cleanup          # Clean temporary files
"""

import os
import sys
from pathlib import Path

# Add project paths to Python path
current_dir = Path(__file__).parent
core_dir = current_dir / "core"
i18n_dir = current_dir / "i18n"
src_dir = current_dir / "src"
tools_dir = current_dir / "tools"

# Add all necessary directories to Python path
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(core_dir))
sys.path.insert(0, str(i18n_dir))
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(tools_dir))

def main():
    """Main function"""
    try:
        # Import core modules
        from core.parallel_run import main as parallel_main
        
        # Call core module's main function
        return parallel_main()
        
    except ImportError as e:
        # Import i18n after path setup
        try:
            from i18n.i18n_manager import get_message
            print(get_message("import_error", error=str(e)))
            print(get_message("dependencies_check"))
            print(get_message("install_requirements"))
        except:
            print(f"❌ Import Error: {e}")
            print("Please ensure all dependencies are properly installed")
            print("Run: pip install -r requirements.txt")
        return 1
    except Exception as e:
        try:
            from i18n.i18n_manager import get_message
            print(get_message("system_error", error=str(e)))
        except:
            print(f"❌ System Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())