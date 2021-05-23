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

from PIL import Image
from PyQt5.QtCore import (
    QSize,
    Qt
)
from PyQt5.QtGui import (
    QIcon,
    QPixmap
)
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QProgressDialog,
    QWidget
)
from concurrent import futures
from itertools import count
from pathlib import Path

import argparse
import collections
import hashlib
import glob
import logging
import os
import sys
import time

import settings


###############################################################################
# CONSTANTS
###############################################################################

IMAGES_GLOB_PREFIX = '**/*.'

MINIMUM_LABEL_SIZE_X = 1
MINIMUM_LABEL_SIZE_Y = 1


###############################################################################
# CLASSES
###############################################################################

IWConfig = collections.namedtuple(
    'IWConfig',
    [
        'file',
        'owner',
        'width',
        'height',
        'size'
    ]
)


SConfig = collections.namedtuple(
    'SConfig',
    [
        'width',
        'height',
        'to_refresh',
        'to_compact'
    ]
)


CacheData = collections.namedtuple(
    'CacheData',
    [
        'cache_file',
        'size',
        'width',
        'height',
        'mtime'
    ]
)


FileData = collections.namedtuple(
    'FileData',
    [
        'file_name',
        'cache_file_name'
    ]
)


class ImageWindow(QWidget):
    """Creates a window showing an image at a size that fits the screen."""

    def __init__(self, iw_cfg):
        """
        Parameters
        ----------
        iw_cfg : IWConfig
            All configuration data needed to display a selected image
        """

        super().__init__()

        logging.debug(f"    Enter __init__ for {self}")
        image_file = iw_cfg.file
        owner = iw_cfg.owner
        max_width = iw_cfg.width
        max_height = iw_cfg.height
        size = iw_cfg.size

        image_name = image_file[image_file.rfind('/') + 1:]
        pixmap = QPixmap(image_file)
        image_width = pixmap.width()
        image_height = pixmap.height()
        width = image_width
        height = image_height
        if width > max_width:
            width = max_width
            height *= (max_width / image_width)
        if height > max_height:
            previous_height = height
            height = max_height
            width *= (height / previous_height)
        width = int(width)
        height = int(height)

        self.setWindowFlags(
            Qt.WindowTitleHint
            | Qt.WindowCloseButtonHint
            | Qt.WindowMinimizeButtonHint
        )
        self.setWindowTitle(
            f"{image_name} [{image_width}x{image_height}] ({size:,} bytes)"
        )
        self.setGeometry(
            settings.IMAGE_TOP_LEFT_X,
            settings.IMAGE_TOP_LEFT_Y,
            width,
            height
        )
        self.setFixedSize(self.size())
        self._label = QLabel(self)
        self._pixmap = pixmap
        self._label.setPixmap(
            self._pixmap.scaled(
                width,
                height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        self._label.setMinimumSize(MINIMUM_LABEL_SIZE_X, MINIMUM_LABEL_SIZE_Y)
        self.setAttribute(Qt.WA_DeleteOnClose)

        owner.add_image_window(self)
        self._owner = owner

        logging.debug(
            f"      {self} created for '{image_file}' [{image_width}x"
            f"{image_height}] with dimensions {width}x{height} in active "
        )
        logging.debug(f"    Leave __init__ for {self}")

    def resizeEvent(self, event):
        """Handles a resize request."""

        width = self.width()
        height = self.height()
        self._label.setPixmap(
            self._pixmap.scaled(
                width,
                height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        self._label.resize(width, height)

    def closeEvent(self, event):
        """Handles a close request."""

        logging.debug(f"    Enter closeEvent for {self}")
        self._owner.remove_image_window(self)
        logging.debug(f"      Removed {self} from set of active image windows")
        logging.debug(f"    Leave closeEvent for {self}")


class Selector(QMainWindow):
    """A resizeable icon view window for image files in directories."""

    def __init__(self, cfg):
        """
        Parameters
        ----------
        cfg : SConfig
            Configuration data to set up the main window
        """

        super().__init__()

        logging.debug(f"  Enter __init__ for {self}")
        cfg_width = cfg.width
        cfg_height = cfg.height
        width = int(
            cfg_width
            * settings.SELECTOR_WIDTH_FACTOR
        )
        height = int(
            cfg_height
            * settings.SELECTOR_HEIGHT_FACTOR
        )
        self._img_max_width = (
            cfg_width * settings.IMAGE_WIDTH_FACTOR
        )
        self._img_max_height = (
            cfg_height * settings.IMAGE_HEIGHT_FACTOR
        )
        self.setWindowTitle(settings.SELECTOR_TITLE)
        self.setGeometry(
            settings.SELECTOR_TOP_LEFT_X,
            settings.SELECTOR_TOP_LEFT_Y,
            width,
            height
        )
        self.setStyleSheet(settings.WINDOW_STYLE)
        self.statusBar().showMessage('')
        self._image_window_refs = set()
        self._cache_changed = False
        self._cache_data = {}
        self._refresh_needed = cfg.to_refresh
        self._compact_needed = cfg.to_compact

        logging.debug(f"  Leave __init__ for {self}")

    def create_view(self, files, cache):
        """
        Creates the view of image files that can be selected.

        Parameters
        ----------
        files : list
            List of full names and paths of image files to show
        cache : str
            Full path of a cache directory
        """

        logging.debug(f"  Enter create_view for {self}")

        cache_db_file = settings.CACHE_DATABASE
        cached_information = {}
        delete_set = set()
        if Path(cache_db_file).is_file():
            with open(cache_db_file, 'r', encoding='utf-8') as f:
                for line in f:
                    (
                        filename,
                        cached_file,
                        size,
                        width,
                        height,
                        mtime
                    ) = line.strip().split('|')
                    cached_information[filename] = CacheData(
                        cached_file,
                        int(size),
                        int(width),
                        int(height),
                        float(mtime)
                    )
                    delete_set.add(FileData(filename, cached_file))

        files_list = []
        cache_misses = []
        newer_files_dict = {}
        for name in files:
            code = hashlib.sha3_224()
            code.update(bytes(name, 'utf-8', 'ignore'))
            cache_entry = (
                f"{cache}{code.hexdigest()}"
                f"{settings.CACHE_FILE_EXTENSION}"
            )
            file_info = FileData(name, cache_entry)
            files_list.append(file_info)
            file_stat = Path(name).stat()
            mtime = file_stat.st_mtime
            if not Path(cache_entry).is_file():
                cache_misses.append(file_info)
                size = file_stat.st_size
                with Image.open(name) as image:
                    width, height = image.size
                    cached_information[name] = CacheData(
                        cache_entry,
                        size,
                        width,
                        height,
                        mtime
                    )
            else:
                delete_set.remove(file_info)
                current_cache_data = cached_information[name]
                if mtime > current_cache_data.mtime:
                    newer_files_dict[name] = CacheData(
                        cache_entry,
                        current_cache_data.size,
                        current_cache_data.width,
                        current_cache_data.height,
                        mtime
                    )

        if self._refresh_needed:
            logging.debug(f"    Newer files found = {len(newer_files_dict)}")
            if newer_files_dict:
                for k, v in newer_files_dict.items():
                    cached_information[k] = v
                    logging.debug(
                        f"      Cache data changed for '{k}' to: {v}"
                    )
                    cache_misses.append(file_info)
                self._cache_changed = True

        if self._compact_needed:
            logging.debug(f"    Cache files to remove = {len(delete_set)}")
            if delete_set:
                for entry in delete_set:
                    del(cached_information[entry.file_name])
                    logging.debug(
                        '      Deleted cache data entry for file '
                        f"'{entry.file_name}'"
                    )
                    Path(entry.cache_file_name).unlink()
                    logging.debug(
                        f"      Deleted cache file '{entry.cache_file_name}'"
                    )
                self._cache_changed = True

        logging.debug(f"    Cache misses in {cache} = {len(cache_misses)}")
        if cache_misses:
            slice_start = 0
            slice_end = 0
            tasks_left = len(cache_misses)

            cache_dlg = QProgressDialog(self)
            cache_dlg.setMinimum(0)
            cache_dlg.setMaximum(tasks_left)
            current_value = 0
            cache_dlg.setValue(current_value)
            cache_dlg.setFixedSize(
                settings.PROGRESS_DIALOG_WIDTH,
                settings.PROGRESS_DIALOG_HEIGHT
            )
            cache_dlg.setCancelButton(None)
            cache_dlg.setWindowModality(Qt.WindowModal)
            cache_dlg.setWindowTitle('Building cache ...')
            time.sleep(settings.GUI_TIMEOUT)

            cpus = os.cpu_count()
            while tasks_left > 0:
                workers = min(cpus, tasks_left)
                slice_end = slice_start + workers
                with futures.ThreadPoolExecutor(workers) as executor:
                    result = executor.map(
                        make_cache_file, cache_misses[slice_start:slice_end:])
                _ = list(result)
                slice_start = slice_end
                tasks_left -= workers
                current_value += workers
                cache_dlg.setValue(current_value)

            self._cache_changed = True

        files_dlg = QProgressDialog(self)
        files_dlg.setMinimum(0)
        files_dlg.setMaximum(len(files))
        current_file_count = 0
        files_dlg.setValue(current_file_count)
        files_dlg.setFixedSize(
            settings.PROGRESS_DIALOG_WIDTH,
            settings.PROGRESS_DIALOG_HEIGHT
        )
        files_dlg.setCancelButton(None)
        files_dlg.setWindowModality(Qt.WindowModal)
        files_dlg.setWindowTitle('Loading files ...')
        time.sleep(settings.GUI_TIMEOUT)

        self._listwidget = QListWidget()
        self._listwidget.setIconSize(
            QSize(
                settings.ICON_WIDTH,
                settings.ICON_HEIGHT
            )
        )
        self._listwidget.setStyleSheet(settings.SELECTOR_STYLE)
        file_name_iter = count(1)
        file_dict = {}
        for entry in files_list:
            real_image = entry.file_name
            thumbnail_image = entry.cache_file_name
            key = f"{next(file_name_iter)}"
            item = QListWidgetItem(QIcon(thumbnail_image), key)
            file_info = cached_information[real_image]
            size = file_info.size
            width = file_info.width
            height = file_info.height
            item.setStatusTip(
                f"{real_image} [{width}x{height}] ({size:,} bytes)"
            )
            self._listwidget.addItem(item)
            file_dict[key] = real_image

            current_file_count += 1
            files_dlg.setValue(current_file_count)

        self._file_dict = file_dict
        self._listwidget.clicked.connect(self.clicked)
        self._listwidget.setResizeMode(QListView.Adjust)
        self._listwidget.setViewMode(QListView.IconMode)
        self._listwidget.setMouseTracking(True)
        self.setCentralWidget(self._listwidget)
        logging.debug(f"    Icons set up in QListWidget = {len(file_dict)}")

        self._cache_data = cached_information

        logging.debug(f"  Leave create_view for {self}")

    def add_image_window(self, image_window_ref):
        """Adds an image window to the record of all active ones."""

        self._image_window_refs.add(image_window_ref)

    def remove_image_window(self, image_window_ref):
        """Removes an image window from the record of all active ones."""

        self._image_window_refs.remove(image_window_ref)

    def clicked(self, qmodelindex):
        """Handles selection of an item."""

        logging.debug(f"  Enter clicked for {self}")
        item = self._listwidget.currentItem()
        logging.debug(f"    Processing selected item '{item.text()}'")
        name = self._file_dict[item.text()]
        iw_cfg = IWConfig(
            name,
            self,
            self._img_max_width,
            self._img_max_height,
            self._cache_data[name].size
        )
        picture_window = ImageWindow(iw_cfg)
        picture_window.show()
        logging.debug(f"  Leave clicked for {self}")

    def closeEvent(self, event):
        """Handles a close event, closing active image windows too."""

        logging.debug(f"  Enter closeEvent for {self}")
        active_refs = list(self._image_window_refs)
        logging.debug(f"    Active windows to close = {active_refs}")
        for w in active_refs:
            logging.debug(f"    Sending close event to {w}")
            w.close()

        if self._cache_changed:
            cache_db_file = settings.CACHE_DATABASE
            with open(cache_db_file, 'w', encoding='utf-8') as f:
                for k, v in self._cache_data.items():
                    print(
                        k,
                        v.cache_file,
                        v.size,
                        v.width,
                        v.height,
                        v.mtime,
                        file=f,
                        sep='|'
                    )
            logging.debug(f"    Updated cache file '{cache_db_file}'")

        logging.debug(f"  Leave closeEvent for {self}")
        logging.info('ImageSelector.py - End')


###############################################################################
# FUNCTIONS
###############################################################################

def init():
    """Sets up the logging system."""

    log_level = logging.NOTSET
    log_config_level = settings.LOGGING
    if log_config_level == 'debug':
        log_level = logging.DEBUG
    if log_config_level == 'info':
        log_level = logging.INFO
    if log_config_level == 'warning':
        log_level = logging.WARNING
    if log_config_level == 'error':
        log_level = logging.ERROR
    if log_config_level == 'critical':
        log_level = logging.CRITICAL

    logging.basicConfig(
        format=(
            '%(asctime)s '
            '%(levelname)-8s '
            '[%(process)06d] '
            '<%(thread)08X> '
            '(%(lineno)06d): '
            '%(message)s'
        ),
        datefmt='%H:%M:%S',
        level=log_level
    )


def make_cache_file(file_info):
    """
    Creates an icon using a FileData object.

    Parameters
    ----------
    file_info : FileData
        The file name and the cache file name to make from it
    """

    QIcon(file_info.file_name).pixmap(
        settings.ICON_WIDTH,
        settings.ICON_HEIGHT
    ).save(
        file_info.cache_file_name,
        None,
        settings.CACHE_IMAGE_QUALITY
    )

    return True


def main():
    """The application driver function."""

    init()
    logging.info('ImageSelector.py - Start')

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

    cache_directory = args.cache_directory
    if not cache_directory.endswith('/'):
        cache_directory += '/'
    directory = args.directory
    if not directory.endswith('/'):
        directory += '/'
    image_type = args.image_type
    do_refresh = args.do_refresh
    do_compact_cache = args.do_compact_cache
    logging.debug(f"  Cache directory = {cache_directory}")
    logging.debug(f"  Image directory root = {directory}")
    logging.debug(f"  Type = {image_type}")
    logging.debug(f"  Refresh? = {do_refresh}")
    logging.debug(f"  Compact cache? = {do_compact_cache}")

    file_list = [
        Path(file).as_posix() for file in glob.iglob(
            directory + IMAGES_GLOB_PREFIX + image_type,
            recursive=True
        ) if cache_directory not in directory
    ]

    if file_list:
        logging.debug(f"  Image files found = {file_list}")
        app = QApplication(sys.argv)
        screen_size = app.primaryScreen().size()
        selector_cfg = SConfig(
            screen_size.width(),
            screen_size.height(),
            do_refresh,
            do_compact_cache
        )
        selector = Selector(selector_cfg)
        selector.show()
        time.sleep(settings.GUI_TIMEOUT)
        selector.create_view(file_list, cache_directory)
        logging.debug(
            f"  Created Selector for screen size = {screen_size.width()}"
            f"x{screen_size.height()}"
        )

        logging.debug('  Transferring control to QMainWindow')
        sys.exit(app.exec_())
    else:
        logging.warning('  No image files found !')
        logging.info('ImageSelector.py - End')


###############################################################################
# DRIVER
###############################################################################

if __name__ == '__main__':
    main()


###############################################################################
# END
###############################################################################
