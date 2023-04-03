#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : settings.py
# SYNOPSIS : Configuration file for Checksum project on the import path.
# LICENSE  : MIT
###############################################################################


###############################################################################
# BEGIN
###############################################################################

####################
# General settings #
####################

# The amount of bytes to read from a file as a block
READ_AMOUNT = 1048576

################
# GUI settings #
################

# The main window title
GUI_WINDOW_TITLE = 'Checksum (v0.1)'

# Top left X position of the main window
GUI_TOP_LEFT_X = 10

# Top left Y position of the main window
GUI_TOP_LEFT_Y = 40

# Width of the main window
GUI_WIDTH = 1350

# Height of the main window
GUI_HEIGHT = 250

# Default style sheet for the checksum match label
GUI_DEFAULT_MATCH_STYLE = 'border: 1px solid gray;'

# Stylesheet for when the given checksum matches the file's
GUI_RIGHT_MATCH_STYLE = (
    'background-color: green; color: white; border: 1px solid gray;'
)

# Stylesheet for when the given checksum does not match the file's
GUI_WRONG_MATCH_STYLE = (
    'background-color: red; color: white; border: 1px solid gray;'
)

# Set the logging level to one of:
#     {'debug', 'info', 'warning', 'error', 'critical'}
GUI_LOGGING = 'error'


###############################################################################
# END
###############################################################################
# Local Variables:
# mode: python
# End:
