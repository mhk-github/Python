#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : ViewMPS.py
# SYNOPSIS : Show information about MPS files.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import argparse
import collections
import logging
import re
import reprlib
import traceback

from types import MappingProxyType


###############################################################################
# CONSTANTS
###############################################################################

MPS_NAME_RE = re.compile(r'^NAME\s+(.*)$')
MPS_ROWS_RE = re.compile(r'^\s+(\S)\s+(\S+)$')
MPS_COLUMNS_2_RE = re.compile(r'^\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$')
MPS_COLUMNS_1_RE = re.compile(r'^\s+(\S+)\s+(\S+)\s+(\S+)$')
MPS_RHS_2_RE = re.compile(r'^\s+(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$')
MPS_RHS_1_RE = re.compile(r'^\s+(\S*)\s+(\S+)\s+(\S+)$')
MPS_RANGES_2_RE = re.compile(r'^\s+(\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$')
MPS_RANGES_1_RE = re.compile(r'^\s+(\S*)\s+(\S+)\s+(\S+)$')
MPS_BOUNDS_RE = re.compile(r'^\s+(\S+)\s+(\S*)\s+(\S+)\s+(\S+)$')

MPS_ROW_TYPES = frozenset('NLGE')
MPS_BOUNDS_TYPES = frozenset({'LO', 'UP', 'FX', 'FR', 'MI', 'PL'})


###############################################################################
# CLASSES
###############################################################################

RowData = collections.namedtuple(
    'RowData',
    [
        'row_id',
        'row_type'
    ]
)


ElementData = collections.namedtuple(
    'ElementData',
    [
        'row_id',
        'column_id'
    ]
)


BoundData = collections.namedtuple(
    'BoundData',
    [
        'bound_type',
        'value'
    ]
)


