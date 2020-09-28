# file_renamer
Python solutions for bulk-renaming files. Use ReNamer object to interact with/change filenames within a desired directory.

# renamer.py
- ReNamer class: takes a directory path, default is current working directory, allows for various filename manipulations over every file within directory.
- Methods:

rename()        base renaming function, renames one file based on (old_name, new_name)

rename_these()	renames multiple files from dict mapping of {old_names: new_names}

replace()		    replace occurence of a string in each filename (ex. IMG_0243.jpg..., replace("IMG", "SLR") -> SLR_0243.jpg...)

replace_these()	replace multiple strings

add_prefix()	  add string to beginning of each filename (ex. 0243.jpg..., add_prefix("IMG_") -> IMG_0243.jpg...)

add_suffix()	  add something to end of each filename (ex. 0243.jpg..., add_suffix("-large") -> 0243-large.jpg...)

add_enum()		  enumerate filenames (under construction!)

add_from_file()	search each .txt file for RegEx pattern match, add match as suffix or prefix
