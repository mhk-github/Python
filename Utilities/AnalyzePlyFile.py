#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : AnalyzePlyFile.py
# SYNOPSIS : Provides information on Stanford PLY files.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import argparse
import logging

import PLYUtilities


###############################################################################
# FUNCTIONS
###############################################################################

def init() -> None:
    """Sets up logging."""

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
        description='Provide information on Stanford 3D PLY files'
    )
    parser.add_argument(
        '-f',
        '--file',
        metavar='FILE',
        help='OBJ input file',
        required=True,
        dest='infile'
    )
    args = parser.parse_args()

    logging.info('AnalyzePlyFile.py - Start')

    logging.debug(f"  Input file = '{args.infile}'")
    ply_header = PLYUtilities.PLYHeader(args.infile)
    logging.debug(f"  Closed file '{args.infile}'")

    logging.info(f"  {ply_header}")
    logging.info('AnalyzePlyFile.py - End')


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
