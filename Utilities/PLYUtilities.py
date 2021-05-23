#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : PLYUtilities.py
# SYNOPSIS : A module for common data structures and tasks for PLY files.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import re


###############################################################################
# CONSTANTS
###############################################################################

PLY_HEADER_START_STRING = 'ply'
PLY_HEADER_END_STRING = 'end_header'
PLY_HEADER_ELEMENT_STRING = 'element'
PLY_HEADER_PROPERTY_STRING = 'property'
PLY_HEADER_FORMAT_STRING = 'format'
PLY_HEADER_COMMENT_STRING = 'comment'

PLY_BINARY_HEADER_END_DATA = list(
    bytes(f"{PLY_HEADER_END_STRING}\n", 'utf-8', 'strict')
)
PLY_SLIDING_WINDOW_SIZE = len(PLY_BINARY_HEADER_END_DATA)

PLY_HEADER_FORMAT_ASCII_RE = re.compile(r'^format\s+ascii\s+1\.0$')
PLY_HEADER_FORMAT_BINARY_BIG_ENDIAN_RE = re.compile(
    r'^format\s+binary_big_endian\s+1\.0$'
)
PLY_HEADER_FORMAT_BINARY_LITTLE_ENDIAN_RE = re.compile(
    r'^format\s+binary_little_endian\s+1\.0$'
)
PLY_HEADER_VERTEX_RE = re.compile(r'^element\s+vertex\s+(\d+)$')
PLY_HEADER_FACE_RE = re.compile(r'^element\s+face\s+(\d+)$')
PLY_HEADER_PROPERTY_LIST_RE = re.compile(
    r'^property\s+list\s+(\S+)\s+(\S+)\s+'
)
PLY_HEADER_VERTEX_X_FLOAT_RE = re.compile(r'^property\s+float\s+x$')
PLY_HEADER_VERTEX_Y_FLOAT_RE = re.compile(r'^property\s+float\s+y$')
PLY_HEADER_VERTEX_Z_FLOAT_RE = re.compile(r'^property\s+float\s+z$')
PLY_HEADER_VERTEX_X_DOUBLE_RE = re.compile(r'^property\s+double\s+x$')
PLY_HEADER_VERTEX_Y_DOUBLE_RE = re.compile(r'^property\s+double\s+y$')
PLY_HEADER_VERTEX_Z_DOUBLE_RE = re.compile(r'^property\s+double\s+z$')
PLY_VERTEX_RE = re.compile(r'^([0-9.eE-]+)\s+([0-9.eE-]+)\s+([0-9.eE-]+)\s*')
PLY_FACE_RE = re.compile(r'^(\d+)\s+(.*)$')


###############################################################################
# CLASSES
###############################################################################

class PLYHeader:
    """Represents header data in a PLY file."""

    def __init__(self, file):
        """
        Parameters
        ----------
        file : str
            Fully qualified name and path of a PLY data file
        """

        with open(file, 'rb') as binfile:
            sliding_window = list(binfile.read(PLY_SLIDING_WINDOW_SIZE))
            if len(sliding_window) != PLY_SLIDING_WINDOW_SIZE:
                msg = (
                    f"Read only {len(sliding_window)} bytes instead of "
                    f"{PLY_SLIDING_WINDOW_SIZE} bytes from file '{file}' to "
                    'initialize sliding window !'
                )
                raise Exception(msg)
            elif sliding_window == PLY_BINARY_HEADER_END_DATA:
                msg = f"Degenerate PLY file '{file}' due to no header start !"
                raise Exception(msg)
            file_data = sliding_window
            current_sliding_win_start_pos = 0
            while True:
                read_byte = binfile.read(1)
                if not read_byte:
                    msg = (
                        f"EOF reached in file '{file}' while looking for PLY "
                        'header data !'
                    )
                    raise Exception(msg)
                file_data.append(read_byte[0])
                current_sliding_win_start_pos += 1
                sliding_window = file_data[
                    current_sliding_win_start_pos:
                    current_sliding_win_start_pos + PLY_SLIDING_WINDOW_SIZE
                ]
                if sliding_window == PLY_BINARY_HEADER_END_DATA:
                    break

            header_string = ''
            try:
                header_string = bytes(file_data).decode('utf-8', 'strict')
            except Exception:
                msg = (
                    f"Failed to convert header bytes [{file_data}] into "
                    f"header string in file '{file}' !"
                )
                raise Exception(msg)

            active_element = None
            format_line = None
            elements = []
            for line in header_string.split('\n'):
                if line.startswith(PLY_HEADER_START_STRING):
                    next
                elif line.startswith(PLY_HEADER_FORMAT_STRING):
                    format_line = line
                elif line.startswith(PLY_HEADER_ELEMENT_STRING):
                    new_element = (line, [])
                    elements.append(new_element)
                    active_element = new_element
                elif line.startswith(PLY_HEADER_PROPERTY_STRING):
                    active_element[1].append(line)
                elif line.startswith(PLY_HEADER_COMMENT_STRING):
                    next
                elif line.startswith(PLY_HEADER_END_STRING):
                    break
                else:
                    msg = (
                        f"Unexpected line '{line}' in PLY header data in file "
                        f"'{file}' !"
                    )
                    raise Exception(msg)

            self._file_offset = len(file_data)
            self._format = format_line
            self._elements = elements

    def __repr__(self):
        return (
            f"<PLYHeader object: offset={self._file_offset}, "
            f"format='{self._format}', elements={self._elements}>"
        )

    @property
    def file_offset(self):
        return self._file_offset

    @property
    def format(self):
        return self._format

    @property
    def elements(self):
        return self._elements


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
