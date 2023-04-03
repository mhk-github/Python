#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : Checksum.py
# SYNOPSIS : Checks a given file against its stated checksum.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import argparse
import hashlib

import settings


###############################################################################
# FUNCTIONS
###############################################################################

def main() -> None:
    """The driver function for this script."""

    parser = argparse.ArgumentParser(
        description='Check a file against its stated checksum'
    )
    parser.add_argument(
        '-i',
        '--input-file',
        metavar='FILE',
        required=True,
        dest='in_file',
        help='Input file'
    )
    parser.add_argument(
        '-c',
        '--checksum',
        metavar='CHECKSUM',
        required=True,
        dest='checksum',
        help='Checksum to test file against'
    )
    parser.add_argument(
        '-a',
        '--algorithm',
        metavar=(
            '{'
            'md5'
            '|sha1'
            '|sha224'
            '|sha256'
            '|sha384'
            '|sha512'
            '|sha3_224'
            '|sha3_256'
            '|sha3_384'
            '|sha3_512'
            '}'
        ),
        choices=[
            'md5',
            'sha1',
            'sha224',
            'sha256',
            'sha384',
            'sha512',
            'sha3_224',
            'sha3_256',
            'sha3_384',
            'sha3_512'
        ],
        required=True,
        dest='algorithm',
        help='Hash algorithm to use'
    )
    args = parser.parse_args()
    input_file = args.in_file
    checksum_wanted = args.checksum
    algorithm = args.algorithm

    m = None
    if algorithm == 'md5':
        m = hashlib.md5()
    elif algorithm == 'sha1':
        m = hashlib.sha1()
    elif algorithm == 'sha224':
        m = hashlib.sha224()
    elif algorithm == 'sha256':
        m = hashlib.sha256()
    elif algorithm == 'sha384':
        m = hashlib.sha384()
    elif algorithm == 'sha512':
        m = hashlib.sha512()
    elif algorithm == 'sha3_224':
        m = hashlib.sha3_224()
    elif algorithm == 'sha3_256':
        m = hashlib.sha3_256()
    elif algorithm == 'sha3_384':
        m = hashlib.sha3_384()
    elif algorithm == 'sha3_512':
        m = hashlib.sha3_512()

    with open(input_file, 'rb') as f:
        while True:
            data = f.read(settings.READ_AMOUNT)
            if not data:
                break
            m.update(data)
    checksum_found = m.hexdigest()

    if checksum_found == checksum_wanted:
        print(
            f"File '{input_file}' has {algorithm} matching '{checksum_found}'"
        )
    else:
        print(
            f"File '{input_file}' has {algorithm} '{checksum_found}' but "
            f"checksum should be '{checksum_wanted}' !"
        )


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
