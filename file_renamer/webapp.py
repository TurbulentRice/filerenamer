"""
Web application for bulk file renaming.

This module provides a Flask web application that exposes the file renaming functionality
through a REST API. It allows users to:

- List files in a target directory
- Preview file renaming operations before applying them
- Apply renaming operations to files

The application uses the core file renaming logic from file_renamer.core module.

Routes:
    /api/list-files (GET) - Returns list of files in target directory
    /api/preview (POST) - Shows preview of renaming operations
    /api/apply (POST) - Applies renaming operations to files

Configuration:
    TARGET_DIR - Directory containing files to be renamed
"""


import os
import sys
import subprocess
import shutil
import webbrowser
from flask import Flask, jsonify, request
from flask import send_from_directory
from file_renamer.file_renamer import FileReNamer


def prompt_for_directory(title: str = "Select folder to rename files in") -> str:
    """
    Cross-platform folder picker:
      - macOS: use AppleScript via osascript (executes in separate process).
      - Windows: use Tkinter’s askdirectory() (works on main thread).
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


app = Flask(__name__)
app.config["TARGET_DIR"] = None  # set after folder‐picker

@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def serve_index():
    return send_from_directory(os.path.join(os.path.dirname(__file__), "templates"), "index.html")

@app.route("/api/list-files", methods=["GET"])
def list_files():
    """
    Return JSON list of all filenames in TARGET_DIR.
    """
    d = app.config["TARGET_DIR"]
    if d is None or not os.path.isdir(d):
        return jsonify({"error": "No target directory set"}), 400

    files = sorted(os.listdir(d))
    return jsonify({"files": files})


@app.route("/api/preview", methods=["POST"])
def preview_mapping():
    """
    Given JSON payload like {"action":"replace","change_this":"foo","to_this":"bar"},
    call the corresponding core.* function to get a mapping, then return it.
    """
    data = request.json or {}
    d = app.config["TARGET_DIR"]
    if d is None or not os.path.isdir(d):
        return jsonify({"error": "No target directory set"}), 400

    action = data.get("action")
    fr = FileReNamer(d)
    if action == "replace":
        change_this = data["change_this"]
        to_this     = data["to_this"]
        mapping = fr.replace_mapping(change_this, to_this)

    elif action == "prefix":
        prefix = data["prefix"]
        mapping = fr.prefix_mapping(prefix)

    elif action == "suffix":
        suffix = data["suffix"]
        mapping = fr.suffix_mapping(suffix)

    elif action == "enum":
        start = int(data.get("start", 1))
        sep   = data.get("sep", "_")
        direction = data.get("loc", "end")
        mapping = fr.enum_mapping(start, direction, sep)

    else:
        return jsonify({"error": "Unknown action"}), 400

    return jsonify({"mapping": mapping})


@app.route("/api/apply", methods=["POST"])
def apply_mapping():
    """
    Given JSON payload {"mapping": { old_name: new_name, ... }},
    actually rename on disk. Return success or error.
    """
    data = request.json or {}
    mapping = data.get("mapping", {})
    d = app.config["TARGET_DIR"]
    if d is None or not os.path.isdir(d):
        return jsonify({"error": "No target directory set"}), 400

    # You could add more validation here (e.g., confirm no collisions)
    fr = FileReNamer(d)
    fr.apply_mapping(mapping)
    return jsonify({"status": "ok"}), 200


# --- New route for changing directory via native dialog ---
@app.route("/api/change-dir", methods=["POST"])
def change_directory():
    """
    Open a native folder picker, set TARGET_DIR to the chosen folder,
    and return the new file list.
    """
    folder = prompt_for_directory("Select new target directory")

    if not folder or not os.path.isdir(folder):
        return jsonify({"error": "No folder chosen or invalid directory"}), 400

    app.config["TARGET_DIR"] = folder
    files = sorted(os.listdir(folder))
    return jsonify({"files": files, "target_dir": folder}), 200


def main():
    # 1) Prompt for initial directory
    folder = prompt_for_directory("Select folder to rename files in")
    if not folder:
        print("No folder chosen. Exiting.")
        return

    app.config["TARGET_DIR"] = folder

    # 2) Open default browser to the frontend page
    webbrowser.open("http://127.0.0.1:8000/index.html")

    # 3) Run Flask on the main thread (threaded=True for concurrent requests, disable reloader)
    app.run(port=8000, debug=False, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()