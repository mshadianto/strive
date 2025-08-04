#!/usr/bin/env python3
"""
STRIVE Pro Phase 2 - Main Application Entry Point
"""
import sys
import os
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

try:
    # Import and run the main application
    from core.main import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"‚ùå Import error: {e}")
    print("Ì¥ß Fallback to simple application...")
    
    # Fallback to simple app if core modules not available
    import subprocess
    
    # Check if simple_app.py exists
    if os.path.exists("simple_app.py"):
        subprocess.run([sys.executable, "-m", "streamlit", "run", "simple_app.py"])
    else:
        print("‚ùå No application files found. Please run setup first.")
