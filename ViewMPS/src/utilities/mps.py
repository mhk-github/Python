#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : mps.py
# SYNOPSIS : Processes MPS files.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import logging
import re
import reprlib

from dataclasses import dataclass
from types import MappingProxyType
from typing import (
    List,
    Dict,
    Tuple,
    TypeVar
)


###############################################################################
# CONSTANTS
###############################################################################

MPS_ROW_TYPES = frozenset('NLGE')
MPS_BOUNDS_TYPES = frozenset({'LO', 'UP', 'FX', 'FR', 'MI', 'PL'})

MPS_NAME_SECTION_RE = re.compile(r'^NAME\s+(\S.*)$')
MPS_ROWS_SECTION_RE = re.compile(r'^ROWS$')
MPS_COLUMNS_SECTION_RE = re.compile(r'^COLUMNS$')
MPS_RHS_SECTION_RE = re.compile(r'^RHS$')
MPS_RANGES_SECTION_RE = re.compile(r'^RANGES$')
MPS_BOUNDS_SECTION_RE = re.compile(r'^BOUNDS$')
MPS_ENDATA_SECTION_RE = re.compile(r'^ENDATA$')
MPS_ROWS_DATA_RE = re.compile(r'^(\S)\s+(\S+)$')
MPS_COLUMNS_2_DATA_RE = re.compile(
    r'^(\S+)\s+(\S+)\s+([0-9eE.+-]+)\s+(\S+)\s+([0-9eE.+-]+)$'
)
MPS_COLUMNS_1_DATA_RE = re.compile(r'^(\S+)\s+(\S+)\s+([0-9eE.+-]+)$')
MPS_RHS_2_DATA_RE = re.compile(
    r'^(\S+)\s+(\S+)\s+([0-9eE.+-]+)\s+(\S+)\s+([0-9eE.+-]+)$'
)
MPS_RHS_1_DATA_RE = re.compile(r'^(\S+)\s+(\S+)\s+([0-9eE.+-]+)$')
MPS_RHS_2_DATA_EXTRA_RE = re.compile(
    r'^(\S+)\s+([0-9eE.+-]+)\s+(\S+)\s+([0-9eE.+-]+)$'
)
MPS_RHS_1_DATA_EXTRA_RE = re.compile(r'^(\S+)\s+([0-9eE.+-]+)$')
MPS_RANGES_2_DATA_RE = re.compile(
    r'^(\S*)\s+(\S+)\s+([0-9eE.+-]+)\s+(\S+)\s+([0-9eE.+-]+)$'
)
MPS_RANGES_1_DATA_RE = re.compile(r'^(\S*)\s+(\S+)\s+([0-9eE.+-]+)$')
MPS_BOUNDS_DATA_RE = re.compile(r'^(\S+)\s+(\S*)\s+(\S+)\s+([0-9eE.+-]+)$')


###############################################################################
# TYPING
###############################################################################

BoundData = TypeVar('BoundData')
ElementData = TypeVar('ElementData')
MPSSectionsData = TypeVar('MPSSectionsData')
RowData = TypeVar('RowData')


###############################################################################
# CLASSES
###############################################################################

##############
# EXCEPTIONS #
##############

class MPSException(Exception):
    """The base class for all MPS exceptions."""

    pass


class NotMPSFileException(MPSException):
    """Thrown when a given file is not in MPS format."""

    pass


class NoNAMEException(MPSException):
    """Thrown when there is no NAME section in the file."""

    pass


class NoROWSException(MPSException):
    """Thrown when there is no ROWS section in the file."""

    pass


class UnknownROWSTypeException(MPSException):
    """Thrown when an unknown ROWS type is encountered."""

    pass


class BadROWSDataException(MPSException):
    """Thrown when a line in the ROWS section cannot be parsed."""

    pass


class UnknownRowException(MPSException):
    """Thrown when a unknown row is encountered."""

    pass


class NoCOLUMNSException(MPSException):
    """Thrown when there is no COLUMNS section in the file."""

    pass


class BadCOLUMNSDataException(MPSException):
    """Thrown when a line in the COLUMNS section cannot be parsed."""

    pass


