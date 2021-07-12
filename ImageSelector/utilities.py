#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : utilities.py
# SYNOPSIS : A selection of commonly used classes for this project.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

from collections import namedtuple


###############################################################################
# CLASSES
###############################################################################

ImageCacheData = namedtuple(
    'ImageCacheData',
    [
        'cache_file',
        'size',
        'width',
        'height',
        'mtime'
    ]
)


IWConfig = namedtuple(
    'IWConfig',
    [
        'file',
        'owner',
        'width',
        'height',
        'size'
    ]
)

SConfig = namedtuple(
    'SConfig',
    [
        'width',
        'height'
    ]
)


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
