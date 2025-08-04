#!/usr/bin/env python3
"""
STRIVE Pro Phase 2 - Quick Launcher
"""
import subprocess
import sys
import os

def main():
    print("Ì∑† Starting STRIVE Pro Phase 2...")
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check for different app files and run the best available
    app_files = [
        "main.py",
        "simple_app.py", 
        "app/core/main.py"
    ]
    
    for app_file in app_files:
        if os.path.exists(app_file):
            print(f"Ì∫Ä Running: {app_file}")
            try:
                subprocess.run([
                    sys.executable, "-m", "streamlit", "run", 
                    app_file,
                    "--server.port=8501"
                ])
                break
            except KeyboardInterrupt:
                print("\nÌ±ã STRIVE Pro stopped by user")
                break
            except Exception as e:
                print(f"‚ùå Error running {app_file}: {e}")
                continue
    else:
        print("‚ùå No application files found!")
        print("Ì¥ß Please run setup first: python scripts/setup/quick_setup.py")

if __name__ == "__main__":
    main()
