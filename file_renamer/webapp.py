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
import threading
import webbrowser
from flask import Flask, jsonify, request
from flask import send_from_directory
import file_renamer.core as core   # your refactored logic

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
    if action == "replace":
        change_this = data["change_this"]
        to_this     = data["to_this"]
        mapping = core.build_replace_mapping(d, change_this, to_this)

    elif action == "prefix":
        prefix = data["prefix"]
        mapping = core.build_prefix_mapping(d, prefix)

    elif action == "suffix":
        suffix = data["suffix"]
        mapping = core.build_suffix_mapping(d, suffix)

    elif action == "enum":
        start = int(data.get("start", 1))
        sep   = data.get("sep", "_")
        direction = data.get("loc", "end")
        mapping = core.build_enum_mapping(d, start, sep, direction)

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
    core.apply_mapping(d, mapping)
    return jsonify({"status": "ok"}), 200


def main():
    # 1) Let user pick a folder via a native dialog
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder = filedialog.askdirectory(title="Select folder to rename files in")
    root.destroy()

    if not folder:
        print("No folder chosen. Exiting.")
        return

    app.config["TARGET_DIR"] = folder

    # 2) Launch Flask in a background thread (so we can open a browser)
    def run_server():
        app.run(port=5000, debug=False)

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    # 3) Open default browser to the frontend page
    webbrowser.open("http://127.0.0.1:5000/index.html")

    # 4) Prevent main thread from exiting immediately
    thread.join()


if __name__ == "__main__":
    main()