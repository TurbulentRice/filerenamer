"""
Web application for bulk file renaming.

This module provides a Flask web application that exposes FileRenamer functionality
through a REST API. It allows users to:

- List files in a target directory
- Preview file renaming operations before applying them
- Apply, undo, and redo renaming operations to files

Routes:
    /api/list-files (GET) - Returns list of files in target directory
    /api/preview (POST) - Shows preview of renaming operations
    /api/apply (POST) - Applies renaming operations to files
"""

import os
import webbrowser
from flask import Flask, jsonify, request
from flask import send_from_directory
from functools import wraps
from file_renamer.core import FileRenamerSingleton
from file_renamer.util import prompt_for_directory


def with_filerenamer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        fr = FileRenamerSingleton.get()
        if fr is None:
            return jsonify({"error": "FileRenamer not initialized"}), 500
        return func(*args, **kwargs)
    return wrapper

app = Flask(__name__)

@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def serve_index():
    return send_from_directory(os.path.join(os.path.dirname(__file__), "templates"), "index.html")

@with_filerenamer
@app.route("/api/list-files", methods=["GET"])
def list_files():
    """
    Return JSON list of all filenames in target dir.
    """
    fr = FileRenamerSingleton.get()
    files = fr.filenames
    return jsonify({"files": files})


@with_filerenamer
@app.route("/api/preview", methods=["POST"])
def preview_mapping():
    """
    Given JSON payload like {"action":"replace","change_this":"foo","to_this":"bar"},
    call the corresponding core.* function to get a mapping, then return it.
    """
    fr = FileRenamerSingleton.get()

    data = request.json or {}

    action = data.get("action")
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


@with_filerenamer
@app.route("/api/apply", methods=["POST"])
def apply_mapping():
    """
    Given JSON payload {"mapping": { old_name: new_name, ... }},
    actually rename on disk. Return success or error.
    """
    fr = FileRenamerSingleton.get()

    data = request.json or {}
    mapping = data.get("mapping", {})

    # TODO add more validation here (e.g., confirm no collisions)
    fr.apply_mapping(mapping)
    files = fr.filenames
    return jsonify({"status": "ok", "files": files}), 200


# --- Change directory via native dialog ---
@app.route("/api/change-dir", methods=["POST"])
def change_directory():
    """
    Open a native folder picker, set the new directory, return new file list.
    """
    folder = prompt_for_directory("Select new target directory")
    if not folder:
        return jsonify({"error": "No folder chosen"}), 400
    try:
        FileRenamerSingleton.initialize(folder)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    fr = FileRenamerSingleton.get()
    files = fr.filenames
    return jsonify({"files": files, "target_dir": folder}), 200

@with_filerenamer
@app.route("/api/undo", methods=["POST"])
def undo_operation():
    """
    Revert the most recently applied mapping on target dir.
    """
    fr = FileRenamerSingleton.get()

    try:
        fr.undo()
        files = fr.filenames
        return jsonify({"status": "ok", "files": files}), 200
    except IndexError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Undo failed: {e}"}), 500


# --- New /api/redo route ---
@with_filerenamer
@app.route("/api/redo", methods=["POST"])
def redo_operation():
    """
    Reapply the most recently undone mapping on target dir.
    """
    fr = FileRenamerSingleton.get()

    try:
        fr.redo()
        files = fr.filenames
        return jsonify({"status": "ok", "files": files}), 200
    except IndexError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Redo failed: {e}"}), 500


def main():
    # 1) Prompt for initial directory
    folder = prompt_for_directory("Select folder to rename files in")
    if not folder:
        print("No folder chosen. Exiting.")
        return

    # Initialize filerenamer singleton
    FileRenamerSingleton.initialize(folder)

    # 2) Open default browser to the frontend page
    webbrowser.open("http://127.0.0.1:8000/index.html")

    # 3) Run Flask on the main thread (threaded=True for concurrent requests, disable reloader)
    app.run(port=8000, debug=False, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()