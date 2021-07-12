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
import time

from PyQt5.QtCore import (
    QSize,
    Qt
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QListView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QProgressDialog
)
from itertools import count

import settings

from imageview import ImageWindow
from utilities import (
    IWConfig,
    SConfig
)


###############################################################################
# CLASSES
###############################################################################

class SelectionWindow(QMainWindow):
    """A resizeable icon view window for image files in directories."""

    def __init__(self, cfg, cache):
        """
        Parameters
        ----------
        cfg : SConfig
            Configuration data to set up the main window
        cache : dict
            Information on every image file to show
        """

        super().__init__()

        logger = logging.getLogger(__name__)
        logger.debug(
            f"  Enter SelectionWindow.__init__({self}, {cfg}, {cache})"
        )
        cfg_width = cfg.width
        cfg_height = cfg.height
        width = int(cfg_width * settings.SELECTOR_WIDTH_FACTOR)
        height = int(cfg_height * settings.SELECTOR_HEIGHT_FACTOR)
        self._img_max_width = (cfg_width * settings.IMAGE_WIDTH_FACTOR)
        self._img_max_height = (cfg_height * settings.IMAGE_HEIGHT_FACTOR)
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
        self._cache_data = cache

        logger.debug(f"  Leave SelectionWindow.__init__({self}, ...)")

    def create_view(self):
        """Creates the view of image files that can be selected."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter SelectionWindow.create_view({self})")

        files_dlg = QProgressDialog(self)
        files_dlg.setMinimum(0)
        files_dlg.setMaximum(len(self._cache_data))
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
        file_dict = {}
        for k, v in self._cache_data.items():
            thumbnail_image = v.cache_file
            key = f"{next(file_name_iter)}"
            item = QListWidgetItem(QIcon(thumbnail_image), key)
            size = v.size
            width = v.width
            height = v.height
            item.setStatusTip(f"{k} [{width}x{height}] ({size:,} bytes)")
            self._listwidget.addItem(item)
            file_dict[key] = k

            current_file_count += 1
            files_dlg.setValue(current_file_count)

        self._file_dict = file_dict
        self._listwidget.clicked.connect(self.clicked)
        self._listwidget.setResizeMode(QListView.Adjust)
        self._listwidget.setViewMode(QListView.IconMode)
        self._listwidget.setMouseTracking(True)
        self.setCentralWidget(self._listwidget)
        logger.debug(f"    Icons set up in QListWidget = {len(file_dict)}")

        logger.debug(f"  Leave SelectionWindow.create_view({self})")

    def add_image_window(self, image_window_ref):
        """Adds an image window to the record of all active ones."""

        self._image_window_refs.add(image_window_ref)

    def remove_image_window(self, image_window_ref):
        """Removes an image window from the record of all active ones."""

        self._image_window_refs.remove(image_window_ref)

    def clicked(self, qmodelindex):
        """Handles selection of an item."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter SelectionWindow.clicked({self}, {qmodelindex})")
        item = self._listwidget.currentItem()
        logger.debug(f"    Processing selected item '{item.text()}'")
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
        logger.debug(f"  Leave SelectionWindow.clicked({self}, ...)")

    def closeEvent(self, event):
        """Handles a close event, closing active image windows too."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter SelectionWindow.closeEvent({self}, {event})")
        active_refs = list(self._image_window_refs)
        logger.debug(f"    Active windows to close = {active_refs}")
        for w in active_refs:
            logger.debug(f"    Sending close event to {w}")
            w.close()

        logger.debug(f"  Leave SelectionWindow.closeEvent({self}, ...)")


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
