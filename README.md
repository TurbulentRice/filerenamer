# FileReNamer

Effortlessly rename files in bulk with this Python program. Created to simplify the task of renaming a lot of files, it was written in the time it would have taken to manually fix the filename typo in those 2000 images I just exported...

## Getting started

```sh
# Clone the repo 
git clone https://github.com/TurbulentRice/file_renamer.git
cd file_renamer/

# Use a virtual environment (optional)
python -m venv venv
source venv/bin/activate

# Install package in edit mode
pip install -e .

# Run the entry point console script
rename-files
```

## Usage

### Search and replace

ex. Replace occurences of "IMG" with "PHOTO", and "_sm" with nothing:

```sh
your_folder/
|-- IMG_0001_sm.png -> PHOTO_0001.png
|-- IMG_0002_sm.png -> PHOTO_0002.png
|-- IMG_0003_sm.png -> PHOTO_0003.png
|-- ...
```

### Add prefixes

ex. Add "IMG_" to the beginning of each filename:

```sh
your_folder/
|-- 0001.png -> IMG_0001.png
|-- 0002.png -> IMG_0002.png
|-- 0003.png -> IMG_0003.png
|-- ...
```

### Add sufixes

ex. Add "_sm" to end of each filename:

```sh
your_folder/
|-- IMG_0001.png -> IMG_0001_sm.png
|-- IMG_0002.png -> IMG_0002_sm.png
|-- IMG_0003.png -> IMG_0003_sm.png
|-- ...
```

### Enumerate (WIP)

Add numbers to filenames:

```sh
your_folder/
|-- logo.png        -> 01_logo.png
|-- background.png  -> 02_background.png
|-- header.png      -> 03_header.png
|-- ...
```

### Add from file (WIP)

Use some content from within the file that is being changed to determine its new name.

For example, say you had a folder like this:

```sh
your_folder/
|-- address_file01.txt
|-- address_file02.txt
|-- address_file03.txt
|-- ...
```

Where each `address_file.txt` contains a zipcode somehwere in its contents, and you want to organize the files by those zipcode values. Using regular expressions, we can search the file contents for a zipcode, and rename them so they look like this:

```sh
your_folder/
|-- 01234.txt
|-- 43210.txt
|-- 99999.txt
|-- ...
```
