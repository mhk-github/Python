#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : files.py
# SYNOPSIS : Utilities for processing DAT files.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import glob
import logging
import os
import re
import zipfile

from concurrent import futures
from datetime import datetime
from pathlib import (
    Path,
    PurePath,
)
from typing import (
    List,
    Optional,
    TypeVar,
)

import settings
import sql


###############################################################################
# TYPING
###############################################################################

DatRecord = TypeVar('DatRecord')
DateTime = TypeVar('DateTime')
Directory = TypeVar('Directory')
Glob = TypeVar('Glob')


###############################################################################
# CONSTANTS
###############################################################################

RE_DIRECTORY = re.compile(r'^Directory:\s+(.*)$')
RE_FILE = re.compile(
    r'^-a[r-]--\s+(\d{2})\/(\d{2})\/(\d{2})\s+(\d+):(\d{2})\s+(AM|PM)'
    r'\s+(\d+)\s+(.*)$'
)
RE_IGNORE = re.compile(r'^(?:d[ar-]{4}|Mode|[-]{4})\s+')
RE_WINDOWS_DRIVE = re.compile(r'^\S:')
RE_DATRECORD = re.compile(
    r"^<DatRecord: dat_id=\d+, file_name='(.+?)', file_size=(\d+), "
    r"file_mtime=(\d+), source_is_new=(\d), source_name='(.+?)', "
    r"directory_name='(.+?)'>$")

ARCHIVE_TYPE = zipfile.ZIP_DEFLATED
ARCHIVE_EXT = '.zip'

COMPILED_DAT_EXT = '.cdat'
DAT_EXT = '.dat'


###############################################################################
# FUNCTIONS
###############################################################################

def process_cdat_line(line: str, indent: int = 6) -> Optional[DatRecord]:
    """Processes a single line of compressed CDAT data.

    Parameters
    ----------
    line : str
        Line from a compressed CDAT file
    indent : int
        Used for log formatting

    Returns
    -------
    Optional[DatRecord]
        A DatRecord object or None
    """

    logger = logging.getLogger(__name__)
    preamble = ' ' * indent
    logger.debug(
        f"{preamble}Enter process_cdat_line(line='{line}', {indent=})"
    )

    if (matched := RE_DATRECORD.search(line)):
        dr_file_name = matched.group(1)
        dr_file_size = int(matched.group(2))
        dr_file_mtime = datetime.fromtimestamp(
            int(matched.group(3))
        )
        dr_source_is_new = bool(int(matched.group(4)))
        dr_source_name = matched.group(5)
        dr_directory_name = matched.group(6)
        return (
            sql.DatRecord(
                file_name=dr_file_name,
                file_size=dr_file_size,
                file_mtime=dr_file_mtime,
                source_is_new=dr_source_is_new,
                source_name=dr_source_name,
                directory_name=dr_directory_name
            )
        )

    logger.debug(f"{preamble}Leave process_cdat_line(...)")
    return None


def import_cdat_archive(
    cdat_archive: str,
    indent: int = 4
) -> List[DatRecord]:
    """Imports all DatRecord objects found in a compiled DAT archive file.

    Parameters
    ----------
    cdat_archive : str
        Canonical path of compiled DAT archive file
    indent : int
        Used for log formatting

    Returns
    -------
    List[DatRecord]
        A list of DatRecord objects found in the DAT file
    """

    logger = logging.getLogger(__name__)
    preamble = ' ' * indent
    logger.debug(
        f"{preamble}Enter import_cdat_archive(cdat_archive='{cdat_archive}', "
        f"{indent=})"
    )

    return_data = []
    with zipfile.ZipFile(
            cdat_archive,
            compression=ARCHIVE_TYPE
    ) as archive:
        for entry in archive.namelist():
            with archive.open(entry) as compressed_file:
                text_a = compressed_file.read().decode(
                    encoding='utf-8', errors='ignore'
                ).split('\n')
                for line in text_a:
                    dr = process_cdat_line(line.strip())
                    if dr:
                        return_data.append(dr)

    logger.debug(f"{preamble}Leave import_cdat_archive(...)")
    return return_data