class UnknownColumnException(MPSException):
    """Thrown when an unknown column is encountered."""

    pass


class NoRHSException(MPSException):
    """Thrown when there is no RHS section in the file."""

    pass


class BadRHSDataException(MPSException):
    """Thrown when a line in the RHS section cannot be parsed."""

    pass


class BadRANGESDataException(MPSException):
    """Thrown when a line in the RANGES section cannot be parsed."""

    pass


class UnknownBOUNDSTypeException(MPSException):
    """Thrown when an unknown BOUNDS type is encountered."""

    pass


class BadBOUNDSDataException(MPSException):
    """Thrown when a line in the BOUNDS section cannot be parsed."""

    pass


class NoENDATAException(MPSException):
    """Thrown when there is no ENDATA marker in the file."""

    pass


class NoROWSDataException(MPSException):
    """Thrown when the ROWS section is devoid of data."""

    pass


class NoCOLUMNSDataException(MPSException):
    """Thrown when the COLUMNS section is devoid of data."""

    pass


#######
# POD #
#######

@dataclass(frozen=True, eq=False)
class MPSSectionsData:
    """Represents MPS file data in memory."""

    __slots__ = [
        'name',
        'rows_data',
        'columns_data',
        'rhs_data',
        'ranges_data',
        'bounds_data'
    ]
    name: str
    rows_data: List[str]
    columns_data: List[str]
    rhs_data: List[str]
    ranges_data: List[str]
    bounds_data: List[str]


@dataclass(frozen=True, eq=False)
class RowData:
    """Represents a row."""

    __slots__ = [
        'row_id',
        'row_type',
    ]
    row_id: int
    row_type: str


@dataclass(frozen=True)
class ElementData:
    """Represents a key to access a non-zero element."""

    __slots__ = [
        'row_id',
        'column_id',
    ]
    row_id: int
    column_id: int


@dataclass(frozen=True, eq=False)
class BoundData:
    """Represents a bound."""

    __slots__ = [
        'bound_type',
        'value',
    ]
    bound_type: str
    value: float


############
# STANDARD #
############

class CMPS:
    """ Parses MPS files."""

    def __init__(self, file_name: str) -> None:
        """
        Parameters
        ----------
        file_name : str
            Canonical path of MPS file
        """

        logger = logging.getLogger(__name__)
        logger.debug(f"  Enter CMPS.__init__({file_name=})")

        problem_name = ''
        rows_dict = {}
        columns_dict = {}
        elements_dict = {}
        rhs_dict = {}
        ranges_dict = {}
        bounds_dict = {}

        mps_data = intake_mps_file(file_name)
        logger.debug(f"    Data = {mps_data}")
        problem_name = process_NAME(mps_data.name)
        logger.debug(f"    MPS problem name = '{problem_name}'")
        rows_dict = process_ROWS(mps_data.rows_data)
        logger.debug(f"    Rows = {rows_dict}")
        columns_dict, elements_dict = process_COLUMNS(
            mps_data.columns_data,
            rows_dict
        )
        logger.debug(f"    Columns = {columns_dict}")
        logger.debug(f"    Non-zero elements = {elements_dict}")
        if mps_data.rhs_data:
            rhs_dict = process_RHS(mps_data.rhs_data, rows_dict)
            logger.debug(f"    RHS = {rhs_dict}")

        if mps_data.ranges_data:
            ranges_dict = process_RANGES(mps_data.ranges_data, rows_dict)
            logger.debug(f"    Ranges {ranges_dict}")

        if mps_data.bounds_data:
            bounds_dict = process_BOUNDS(mps_data.bounds_data, columns_dict)
            logger.debug(f"    Bounds = {bounds_dict}")

        self._name = problem_name
        self._rows = MappingProxyType(rows_dict)
        self._columns = MappingProxyType(columns_dict)
        self._elements = MappingProxyType(elements_dict)
        self._rhs = MappingProxyType(rhs_dict)
        self._ranges = MappingProxyType(ranges_dict)
        self._bounds = MappingProxyType(bounds_dict)

        logger.debug('  Leave CMPS.__init__(...)')

    def __repr__(self) -> str:
        return (
            '<CMPS object: '
            f"name='{self._name}', "
            f"rows={reprlib.repr(self._rows)}, "
            f"columns={reprlib.repr(self._columns)}, "
            f"elements={reprlib.repr(self._elements)}, "
            f"rhs={reprlib.repr(self._rhs)}, "
            f"ranges={reprlib.repr(self._ranges)}, "
            f"bounds={reprlib.repr(self._bounds)}>"
        )

    @property
    def name(self) -> str:
        """Returns the MPS problem name."""

        return self._name

    @property
    def rows(self) -> MappingProxyType:
        """Returns the MPS rows."""

        return self._rows

    @property
    def columns(self) -> MappingProxyType:
        """Returns the MPS columns."""

        return self._columns

    @property
    def elements(self) -> MappingProxyType:
        """Returns the MPS non-zero elements."""

        return self._elements

    @property
    def rhs(self) -> MappingProxyType:
        """Returns the MPS right hand side."""

        return self._rhs

    @property
    def ranges(self) -> MappingProxyType:
        """Returns the MPS ranges."""

        return self._ranges

    @property
    def bounds(self) -> MappingProxyType:
        """Returns the MPS bounds."""

        return self._bounds


