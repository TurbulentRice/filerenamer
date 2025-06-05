"""
Stateless file-renaming functions
"""

import os
from typing import Dict
import re

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