class CMPS:
    """ Parses MPS files."""

    def __init__(self, filename):
        """
        Parameters
        ----------
        filename : str
            Full name and path of MPS file
        """

        problem_name = ""
        rows_dict = {}
        columns_dict = {}
        elements_dict = {}
        rhs_dict = {}
        ranges_dict = {}
        bounds_dict = {}

        with open(filename, 'r', encoding='utf-8') as f:
            line_ctr = 0
            while True:
                # Check for EOF using newlines
                line = f.readline()
                if not line:
                    error = f"File '{filename}' is not in MPS format !"
                    logging.exception(error)
                    raise Exception(error)

                # Strip out empty and comment lines
                line_ctr += 1
                line = line.rstrip()
                if not line or line.startswith('*'):
                    next

                if line.startswith('NAME'):
                    matched = MPS_NAME_RE.search(line)
                    if matched:
                        problem_name = matched.group(1)
                    else:
                        error = (
                            f"Cannot parse '{line}' in NAME at line "
                            f"{line_ctr} !"
                        )
                        logging.exception(error)
                        raise Exception(error)

                if line.startswith('ROWS'):
                    current_row_id = 0
                    while True:
                        line = f.readline()
                        if not line:
                            error = 'Unexpected EOF while processing ROWS !'
                            logging.exception(error)
                            raise Exception(error)
                        line_ctr += 1
                        line = line.rstrip()
                        if not line or line.startswith('*'):
                            next
                        elif line.startswith('COLUMNS'):
                            break
                        matched = MPS_ROWS_RE.search(line)
                        if matched:
                            row_type = matched.group(1)
                            if row_type not in MPS_ROW_TYPES:
                                error = (
                                    f"Unknown type '{row_type}' in ROWS at "
                                    f"line {line_ctr} !"
                                )
                                logging.exception(error)
                                raise Exception(error)
                            rows_dict[matched.group(2)] = RowData(
                                current_row_id,
                                row_type
                            )
                            current_row_id += 1
                        else:
                            error = (
                                f"Cannot parse '{line}' in ROWS at line "
                                f"{line_ctr} !"
                            )
                            logging.exception(error)
                            raise Exception(error)

                if line.startswith('COLUMNS'):
                    current_column_id = 0
                    while True:
                        line = f.readline()
                        if not line:
                            error = 'Unexpected EOF while processing COLUMNS !'
                            logging.exception(error)
                            raise Exception(error)
                        line_ctr += 1
                        line = line.rstrip()
                        if not line or line.startswith('*'):
                            next
                        elif line.startswith('RHS'):
                            break
                        matched = MPS_COLUMNS_2_RE.search(line)
                        if matched:
                            column_name = matched.group(1)
                            row_1_name = matched.group(2)
                            if row_1_name not in rows_dict:
                                error = (
                                    f" Unknown row '{row_1_name}' for column "
                                    f"'{column_name}' at line {line_ctr} !"
                                )
                                logging.exception(error)
                                raise Exception(error)
                            element_1_value = matched.group(3)
                            row_2_name = matched.group(4)
                            if row_2_name not in rows_dict:
                                error = (
                                    f" Unknown row '{row_2_name}' for column "
                                    f"'{column_name}' at line {line_ctr} !"
                                )
                                logging.exception(error)
                                raise Exception(error)
                            element_2_value = matched.group(5)
                            if column_name not in columns_dict:
                                columns_dict[column_name] = current_column_id
                                current_column_id += 1
                            column_id = columns_dict[column_name]
                            value = float(element_1_value)
                            if value != 0.0:
                                elements_dict[
                                    ElementData(
                                        rows_dict[row_1_name].row_id,
                                        column_id
                                    )
                                ] = value
                            else:
                                logging.warn(
                                    f"    Zero element in '{line}' at line "
                                    f"{line_ctr}"
                                )
                            value = float(element_2_value)
                            if value != 0.0:
                                elements_dict[
                                    ElementData(
                                        rows_dict[row_2_name].row_id,
                                        column_id
                                    )
                                ] = value
                            else:
                                logging.warn(
                                    f"    Zero element in '{line}' at line "
                                    f"{line_ctr}"
                                )
                        else:
                            matched = MPS_COLUMNS_1_RE.search(line)
                            if matched:
                                column_name = matched.group(1)
                                row_name = matched.group(2)
                                element_value = matched.group(3)
                                if column_name not in columns_dict:
                                    columns_dict[column_name] = (
                                        current_column_id
                                    )
                                    current_column_id += 1
                                if row_name not in rows_dict:
                                    error = (
                                        f" Unknown row '{row_name}' for "
                                        f"column '{column_name}' at line "
                                        f"{line_ctr} !"
                                    )
                                    logging.exception(error)
                                    raise Exception(error)
                                value = float(element_value)
                                if value != 0.0:
                                    elements_dict[
                                        ElementData(
                                            rows_dict[row_name].row_id,
                                            column_id
                                        )
                                    ] = value
                                else:
                                    logging.warn(
                                        f"    Zero element in '{line}' at "
                                        f"line {line_ctr}"
                                    )
                            else:
                                error = (
                                    f"Cannot parse '{line}' in COLUMNS at "
                                    f"line {line_ctr} !"
                                )
                                logging.exception(error)
                                raise Exception(error)

                if line.startswith('RHS'):
                    rhs_name = None
                    while True:
                        line = f.readline()
                        if not line:
                            error = 'Unexpected EOF while processing RHS !'
                            logging.exception(error)
                            raise Exception(error)
                        line_ctr += 1
                        line = line.rstrip()
                        if not line or line.startswith('*'):
                            next
                        elif (
                                line.startswith('RANGES')
                                or line.endswith('BOUNDS')
                                or line.endswith('ENDATA')
                        ):
                            break
                        matched = MPS_RHS_2_RE.search(line)
                        if matched:
                            if not rhs_name:
                                rhs_name = matched.group(1)
                            else:
                                if rhs_name != matched.group(1):
                                    break
                            row_1_name = matched.group(2)
                            if row_1_name not in rows_dict:
                                error = (
                                    f"Unknown row '{row_1_name}' in RHS at "
                                    f"line {line_ctr} !"
                                )
                                logging.exception(error)
                                raise Exception(error)
                            value_1 = matched.group(3)
                            row_2_name = matched.group(4)
                            if row_2_name not in rows_dict:
                                error = (
                                    f"Unknown row '{row_2_name}' in RHS at "
                                    f"line {line_ctr} !"
                                )
                                logging.exception(error)
                                raise Exception(error)
                            value_2 = matched.group(5)
                            rhs_dict[row_1_name] = float(value_1)
                            rhs_dict[row_2_name] = float(value_2)
                        else:
                            matched = MPS_RHS_1_RE.search(line)
                            if matched:
                                if not rhs_name:
                                    rhs_name = matched.group(1)
                                else:
                                    if rhs_name != matched.group(1):
                                        break
                                row_name = matched.group(2)
                                if row_name not in rows_dict:
                                    error = (
                                        f"Unknown row '{row_name}' in RHS at "
                                        f"line {line_ctr} !"
                                    )
                                    logging.exception(error)
                                    raise Exception(error)
                                value = matched.group(3)
                                rhs_dict[row_name] = float(value)
                            else:
                                error = (
                                    f"Cannot parse '{line}' in RHS at line "
                                    f"{line_ctr} !"
                                )
                                logging.exception(error)
                                raise Exception(error)

                if line.startswith('RANGES'):
                    ranges_name = None
                    while True:
                        line = f.readline()
                        if not line:
                            error = 'Unexpected EOF while processing RANGES !'
                            logging.exception(error)
                            raise Exception(error)
                        line_ctr += 1
                        line = line.rstrip()
                        if not line or line.startswith('*'):
                            next
                        elif (
                                line.endswith('BOUNDS')
                                or line.endswith('ENDATA')
                        ):
                            break
                        matched = MPS_RANGES_2_RE.search(line)
                        if matched:
                            if not ranges_name:
                                ranges_name = matched.group(1)
                            else:
                                if ranges_name != matched.group(1):
                                    break
                            row_1_name = matched.group(2)
                            if row_1_name not in rows_dict:
                                error = (
                                    f"Unknown row '{row_1_name}' in RANGES at"
                                    f"line {line_ctr} !"
                                )
                                logging.exception(error)
                                raise Exception(error)
                            value_1 = matched.group(3)
                            row_2_name = matched.group(4)
                            if row_2_name not in rows_dict:
                                error = (
                                    f"Unknown row '{row_2_name}' in RANGES at"
                                    f"line {line_ctr} !"
                                )
                                logging.exception(error)
                                raise Exception(error)
                            value_2 = matched.group(5)
                            ranges_dict[row_1_name] = float(value_1)
                            ranges_dict[row_2_name] = float(value_2)
                        else:
                            matched = MPS_RANGES_1_RE.search(line)
                            if matched:
                                if not ranges_name:
                                    ranges_name = matched.group(1)
                                else:
                                    if ranges_name != matched.group(1):
                                        break
                                row_name = matched.group(2)
                                if row_name not in rows_dict:
                                    error = (
                                        f"Unknown row '{row_name}' in RANGES "
                                        f"at line {line_ctr} !"
                                    )
                                    logging.exception(error)
                                    raise Exception(error)
                                value = matched.group(3)
                                ranges_dict[row_name] = float(value)
                            else:
                                error = (
                                    f"Cannot parse '{line}' in RANGES at line"
                                    f" {line_ctr} !"
                                )
                                logging.exception(error)
                                raise Exception(error)

                if line.startswith('BOUNDS'):
                    bounds_name = None
                    while True:
                        line = f.readline()
                        if not line:
                            error = 'Unexpected EOF while processing BOUNDS !'
                            logging.exception(error)
                            raise Exception(error)
                        line_ctr += 1
                        line = line.rstrip()
                        if not line or line.startswith('*'):
                            next
                        elif line.startswith('ENDATA'):
                            break
                        matched = MPS_BOUNDS_RE.search(line)
                        if matched:
                            bound_type = matched.group(1)
                            if bound_type not in MPS_BOUNDS_TYPES:
                                error = (
                                    f"Unknown bounds type '{bound_type}' at "
                                    f"line {line_ctr}"
                                )
                                logging.exception(error)
                                raise Exception(error)
                            if not bounds_name:
                                bounds_name = matched.group(2)
                            else:
                                if bounds_name != matched.group(2):
                                    break
                            column_name = matched.group(3)
                            if column_name not in columns_dict:
                                error = (
                                    f"Unknown column '{column_name}' in "
                                    f"BOUNDS at line {line_ctr} !"
                                )
                                logging.exception(error)
                                raise Exception(error)
                            value = matched.group(4)
                            bounds_dict.setdefault(column_name, [])
                            bounds_dict[column_name].append(
                                BoundData(
                                    bound_type,
                                    float(value)
                                )
                            )
                        else:
                            error = (
                                f"Cannot parse '{line}' in BOUNDS at line "
                                f"{line_ctr} !"
                            )
                            logging.exception(error)
                            raise Exception(error)

                if line.startswith('ENDATA'):
                    break

        self._name = problem_name
        self._rows = MappingProxyType(rows_dict)
        self._columns = MappingProxyType(columns_dict)
        self._elements = MappingProxyType(elements_dict)
        self._rhs = MappingProxyType(rhs_dict)
        self._ranges = MappingProxyType(ranges_dict)
        self._bounds = MappingProxyType(bounds_dict)

    @property
    def name(self):
        return self._name

    @property
    def rows(self):
        return self._rows

    @property
    def columns(self):
        return self._columns

    @property
    def elements(self):
        return self._elements

    @property
    def rhs(self):
        return self._rhs

    @property
    def ranges(self):
        return self._ranges

    @property
    def bounds(self):
        return self._bounds

    def __repr__(self):
        name = self._name
        rows = reprlib.repr(self._rows)
        cols = reprlib.repr(self._columns)
        els = reprlib.repr(self._elements)
        rhs = reprlib.repr(self._rhs)
        rng = reprlib.repr(self._ranges)
        bnd = reprlib.repr(self._bounds)
        return (
            f"<CMPS object: name={name}, rows={rows}, columns={cols}, "
            f"elements={els}, rhs={rhs}, ranges={rng}, bounds={bnd}>"
        )


