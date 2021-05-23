#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : AnalyzeObjFile.py
# SYNOPSIS : Provides information on Wavefront 3D OBJ files.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import argparse
import logging
import re


###############################################################################
# CONSTANTS
###############################################################################

MODEL_NAME_REGEX = re.compile(r'^o\s+(.*)$')
LINE_ELEMENT_REGEX = re.compile(r'^\d+')


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
        description='Provide information on Wavefront 3D OBJ files'
    )
    parser.add_argument(
        '-f',
        '--file',
        metavar='FILE',
        help='OBJ input file',
        required=True,
        dest='filename'
    )
    args = parser.parse_args()

    logging.info('AnalyzeObjFile.py - Start')

    model_name = None
    num_vertices = 0
    num_texture_coordinates = 0
    num_vertex_normals = 0
    num_parameter_space_vertices = 0
    num_polygonal_face_elements = 0
    num_groups = 0
    num_line_elements = 0
    with open(args.filename, 'r', encoding='utf-8') as file:
        logging.debug(
            f"  Opened file '{args.filename}' in text mode for reading"
        )
        line_ctr = 0
        while True:
            line = file.readline()
            if not line:
                break
            line = line.strip()
            line_ctr += 1
            if line.startswith('#'):
                next
            elif line.startswith('vt'):
                num_texture_coordinates += 1
            elif line.startswith('vn'):
                num_vertex_normals += 1
            elif line.startswith('vp'):
                num_parameter_space_vertices += 1
            elif line.startswith('v'):
                num_vertices += 1
            elif line.startswith('f'):
                num_polygonal_face_elements += 1
            elif line.startswith('g'):
                num_groups += 1
            elif line.startswith('o'):
                matched = MODEL_NAME_REGEX.search(line)
                model_name = matched.group(1)
            elif LINE_ELEMENT_REGEX.search(line):
                num_line_elements += 1
            else:
                logging.warning(
                    f"    Cannot process '{line}' at line {line_ctr}"
                )

    logging.debug(f"  Closed file '{args.filename}'")

    if model_name:
        print(f"Model name               = {model_name}")
    else:
        print(f"Model name               = {args.filename}")
    print(f"Vertices                 = {num_vertices}")
    print(f"Texture coordinates      = {num_texture_coordinates}")
    print(f"Vertex normals           = {num_vertex_normals}")
    print(f"Parameter space vertices = {num_parameter_space_vertices}")
    print(f"Polygonal face elements  = {num_polygonal_face_elements}")
    print(f"Groups                   = {num_groups}")
    print(f"Line elements            = {num_line_elements}")

    logging.info('AnalyzeObjFile.py - End')


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
