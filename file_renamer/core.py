"""
Core logic and data structures for file renaming functionality
"""

import os
import re
from typing import Dict

class FileRenamer:
    """
    Wrapper around stateless file-renaming functions. Instantiate with a target `directory`,
    then use one of the mapping methods to generate { old_name: new_name } or use chainable
    methods to build and apply in a single step. Supports undo/redo of each batch operation.

    Properties
    ----------
    directory : str
        Path to the folder on which operations will be performed. Must exist.

    Methods
    -------
    replace_mapping(change_this, to_this) -> Dict[str, str]
        Build a mapping to replace occurrences of `change_this` with `to_this` in filenames.
    prefix_mapping(prefix) -> Dict[str, str]
        Build a mapping to add `prefix` to all filenames not already starting with it.
    suffix_mapping(suffix) -> Dict[str, str]
        Build a mapping to add `suffix` (before extension) to all filenames not already ending with it.
    enum_mapping(start=1, loc="end", sep="_") -> Dict[str, str]
        Build a mapping to enumerate files by appending (loc="end") or prepending (loc="start") an
        increasing number beginning at `start`, separated by `sep`.
    rename_with_enum_mapping(basename) -> Dict[str, str]
        Build a mapping to rename each file to `basename + index + original_extension`.
    add_from_file_mapping(pattern, loc="end") -> Dict[str, str]
        Build a mapping by searching each .txt file in `directory` for `pattern` 
        (a regex with a capture group) and appending (loc="end") or prepending (loc="start") the
        first captured group to its filename.
    apply_mapping(mapping) -> FileRenamer
        Apply the given mapping of old_name: new_name to disk and record the operation for undo.

    Chainable Methods
    ------------------
    replace(change_this, to_this) -> FileRenamer        Build and apply a replace mapping.
    prefix(prefix) -> FileRenamer                       Build and apply a prefix mapping.
    suffix(suffix) -> FileRenamer                       Build and apply a suffix mapping.
    enum(start=1, loc="end", sep="_") -> FileRenamer    Build and apply an enumeration mapping.
    rename_with_enum(basename) -> FileRenamer           Build and apply a rename-with-enumeration mapping.
    add_from_file(pattern, loc="end") -> FileRenamer    Build and apply an "add from file" mapping.

    Undo/Redo
    ---------
    undo() -> FileRenamer       Revert the most recently applied mapping. Raises IndexError if no history.
    redo() -> FileRenamer       Reapply the most recently undone mapping. Raises IndexError if nothing to redo.
    """

    def __init__(self, directory: str = None):
        self.directory = directory
        self._history = []       # stack of applied mappings for undo
        self._redo_stack = []    # stack for redo

    @property
    def directory(self):
        if not self._directory:
            raise ValueError("No directory specified")
        if not os.path.isdir(self._directory):
            raise ValueError(f"The specified directory does not exist: '{self._directory}'")
        return self._directory

    @directory.setter
    def directory(self, directory):
        if not directory:
            raise ValueError("No directory specified")
        if not os.path.isdir(directory):
            raise ValueError(f"The specified directory does not exist: '{directory}'")
        self._directory = directory

    @property
    def filenames(self, sort = True):
        files = os.listdir(self.directory)
        return sorted(files) if sort else files

    def replace_mapping(self, change_this: str, to_this: str) -> Dict[str, str]:
        return build_replace_mapping(self.directory, change_this, to_this)

    def prefix_mapping(self, prefix: str) -> Dict[str, str]:
        return build_prefix_mapping(self.directory, prefix)

    def suffix_mapping(self, suffix: str) -> Dict[str, str]:
        return build_suffix_mapping(self.directory, suffix)

    def enum_mapping(self, start: int = 1, loc: str = "end", sep: str = "_") -> Dict[str, str]:
        return build_enum_mapping(self.directory, start, loc, sep)

    def rename_with_enum_mapping(self, basename: str) -> Dict[str, str]:
        return build_rename_with_enum(self.directory, basename)

    def add_from_file_mapping(self, pattern: str, loc: str = "end") -> Dict[str, str]:
        return build_add_from_file_mapping(self.directory, pattern, loc)

    def apply_mapping(self, mapping: Dict[str, str]) -> "FileRenamer":
        # Record mapping for undo/redo
        self._history.append(mapping)
        self._redo_stack.clear()
        apply_mapping(self.directory, mapping)
        return self

    # --- Chainable Methods (build & apply in one step) ---
    def replace(self, change_this: str, to_this: str) -> "FileRenamer":
        mapping = self.replace_mapping(change_this, to_this)
        return self.apply_mapping(mapping)

    def prefix(self, prefix: str) -> "FileRenamer":
        mapping = self.prefix_mapping(prefix)
        return self.apply_mapping(mapping)

    def suffix(self, suffix: str) -> "FileRenamer":
        mapping = self.suffix_mapping(suffix)
        return self.apply_mapping(mapping)

    def enum(self, start: int = 1, loc: str = "end", sep: str = "_") -> "FileRenamer":
        mapping = self.enum_mapping(start, loc, sep)
        return self.apply_mapping(mapping)

    def rename_with_enum(self, basename: str) -> "FileRenamer":
        mapping = self.rename_with_enum_mapping(basename)
        return self.apply_mapping(mapping)

    def add_from_file(self, pattern: str, loc: str = "end") -> "FileRenamer":
        mapping = self.add_from_file_mapping(pattern, loc)
        return self.apply_mapping(mapping)

    # --- Undo/Redo methods ---
    def undo(self) -> "FileRenamer":
        if not self._history:
            raise IndexError("No operations to undo")
        last_mapping = self._history.pop()
        inverted = {new: old for old, new in last_mapping.items()}
        # Apply inverted mapping without recording in history
        apply_mapping(self.directory, inverted)
        self._redo_stack.append(last_mapping)
        return self

    def redo(self) -> "FileRenamer":
        if not self._redo_stack:
            raise IndexError("No operations to redo")
        mapping = self._redo_stack.pop()
        apply_mapping(self.directory, mapping)
        self._history.append(mapping)
        return self
    

