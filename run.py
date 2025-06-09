#!/usr/bin/env python3

import os
import sys
import subprocess

os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")

def ensure_tkinter():
    """
    Ensure tkinter is available on Windows. Other platforms
    use native folder pickers (osascript/zenity) in the web app.
    """
    if os.name == "nt":
        try:
            import tkinter
        except (ImportError, ModuleNotFoundError):
            print("Tkinter not found. Please install it manually on Windows.")
            sys.exit(1)

def check_python_version():
    if sys.version_info < (3, 7):
        print("⚠️  Python 3.7 or higher is required.")
        sys.exit(1)

def create_venv():
    try:
        subprocess.check_call([sys.executable, "-m", "venv", ".venv"])
    except subprocess.CalledProcessError:
        print("⚠️  Failed to create virtual environment.")
        sys.exit(1)

def install_requirements(venv_python):
    try:
        subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("⚠️  Failed to install requirements.")
        sys.exit(1)

def main():
    check_python_version()
    ensure_tkinter()
    print("🐍 Creating virtual environment…")
    create_venv()
    if os.name == "nt":
        venv_python = os.path.join(".venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(".venv", "bin", "python")
    print("📦 Installing dependencies…")
    install_requirements(venv_python)
    print("✅ Dependencies installed, launching app 🚀")
    os.execv(venv_python, [venv_python, "-m", "filerenamer.webapp"])

if __name__ == "__main__":
    main()