###############################################################################
# FUNCTIONS
###############################################################################

def init() -> None:
    """Sets up the logging system."""

    log_level = logging.INFO
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s: %(message)s',
        datefmt='%H:%M:%S',
        level=log_level
    )


def main() -> None:
    """Driver for this script."""

    init()

    parser = argparse.ArgumentParser(
        description='Show information about MPS files'
    )
    parser.add_argument(
        '-f',
        '--file',
        metavar='FILE',
        help='MPS input file',
        required=True,
        dest='filename'
    )
    args = parser.parse_args()

    logging.info('Start - ViewMPS.py')

    in_file = args.filename
    logging.debug(f"  File = {in_file}")

    mps = None
    try:
        mps = CMPS(in_file)
    except Exception:
        traceback.print_exc()

    if mps:
        logging.info(f"  MPS problem name = {mps.name}")
        logging.debug(f"    MPS ROWS data = {mps.rows}")
        logging.info(f"    Rows = {len(mps.rows)}")
        logging.debug(f"    MPS COLUMNS data = {mps.columns}")
        logging.info(f"    Columns = {len(mps.columns)}")
        logging.debug(f"    MPS nonzero element data = {mps.elements}")
        logging.info(f"    Nonzero elements = {len(mps.elements)}")
        logging.debug(f"    MPS RHS data = {mps.rhs}")
        logging.info(
            '    Non-empty RHS section = '
            f"{'Yes' if mps.rhs else 'No'}"
        )
        logging.debug(f"    MPS RANGES data = {mps.ranges}")
        logging.info(
            '    Non-empty RANGES section = '
            f"{'Yes' if mps.ranges else 'No'}"
        )
        logging.debug(f"    MPS BOUNDS data = {mps.bounds}")
        logging.info(
            '    Non-empty BOUNDS section = '
            f"{'Yes' if mps.bounds else 'No'}"
        )
        logging.debug(f"    String representaton = '{mps}'")

    logging.info('End - ViewMPS.py')


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
