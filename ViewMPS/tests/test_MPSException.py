#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : test_MPSException.py
# SYNOPSIS : Checks all specific MPS exceptions are thrown correctly.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import pytest
import utilities.mps


###############################################################################
# TESTS
###############################################################################

@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_BOUNDS_type.mps'
    ]
)
def test_bad_BOUNDS_type(identifier):
    with pytest.raises(utilities.mps.UnknownBOUNDSTypeException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_BOUNDS_column.mps'
    ]
)
def test_bad_BOUNDS_column(identifier):
    with pytest.raises(utilities.mps.UnknownColumnException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_COLUMNS_missing.mps'
    ]
)
def test_bad_COLUMNS_missing(identifier):
    with pytest.raises(utilities.mps.NoCOLUMNSException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_COLUMNS_row.mps'
    ]
)
def test_bad_COLUMNS_row(identifier):
    with pytest.raises(utilities.mps.UnknownRowException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_ENDATA_missing.mps'
    ]
)
def test_bad_ENDATA_missing(identifier):
    with pytest.raises(utilities.mps.NoENDATAException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_mps_file.mps'
    ]
)
def test_bad_mps_file(identifier):
    with pytest.raises(utilities.mps.NotMPSFileException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_NAME_missing.mps'
    ]
)
def test_bad_NAME_missing(identifier):
    with pytest.raises(utilities.mps.NoNAMEException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_RHS_missing.mps'
    ]
)
def test_bad_RHS_missing(identifier):
    with pytest.raises(utilities.mps.NoRHSException):
        utilities.mps.CMPS(identifier)


@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_RHS_row.mps'
    ]
)
def test_bad_RHS_row(identifier):
    with pytest.raises(utilities.mps.UnknownRowException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_ROWS_missing.mps'
    ]
)
def test_bad_ROWS_missing(identifier):
    with pytest.raises(utilities.mps.NoROWSException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_ROWS_type.mps'
    ]
)
def test_bad_ROWS_type(identifier):
    with pytest.raises(utilities.mps.UnknownROWSTypeException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_ROWS_data.mps'
    ]
)
def test_bad_ROWS_data(identifier):
    with pytest.raises(utilities.mps.BadROWSDataException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_COLUMNS_data.mps'
    ]
)
def test_bad_COLUMNS_data(identifier):
    with pytest.raises(utilities.mps.BadCOLUMNSDataException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_RHS_data.mps'
    ]
)
def test_bad_RHS_data(identifier):
    with pytest.raises(utilities.mps.BadRHSDataException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_RANGES_data.mps'
    ]
)
def test_bad_RANGES_data(identifier):
    with pytest.raises(utilities.mps.BadRANGESDataException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_BOUNDS_data.mps'
    ]
)
def test_bad_BOUNDS_data(identifier):
    with pytest.raises(utilities.mps.BadBOUNDSDataException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_no_ROWS_data.mps'
    ]
)
def test_no_ROWS_data(identifier):
    with pytest.raises(utilities.mps.NoROWSDataException):
        utilities.mps.CMPS(identifier)


@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        './tests/data/bad_no_COLUMNS_data.mps'
    ]
)
def test_no_COLUMNS_data(identifier):
    with pytest.raises(utilities.mps.NoCOLUMNSDataException):
        utilities.mps.CMPS(identifier)


###############################################################################
# END
###############################################################################
# Local Variables:
# mode: python
# End:
