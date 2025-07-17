import os
import sys
import subprocess
import shutil

def prompt_for_directory(title: str = "Select folder to rename files in") -> str:
    """
    Cross-platform folder picker:
      - macOS: use AppleScript via osascript (executes in separate process).
      - Windows: use Tkinter's askdirectory() (works on main thread).
      - Linux: try 'zenity' first, then fallback to Tkinter.
    Returns a POSIX path string or "" if the user canceled.
    """
    # macOS: use AppleScript via osascript
    if sys.platform == "darwin":
        apple_script = f'POSIX path of (choose folder with prompt "{title}")'
        try:
            output = subprocess.check_output(["osascript", "-e", apple_script])
            return output.decode().strip()
        except subprocess.CalledProcessError:
            return ""
    
    # Windows: use Tkinter
    if os.name == "nt":
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title=title)
        root.destroy()
        return folder or ""
    
    # Linux: try 'zenity' first, else Tkinter
    if sys.platform.startswith("linux"):
        zenity_path = shutil.which("zenity")
        if zenity_path:
            try:
                output = subprocess.check_output([zenity_path, "--file-selection", "--directory", "--title", title])
                return output.decode().strip()
            except subprocess.CalledProcessError:
                return ""
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title=title)
        root.destroy()
        return folder or ""
    
    # Fallback: Tkinter for other platforms
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder = filedialog.askdirectory(title=title)
    root.destroy()
    return folder or ""

def list_directories(path: str) -> list:
    """
    Return a sorted list of subdirectories in the given path.
    If the path is invalid or not a directory, returns an empty list.
    """
    try:
        return sorted([
            d for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d))
        ])
    except Exception:
        return []
