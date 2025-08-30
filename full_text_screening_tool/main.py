#!/usr/bin/env python3
"""
SmartEBM Full-Text Screening Tool - Main Entry Point

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
i18n_dir = current_dir / "i18n"
src_dir = current_dir / "src"
scripts_dir = current_dir / "scripts"

# Add all necessary directories to Python path
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(i18n_dir))
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(scripts_dir))

def main():
    """Main function"""
    try:
        # Import core module using importlib for better compatibility
        import importlib.util
        import importlib
        
        core_run = None
        import_errors = []
        
        # Try different import methods
        try:
            # Method 1: Try direct import
            core_run = importlib.import_module('core_run')
        except ImportError as e1:
            import_errors.append(f"Direct import failed: {e1}")
            try:
                # Method 2: Try importing from scripts package
                core_run = importlib.import_module('scripts.core_run')
            except ImportError as e2:
                import_errors.append(f"Package import failed: {e2}")
                try:
                    # Method 3: Try loading from file path
                    script_path = current_dir / "scripts" / "core_run.py"
                    spec = importlib.util.spec_from_file_location("core_run", script_path)
                    if spec is not None and spec.loader is not None:
                        core_run = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(core_run)
                    else:
                        raise ImportError("Could not create module spec")
                except Exception as e3:
                    import_errors.append(f"File import failed: {e3}")
                    raise ImportError(f"Could not import core_run module. Attempts: {'; '.join(import_errors)}")
        
        # Modify sys.argv to ensure correct config file path
        import sys
        original_argv = sys.argv.copy()
        
        # Get project root directory
        project_root = str(current_dir)
        
        # Check if relative path config file needs to be adjusted to absolute path
        config_specified = False
        for i, arg in enumerate(sys.argv):
            if arg in ['--config', '-c'] and i + 1 < len(sys.argv):
                config_specified = True
                config_path = sys.argv[i + 1]
                if not os.path.isabs(config_path):
                    # Convert to absolute path
                    if config_path.startswith('config/'):
                        sys.argv[i + 1] = os.path.join(project_root, config_path)
                    else:
                        sys.argv[i + 1] = os.path.join(project_root, 'config', config_path)
        
        # If no config file specified and not in interactive mode, use default absolute path
        if not config_specified and len(sys.argv) > 1:
            # Only add default config if there are other arguments (non-interactive mode)
            config_path = os.path.join(project_root, 'config', 'config.json')
            sys.argv.extend(['--config', config_path])
        
        # Call core module's main function
        result = core_run.main()
        
        # Restore original argv
        sys.argv = original_argv
        
        return result
        
    except ImportError as e:
        # Try to import i18n for error messages, fallback to English if not available
        try:
            from i18n.i18n_manager import get_message
            print(get_message("import_error", error=str(e)))
            print(get_message("dependencies_check"))
            print(get_message("install_dependencies"))
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