class FileRenamerSingleton:
    """
    A thin wrapper providing a single shared FileRenamer instance.
    Use initialize(directory) to create or reset, and get() to access it.
    This is way overkill but was fun to make.
    """
    _instance = None

    @staticmethod
    def initialize(directory: str):
        if FileRenamerSingleton._instance is None:
            FileRenamerSingleton._instance = FileRenamer(directory)
        else:
            FileRenamerSingleton._instance.directory = directory
            # Clear history/redo since directory changed
            FileRenamerSingleton._instance._history.clear()
            FileRenamerSingleton._instance._redo_stack.clear()

    @staticmethod
    def get():
        return FileRenamerSingleton._instance
    

"""
Stateless file-renaming functions
"""

def build_replace_mapping(
    directory: str,
    change_this: str,
    to_this: str
) -> Dict[str, str]:
    """
    Scan `directory` for any file that contains `change_this` in its name,
    and build a mapping { old_name: new_name } without touching disk.
    """
    out: Dict[str, str] = {}
    for fname in sorted(os.listdir(directory)):
        if change_this in fname:
            new_name = fname.replace(change_this, to_this)
            out[fname] = new_name
    return out

def apply_mapping(directory: str, mapping: Dict[str, str]) -> None:
    """
    Actually perform os.rename(old → new) on each pair in `mapping`.
    """
    for old, new in mapping.items():
        old_path = os.path.join(directory, old)
        new_path = os.path.join(directory, new)
        if not os.path.exists(old_path):
            # TODO handle old path is gone
            continue
        if os.path.exists(new_path):
            # TODO handle new path collisions
            continue
        os.rename(old_path, new_path)


def build_prefix_mapping(
    directory: str,
    prefix: str
) -> Dict[str, str]:
    """
    Add `prefix` to every filename in `directory` that does not already start with it.
    """
    return {
        filename: prefix + filename
        for filename in sorted(os.listdir(directory))
        if not filename.startswith(prefix)
    }

def build_suffix_mapping(
    directory: str,
    suffix: str
) -> Dict[str, str]:
    """
    Add `suffix` before the file extension for every filename in `directory`
    that does not already end with `suffix` (ignoring the extension).
    """
    mapping: Dict[str, str] = {}
    for filename in sorted(os.listdir(directory)):
        root, ext = os.path.splitext(filename)
        if root.endswith(suffix):
            continue
        new_name = root + suffix + ext
        mapping[filename] = new_name
    return mapping

# TODO optional sort func
def build_enum_mapping(
    directory: str,
    start: int = 1,
    loc: str = "end",
    sep: str = "_"
) -> Dict[str, str]:
    """
    Append (loc='end') or prepend (loc='start') an enumeration number to each filename.
    Enumeration starts at `start` and increments by 1, separated by `sep`.
    """
    mapping: Dict[str, str] = {}
    filenames = sorted(os.listdir(directory))
    for idx, filename in enumerate(filenames):
        root, ext = os.path.splitext(filename)
        number = str(idx + start)
        if loc == "start":
            new_name = number + root + ext
        else:
            new_name = root + sep + number + ext
        mapping[filename] = new_name
    return mapping

# TODO optional sort func
def build_rename_with_enum(
    directory: str,
    basename: str
) -> Dict[str, str]:
    """
    Rename each file in `directory` to basename + index + original extension.
    Indexing starts at 1 and increases by 1 for each file.
    """
    mapping: Dict[str, str] = {}
    filenames = sorted(os.listdir(directory))
    for idx, filename in enumerate(filenames):
        _, ext = os.path.splitext(filename)
        new_name = f"{basename}{idx + 1}{ext}"
        mapping[filename] = new_name
    return mapping

def build_add_from_file_mapping(
    directory: str,
    pattern: str,
    loc: str = "end"
) -> Dict[str, str]:
    """
    Search inside each .txt file in `directory` for `pattern` (regex).
    If a match is found, append (loc='end') or prepend (loc='start')
    the first capture group to the filename, preserving extension.
    """
    mapping: Dict[str, str] = {}
    filenames = sorted(os.listdir(directory))
    for filename in filenames:
        if not filename.lower().endswith(".txt"):
            continue
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        except (IOError, OSError):
            continue
        m = re.search(pattern, text)
        if not m:
            continue
        match_text = m.group(1)
        root, ext = os.path.splitext(filename)
        if loc == "start":
            new_name = match_text + filename
        else:
            new_name = root + match_text + ext
        mapping[filename] = new_name
    return mapping
