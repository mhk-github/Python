#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : ViewMPS.py
# SYNOPSIS : A Python 3 PyQt5 MPS file viewer.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import argparse
import logging
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QMessageBox,
    QPushButton,
    QWidget,
)
from pathlib import PurePath
from typing import TypeVar

from utilities.mps import CMPS
from windows.histogram.absolute_values import AbsoluteValuesHistogramWindow
from windows.histogram.column_tallies import ColumnTalliesHistWindow
from windows.histogram.row_tallies import RowTalliesHistWindow
from windows.kernel.structure import MPSStructureWindow

import settings


###############################################################################
# TYPING
###############################################################################

QEvent = TypeVar('QEvent')
Qwidget = TypeVar('Qwidget')


###############################################################################
# CLASSES
###############################################################################

class MPSMainWindow(QWidget):
    """The main window for this application."""

    def __init__(self) -> None:
        super().__init__()

        logger = logging.getLogger(__name__)
        logger.debug('  Enter MPSMainWindow.__init__()')

        file_button = QPushButton('File', self)
        file_button.clicked.connect(self.click_open_file)

        layout = QGridLayout()
        layout.addWidget(file_button, 0, 0, 1, 1)

        self.setLayout(layout)
        self.setWindowTitle(settings.MAIN_WINDOW_TITLE)
        self.setStyleSheet(settings.MAIN_WINDOW_STYLESHEET)
        self.setGeometry(
            settings.MAIN_WINDOW_TOP_LEFT_X,
            settings.MAIN_WINDOW_TOP_LEFT_Y,
            settings.MAIN_WINDOW_WIDTH,
            settings.MAIN_WINDOW_HEIGHT
        )

        self.child_window_refs = set()
        self.file_name = ''
        self.cmps = None
        self.layout = layout

        logger.debug('  Leave MPSMainWindow.__init__()')

    def click_open_file(self) -> None:
        """Shows the file open dialog allowing one MPS file to be selected."""

        logger = logging.getLogger(__name__)
        logger.debug('  Enter MPSMainWindow.click_open_file()')

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            'Open file',
            settings.GUI_START_DIRECTORY,
            'MPS files (*.mps);;SIF files (*.sif)'
        )
        if file_name:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            try:
                cmps = CMPS(file_name)
            except Exception as e:
                mb = QMessageBox()
                mb.setWindowTitle(f"Error - {PurePath(file_name).name}")
                mb.setText(f"{e}")
                mb.setIcon(QMessageBox.Critical)
                mb.setStandardButtons(QMessageBox.Ok)
                mb.exec_()
            else:
                if not self.cmps:
                    details_button = QPushButton('Details', self)
                    details_button.clicked.connect(self.click_details)

                    structure_button = QPushButton('Structure', self)
                    structure_button.clicked.connect(self.click_structure)

                    histogram_absolute_element_values_button = QPushButton(
                        'Histogram [Absolute values]',
                        self
                    )
                    histogram_absolute_element_values_button.clicked.connect(
                        self.click_histogram_absolute_element_values
                    )

                    histogram_row_tallies_button = QPushButton(
                        'Histogram [Row tallies]',
                        self
                    )
                    histogram_row_tallies_button.clicked.connect(
                        self.click_histogram_row_tallies
                    )

                    histogram_column_tallies_button = QPushButton(
                        'Histogram [Column tallies]',
                        self
                    )
                    histogram_column_tallies_button.clicked.connect(
                        self.click_histogram_column_tallies
                    )

                    self.layout.addWidget(details_button, 1, 0, 1, 1)
                    self.layout.addWidget(structure_button, 2, 0, 1, 1)
                    self.layout.addWidget(
                        histogram_absolute_element_values_button,
                        3,
                        0,
                        1,
                        1
                    )
                    self.layout.addWidget(
                        histogram_row_tallies_button,
                        4,
                        0,
                        1,
                        1
                    )
                    self.layout.addWidget(
                        histogram_column_tallies_button,
                        5,
                        0,
                        1,
                        1
                    )

                self.cmps = cmps
                self.file_name = file_name
                logger.debug(f"    Input file '{file_name}'")
                self.setWindowTitle(
                    f"{settings.MAIN_WINDOW_TITLE} - "
                    f"{PurePath(file_name).name}"
                )

            QApplication.restoreOverrideCursor()

        logger.debug('  Leave MPSMainWindow.click_open_file()')

    def click_details(self) -> None:
        """Shows the details for the MPS file."""

        logger = logging.getLogger(__name__)
        logger.debug('  Enter MPSMainWindow.click_details()')

        mb = QMessageBox()
        mb.setWindowTitle(f"Details - {PurePath(self.file_name).name}")
        mb.setText(
            f"Name : '{self.cmps.name}'\n\n"
            f"Rows     : {len(self.cmps.rows):9,d}\n"
            f"Columns  : {len(self.cmps.columns):9,d}\n"
            f"Elements : {len(self.cmps.elements):9,d}\n\n"
            f"RHS    ? {bool(self.cmps.rhs)}\n"
            f"Ranges ? {bool(self.cmps.ranges)}\n"
            f"Bounds ? {bool(self.cmps.bounds)}"
        )
        mb.setStandardButtons(QMessageBox.Ok)
        mb.exec_()

        logger.debug('  Leave MPSMainWindow.click_details()')

    def click_structure(self) -> None:
        """Shows the structure of the MPS file."""

        logger = logging.getLogger(__name__)
        logger.debug('  Enter MPSMainWindow.click_structure()')

        cw = MPSStructureWindow(self, self.file_name)
        cw.show()

        logger.debug('  Leave MPSMainWindow.click_structure()')

    def click_histogram_absolute_element_values(self) -> None:
        """Shows the histogram of absolute values of elements."""

        logger = logging.getLogger(__name__)
        logger.debug(
            '  Enter MPSMainWindow.click_histogram_absolute_element_values()'
        )

        hw = AbsoluteValuesHistogramWindow(self, self.file_name)
        hw.show()

        logger.debug(
            '  Leave MPSMainWindow.click_histogram_absolute_element_values()'
        )

    def click_histogram_row_tallies(self) -> None:
        """Shows the histogram of rows with x number of elements."""

        logger = logging.getLogger(__name__)
        logger.debug('  Enter MPSMainWindow.click_histogram_row_tallies()')

        hw = RowTalliesHistWindow(self, self.file_name)
        hw.show()

        logger.debug('  Leave MPSMainWindow.click_histogram_row_tallies()')

    def click_histogram_column_tallies(self) -> None:
        """Shows the histogram of columns with x number of elements."""

        logger = logging.getLogger(__name__)
        logger.debug('  Enter MPSMainWindow.click_histogram_column_tallies()')

        hw = ColumnTalliesHistWindow(self, self.file_name)
        hw.show()

        logger.debug('  Leave MPSMainWindow.click_histogram_column_tallies()')

    def closeEvent(self, event: QEvent) -> None:
        """
        Handles a close event, closing active child windows too.

        Parameters
        ----------
        event : QEvent
            A specific event to close the main window
        """

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter MPSMainWindow.closeEvent({event=})")
        active_refs = list(self.child_window_refs)
        logger.debug(f"    Child windows to close = {active_refs}")
        for w in active_refs:
            logger.debug(f"    Sending close event to {w}")
            w.close()

        logger.debug('  Leave MPSMainWindow.closeEvent(...)')

    def add_child_ref(self, child: Qwidget) -> None:
        """Adds a reference to a child window in the parent.

        Parameters
        ----------
        child : Qwidget
            The child window reference to add
        """
        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter MPSMainWindow.add_child_ref({child=})")

        self.child_window_refs.add(child)
        logger.debug(f"    Added child reference {child} to {self}")

        logger.debug('  Leave MPSMainWindow.add_child_ref(...)')

    def remove_child_ref(self, child: Qwidget) -> None:
        """Removes a reference to a child window in the parent.

        Parameters
        ----------
        child : Qwidget
            The child window reference to delete
        """

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter MPSMainWindow.remove_child_ref({child=})")

        self.child_window_refs.remove(child)
        logger.debug(f"    Removed child reference {child} from {self}")

        logger.debug('  Leave MPSMainWindow.remove_child_ref(...)')


###############################################################################
# FUNCTIONS
###############################################################################

def init() -> None:
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
            '[%(process)06d] '
            '<%(thread)08X> '
            '%(name)s '
            '%(levelname)-8s: '
            '%(message)s'
        ),
        level=log_level
    )


def main() -> None:
    """Driver for this script."""

    parser = argparse.ArgumentParser(
        description='Show information about MPS files'
    )
    args = parser.parse_args()

    init()
    logger = logging.getLogger(__name__)
    logger.info('ViewMPS.py - Start')
    logger.info(f"  Arguments = {args}")

    app = QApplication(sys.argv)
    app.setFont(QFontDatabase().font('Consolas', 'Regular', 10))

    main_window = MPSMainWindow()
    main_window.show()

    logger.info('ViewMPS.py - End -- Control moving to PyQt5')
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
