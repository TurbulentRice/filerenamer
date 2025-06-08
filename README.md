# FileRenamer

Easily rename files in bulk with this Python application. Originally created to simplify renaming many files quickly, FileRenamer now provides both a browser-based GUI and command-line interface (CLI), with support for undo/redo of batch operations.

## Getting started

**Requirements**
- Python 3.7+

**Clone the repository**
```sh
git clone https://github.com/TurbulentRice/filerenamer.git
cd filerenamer/
```

**Launch the application**
The cross-platform Python launcher script will:
1. Create a virtual environment (`.venv/`) if missing.  
2. Install Python dependencies.  
3. Start a local web UI in your default browser.  
```sh
./run.py
```

**Notes**
- On some systems, you may need to mark `run.py` as executable: `chmod +x run.py`.
- To use the command line tool, see "Command-Line Interface (WIP)" below


## Features

### Web-based GUI
- Launches a local web server and opens your default browser.  
- Native folder picker to select the target directory, or Tkinter.  
- Choose from several operations:  
  - **Search & Replace**: Replace substrings in filenames.  
  - **Add Prefix/Suffix**: Prepend or append text.  
  - **Enumerate**: Prepend or append incremental numbers.  
  - **Rename with Enumeration**: Overwrite filenames entirely with a base name + index.  
  - **Add from File**: For `.txt` files, uses a regex to extract content and add it to the filename.  
- **Live Preview**: Shows old and new filenames before applying.  
- **Undo/Redo**: Revert or reapply the last batch operation.

### Command-Line Interface

`.venv/bin/python -m file_renamer.cli`

  Arguments:
    --target, -t: Target directory containing files to rename
    --replace, -r: Replace occurrences in filenames (format: old=new)
    --prefix, -p: Add prefix to all filenames
    --suffix, -s: Add suffix to all filenames
    --enum: Enable file enumeration
    --enum-start: Starting number for enumeration
    --enum-loc: Location for enumeration (start/end)
    --enum-sep: Separator for enumeration
    --rename-with-enum: Base name for enumerated renaming
    --add-from-file: Regex pattern to extract from .txt files
    --add-loc: Location to add extracted content (start/end)
    --undo: Undo the last rename operation
    --redo: Redo the last undone operation
    --dry-run: Preview changes without applying them
    --recursive: Include files in subdirectories
    --yes: Skip confirmation prompt

  - Example:
    ```sh
     .venv/bin/python --target ./photos --replace "IMG_"="PIC_" --suffix "_edited" --yes
    ```

- **Undo/Redo Support**  
  - Both the web UI and the CLI track the last rename mapping.  
  - In the web UI, click **Undo** or **Redo** after a batch rename.  
  - In Python code, use the `FileRenamer` class to call `.undo()` or `.redo()`

## Examples

### Web UI Workflow

1. `./run.py`  
2. A browser window opens:  
   - Click **Change Directory** to select your folder.  
   - Pick an action (Replace, Prefix, Suffix, Enumerate, etc.).  
   - Type in the parameters (e.g. replace “IMG” with “PHOTO”).  
   - Click **Preview** to see old vs. new names.  
   - Click **Rename Files** to apply.  
   - If you make a mistake, click **Undo** to revert or **Redo** to reapply.

### Using the `FileRenamer` class in Python

```python
from file_renamer.filerenamer import FileRenamer

# Instantiate for a folder
fr = FileRenamer("/path/to/my_folder")

# Build a mapping and apply
mapping = fr.replace_mapping("old", "new")
fr.apply_mapping(mapping)

# Chain methods (each step renames on disk)
# e.g. ["DSC_A.jpg", "DSC_B,jpg"] -> ["PRE_IMG_A_1.jpg", "PRE_IMG_B_2.jpg"]
fr.replace("DSC", "IMG").prefix("PRE_").enum(start=1)

# Undo the last operation
fr.undo()

# Redo it
fr.redo()
```


## License

MIT License © [TurbulentRice](https://github.com/TurbulentRice)