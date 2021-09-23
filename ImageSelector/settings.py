#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : settings.py
# SYNOPSIS : Configuration file for ImageSelector.py on the import path
# LICENSE  : MIT
###############################################################################


#
# Options that cannot be set on the command line
#

# Seconds to pause to allow GUI to refresh correctly
GUI_TIMEOUT = 0.1

# Stylesheet for the image window
WINDOW_STYLE = 'background-color: gray;'

# Stylesheet for the selector window
SELECTOR_STYLE = 'background-color: gray; color: white; font-weight: bold;'

# Type of thumbnails in cache - '.png' or '.jpg'
CACHE_FILE_EXTENSION = '.jpg'

# Main window title
SELECTOR_TITLE = 'Image Selector v1.1'

# Main window top left x coordinate
SELECTOR_TOP_LEFT_X = 0

# Main window top left y coordinate
SELECTOR_TOP_LEFT_Y = 0

# Amount of screen width main window takes initially
SELECTOR_WIDTH_FACTOR = 0.987

# Amount of screen height main window takes initially
SELECTOR_HEIGHT_FACTOR = 0.92

# Maximum amount of screen width an image window can take
IMAGE_WIDTH_FACTOR = 0.99

# Maximum amount of screen height an image window can take
IMAGE_HEIGHT_FACTOR = 0.926

# Thumbnail width
ICON_WIDTH = 256

# Thumbnail height
ICON_HEIGHT = 256

# Image window top left x coordinate
IMAGE_TOP_LEFT_X = 12

# Image window top left y coordinate
IMAGE_TOP_LEFT_Y = 40

# Progress dialog width
PROGRESS_DIALOG_WIDTH = 400

# Progress dialog height
PROGRESS_DIALOG_HEIGHT = 30


#
# Options that can be set on the command line
#

# Set the logging level to one of:
#     {'debug', 'info', 'warning', 'error', 'critical'}
LOGGING = 'critical'

# Default image directory
IMAGE_DIRECTORY = 'C:/IMAGES/'

# Default cache directory
CACHE_DIRECTORY = 'C:/IMAGES/.cache/256x256/'

# Cache database file
CACHE_DATABASE = 'C:/IMAGES/.cache/256x256/database.txt'

# Default image type to search for
IMAGE_TYPE = 'jpg'


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
