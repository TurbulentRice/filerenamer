import os
from typing import Dict
import file_renamer.core as core

class FileReNamer:

	'''
	Class for bulk-renaming files in a folder.

	Properties:
	----------------
	directory : str 	filepath to target folder, default == cwd
	filenames : [str] 	current list of filenames in directory

	Methods:
	----------------
	rename()		base renaming function, renames one file
	apply_mapping()	applies a dictionary of old_name:new_name renames

	replace_mapping()	build mapping for replacing substrings in filenames
	prefix_mapping()	build mapping for adding prefixes
	suffix_mapping()	build mapping for adding suffixes
	enum_mapping()	build mapping for enumerating filenames
	rename_with_enum_mapping()	build mapping for renaming files with a basename and enumeration
	add_from_file_mapping()	build mapping by extracting text from files and adding it to filenames

	TODO
	- Method chaining
	- "Remove" functinoality (wrapper for replace with empty string)
	- Allow undo/redo with internal history of changesets
	'''

	def __init__(self, directory: str=None):
		self.directory = directory

	#########################
	#	PROPERTIES
	#########################
	@property
	def directory(self):
		return self._directory
	@directory.setter
	def directory(self, directory):
		if directory is None:
			self._directory = os.getcwd()
		else:
			# Validate that the directory exists
			if not os.path.exists(directory):
				raise ValueError(f"The specified directory does not exist: '{directory}'")
			self._directory = directory

	@property
	def filenames(self):
		return os.listdir(self.directory)
	
	#########################
	#	RENAMING METHODS
	#########################

	def apply_mapping(self, mapping: Dict[str, str]) -> None:
		"""
		Apply a dictionary mapping of old filename to new filename to rename files.
		"""
		core.apply_mapping(self.directory, mapping)

	#########################
	#	MAPPING BUILDERS
	#########################

	def replace_mapping(self, change_this: str, to_this: str) -> Dict[str, str]:
		"""
		Build a mapping dict for replacing occurrences of change_this with to_this in filenames.
		"""
		return core.build_replace_mapping(self.directory, change_this, to_this)

	def prefix_mapping(self, prefix: str) -> Dict[str, str]:
		"""
		Build a mapping dict for adding a prefix to filenames that don't already start with it.
		"""
		return core.build_prefix_mapping(self.directory, prefix)

	def suffix_mapping(self, suffix: str) -> Dict[str, str]:
		"""
		Build a mapping dict for adding a suffix before the extension of filenames that don't already end with it.
		"""
		return core.build_suffix_mapping(self.directory, suffix)

	def enum_mapping(self, start: int=1, loc: str='end', sep: str='_') -> Dict[str, str]:
		"""
		Build a mapping dict for enumerating filenames by appending or prepending numbers with a separator.

		loc: 'end' to append, 'start' to prepend
		"""
		return core.build_enum_mapping(self.directory, start, loc, sep)

	def rename_with_enum_mapping(self, basename: str) -> Dict[str, str]:
		"""
		Build a mapping dict for renaming files to basename + enumeration + original extension.
		"""
		return core.build_rename_with_enum(self.directory, basename)

	def add_from_file_mapping(self, pattern: str, loc: str='end') -> Dict[str, str]:
		"""
		Build a mapping dict by searching each .txt file for a regex pattern and adding the matched group to the filename.

		loc: 'end' to add suffix, otherwise prefix
		"""
		return core.build_add_from_file_mapping(self.directory, pattern, loc)