def import_cdat(
    cdat_file: str,
    indent: int = 4
) -> List[DatRecord]:
    """Imports all DatRecord objects found in a compiled DAT file.

    Parameters
    ----------
    cdat_file : str
        Canonical path of compiled DAT file
    indent : int
        Used for log formatting

    Returns
    -------
    List[DatRecord]
        A list of DatRecord objects found in the DAT file
    """

    logger = logging.getLogger(__name__)
    preamble = ' ' * indent
    logger.debug(
        f"{preamble}Enter import_cdat(cdat_file='{cdat_file}', {indent=})"
    )

    return_data = []
    with open(cdat_file, 'r', encoding='utf-8') as in_file:
        for line in in_file:
            dr = process_cdat_line(line.strip())
            if dr:
                return_data.append(dr)

    logger.debug(f"{preamble}Leave import_cdat(...)")
    return return_data


def process_dat_file(
    dat_file: str,
    enc: str,
    is_new: bool,
    to_compile: bool,
    indent: int = 4
) -> List[DatRecord]:
    """Processes a DAT file into a list of DatRecord objects.

    Parameters
    ----------
    dat_file : str
        Canonical path of DAT file
    enc : str
        File encoding (e.g. utf-8, utf-16, etc.)
    is_new : bool
        True if the file exists
    to_compile : bool
        True if a compiled DAT file (*.cdat) is to be made from the DAT file
    indent : int
        Used for log formatting

    Returns
    -------
    List[DatRecord]
        A list of DatRecord objects found in the DAT file
    """

    logger = logging.getLogger(__name__)
    preamble = ' ' * indent
    logger.debug(
        f"{preamble}Enter process_dat_file(dat_file='{dat_file}', enc='{enc}',"
        f" {is_new=}, {to_compile=}, {indent=})"
    )

    return_data = []
    if dat_file.endswith(DAT_EXT):
        source = PurePath(dat_file).stem
        logger.debug(f"{preamble}  Source = '{source}'")

        current_line = 0
        directory = ''
        posix_directory = ''
        maybe_multiline_directory = False
        maybe_multiline_file = False
        with open(dat_file, 'r', encoding=enc) as in_file:
            for line in in_file:
                current_line += 1
                b = line.strip().encode('utf-8')
                t = b.decode('utf-8')
                if t:
                    if t.startswith('-a---') or t.startswith('-ar--'):
                        maybe_multiline_directory = False
                        maybe_multiline_file = True
                        if directory:
                            posix_directory = PurePath(
                                RE_DIRECTORY.search(directory)[1]
                            ).as_posix()
                            if RE_WINDOWS_DRIVE.search(posix_directory):
                                posix_directory = posix_directory[2:]
                            directory = None
                            logger.debug(
                                f"{preamble}    Directory = "
                                f"'{posix_directory}'"
                            )

                        match = RE_FILE.search(t)
                        month = int(match[1])
                        day = int(match[2])
                        y = int(match[3])
                        h = int(match[4])
                        minute = int(match[5])
                        is_pm = (match[6] == 'PM')
                        file_size = int(match[7])
                        file_name = match[8]

                        year = 2000 + y if y < settings.CUTOFF else 1900 + y
                        hour = h
                        if is_pm:
                            if h != 12:
                                hour += 12
                            else:
                                if h == 12:
                                    hour = 0
                        file_mtime = datetime(year, month, day, hour, minute)

                        return_data.append(
                            sql.DatRecord(
                                file_name=file_name,
                                file_size=file_size,
                                file_mtime=file_mtime,
                                source_is_new=is_new,
                                source_name=source,
                                directory_name=posix_directory
                            )
                        )
                        logger.debug(
                            f"{preamble}      Created DatRecord: "
                            f"{return_data[-1]}"
                        )
                    elif t.startswith('Directory:'):
                        directory = t
                        maybe_multiline_directory = True
                        maybe_multiline_file = False
                    elif RE_IGNORE.search(t):
                        maybe_multiline_directory = False
                        maybe_multiline_file = False
                    else:
                        if maybe_multiline_directory:
                            directory = directory + t
                            logger.debug(
                                f"{preamble}      Directory name update due "
                                f"to '{dat_file}' line {current_line}: "
                                f"'{directory}'"
                            )
                        elif maybe_multiline_file:
                            latest_dat_record = return_data[-1]
                            latest_dat_record.file_name = (
                                latest_dat_record.file_name + t
                            )
                            logger.debug(
                                f"{preamble}      File name update due to "
                                f"'{dat_file}' line {current_line}: "
                                f"'{latest_dat_record.file_name}'"
                            )

            if to_compile:
                output_file = dat_file + COMPILED_DAT_EXT
                with open(output_file, 'w', encoding='utf-8') as out_file:
                    print(*return_data, file=out_file, sep='\n')
                logger.debug(
                    f"{preamble}    Wrote {len(return_data)} DatRecord "
                    f"objects to compiled DAT file '{output_file}'"
                )

                with zipfile.ZipFile(
                    output_file + ARCHIVE_EXT,
                    mode='w',
                    compression=ARCHIVE_TYPE
                ) as archive:
                    archive.write(
                        output_file,
                        arcname=PurePath(output_file).name
                    )
                    if settings.DELETE_INTERMEDIATE_CDAT_FILES:
                        Path(output_file).unlink(missing_ok=True)

    elif dat_file.endswith(COMPILED_DAT_EXT):
        return_data = import_cdat(dat_file)
        logger.debug(
            f"{preamble}    Read {len(return_data)} DatRecord objects from "
            f"compiled DAT file '{dat_file}'"
        )

    elif dat_file.endswith(ARCHIVE_EXT):
        return_data = import_cdat_archive(dat_file)
        logger.debug(
            f"{preamble}    Read {len(return_data)} DatRecord objects from "
            f"compiled DAT archive file '{dat_file}'"
        )

    logger.debug(f"{preamble}Leave process_dat_file(...)")
    return return_data


