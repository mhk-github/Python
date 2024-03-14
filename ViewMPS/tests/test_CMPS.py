#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : test_simple_mps.py
# SYNOPSIS : Smoke tests using a simple MPS file.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import pytest
import utilities.mps


###############################################################################
# FIXTURES
###############################################################################

@pytest.fixture(scope='module', params=['./tests/data/simple.mps'])
def simple_mps(request):
    test_mps = utilities.mps.CMPS(request.param)
    yield test_mps


###############################################################################
# TESTS
###############################################################################

@pytest.mark.smoke
@pytest.mark.parametrize(
    'identifier',
    [
        'TESTPROB',
    ]
)
def test_NAME(simple_mps, identifier):
    assert simple_mps.name == identifier


@pytest.mark.parametrize(
    'identifier',
    [
        'VOID',
    ]
)
def test_nonexistent_NAME(simple_mps, identifier):
    assert simple_mps.name != identifier


@pytest.mark.smoke
def test_num_rows(simple_mps):
    assert len(simple_mps.rows) == 4


def test_rowdata(simple_mps):
    assert (
        simple_mps.rows['COST'].row_id == 0
        and simple_mps.rows['COST'].row_type == 'N'
        and simple_mps.rows['LIM1'].row_id == 1
        and simple_mps.rows['LIM1'].row_type == 'L'
        and simple_mps.rows['LIM2'].row_id == 2
        and simple_mps.rows['LIM2'].row_type == 'G'
        and simple_mps.rows['MYEQN'].row_id == 3
        and simple_mps.rows['MYEQN'].row_type == 'E'
    )


@pytest.mark.parametrize(
    'identifier',
    [
        'VOID',
    ]
)
def test_nonexistent_row(simple_mps, identifier):
    assert identifier not in simple_mps.rows


@pytest.mark.smoke
def test_num_columns(simple_mps):
    assert len(simple_mps.columns) == 3


def test_columns(simple_mps):
    assert (
        simple_mps.columns['XONE'] == 0
        and simple_mps.columns['YTWO'] == 1
        and simple_mps.columns['ZTHREE'] == 2
    )


@pytest.mark.parametrize(
    'identifier',
    [
        'VOID',
    ]
)
def test_nonexistent_column(simple_mps, identifier):
    assert identifier not in simple_mps.columns


@pytest.mark.smoke
def test_num_elements(simple_mps):
    assert len(simple_mps.elements) == 9


def test_elementdata(simple_mps):
    assert (
        simple_mps.elements[utilities.mps.ElementData(0, 0)] == 1.0
        and simple_mps.elements[utilities.mps.ElementData(1, 0)] == 1.0
        and simple_mps.elements[utilities.mps.ElementData(2, 0)] == 1.0
        and simple_mps.elements[utilities.mps.ElementData(0, 1)] == 4.0
        and simple_mps.elements[utilities.mps.ElementData(1, 1)] == 1.0
        and simple_mps.elements[utilities.mps.ElementData(3, 1)] == -1.0
        and simple_mps.elements[utilities.mps.ElementData(0, 2)] == 9.0
        and simple_mps.elements[utilities.mps.ElementData(2, 2)] == 1.0
        and simple_mps.elements[utilities.mps.ElementData(3, 2)] == 1.0
    )


@pytest.mark.smoke
def test_num_rhs(simple_mps):
    assert len(simple_mps.rhs) == 3


def test_rhs(simple_mps):
    assert (
        simple_mps.rhs['LIM1'] == 5.0
        and simple_mps.rhs['LIM2'] == 10.0
        and simple_mps.rhs['MYEQN'] == 7.0
    )


@pytest.mark.smoke
def test_num_ranges(simple_mps):
    assert len(simple_mps.ranges) == 2


def test_ranges(simple_mps):
    assert (
        simple_mps.ranges['LIM1'] == 6.0
        and simple_mps.ranges['LIM2'] == 5.0
    )


@pytest.mark.smoke
def test_num_bounds(simple_mps):
    assert len(simple_mps.bounds) == 2


def test_bounds(simple_mps):
    assert (
        simple_mps.bounds['XONE'][0].bound_type == 'UP'
        and simple_mps.bounds['XONE'][0].value == 4.0
        and simple_mps.bounds['YTWO'][0].bound_type == 'LO'
        and simple_mps.bounds['YTWO'][0].value == -1.0
        and simple_mps.bounds['YTWO'][1].bound_type == 'UP'
        and simple_mps.bounds['YTWO'][1].value == 1.0
    )


###############################################################################
# END
###############################################################################
# Local Variables:
# mode: python
# End:
