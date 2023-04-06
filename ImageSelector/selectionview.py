#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : selectionview.py
# SYNOPSIS : Presents thumbnails to select in a PyQt5 window.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import logging
import re
import time

from PyQt5.QtCore import (
    QSize,
    Qt
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QProgressDialog
)
from itertools import count
from typing import (
    List,
    TypeVar
)

import settings

from imageview import ImageWindow


###############################################################################
# TYPING
###############################################################################

ImageData = TypeVar('ImageData')
Image_Window = TypeVar('Image_Window')
QEvent = TypeVar('QEvent')
QModelIndex = TypeVar('QModelIndex')


###############################################################################
# CONSTANTS
###############################################################################

IMAGE_REGEX = re.compile(r'^(.*)\s+\[')


###############################################################################
# CLASSES
###############################################################################

class SelectionWindow(QMainWindow):
    """A resizeable icon view window for image files in directories."""

    def __init__(self) -> None:
        super().__init__()

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter SelectionWindow.__init__({self})")

        self.setWindowTitle(settings.SELECTOR_TITLE)
        screen_size = QApplication.primaryScreen().size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.setGeometry(
            settings.SELECTOR_TOP_LEFT_X,
            settings.SELECTOR_TOP_LEFT_Y,
            int(screen_width * settings.SELECTOR_WIDTH_FACTOR),
            int(screen_height * settings.SELECTOR_HEIGHT_FACTOR)
        )
        self.setStyleSheet(settings.WINDOW_STYLE)
        self.statusBar().showMessage('')
        self._image_window_refs = set()

        logger.debug(f"  Leave SelectionWindow.__init__({self})")

    def create_view(self, cache: List[ImageData]) -> None:
        """
        Creates the view of image files that can be selected.

        Parameters
        ----------
        cache : list
            ImageData objects for all images that can be viewed
        """

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter SelectionWindow.create_view({self}, {cache})")

        files_dlg = QProgressDialog(self)
        files_dlg.setMinimum(0)
        files_dlg.setMaximum(len(cache))
        current_file_count = 0
        files_dlg.setValue(current_file_count)
        files_dlg.setFixedSize(
            settings.PROGRESS_DIALOG_WIDTH,
            settings.PROGRESS_DIALOG_HEIGHT
        )
        files_dlg.setCancelButton(None)
        files_dlg.setWindowModality(Qt.WindowModal)
        files_dlg.setWindowTitle('Loading cache ...')
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
        for image_data in cache:
            item = QListWidgetItem(
                QIcon(image_data.cache_file),
                f"{next(file_name_iter)}"
            )
            size = image_data.size
            width = image_data.width
            height = image_data.height
            item.setStatusTip(
                f"{image_data.image_file} [{width}x{height}] ({size:,} bytes)"
            )
            self._listwidget.addItem(item)
            current_file_count += 1
            files_dlg.setValue(current_file_count)

        self._listwidget.clicked.connect(self.clicked)
        self._listwidget.setResizeMode(QListView.Adjust)
        self._listwidget.setViewMode(QListView.IconMode)
        self._listwidget.setMouseTracking(True)
        self.setCentralWidget(self._listwidget)
        logger.debug(f"    Icons set up in QListWidget = {len(cache)}")

        logger.debug(f"  Leave SelectionWindow.create_view({self}, ...)")

    def add_image_window(self, image_window_ref: Image_Window) -> None:
        """
        Adds an image window to the record of all active ones.

        Parameters
        ----------
        image_window_ref : ImageWindow
            ImageWindow object to add to the internal set of references
        """

        self._image_window_refs.add(image_window_ref)

    def remove_image_window(self, image_window_ref: Image_Window) -> None:
        """
        Removes an image window from the record of all active ones.

        Parameters
        ----------
        image_window_ref : ImageWindow
            ImageWindow object to remove from the internal set of references.
        """

        self._image_window_refs.remove(image_window_ref)

    def clicked(self, qmodelindex: QModelIndex) -> None:
        """
        Handles selection of an item.

        Parameters
        ----------
        qmodelindex : QModelIndex
            The item clicked
        """

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter SelectionWindow.clicked({self}, {qmodelindex})")
        item = self._listwidget.currentItem()
        status_text = item.statusTip()
        logger.debug(
            f"    Processing selected item '{item.text()}' possessing status "
            f"tip '{status_text}'"
        )
        match = IMAGE_REGEX.match(status_text)
        image = match.group(1)
        picture_window = ImageWindow(
            image,
            status_text[status_text.rfind('/') + 1:],
            self
        )
        picture_window.show()
        logger.debug(f"  Leave SelectionWindow.clicked({self}, ...)")

    def closeEvent(self, event: QEvent) -> None:
        """
        Handles a close event, closing active image windows too.

        Parameters
        ----------
        event : QEvent
            A specific event to close all windows
        """

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter SelectionWindow.closeEvent({self}, {event})")
        active_refs = list(self._image_window_refs)
        logger.debug(f"    Active windows to close = {active_refs}")
        for w in active_refs:
            logger.debug(f"    Sending close event to {w}")
            w.close()

        logger.debug(f"  Leave SelectionWindow.closeEvent({self}, ...)")


###############################################################################
# FUNCTIONS
###############################################################################

def main() -> None:
    """A driver for testing purposes only."""

    import sys
    from PyQt5.QtWidgets import QApplication

    from cache import ImageFileCache

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
        level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)
    logger.info('selectionview.py - Start')

    c = ImageFileCache(
        'C:/Learning/Programming/Python/ImageSelector/test/DB/database.txt',
        'C:/Learning/Programming/Python/ImageSelector/test/cache/',
        'C:/Learning/Programming/Python/ImageSelector/test/images/',
        'jpg'
    )
    app = QApplication(sys.argv)
    window = SelectionWindow()
    window.show()
    time.sleep(settings.GUI_TIMEOUT)
    window.create_view(c.data)
    logger.info('selectionview.py - End -- Control moving to PyQt5')
    sys.exit(app.exec_())


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
