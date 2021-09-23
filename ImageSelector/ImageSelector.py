#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : ImageSelector.py
# SYNOPSIS : Presents a listbox to select an image file to display.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import argparse
import logging
import sys
import time

from PyQt5.QtWidgets import QApplication
from pathlib import Path

import settings

from cache import ImageFileCache
from selectionview import SelectionWindow


###############################################################################
# FUNCTIONS
###############################################################################

def init(logging_level):
    """
    Sets up the logging system.

    Parameters
    ----------
    logging_level : str
        One of '{debug|info|warning|error|critical}'
    """

    log_level = logging.NOTSET
    if logging_level == 'debug':
        log_level = logging.DEBUG
    elif logging_level == 'info':
        log_level = logging.INFO
    elif logging_level == 'warning':
        log_level = logging.WARNING
    elif logging_level == 'error':
        log_level = logging.ERROR
    elif logging_level == 'critical':
        log_level = logging.CRITICAL

    logging.basicConfig(
        format=(
            '%(asctime)s '
            '%(name)s '
            '%(levelname)-8s '
            '[%(process)06d] '
            '<%(thread)08X> '
            '(%(lineno)06d): '
            '%(message)s'
        ),
        datefmt='%H:%M:%S',
        level=log_level
    )


def main():
    """The application driver function."""

    parser = argparse.ArgumentParser(
        description='Allows images to be displayed from a selection.'
    )
    parser.add_argument(
        '-c',
        '--cache',
        dest='cache_directory',
        metavar='DIR',
        default=settings.CACHE_DIRECTORY,
        help='Image thumbnail cache location'
    )
    parser.add_argument(
        '-d',
        '--directory',
        dest='directory',
        metavar='DIR',
        default=settings.IMAGE_DIRECTORY,
        help='Root directory for image files'
    )
    parser.add_argument(
        '-l',
        '--log',
        dest='logging_level',
        metavar='{debug|info|warning|error|critical}',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        default=settings.LOGGING,
        help='Logging level'
    )
    parser.add_argument(
        '-t',
        '--type',
        dest='image_type',
        metavar='{jpg|png}',
        choices=['jpg', 'png'],
        default=settings.IMAGE_TYPE,
        help='Type of image files'
    )
    parser.add_argument(
        '--cache-database',
        dest='cache_database',
        metavar='FILE',
        default=settings.CACHE_DATABASE,
        help='Canonical path of the cache database file'
    )
    args = parser.parse_args()

    logging_level = args.logging_level
    init(logging_level)
    logger = logging.getLogger(__name__)
    logger.info('ImageSelector.py - Start')

    cache_directory = Path(args.cache_directory).as_posix()
    if not cache_directory.endswith('/'):
        cache_directory += '/'
    image_directory = Path(args.directory).as_posix()
    if not image_directory.endswith('/'):
        image_directory += '/'
    image_type = args.image_type
    cache_database = args.cache_database

    logger.debug('  Setup:')
    logger.debug(f"    Arguments = {args}")
    logger.debug(f"    GUI timeout = {settings.GUI_TIMEOUT}")
    logger.debug(f"    Window style = {settings.WINDOW_STYLE}")
    logger.debug(f"    Selector style = {settings.SELECTOR_STYLE}")
    logger.debug(f"    Cache file extension = {settings.CACHE_FILE_EXTENSION}")
    logger.debug(f"    Selector title = {settings.SELECTOR_TITLE}")
    logger.debug(f"    Selector top left X = {settings.SELECTOR_TOP_LEFT_X}")
    logger.debug(f"    Selector top left Y = {settings.SELECTOR_TOP_LEFT_Y}")
    logger.debug(
        f"    Selector width factor = {settings.SELECTOR_WIDTH_FACTOR}"
    )
    logger.debug(
        f"    Selector height factor = {settings.SELECTOR_HEIGHT_FACTOR}"
    )
    logger.debug(f"    Image width factor = {settings.IMAGE_WIDTH_FACTOR}")
    logger.debug(f"    Image height factor = {settings.IMAGE_HEIGHT_FACTOR}")
    logger.debug(f"    Icon width = {settings.ICON_WIDTH}")
    logger.debug(f"    Icon height = {settings.ICON_HEIGHT}")
    logger.debug(f"    Image top left X = {settings.IMAGE_TOP_LEFT_X}")
    logger.debug(f"    Image top left Y = {settings.IMAGE_TOP_LEFT_Y}")
    logger.debug(
        f"    Progress dialog width = {settings.PROGRESS_DIALOG_WIDTH}"
    )
    logger.debug(
        f"    Progress dialog height = {settings.PROGRESS_DIALOG_HEIGHT}"
    )

    cache = ImageFileCache(
        cache_database,
        cache_directory,
        image_directory,
        image_type
    ).data
    if cache:
        app = QApplication(sys.argv)
        selector = SelectionWindow()
        selector.show()
        time.sleep(settings.GUI_TIMEOUT)
        selector.create_view(cache)
        logger.info('ImageSelector.py - End -- Control moving to PyQt5')
        sys.exit(app.exec_())
    else:
        logger.warning('  No image files found !')
        logger.info('ImageSelector.py - End')


###############################################################################
# DRIVER
###############################################################################

if __name__ == '__main__':
    main()


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
