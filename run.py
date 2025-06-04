#!/usr/bin/env python3

import os
import sys
import subprocess

os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")

def ensure_tkinter():
    try:
        import tkinter
    except (ImportError, ModuleNotFoundError):
        if os.name == "nt":
            print("Tkinter not found. Please install it manually on Windows.")
            sys.exit(1)
        elif sys.platform.startswith("darwin"):
            try:
                subprocess.check_call(["brew", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                try:
                    subprocess.check_call(["brew", "install", "python-tk"])
                except subprocess.CalledProcessError:
                    pass
                try:
                    import tkinter
                except (ImportError, ModuleNotFoundError):
                    print("Please install Tkinter manually (e.g., via your Python installer or `brew install python-tk`).")
                    sys.exit(1)
            except subprocess.CalledProcessError:
                print("Homebrew not found; please install Tkinter via your Python installer or use `brew install python-tk` if you have Homebrew.")
                sys.exit(1)
        else:
            try:
                subprocess.check_call(["sudo", "apt-get", "update"])
                subprocess.check_call(["sudo", "apt-get", "install", "-y", "python3-tk"])
            except subprocess.CalledProcessError:
                print("Please install Tkinter manually (e.g., `sudo apt-get install python3-tk`).")
                sys.exit(1)

def check_python_version():
    if sys.version_info < (3, 7):
        print("Python 3.7 or higher is required.")
        sys.exit(1)

def create_venv():
    try:
        subprocess.check_call([sys.executable, "-m", "venv", ".venv"])
    except subprocess.CalledProcessError:
        print("Failed to create virtual environment.")
        sys.exit(1)

def install_requirements(venv_python):
    try:
        subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("Failed to install requirements.")
        sys.exit(1)

def main():
    ensure_tkinter()
    check_python_version()
    print("🐍 Creating virtual environment…")
    create_venv()
    if os.name == "nt":
        venv_python = os.path.join(".venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(".venv", "bin", "python")
    print("📦 Installing dependencies…")
    install_requirements(venv_python)
    print("✅ Dependencies installed, launching app 🚀")
    os.execv(venv_python, [venv_python, "-m", "file_renamer.webapp"])

if __name__ == "__main__":
    main()