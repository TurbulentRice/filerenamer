import os
import re
import sys

class ReNamer:

	'''
	Class that allows for bulk renaming of files within a folder.

	Properties:
	----------------
	directory : str 	filepath to target folder, default == cwd
	filenames : [str] 	current list of filenames in directory

	Methods:
	----------------
	get_ext()		return the file extension of a given filename
	join_with_dir()	return new filename joined with directory path
	show_dir()		pretty print current target directory and filenames

	rename()		base renaming function, renames one file
	rename_these()	rename multiple files

	replace()		replace occurences of a string in filenames 
	replace_these()	replace multiple strings
	add_prefix()	add string to beginning of each filename
	add_suffix()	add something to end of each filename (before ext)
	add_enum()		enumerate filenames (start_num, end_num)
	add_from_file()	search each file and add desired match to filename
	'''

	def __init__(self, directory=None):

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
			self._directory = directory

	@property
	def filenames(self):
		return os.listdir(self.directory)
	
	#########################
	#	QUICK METHODS
	#########################
	@staticmethod
	def get_ext(fname):
		return fname[fname.index("."):]

	# Return a new suffixed filepath/filename with extension at end
	@staticmethod
	def get_suffixed(fname, suffix):
		return fname[:fname.index(".")]+suffix+ReNamer.get_ext(fname)

	# Return a new suffixed filepath/filename with extension at end
	@staticmethod
	def get_prefixed(fname, prefix):
		return prefix+fname

	def join_with_dir(self, fname):
		return os.path.join(self.directory, fname)

	def show_dir(self):
		print(f'{"-"*20}\nCurrent directory: "{self.directory}"')
		print(f'{"-"*20}\nFiles: ')
		for n, file in enumerate(self.filenames, 1):
			print(f"{n})\t{file}")

	#########################
	#	GENERIC RENAMING METHODS
	#	- main methods for changing multiple files, used by all others
	#	- make changes based on {old: new} key value pairs
	#########################

	# Rename one file (a key:value pair)
	def rename(self, old_path, new_path):
		# Make sure old_path exists and new_path doesn't
		if not os.path.exists(old_path):
			print(f'ERROR: "{old_path}" does not exist. Skipping...')
			return
		elif os.path.exists(new_path):
			print(f'ERROR: "{new_path}" already exists. Skipping...')
			return

		os.rename(old_path, new_path)

	# Rename multiple files using dict mapping of {old_name: new_name}
	# Adds folder paths to filenames and sends each to self.rename()
	def rename_these(self, files_to_change: dict, display=True):
		# Display and verify changes to be made
		if display:
			print(f"{"-"*20}\nCHANGES:\n{"-"*20}")
			for old, new in files_to_change.items():
				print(f"{old}\t->\t{new}")
		ans = input(f"Make these changes? (y/n): ")
		if ans != "y":
			print("Changes discarded...\n")
			return

		# Make changes
		for old, new in files_to_change.items():
			self.rename(self.join_with_dir(old), self.join_with_dir(new))
			# Log changes so they can be reversed later

	#########################
	#	MAIN METHODS
	#	- wrappers to add functionality to renaming methods
	#########################

	# Replace every occurence of a string in every filename
	def replace(self, change_this, to_this):
		def is_in()
		change_list = {

		filename: filename.replace(change_this, to_this)
		for filename in self.filenames if change_this in filename

		}
		
		self.rename_these(change_list)

	# Replace multiple strings
	def replace_these(self, ammendments: dict):
		for change_this, to_this in ammendments:
			self.replace(change_this, to_this)
			
	# Add prefix to filenames
	def add_prefix(self, prefix, display=True):
		change_list = {

		filename: prefix+filename
		for filename in self.filenames if not filename.startswith(prefix)

		} 

		self.rename_these(change_list, display)

	# Add suffix to filenames before extensions
	def add_suffix(self, suffix, display=True):
		change_list = {

		filename: self.get_suffixed(filename, suffix)
		for filename in self.filenames if not filename.endswith(suffix)

		} 

		self.rename_these(change_list, display)

	# Enumerate files (suffix or prefix), replace existing suffix enum
	def add_enum(self, start, ascending=True, loc='end'):
		pass

	# Search for a regex pattern within each .txt file, append match to filename
	# Takes a pattern, loc in filename to append ('start' prefix || 'end' suffix)
	def add_from_file(self, pattern, loc='end'):

		ext = '.txt'
		change_list = {}

		# Determine how we'll join the match with the filename
		if loc == "end":
			joiner = ReNamer.get_suffixed
		else:
			joiner = ReNamer.get_prefixed

		
		for filename in self.filenames:
			# Skip non .txt files
			if not filename.endswith(ext):
				print(f"Skipping {filename}")
				continue

			# Otherwise, open and read-in the file, re.search for pattern
			with open(self.join_with_dir(filename)) as f:
				txt = f.read()
			search_result = re.search(pattern, txt)

			# If there's a match, join it and add to changelist
			if search_result is not None:
				change_list[filename] = joiner(filename, search_result.group(1))

		self.rename_these(change_list)




