#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : DatAnalyzer.py
# SYNOPSIS : Analyzes DAT files of file and directory data.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import argparse
import logging

import files
import settings
import sql


###############################################################################
# FUNCTIONS
###############################################################################

def init(logging_level: str) -> None:
    """
    Sets up the logging system.

    Parameters
    ----------
    logging_level : str
        One of '{debug|info|warning|error|critical}'
    """

    log_level = logging.NOTSET
    if logging_level == 'debug':
        log_level = logging.DEBUG
    elif logging_level == 'info':
        log_level = logging.INFO
    elif logging_level == 'warning':
        log_level = logging.WARNING
    elif logging_level == 'error':
        log_level = logging.ERROR
    elif logging_level == 'critical':
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
        description='Analyzes the information in DAT text files.'
    )
    parser.add_argument(
        '-c',
        '--compile',
        action='store_true',
        dest='do_compile',
        help='Compile DAT files into CDAT files'
    )
    parser.add_argument(
        '-d',
        '--database',
        metavar='DATABASE',
        dest='database',
        required=True,
        help='Database to use'
    )
    parser.add_argument(
        '-e',
        '--encoding',
        metavar='utf-{8|16|32}',
        dest='encoding',
        choices=['utf-8', 'utf-16', 'utf-32'],
        default='utf-16',
        help='UTF encoding of text in DAT data files (default: utf-16)'
    )
    parser.add_argument(
        '-l',
        '--log',
        dest='logging_level',
        metavar='{debug|info|warning|error|critical}',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        default='info',
        help='Logging level (default: info)'
    )
    parser.add_argument(
        '-m',
        '--make-database',
        action='store_true',
        dest='make_database',
        help='Make a new database from DAT file data'
    )
    parser.add_argument(
        '-n',
        '--new-files',
        metavar='GLOB',
        dest='new_globs',
        action='append',
        default=[],
        help='DAT files for new data'
    )
    parser.add_argument(
        '-o',
        '--old-files',
        metavar='GLOB',
        dest='old_globs',
        action='append',
        default=[],
        help='DAT files for old data'
    )
    args = parser.parse_args()
    do_compile = args.do_compile
    db = args.database
    enc = args.encoding
    logging_level = args.logging_level
    make_database = args.make_database
    new_globs = args.new_globs
    old_globs = args.old_globs

    init(logging_level)
    logger = logging.getLogger(__name__)
    logger.info('DatAnalyzer.py - Start')
    logger.info(f"  Options = {args}")

    dat_data = []
    dat_data.extend(files.process_dat_globs(new_globs, enc, True, do_compile))
    dat_data.extend(files.process_dat_globs(old_globs, enc, False, do_compile))

    if make_database:
        sql.create_new_database(
            db,
            dat_data,
            settings.SHOW_SQL
        )

    logger.info('DatAnalyzer.py - End')


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
