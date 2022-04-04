# procare-download

Downloads photos and videos from Procare and updates their filenames and EXIF tags.

## Requirements

**procare-download** requires Python 3.7 or later. It additionally has PyPI dependencies, which can be installed with:

    pip install -r requirements.txt

## Usage

**procare-download** includes two python scripts, which should be executed sequentially:

* **procare_download.py**: Bulk downloads photos and videos. **procare_download.py** requires a valid Procare username and password (password prompted for after starting the script).
* **procare_cleanup.py**: Updates photo EXIF tags and renames photos and videos.

Examples of running each script are provided below:

Retrieving all photos and videos:

    python3 procare_download.py -e 'myemail@myprovider.com' -d ~/Downloads

Retrieving photos and videos since March 1st, 2022

    python3 procare_download.py -e 'myemail@myprovider.com' -d ~/Downloads -f 20220301

Cleaning photos and videos in the same directory

    python3 procare_cleanup.py -i ~/Downloads -o ~/Downloads

## Known Issues

The Procare API is currently only authorized against once, and the received token may expire. This will be fixed in a future version 