###############################################################################
# FUNCTIONS
###############################################################################

def intake_mps_file(file_name: str) -> MPSSectionsData:
    """Reads in MPS file and delineates its sections.

    Parameters
    ----------
    file_name : str
        Canonical path of MPS file

    Returns
    -------
    MPSSectionsData
        The MPS file contents and section indices
    """

    logger = logging.getLogger(__name__)
    logger.debug(f"    Enter intake_mps_file({file_name=})")

    name = ''
    rows_l = []
    columns_l = []
    rhs_l = []
    ranges_l = []
    bounds_l = []
    active_l = None
    has_rows = False
    has_columns = False
    has_rhs = False
    has_endata = False
    with open(file_name, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith('*') or line.startswith('&'):
                continue
            elif MPS_NAME_SECTION_RE.match(line):
                name = line
                continue
            elif MPS_ROWS_SECTION_RE.match(line):
                active_l = rows_l
                has_rows = True
                continue
            elif MPS_COLUMNS_SECTION_RE.match(line):
                active_l = columns_l
                has_columns = True
                continue
            elif MPS_RHS_SECTION_RE.match(line):
                active_l = rhs_l
                has_rhs = True
                continue
            elif MPS_RANGES_SECTION_RE.match(line):
                active_l = ranges_l
                continue
            elif MPS_BOUNDS_SECTION_RE.match(line):
                active_l = bounds_l
                continue
            elif MPS_ENDATA_SECTION_RE.match(line):
                has_endata = True
                break

            try:
                active_l.append(line)
            except Exception:
                error = f"NotMPSFileException: '{file_name}' not MPS file !"
                logger.exception(f"      {error}")
                raise NotMPSFileException(error)

    if not name:
        error = f"NoNAMEException: '{file_name}' has no NAME section !"
        logger.exception(f"      {error}")
        raise NoNAMEException(error)
    elif not has_rows:
        error = f"NoROWSException: '{file_name}' has no ROWS section !"
        logger.exception(f"      {error}")
        raise NoROWSException(error)
    elif not has_columns:
        error = f"NoCOLUMNSException: '{file_name}' has no COLUMNS section !"
        logger.exception(f"      {error}")
        raise NoCOLUMNSException(error)
    elif not has_rhs:
        error = f"NoRHSException: '{file_name}' has no RHS section !"
        logger.exception(f"      {error}")
        raise NoRHSException(error)
    elif not has_endata:
        error = f"NoENDATAException: '{file_name}' has no ENDATA marker !"
        logger.exception(f"      {error}")
        raise NoENDATAException(error)
    elif not rows_l:
        error = f"NoROWSDataException: '{file_name}' has no ROWS data !"
        logger.exception(f"      {error}")
        raise NoROWSDataException(error)
    elif not columns_l:
        error = f"NoCOLUMNSDataException: '{file_name}' has no COLUMNS data !"
        logger.exception(f"      {error}")
        raise NoCOLUMNSDataException(error)

    logger.debug('    Leave intake_mps_file(...)')
    return MPSSectionsData(
        name,
        rows_l,
        columns_l,
        rhs_l,
        ranges_l,
        bounds_l
    )


def process_NAME(data: str) -> str:
    """Returns the MPS problem name.

    Parameters
    ----------
    data : str
        NAME section line from MPS file

    Returns
    -------
    str
        MPS problem name
    """

    return MPS_NAME_SECTION_RE.match(data).group(1)


def process_ROWS(data: List[str]) -> Dict[str, RowData]:
    """Processes ROWS section of MPS file.

    Parameters
    ----------
    data : List[str]
        Lines of data frmo ROWS

    Returns
    -------
    Dict[str, RowData]
        A dictionary of rows data keyed on the row name
    """

    logger = logging.getLogger(__name__)
    logger.debug(f"    Enter process_ROWS({data=})")

    rows_info = {}
    current_row_id = 0
    for line in data:
        if (matched := MPS_ROWS_DATA_RE.match(line)):
            row_type = matched.group(1)
            if row_type not in MPS_ROW_TYPES:
                error = (
                    f"UnknownROWSTypeException: Unknown ROWS type '{row_type}'"
                    ' !'
                )
                logger.exception(f"      {error}")
                raise UnknownROWSTypeException(error)

            rows_info[matched.group(2)] = RowData(
                current_row_id,
                row_type
            )
            current_row_id += 1

        else:
            error = f"BadROWSDataException: Cannot parse '{line}' !"
            logger.exception(f"      {error}")
            raise BadROWSDataException(error)

    logger.debug('    Leave process_ROWS(...)')
    return rows_info


def process_COLUMNS(
    data: List[str],
    rows: Dict[str, RowData]
) -> Tuple[Dict[str, int], Dict[ElementData, float]]:
    """Processes COLUMNS section of MPS file.

    Parameters
    ----------
    data : List[str]
        Strings of data from COLUMNS section
    rows : Dict[str, RowData]
        All the rows information

    Returns
    -------
    Tuple[Dict[str, int], Dict[ElementData, float]]
        A dictionary of column data and a dictionary of non-zero element data
    """

    logger = logging.getLogger(__name__)
    logger.debug(f"    Enter process_COLUMNS({data=}, {rows=})")

    columns_dict = {}
    elements_dict = {}

    current_column_id = 0
    for line in data:
        if (matched := MPS_COLUMNS_2_DATA_RE.match(line)):
            column_name = matched.group(1)
            row_1_name = matched.group(2)
            if row_1_name not in rows:
                error = (
                    'UnknownRowException: Unknown first row '
                    f"'{row_1_name}' for column "
                    f"'{column_name}' in COLUMNS !"
                )
                logger.exception(f"      {error}")
                raise UnknownRowException(error)

            element_1_value = matched.group(3)

            row_2_name = matched.group(4)
            if row_2_name not in rows:
                error = (
                    'UnknownRowException: Unknown second row '
                    f"'{row_2_name}' for column "
                    f"'{column_name}' in COLUMNS !"
                )
                logger.exception(f"      {error}")
                raise UnknownRowException(error)

            element_2_value = matched.group(5)

            if column_name not in columns_dict:
                columns_dict[column_name] = current_column_id
                current_column_id += 1

            column_id = columns_dict[column_name]
            value = float(element_1_value)
            if value != 0.0:
                elements_dict[
                    ElementData(
                        rows[row_1_name].row_id,
                        column_id
                    )
                ] = value
            else:
                logger.warn(f"      Zero element in '{line}' in COLUMNS !")

            value = float(element_2_value)
            if value != 0.0:
                elements_dict[
                    ElementData(
                        rows[row_2_name].row_id,
                        column_id
                    )
                ] = value
            else:
                logger.warn(f"      Zero element in '{line}' in COLUMNS !")

        elif (matched := MPS_COLUMNS_1_DATA_RE.match(line)):
            column_name = matched.group(1)
            row_name = matched.group(2)
            element_value = matched.group(3)
            if column_name not in columns_dict:
                columns_dict[column_name] = current_column_id
                current_column_id += 1

            column_id = columns_dict[column_name]
            if row_name not in rows:
                error = (
                    'UnknownRowException: Unknown sole row'
                    f" '{row_name}' for column "
                    f"'{column_name}' in COLUMNS !"
                )
                logger.exception(f"      {error}")
                raise UnknownRowException(error)

            value = float(element_value)
            if value != 0.0:
                elements_dict[
                    ElementData(
                        rows[row_name].row_id,
                        column_id
                    )
                ] = value
            else:
                logger.warn(f"    Zero element in '{line}' in COLUMNS !")

        else:
            error = (
                f"BadCOLUMNSDataException: Cannot parse {line}' in COLUMNS !"
            )
            logger.exception(f"      {error}")
            raise BadCOLUMNSDataException(error)

    logger.debug('    Leave process_COLUMNS(...)')
    return (columns_dict, elements_dict)


def process_RHS(
    data: List[str],
    rows: Dict[str, RowData]
) -> Dict[str, float]:
    """Processes RHS section of MPS files.

    Parameters
    ----------
    data : List[str]
        Strings of data from RHS section
    rows : Dict[str, RowData]
        Information about all rows

    Return
    ------
    Dict[str, float]
        A dictionary of RHS data
    """

    logger = logging.getLogger(__name__)
    logger.debug(f"    Enter process_RHS({data=}, {rows=})")

    rhs_dict = {}
    rhs_name = ''
    for line in data:
        if (matched := MPS_RHS_2_DATA_RE.match(line)):
            if not rhs_name:
                rhs_name = matched.group(1)
            else:
                if rhs_name != matched.group(1):
                    break

            row_1_name = matched.group(2)
            if row_1_name not in rows:
                error = (
                    f"UnknownRowException: Unknown first row '{row_1_name}' "
                    'in RHS !'
                )
                logger.exception(f"      {error}")
                raise UnknownRowException(error)

            value_1 = matched.group(3)

            row_2_name = matched.group(4)
            if row_2_name not in rows:
                error = (
                    f"UnknownRowException: Unknown second row '{row_2_name}' "
                    'in RHS !'
                )
                logger.exception(f"      {error}")
                raise UnknownRowException(error)

            value_2 = matched.group(5)

            rhs_dict[row_1_name] = float(value_1)
            rhs_dict[row_2_name] = float(value_2)

        elif (matched := MPS_RHS_1_DATA_RE.match(line)):
            if not rhs_name:
                rhs_name = matched.group(1)
            else:
                if rhs_name != matched.group(1):
                    break

            row_name = matched.group(2)
            if row_name not in rows:
                error = (
                    f"UnknownRowException: Unknown sole row '{row_name}' "
                    'in RHS !'
                )
                logger.exception(f"      {error}")
                raise UnknownRowException(error)

            value = matched.group(3)

            rhs_dict[row_name] = float(value)

        elif (matched := MPS_RHS_2_DATA_EXTRA_RE.match(line)):
            row_1_name = matched.group(1)
            if row_1_name not in rows:
                error = (
                    f"UnknownRowException: Unknown first row '{row_1_name}' "
                    'in RHS !'
                )
                logger.exception(f"      {error}")
                raise UnknownRowException(error)

            value_1 = matched.group(2)

            row_2_name = matched.group(3)
            if row_2_name not in rows:
                error = (
                    f"UnknownRowException: Unknown second row '{row_2_name}' "
                    'in RHS !'
                )
                logger.exception(f"      {error}")
                raise UnknownRowException(error)

            value_2 = matched.group(4)

            rhs_dict[row_1_name] = float(value_1)
            rhs_dict[row_2_name] = float(value_2)

        elif (matched := MPS_RHS_1_DATA_EXTRA_RE.match(line)):
            row_name = matched.group(1)
            if row_name not in rows:
                error = (
                    f"UnknownRowException: Unknown sole row '{row_name}' "
                    'in RHS !'
                )
                logger.exception(f"      {error}")
                raise UnknownRowException(error)

            value = matched.group(2)

            rhs_dict[row_name] = float(value)

        else:
            error = f"BadRHSDataException: Cannot parse '{line}' in RHS !"
            logger.exception(f"      {error}")
            raise BadRHSDataException(error)

    logger.debug('    Leave process_RHS(...)')
    return rhs_dict


def process_RANGES(
    data: List[str],
    rows: Dict[str, RowData]
) -> Dict[str, float]:
    """Processes the RANGES section of MPS files.

    Parameters
    ----------
    data : List[str]
        Strings of data from the RANGES section
    rows : Dict[str, RowData]
        Information about all rows

    Returns
    -------
    Dict[str, float]
        A dictionary of ranges data
    """

    logger = logging.getLogger(__name__)
    logger.debug(f"    Enter process_RANGES({data=}, {rows=})")

    ranges_dict = {}
    ranges_name = ''
    for line in data:
        if (matched := MPS_RANGES_2_DATA_RE.match(line)):
            if not ranges_name:
                ranges_name = matched.group(1)
            else:
                if ranges_name != matched.group(1):
                    break

            row_1_name = matched.group(2)
            if row_1_name not in rows:
                error = (
                    f"UnknownRowException: Unknown first row '{row_1_name}' "
                    'in RANGES !'
                )
                logger.exception(f"      {error}")
                raise UnknownRowException(error)

            value_1 = matched.group(3)

            row_2_name = matched.group(4)
            if row_2_name not in rows:
                error = (
                    f"UnknownRowException: Unknown second row '{row_2_name}' "
                    'in RANGES !'
                )
                logger.exception(f"      {error}")
                raise UnknownRowException(error)

            value_2 = matched.group(5)

            ranges_dict[row_1_name] = float(value_1)
            ranges_dict[row_2_name] = float(value_2)

        elif (matched := MPS_RANGES_1_DATA_RE.match(line)):
            if not ranges_name:
                ranges_name = matched.group(1)
            else:
                if ranges_name != matched.group(1):
                    break

            row_name = matched.group(2)
            if row_name not in rows:
                error = (
                    f"UnknownRowException: Unknown sole row '{row_name}' "
                    'in RANGES !'
                )
                logger.exception(f"      {error}")
                raise UnknownRowException(error)

            value = matched.group(3)

            ranges_dict[row_name] = float(value)

        else:
            error = (
                f"BadRANGESDataException: Cannot parse '{line}' in RANGES !"
            )
            logger.exception(f"      {error}")
            raise BadRANGESDataException(error)

    logger.debug('    Leave process_RANGES(...)')
    return ranges_dict


def process_BOUNDS(
    data: List[str],
    columns: Dict[str, int]
) -> Dict[str, List[BoundData]]:
    """Processes the BOUNDS section of MPS files.

    Parameters
    ----------
    data : List[str]
        Strings of data from BOUNDS section
    columns : Dict[str, int]
        Column information

    Returns
    -------
    Dict[str, List[BoundData]]
        A dictionary of bounds data
    """

    logger = logging.getLogger(__name__)
    logger.debug(f"    Enter process_BOUNDS({data=}, {columns=})")

    bounds_dict = {}
    bounds_name = ''
    for line in data:
        if (matched := MPS_BOUNDS_DATA_RE.match(line)):
            bound_type = matched.group(1)
            if bound_type not in MPS_BOUNDS_TYPES:
                error = (
                    'UnknownBOUNDSTypeException: Unknown BOUNDS type '
                    f"'{bound_type}' !"
                )
                logger.exception(f"      {error}")
                raise UnknownBOUNDSTypeException(error)

            if not bounds_name:
                bounds_name = matched.group(2)
            else:
                if bounds_name != matched.group(2):
                    break

            column_name = matched.group(3)
            if column_name not in columns:
                error = (
                    f"UnknownColumnException: Unknown column '{column_name}' "
                    'in BOUNDS !'
                )
                logger.exception(f"      {error}")
                raise UnknownColumnException(error)

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
                f"BadBOUNDSDataException: Cannot parse '{line}' in BOUNDS !"
            )
            logger.exception(f"      {error}")
            raise BadBOUNDSDataException(error)

    logger.debug('    Leave process_BOUNDS(...)')
    return bounds_dict


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
