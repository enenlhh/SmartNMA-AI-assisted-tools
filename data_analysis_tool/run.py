import subprocess
import sys

def run_shiny_app():
    """
    Launches the R Shiny application using a subprocess.
    """
    print("Starting SartNMA Tool...")
    print("This will open a new window in your web browser.")
    print("Please keep this terminal window open. Close it to stop the tool.")

    # The command to execute. We use R's -e flag to run an expression.
    # launch.browser=TRUE ensures it opens in the default web browser.
    command = ["R", "-e", "shiny::runApp('app.R', launch.browser=TRUE)"]

    try:
        # Run the command. This will block until the R process is terminated.
        subprocess.run(command, check=True)
    except FileNotFoundError:
        print("\n--- ERROR ---")
        print("Could not find 'R' in your system's PATH.")
        print("Please make sure you have R installed and that it's accessible from your terminal.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n--- ERROR ---")
        print(f"The R script exited with an error: {e}")
        print("Please check the R console output for more details.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nTool stopped by user.")
    finally:
        print("SartNMA Tool has been closed.")

if __name__ == "__main__":
    run_shiny_app()