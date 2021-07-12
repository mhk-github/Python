#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : imageview.py
# SYNOPSIS : A image file viewer in PyQt5.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QLabel,
    QWidget
)

from utilities import IWConfig
import settings


###############################################################################
# CONSTANTS
###############################################################################

MINIMUM_LABEL_SIZE_X = 1
MINIMUM_LABEL_SIZE_Y = 1


###############################################################################
# CLASSES
###############################################################################

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

        logger = logging.getLogger(__name__)
        logger.debug(f"    Enter __init__({self}, {iw_cfg})")
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

        logger.debug(
            f"      {self} created for '{image_file}' [{image_width}x"
            f"{image_height}] with dimensions {width}x{height}"
        )
        logger.debug(f"    Leave __init__({self}, ...)")

    def resizeEvent(self, event):
        """Handles a resize request."""

        logger = logging.getLogger(__name__)
        logger.debug(f"    Enter resizeEvent for {self} [{event}]")
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
        logger.debug(f"      Resized label in {self} to {width}x{height}")
        logger.debug(f"    Leave resizeEvent for {self}")

    def closeEvent(self, event):
        """Handles a close request."""

        logger = logging.getLogger(__name__)
        logger.debug(f"    Enter closeEvent for {self} [{event}]")
        self._owner.remove_image_window(self)
        logger.debug(f"      Removed {self} from set of active image windows")
        logger.debug(f"    Leave closeEvent for {self}")


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
