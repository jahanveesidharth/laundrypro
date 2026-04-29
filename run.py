#!/usr/bin/env python3
"""
LaundryPro - Quick Start Script
Run: python run.py
"""
import subprocess
import sys
import os

def main():
    print("🧺 LaundryPro — Starting up...")
    
    # Check requirements
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    print("🚀 Server starting at http://localhost:8000")
    print("📚 API Docs at    http://localhost:8000/docs")
    print("Press Ctrl+C to stop\n")
    
    os.chdir(os.path.join(os.path.dirname(__file__), "backend"))
    
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