def process_dat_globs(
    dat_globs: List[Glob],
    enc: str,
    is_new: bool,
    to_compile: bool,
    indent: int = 2
) -> List[DatRecord]:
    """Processes DAT file globs into a list of DatRecord objects.

    Parameters
    ----------
    dat_globs : List[Glob]
        List of canonical path globs for DAT files
    enc : str
        File encoding (e.g. utf-8, utf-16, etc.)
    is_new : bool
        True if the file exists
    to_compile : bool
        True if compiled DAT files (*.dat) are to be made from DAT files
    indent : int
        Used for log formatting

    Returns
    -------
    List[DatRecord]
        List of all DatRecord objects made from DAT files in the globs
    """

    logger = logging.getLogger(__name__)
    preamble = ' ' * indent
    logger.debug(
        f"{preamble}Enter process_dat_globs({dat_globs=}, enc='{enc}', "
        f"{is_new=}, {to_compile=}, {indent=})"
    )

    files_list = []
    for g in dat_globs:
        files_list.extend(glob.iglob(g))
    files_list = sorted(
        files_list,
        key=lambda p: os.path.getsize(p),
        reverse=True
    )

    dat_data = []
    tasks_left = len(files_list)
    slice_start = 0
    while tasks_left > 0:
        workers = min(settings.MAX_THREADS, tasks_left)
        slice_end = slice_start + workers
        with futures.ThreadPoolExecutor(workers) as executor:
            files_slice = files_list[slice_start:slice_end:]
            args = (
                (f, enc, is_new, to_compile) for f in files_slice
            )
            results = executor.map(
                lambda p: process_dat_file(*p),
                args
            )
            for r in results:
                dat_data.extend(r)

            slice_start = slice_end
            tasks_left -= workers

            logger.info(f"{preamble}  Processed files = {files_slice}")

    logger.debug(f"{preamble}Leave process_dat_globs(...)")
    return dat_data


###############################################################################
# END
###############################################################################
# Local Variables:
# mode: python
# End:
