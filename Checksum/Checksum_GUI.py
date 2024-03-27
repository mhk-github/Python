#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : Checksum_GUI.py
# SYNOPSIS : A PyQt5 GUI to verify a file matches its stated checksum.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import argparse
import hashlib
import logging
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QWidget,
)

import settings


###############################################################################
# CLASSES
###############################################################################

class Checksum_GUI(QWidget):
    """The main window for this application."""

    ###########################################################################
    # CLASS VARIABLES
    ###########################################################################

    _sha1 = hashlib.sha1()
    _sha224 = hashlib.sha224()
    _sha256 = hashlib.sha256()
    _sha384 = hashlib.sha384()
    _sha512 = hashlib.sha512()
    _sha3_224 = hashlib.sha3_224()
    _sha3_256 = hashlib.sha3_256()
    _sha3_384 = hashlib.sha3_384()
    _sha3_512 = hashlib.sha3_512()
    _md5 = hashlib.md5()

    ###########################################################################
    # CONSTRUCTOR
    ###########################################################################

    def __init__(self) -> None:
        super().__init__()

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.__init__({self})")

        paste_checksum_button = QPushButton('Paste', self)
        paste_checksum_button.clicked.connect(self.click_paste_checksum)

        stated_checksum_textbox = QLineEdit(self)

        checksum_function_group = QButtonGroup(self)
        sha1_button = QRadioButton('SHA1', self)
        sha1_button.clicked.connect(self.click_sha1)
        checksum_function_group.addButton(sha1_button)
        sha224_button = QRadioButton('SHA224', self)
        sha224_button.clicked.connect(self.click_sha224)
        checksum_function_group.addButton(sha224_button)
        sha256_button = QRadioButton('SHA256', self)
        sha256_button.clicked.connect(self.click_sha256)
        checksum_function_group.addButton(sha256_button)
        sha384_button = QRadioButton('SHA384', self)
        sha384_button.clicked.connect(self.click_sha384)
        checksum_function_group.addButton(sha384_button)
        sha512_button = QRadioButton('SHA512', self)
        sha512_button.clicked.connect(self.click_sha512)
        checksum_function_group.addButton(sha512_button)
        sha3_224_button = QRadioButton('SHA3_224', self)
        sha3_224_button.clicked.connect(self.click_sha3_224)
        checksum_function_group.addButton(sha3_224_button)
        sha3_256_button = QRadioButton('SHA3_256', self)
        sha3_256_button.clicked.connect(self.click_sha3_256)
        checksum_function_group.addButton(sha3_256_button)
        sha3_384_button = QRadioButton('SHA3_384', self)
        sha3_384_button.clicked.connect(self.click_sha3_384)
        checksum_function_group.addButton(sha3_384_button)
        sha3_512_button = QRadioButton('SHA3_512', self)
        sha3_512_button.clicked.connect(self.click_sha3_512)
        checksum_function_group.addButton(sha3_512_button)
        md5_button = QRadioButton('MD5', self)
        md5_button.clicked.connect(self.click_md5)
        checksum_function_group.addButton(md5_button)

        file_button = QPushButton('File ...', self)
        file_button.clicked.connect(self.click_open_file)

        checksum_button = QPushButton('Checksum', self)
        checksum_button.clicked.connect(self.click_checksum)

        match_label = QLabel(self)
        match_label.setStyleSheet(settings.GUI_DEFAULT_MATCH_STYLE)
        match_label.setAlignment(Qt.AlignCenter)
        match_label.resize(1, 1)

        layout = QGridLayout()
        layout.addWidget(paste_checksum_button, 0, 0, 1, 1)
        layout.addWidget(stated_checksum_textbox, 0, 1, 1, 9)
        layout.addWidget(sha1_button, 1, 0, 1, 1)
        layout.addWidget(sha224_button, 1, 1, 1, 1)
        layout.addWidget(sha256_button, 2, 1, 1, 1)
        layout.addWidget(sha384_button, 3, 1, 1, 1)
        layout.addWidget(sha512_button, 4, 1, 1, 1)
        layout.addWidget(sha3_224_button, 1, 2, 1, 1)
        layout.addWidget(sha3_256_button, 2, 2, 1, 1)
        layout.addWidget(sha3_384_button, 3, 2, 1, 1)
        layout.addWidget(sha3_512_button, 4, 2, 1, 1)
        layout.addWidget(md5_button, 1, 3, 1, 1)
        layout.addWidget(file_button, 5, 0, 1, 1)
        layout.addWidget(checksum_button, 5, 1, 1, 1)
        layout.addWidget(match_label, 6, 0, 1, 10)

        self.setLayout(layout)
        self.setWindowTitle(settings.GUI_WINDOW_TITLE)
        self.setGeometry(
            settings.GUI_TOP_LEFT_X,
            settings.GUI_TOP_LEFT_Y,
            settings.GUI_WIDTH,
            settings.GUI_HEIGHT
        )

        self._stated_checksum_textbox = stated_checksum_textbox
        self._match_label = match_label
        self._file_name = ''
        self._hash_function = Checksum_GUI._sha256
        sha256_button.setChecked(True)

        logger.debug(f"  Leave Checksum_GUI.__init__({self})")

    ###########################################################################
    # GUI HANDLERS
    ###########################################################################

    def click_paste_checksum(self) -> None:
        """Pastes text in the system clipboard into the application."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_paste_checksum({self})")

        self._stated_checksum_textbox.setText(QApplication.clipboard().text())

        logger.debug(f"  Leave Checksum_GUI.click_paste_checksum({self})")

    def click_open_file(self) -> None:
        """Shows the file open dialog allowing a file to be selected."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_open_file({self})")

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            'Open file',
            'c:\\',
            'All files (*)'
        )
        if file_name:
            self.setWindowTitle(f"{settings.GUI_WINDOW_TITLE} - '{file_name}'")
            self._file_name = file_name
            logger.debug(f"    Selected file '{file_name}'")

        logger.debug(f"  Leave Checksum_GUI.click_open_file({self})")

    def click_checksum(self) -> None:
        """Finds the checksum selected for the chosen file."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_checksum({self})")

        QApplication.setOverrideCursor(Qt.WaitCursor)
        checksum_function = self._hash_function.copy()
        try:
            with open(self._file_name, 'rb') as f:
                while True:
                    data = f.read(settings.READ_AMOUNT)
                    if not data:
                        break
                    checksum_function.update(data)
        except Exception:
            logger.error(f"    Could not process file '{self._file_name}' !")
        else:
            logger.debug(f"    Processed file '{self._file_name}'")
        found_checksum = checksum_function.hexdigest()
        logger.debug(f"    Found checksum = {found_checksum}")
        QApplication.restoreOverrideCursor()

        stated_checksum = self._stated_checksum_textbox.text()
        logger.debug(f"    Stated checksum = {stated_checksum}")
        label = self._match_label
        if stated_checksum == found_checksum:
            label.setText(f"Matched ({found_checksum})")
            label.setStyleSheet(settings.GUI_RIGHT_MATCH_STYLE)
        else:
            label.setText(f"Mismatch ({found_checksum})")
            label.setStyleSheet(settings.GUI_WRONG_MATCH_STYLE)

        logger.debug(f"  Leave Checksum_GUI.click_checksum({self})")

    def click_sha1(self) -> None:
        """Sets the hash function to SHA1."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_sha1({self})")

        self._hash_function = Checksum_GUI._sha1

        logger.debug(f"  Leave Checksum_GUI.click_sha1({self})")

    def click_sha224(self) -> None:
        """Sets the hash function to SHA224."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_sha224({self})")

        self._hash_function = Checksum_GUI._sha224

        logger.debug(f"  Leave Checksum_GUI.click_sha224({self})")

    def click_sha256(self) -> None:
        """Sets the hash function to SHA256."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_sha256({self})")

        self._hash_function = Checksum_GUI._sha256

        logger.debug(f"  Leave Checksum_GUI.click_sha256({self})")

    def click_sha384(self) -> None:
        """Sets the hash function to SHA384."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_sha384({self})")

        self._hash_function = Checksum_GUI._sha384

        logger.debug(f"  Leave Checksum_GUI.click_sha384({self})")

    def click_sha512(self) -> None:
        """Sets the hash function to SHA512."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_sha512({self})")

        self._hash_function = Checksum_GUI._sha512

        logger.debug(f"  Leave Checksum_GUI.click_sha512({self})")

    def click_sha3_224(self) -> None:
        """Sets the hash function to SHA3_224."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_sha3_224({self})")

        self._hash_function = Checksum_GUI._sha3_224

        logger.debug(f"  Leave Checksum_GUI.click_sha3_224({self})")

    def click_sha3_256(self) -> None:
        """Sets the hash function to SHA3_256."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_sha3_256({self})")

        self._hash_function = Checksum_GUI._sha3_256

        logger.debug(f"  Leave Checksum_GUI.click_sha3_256({self})")

    def click_sha3_384(self) -> None:
        """Sets the hash function to SHA3_384."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_sha3_384({self})")

        self._hash_function = Checksum_GUI._sha3_384

        logger.debug(f"  Leave Checksum_GUI.click_sha3_384({self})")

    def click_sha3_512(self) -> None:
        """Sets the hash function to SHA3_512."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_sha3_512({self})")

        self._hash_function = Checksum_GUI._sha3_512

        logger.debug(f"  Leave Checksum_GUI.click_sha3_512({self})")

    def click_md5(self) -> None:
        """Sets the hash function to MD5."""

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter Checksum_GUI.click_md5({self})")

        self._hash_function = Checksum_GUI._md5

        logger.debug(f"  Leave Checksum_GUI.click_md5({self})")


###############################################################################
# FUNCTIONS
###############################################################################

def init() -> None:
    """Sets up logging."""

    log_level = logging.NOTSET
    log_config_level = settings.GUI_LOGGING
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
    """The driver function for this script."""

    parser = argparse.ArgumentParser(
        description='PyQt5 GUI to verify a file matches its stated checksum'
    )
    args = parser.parse_args()

    init()
    logger = logging.getLogger(__name__)
    logger.info('Checksum_GUI.py - Start')
    logger.info(f"  Arguments = {args}")

    app = QApplication(sys.argv)
    app.setFont(QFontDatabase().font('Consolas', 'Regular', 10))

    main_window = Checksum_GUI()
    main_window.show()

    logger.info('Checksum_GUI.py - End -- Control moving to PyQt5')
    sys.exit(app.exec_())


###############################################################################
# DRIVER
###############################################################################

if __name__ == '__main__':
    main()


###############################################################################
# END
###############################################################################
# Local Variables:
# mode: python
# End:
