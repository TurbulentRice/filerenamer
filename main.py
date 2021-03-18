from renamer import ReNamer

#
# DEMO
#
# Let ReNamer know which directory to alter
# If no path is provided, will assume current directory
#
# Use show_dir() to preview filenames
#
# ReNamer will display proposed changes and ask for confirmation
# before altering any files, for safety.
#
# TO DO
# - Methods should return reference to self to allow chaining alterations
#       e.g. my_folder.replace("this", "that").add_prefix("pre")
# - Add remove() method for easy removing occurences of a string (replace with "")
#       e.g. my_folder.remove("delete") > my_folder.replace("delete", "")
# - Reversal method for undoing previous change(s)

path = "./renamer_test_images/"
my_folder = ReNamer(path)

my_folder.show_dir()

#my_folder.replace("grab", "shot")
#my_folder.add_prefix("screen_")
#my_folder.add_suffix("-test")

my_folder.show_dir()
