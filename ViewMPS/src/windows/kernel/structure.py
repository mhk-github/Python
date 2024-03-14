#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : Structure.py
# SYNOPSIS : A PyQt5 MPS kernel viewer.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QImage,
    QPixmap,
    qRgb,
)
from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
)
from pathlib import PurePath
from typing import TypeVar

import settings


###############################################################################
# TYPING
###############################################################################

QEvent = TypeVar('QEvent')
MPSMainWindow = TypeVar('MPSMainWindow')


###############################################################################
# CONSTANTS
###############################################################################

BLACK = qRgb(0, 0, 0)
WHITE = qRgb(255, 255, 255)


###############################################################################
# CLASSES
###############################################################################

class MPSStructureWindow(QWidget):
    """Shows the kernel of MPS files as bitmaps."""

    def __init__(self, parent: MPSMainWindow, file_name: str) -> None:
        """
        Parameters
        ----------
        parent : MPSMainWindow
            The parent window for this child window
        file_name: str
            Canonical path of the MPS file
        """

        super().__init__()

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter MPSStructureWindow.__init__({parent=})")

        self.setWindowTitle(f"Structure - {PurePath(file_name).name}")
        self.setWindowFlags(
            Qt.WindowTitleHint
            | Qt.WindowCloseButtonHint
            | Qt.WindowMinimizeButtonHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose)

        width = len(parent.mps.columns)
        height = len(parent.mps.rows)
        width_factor = 1.0
        height_factor = 1.0
        if width > settings.MAX_CHILD_WINDOW_WIDTH:
            reduction_factor = settings.MAX_CHILD_WINDOW_WIDTH / width
            width_factor = reduction_factor
            height_factor = reduction_factor
            width = settings.MAX_CHILD_WINDOW_WIDTH
            height *= reduction_factor

        if height > settings.MAX_CHILD_WINDOW_HEIGHT:
            reduction_factor = settings.MAX_CHILD_WINDOW_HEIGHT / height
            width_factor *= reduction_factor
            height_factor *= reduction_factor
            width *= reduction_factor
            height = settings.MAX_CHILD_WINDOW_HEIGHT

        width = int(width) + 1
        height = int(height) + 1

        self.setGeometry(
            settings.CHILD_WINDOW_TOP_LEFT_X,
            settings.CHILD_WINDOW_TOP_LEFT_Y,
            width,
            height
        )
        self.setFixedSize(width, height)

        label = QLabel(self)
        image = QImage(width, height, QImage.Format_RGB32)
        image.fill(BLACK)
        for e in parent.mps.elements.keys():
            x = int(e.column_id * width_factor)
            y = int(e.row_id * height_factor)
            image.setPixel(x, y, WHITE)
        label.setPixmap(QPixmap.fromImage(image))

        parent.add_child_ref(self)
        logger.debug(
            f"    Added child window reference {self} to parent {parent}"
        )
        self._parent = parent

        logger.debug('  Leave MPSStructureWindow.__init__(...)')

    def closeEvent(self, event: QEvent) -> None:
        """
        Handles a close request.

        Parameters
        ----------
        event : QEvent
            Specific event to close the child window
        """

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter MPSStructureWindow.closeEvent({event=})")
        self._parent.remove_child_ref(self)
        logger.debug(
            f"    Removed {self} from set of active image windows"
        )
        logger.debug('  Leave MPSStructureWindow.closeEvent()')


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
