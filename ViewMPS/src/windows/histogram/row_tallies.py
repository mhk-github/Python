#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : RowTalliesHistogram.py
# SYNOPSIS : A PyQt5 window to show non-zero element tallies for MPS rows.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import numpy as np

import collections
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

class RowTalliesHistWindow(QWidget):
    """Shows the histogram of row tallies of non-zero elements."""

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
            f"  Enter RowTalliesHistWindow.__init__({parent=}, "
            f"{file_name=})"
        )

        row_tallies = collections.Counter(
            k.row_id for k in parent.mps.elements.keys()
        )
        hist, bins = np.histogram(tuple(row_tallies.values()))

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
            f"Histogram [Row Tallies] - {PurePath(file_name).name}"
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
        self._parent = parent

        logger.debug('  Leave RowTalliesHistWindow.__init__(...)')

    def closeEvent(self, event: QEvent) -> None:
        """
        Handles a close request.

        Parameters
        ----------
        event : QEvent
            Specific event to close the child window
        """

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter RowTalliesHistWindow.closeEvent({event=})")
        self._parent.remove_child_ref(self)
        logger.debug(
            f"    Removed {self} from set of active image windows"
        )
        logger.debug('  Leave RowTalliesHistWindow.closeEvent()')


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
