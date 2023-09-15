#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : settings.py
# SYNOPSIS : Configuration file for DATProcessor project on the import path.
# LICENSE  : MIT
###############################################################################


###############################################################################
# BEGIN
###############################################################################

####################
# General settings #
####################

# SQLAlchemy can show each line of SQL used
SHOW_SQL = False

# Set to the number of CPUs
MAX_THREADS = 4

# 2-digit years are considered 1900s from this number onwards, 2000s otherwise
CUTOFF = 50

# Whether to delete intermediate CDAT files used to make an archive
DELETE_INTERMEDIATE_CDAT_FILES = True

#####################
# Database settings #
#####################

# Limit sizes for strings
MAX_SOURCE_NAME_LENGTH = 32
MAX_DIRECTORY_NAME_LENGTH = 256
MAX_FILE_NAME_LENGTH = 256

# Limit size for each batch of objects to be added in bulk to the database
BATCH_SIZE = 100000


###############################################################################
# END
###############################################################################
# Local Variables:
# mode: python
# End:
