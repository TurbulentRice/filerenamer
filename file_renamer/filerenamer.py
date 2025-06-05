import os
from typing import Dict
import file_renamer.core as core

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
        if not os.path.isdir(self._directory):
            raise ValueError(f"The specified directory does not exist: '{self._directory}'")
        return self._directory

    @directory.setter
    def directory(self, directory):
        if not os.path.isdir(directory):
            raise ValueError(f"The specified directory does not exist: '{directory}'")
        self._directory = directory

    @property
    def filenames(self, sort = True):
        files = os.listdir(self.directory)
        return sorted(files) if sort else files

    def replace_mapping(self, change_this: str, to_this: str) -> Dict[str, str]:
        return core.build_replace_mapping(self.directory, change_this, to_this)

    def prefix_mapping(self, prefix: str) -> Dict[str, str]:
        return core.build_prefix_mapping(self.directory, prefix)

    def suffix_mapping(self, suffix: str) -> Dict[str, str]:
        return core.build_suffix_mapping(self.directory, suffix)

    def enum_mapping(self, start: int = 1, loc: str = "end", sep: str = "_") -> Dict[str, str]:
        return core.build_enum_mapping(self.directory, start, loc, sep)

    def rename_with_enum_mapping(self, basename: str) -> Dict[str, str]:
        return core.build_rename_with_enum(self.directory, basename)

    def add_from_file_mapping(self, pattern: str, loc: str = "end") -> Dict[str, str]:
        return core.build_add_from_file_mapping(self.directory, pattern, loc)

    def apply_mapping(self, mapping: Dict[str, str]) -> "FileRenamer":
        # Record mapping for undo/redo
        self._history.append(mapping)
        self._redo_stack.clear()
        core.apply_mapping(self.directory, mapping)
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
        core.apply_mapping(self.directory, inverted)
        self._redo_stack.append(last_mapping)
        return self

    def redo(self) -> "FileRenamer":
        if not self._redo_stack:
            raise IndexError("No operations to redo")
        mapping = self._redo_stack.pop()
        core.apply_mapping(self.directory, mapping)
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
    