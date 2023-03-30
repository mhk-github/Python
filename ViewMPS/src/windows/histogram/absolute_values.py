#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : AbsoluteValuesHistogram.py
# SYNOPSIS : A PyQt5 histogram viewer for absolute MPS element values.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import numpy as np

import logging
import pyqtgraph

from PyQt5.QtWidgets import (
    QVBoxLayout,
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
# CLASSES
###############################################################################

class AbsoluteValuesHistogramWindow(QWidget):
    """Shows the histogram of absolute element values."""

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
        logger.debug(
            f"  Enter AbsoluteValuesHistogramWindow.__init__({parent=}, "
            f"{file_name=})"
        )

        hist, bins = np.histogram(np.abs(tuple(parent.cmps.elements.values())))
        pw = pyqtgraph.PlotWidget(self)
        bg = pyqtgraph.BarGraphItem(
            x=bins[:-1],
            width=0.8,
            height=hist,
            brush='g'
        )
        pw.showGrid(y=True)
        pw.addItem(bg)

        layout = QVBoxLayout()
        layout.addWidget(pw)
        self.setLayout(layout)
        self.setWindowTitle(
            f"Histogram [Absolute Element Values] - {PurePath(file_name).name}"
        )
        self.setGeometry(
            settings.CHILD_WINDOW_TOP_LEFT_X,
            settings.CHILD_WINDOW_TOP_LEFT_Y,
            settings.HISTOGRAM_WIDTH,
            settings.HISTOGRAM_HEIGHT
        )

        parent.add_child_ref(self)
        logger.debug(
            f"    Added child window reference {self} to parent {parent}"
        )
        self.parent = parent

        logger.debug('  Leave AbsoluteValuesHistogramWindow.__init__(...)')

    def closeEvent(self, event: QEvent) -> None:
        """
        Handles a close request.

        Parameters
        ----------
        event : QEvent
            Specific event to close the child window
        """

        logger = logging.getLogger(__name__)
        logger.debug(
            f"  Enter AbsoluteValuesHistogramWindow.closeEvent({event=})"
        )
        self.parent.remove_child_ref(self)
        logger.debug(
            f"    Removed {self} from set of active image windows"
        )
        logger.debug('  Leave AbsoluteValuesHistogramWindow.closeEvent()')


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
