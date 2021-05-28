#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : FindCStyleCasts.py
# SYNOPSIS : Find C-style casts in text files.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import argparse
import logging
import re

import settings


###############################################################################
# FUNCTIONS
###############################################################################

def init() -> None:
    """Sets up logging."""

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
        format='%(asctime)s %(levelname)-8s: %(message)s',
        datefmt='%H:%M:%S',
        level=log_level
    )


def main() -> None:
    """Driver for this script."""

    parser = argparse.ArgumentParser(
        description='Find C-style casts in text files'
    )
    parser.add_argument(
        '-f',
        '--file',
        metavar='FILE',
        help='Text input file',
        required=True,
        dest='filename'
    )
    args = parser.parse_args()

    init()

    file = args.filename
    types = settings.TYPES
    num_types = len(types)
    stride = settings.REGEX_TYPES_SLICE_STRIDE

    logging.info('FindCStyleCasts.py - Start')
    logging.info(f"  Input file = '{file}'")
    logging.debug(f"  {num_types} cast types = {types}")
    logging.debug(f"  Regex alternates stride = {stride}")

    regexes = tuple(
        re.compile(
            r'(?:'
            f"{'|'.join(types[i:i + stride])}"
            r')\s*\**&*\s*\)\s*\(?\s*\**&*[A-Za-z_][0-9A-Za-z_]+'
        )
        for i in range(0, num_types, stride)
    )
    logging.debug(f"  {len(regexes)} generated regexes = {regexes}")

    with open(file, 'r', encoding='utf-8') as in_file:
        logging.debug(f"  Opened file '{file}' for reading")
        line_ctr = 1
        while True:
            line = in_file.readline()
            if not line:
                break
            line = line.strip()
            for r in regexes:
                if r.search(line):
                    print(f"    [{line_ctr:6d}] '{line}'")
                    break
            line_ctr += 1
    logging.debug(f"  Closed file '{file}'")

    logging.info('FindCStyleCasts.py - End')


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
