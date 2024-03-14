#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : settings.py
# SYNOPSIS : Configuration file for ViewMPS.py on the import path.
# LICENSE  : MIT
###############################################################################


################
# GUI settings #
################

# The main window title
MAIN_WINDOW_TITLE = 'ViewMPS (v1.0a)'

# Top left X position for the main window
MAIN_WINDOW_TOP_LEFT_X = 10

# Top left Y position for the main window
MAIN_WINDOW_TOP_LEFT_Y = 40

# Width of the main window
MAIN_WINDOW_WIDTH = 370

# Height of the main window
MAIN_WINDOW_HEIGHT = 40

# The styling of the main window
MAIN_WINDOW_STYLESHEET = 'background-color: lightgray; color: black;'

# Top left X position for a child window
CHILD_WINDOW_TOP_LEFT_X = 20

# Top left Y position for a child window
CHILD_WINDOW_TOP_LEFT_Y = 50

# Maximum permitted width of a child window
MAX_CHILD_WINDOW_WIDTH = 1880

# Maximum permitted height of a child window
MAX_CHILD_WINDOW_HEIGHT = 980

# Starting width of a histogram child window
HISTOGRAM_WIDTH = 800

# Starting height of a histogram child window
HISTOGRAM_HEIGHT = 800

# The starting directory to look in for MPS files
GUI_START_DIRECTORY = {DIRECTORY}

####################
# General settings #
####################

# Set the logging level to one of:
#     {'debug', 'info', 'warning', 'error', 'critical'}
LOGGING = 'critical'


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
