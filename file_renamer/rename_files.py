#!/usr/bin/env python

"""
This script uses the FileReNamer class to batch rename files in a folder.
Let FileReNamer know which directory to target by providing a path. Relative paths work too!
"""

from .file_renamer import FileReNamer

def get_target_directory():
  user_input = input("Enter the path of the target directory (or press Enter to use the current directory): ").strip()
  return user_input if user_input else None

def confirm_directory():
  user_input = input("Continue with this directory? (y/n): ").strip()
  return user_input

def hello():
  print("""
  ______ _ _     ______     _   _                           
  |  ___(_) |    | ___ \   | \ | |                          
  | |_   _| | ___| |_/ /___|  \| | __ _ _ __ ___   ___ _ __ 
  |  _| | | |/ _ \    // _ \ . ` |/ _` | '_ ` _ \ / _ \ '__|
  | |   | | |  __/ |\ \  __/ |\  | (_| | | | | | |  __/ |   
  \_|   |_|_|\___\_| \_\___\_| \_/\__,_|_| |_| |_|\___|_|   

""")

def done():
  print("""
  ____                   _ 
  |  _ \  ___  _ __   ___| |
  | | | |/ _ \| '_ \ / _ \ |
  | |_| | (_) | | | |  __/_|
  |____/ \___/|_| |_|\___(_)

""")
  

def main():
  hello()
  target_directory = None
  # Main loop
  while True:
    try:
      # Determine target dir if not already set, or if user wants to change it
      while True:
        if target_directory is None or input(f"Continue in {target_directory}? (y/n): ") == 'n':
          target_directory = get_target_directory()
        my_folder = FileReNamer(target_directory)
        my_folder.show_dir()
        if confirm_directory() == "y": break

      # Get user action
      user_action = input(
        "What would you like to do?\n"
        +"[1] Replace a string\n"
        +"[2] Add a prefi\n"
        +"[3] Add a suffix\n"
        # +"[4] Enumerate\n"
        # +"[5] Add from file\n"
      )

      # Replace
      if user_action == '1':
        # Collect changes to be made sequentially
        changes = {}
        while True:
          change_this = input("Change this: ")
          to_this = input("To this: ")
          changes[change_this] = to_this
          if input("Add another change? (y/n): ") != 'y':
            break
        my_folder.replace_these(changes)
        done()
      # Prefix
      elif user_action == '2':
        prefix = input("Add prefix: ")
        my_folder.add_prefix(prefix)
        done()
      elif user_action == '3':
        suffix = input("Add suffix: ")
        my_folder.add_suffix(suffix)
        done()
      elif user_action == '4':
        print('Enumeration is a WIP!\n')
      elif user_action == '5':
        print('Adding from a file is a WIP!\n')
      else:
        print('Nothing selected. Doing nothing!\n')
    except ValueError as e:
      print(f"Error: {e}")

if __name__ == "__main__":
  main()
