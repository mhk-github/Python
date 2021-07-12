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
from utilities import SConfig


###############################################################################
# FUNCTIONS
###############################################################################

def init():
    """Sets up the logging system."""

    log_level = logging.NOTSET
    log_config_level = settings.LOGGING
    if log_config_level == 'debug':
        log_level = logging.DEBUG
    elif log_config_level == 'info':
        log_level = logging.INFO
    elif log_config_level == 'warning':
        log_level = logging.WARNING
    elif log_config_level == 'error':
        log_level = logging.ERROR
    elif log_config_level == 'critical':
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
        '-t',
        '-type',
        dest='image_type',
        metavar='{jpg|png}',
        choices=['jpg', 'png'],
        default=settings.IMAGE_TYPE,
        help='Type of image files'
    )
    parser.add_argument(
        '--refresh-cache',
        dest='do_refresh',
        action='store_true',
        help='Update cache data based on image file modification time'
    )
    parser.add_argument(
        '--compact-cache',
        dest='do_compact_cache',
        action='store_true',
        help='Remove from cache any data for a file not in the input file list'
    )
    args = parser.parse_args()

    init()
    logger = logging.getLogger(__name__)
    logger.info('ImageSelector.py - Start')

    cache_directory = Path(args.cache_directory).as_posix()
    if not cache_directory.endswith('/'):
        cache_directory += '/'
    image_directory = Path(args.directory).as_posix()
    if not image_directory.endswith('/'):
        image_directory += '/'
    image_type = args.image_type
    do_refresh = args.do_refresh
    do_compact_cache = args.do_compact_cache

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
    logger.debug(f"    Logging = {settings.LOGGING}")
    logger.debug(f"    Cache database = {settings.CACHE_DATABASE}")

    cache = ImageFileCache(
        settings.CACHE_DATABASE,
        cache_directory,
        image_directory,
        image_type
    ).cache
    if cache:
        app = QApplication(sys.argv)
        screen_size = app.primaryScreen().size()
        selector_cfg = SConfig(
            screen_size.width(),
            screen_size.height()
        )
        selector = SelectionWindow(selector_cfg, cache)
        selector.show()
        time.sleep(settings.GUI_TIMEOUT)
        selector.create_view()
        logger.debug(
            f"  Created SelectorWindow for screen size = {screen_size.width()}"
            f"x{screen_size.height()}"
        )

        logger.debug('  Transferring control to PyQt5')
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
