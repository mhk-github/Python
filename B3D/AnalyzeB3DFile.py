#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : AnalyzeB3DFile.py
# SYNOPSIS : Displays B3D file information.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import argparse
import logging

import B3DUtilities


###############################################################################
# FUNCTIONS
###############################################################################

def init() -> None:
    """Sets up logging."""

    log_level = logging.WARNING
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s: %(message)s',
        datefmt='%H:%M:%S',
        level=log_level
    )


def main() -> None:
    """Driver for this script."""

    init()

    parser = argparse.ArgumentParser(
        description='Display B3D file information')
    parser.add_argument(
        '-f',
        '--file',
        metavar='FILE',
        help='B3D input file',
        required=True,
        dest='infile'
    )
    args = parser.parse_args()

    logging.info('AnalyzeB3DFile.py - Start')

    with open(args.infile, 'rb') as infile:
        logging.debug(
            f"  Opened file '{args.infile}' in binary mode for reading"
        )

        print(f"File = '{args.infile}'")
        b3d_header = B3DUtilities.B3DHeader.from_deserialization(
            infile.read(B3DUtilities.B3D_HEADER_SIZE)
        )

        print(f"  Number of vertices = {b3d_header.number_of_vertices}")
        print(f"    => {b3d_header.number_of_vertices * 3} float [x,y,z]")
        print(f"  Number of indices  = {b3d_header.number_of_indices}")
        print(f"    => {int(b3d_header.number_of_indices / 3)} triangles")
        print(f"  Has normals        = {b3d_header.has_normals}")
        if b3d_header.has_normals:
            print(
                f"    => {b3d_header.number_of_vertices * 3} float "
                '[nx,ny,nz]'
            )
        print(f"  Has UVs            = {b3d_header.has_uvs}")
        if b3d_header.has_uvs:
            print(f"    => {b3d_header.number_of_vertices * 2} float [u,v]")
        print(f"  Has colours        = {b3d_header.has_colours}")
        if b3d_header.has_colours:
            print(
                f"    => {b3d_header.number_of_vertices} unsigned int "
                '[RGBA]'
            )
        if b3d_header.indices_type_hint == B3DUtilities.B3D_INDICES_TYPE_UINT:
            print('  Indices type hint  = unsigned int')
        elif b3d_header.indices_type_hint == (
                B3DUtilities.B3D_INDICES_TYPE_USHORT
        ):
            print('  Indices type hint  = unsigned short')
        elif b3d_header.indices_type_hint == (
                B3DUtilities.B3D_INDICES_TYPE_UCHAR
        ):
            print('  Indices type hint  = unsigned char')
        else:
            logging.error(
                f"    Unknown indices type '{b3d_header.indices_type}' !"
            )

    logging.debug(f"  Closed file '{args.infile}'")
    logging.info('AnalyzeB3DFile.py - End')


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
