#!/usr/bin/env python3

"""
Command-line interface for file renaming functionality.

This module provides a command-line interface for the FileRenamer tool, allowing users
to perform batch file renaming operations from the terminal. It supports various
operations including search and replace, adding prefixes/suffixes, enumeration,
and more.

Usage Examples:
    # Replace "IMG_" with "PHOTO_" in all filenames
    python -m file_renamer.cli --target ./photos --replace "IMG_=PHOTO_"

    # Add prefix and suffix to all files
    python -m file_renamer.cli --target ./photos --prefix "PRE_" --suffix "_2023"

    # Enumerate files starting from 1
    python -m file_renamer.cli --target ./photos --enum --enum-start 1

    # Rename all files to "photo_1.jpg", "photo_2.jpg", etc.
    python -m file_renamer.cli --target ./photos --rename-with-enum "photo"

    # Add content from .txt files to filenames
    python -m file_renamer.cli --target ./photos --add-from-file "Title: (.*)"

"""

import sys
import argparse
from file_renamer.core import FileRenamer

def main():
    parser = argparse.ArgumentParser(description="Batch rename files via FileRenamer.")
    parser.add_argument(
        "--target", "-t", required=True,
        help="Target directory (must be an existing directory)."
    )
    parser.add_argument(
        "--replace", "-r", action="append",
        help="Replace occurrences: specify as old=new. Can be used multiple times."
    )
    parser.add_argument(
        "--prefix", "-p", help="Add prefix to all filenames."
    )
    parser.add_argument(
        "--suffix", "-s", help="Add suffix to all filenames."
    )
    parser.add_argument(
        "--enum-start", type=int, default=1,
        help="Starting number for enumeration (used with --enum)."
    )
    parser.add_argument(
        "--enum-loc", choices=["start", "end"], default="end",
        help="Location for enumeration: 'start' or 'end'."
    )
    parser.add_argument(
        "--enum-sep", default="_",
        help="Separator for enumeration."
    )
    parser.add_argument(
        "--enum", action="store_true",
        help="Enumerate files."
    )
    parser.add_argument(
        "--rename-with-enum", help="Rename files to basename+index."
    )
    parser.add_argument(
        "--add-from-file", help="Pattern (regex) to search in .txt files and append/prepend."
    )
    parser.add_argument(
        "--add-loc", choices=["start", "end"], default="end",
        help="Location for add-from-file: 'start' or 'end'."
    )
    parser.add_argument(
        "--undo", action="store_true",
        help="Undo last operation."
    )
    parser.add_argument(
        "--redo", action="store_true",
        help="Redo last undone operation."
    )
    parser.add_argument(
        "--yes", "-y", action="store_true",
        help="Skip confirmation prompts (assumes yes)."
    )

    args = parser.parse_args()

    try:
        fr = FileRenamer(args.target)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Undo/redo take precedence
    if args.undo:
        try:
            fr.undo()
            print("Undo successful.")
        except Exception as e:
            print(f"Undo failed: {e}")
            sys.exit(1)
        sys.exit(0)

    if args.redo:
        try:
            fr.redo()
            print("Redo successful.")
        except Exception as e:
            print(f"Redo failed: {e}")
            sys.exit(1)
        sys.exit(0)

    performed = False

    # Replace operations
    if args.replace:
        for pair in args.replace:
            if "=" not in pair:
                print(f"Invalid replace format: '{pair}'. Use old=new.")
                continue
            old, new = pair.split("=", 1)
            fr.replace(old, new)
            performed = True

    # Prefix
    if args.prefix:
        fr.prefix(args.prefix)
        performed = True

    # Suffix
    if args.suffix:
        fr.suffix(args.suffix)
        performed = True

    # Enumerate
    if args.enum:
        fr.enum(start=args.enum_start, loc=args.enum_loc, sep=args.enum_sep)
        performed = True

    # Rename with enum
    if args.rename_with_enum:
        fr.rename_with_enum(args.rename_with_enum)
        performed = True

    # Add from file
    if args.add_from_file:
        fr.add_from_file(args.add_from_file, loc=args.add_loc)
        performed = True

    if not performed:
        print("No operation specified. Use --help for options.")
        sys.exit(0)

    print("Operations completed successfully.")

if __name__ == "__main__":
    main()
