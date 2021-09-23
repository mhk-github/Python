#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : ObjToB3D.py
# SYNOPSIS : Converts a Wavefront OBJ text file into a B3D binary file.
# LICENSE  : MIT
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import argparse
import logging
import os
import re
import sys

import B3DUtilities


###############################################################################
# CONSTANTS
###############################################################################

VERTEX_REGEX = re.compile(r'^v\s+(\S+)\s+(\S+)\s+(\S+)$')
TEXTURE_REGEX = re.compile(r'^vt\s+(\S+)\s+(\S+)$')
NORMAL_REGEX = re.compile(r'^vn\s+(\S+)\s+(\S+)\s+(\S+)$')

STATUS_UPDATE_MODULUS = 100000


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


###############################################################################
# DRIVER
###############################################################################

if __name__ == '__main__':
    init()
    logging.info('ObjToB3D.py - Start')

    parser = argparse.ArgumentParser(
        description='Convert a Wavefront OBJ file to a B3D file'
    )
    parser.add_argument(
        '-i',
        '--input-file',
        metavar='FILE',
        help='OBJ input file',
        required=True,
        dest='infile'
    )
    parser.add_argument(
        '-o',
        '--output-file',
        metavar='FILE',
        help='B3D output file',
        required=True,
        dest='outfile'
    )
    parser.add_argument(
        '-n',
        '--normals',
        action='store_true',
        help='Save normals data',
        dest='save_normals'
    )
    parser.add_argument(
        '-t',
        '--textures',
        action='store_true',
        help='Save texture coordinate data',
        dest='save_textures'
    )
    parser.add_argument(
        '-u',
        '--use-hint',
        action='store_true',
        help='Store indices as the type suggested by vertex data',
        dest='use_hint'
    )
    args = parser.parse_args()
    in_file = args.infile
    out_file = args.outfile
    if in_file == out_file:
        logging.error(
            f"  Input file '{in_file}' is the same as output file "
            f"'{out_file}' !"
        )
        sys.exit(1)
    has_normals = args.save_normals
    has_uv = args.save_textures
    use_hint = args.use_hint
    logging.debug(f"  Input file = '{in_file}'")
    logging.debug(f"  Output file = '{out_file}'")
    logging.debug(f"  Save normals = {has_normals}")
    logging.debug(f"  Save texture UVs = {has_uv}")
    logging.debug(f"  Use hint = {use_hint}")

    vertices = []
    textures = []
    normals = []
    triangles = []
    b3d_vertex_data = []
    obj_to_b3d_vertex_dict = {}
    current_vertex_index = 0
    line_ctr = 0
    face_count = 0
    indices_count = 0
    with open(in_file, 'r', encoding='utf-8') as infile:
        logging.info(f"  Opened input file '{in_file}' in text read mode")
        sanity_check_done = False
        while True:
            line = infile.readline()
            if not line:
                logging.debug(f"    Reached EOF for input file '{in_file}'")
                break
            line = line.strip()
            line_ctr += 1
            if line_ctr % STATUS_UPDATE_MODULUS == 0:
                logging.info(f"    Processed {line_ctr} lines ...")

            if line.startswith('vt'):
                matched = TEXTURE_REGEX.search(line)
                u = float(matched.group(1))
                v = float(matched.group(2))
                textures.append((u, v))
                logging.debug(f"    Texture coordinate ({u}, {v}) found")
            elif line.startswith('vn'):
                matched = NORMAL_REGEX.search(line)
                nx = float(matched.group(1))
                ny = float(matched.group(2))
                nz = float(matched.group(3))
                normals.append((nx, ny, nz))
                logging.debug(f"    Normal ({nx}, {ny}, {nz}) found")
            elif line.startswith('v'):
                matched = VERTEX_REGEX.search(line)
                x = float(matched.group(1))
                y = float(matched.group(2))
                z = float(matched.group(3))
                vertices.append((x, y, z))
                logging.debug(f"    Vertex ({x}, {y}, {z}) found")
            elif line.startswith('f'):
                if not sanity_check_done:
                    if not normals:
                        if has_normals:
                            logging.warning(
                                '    No normals found but -n flag set to '
                                f"{has_normals}  !"
                            )
                            has_normals = False
                    if not textures:
                        if has_uv:
                            logging.warning(
                                '    No texture UVs found but -t flag set to '
                                f"{has_uv} !"
                            )
                            has_uv = False
                    sanity_check_done = True

                original_indices = line[2:]
                logging.debug(f"    Found face '{original_indices}':")
                indices_data = original_indices.split()
                num_indices_in_face = len(indices_data)
                for i in indices_data:
                    if i not in obj_to_b3d_vertex_dict:
                        indexes = i.split('/')
                        vertex = vertices[int(indexes[0]) - 1]
                        texture = None
                        if has_uv:
                            texture = textures[int(indexes[1]) - 1]
                        normal = None
                        if has_normals:
                            normal = normals[int(indexes[2]) - 1]
                        colour = None
                        new_vertex = B3DUtilities.B3DVertex(
                            current_vertex_index,
                            vertex,
                            normal,
                            texture,
                            colour
                        )
                        b3d_vertex_data.append(new_vertex)
                        obj_to_b3d_vertex_dict[i] = new_vertex
                        logging.debug(
                            f"      Created B3DVertex: id = {new_vertex.id}, "
                            f"coordinates = {new_vertex.coordinates}, normal "
                            f"= {new_vertex.normal}, uv = {new_vertex.uv}, "
                            f"colour = {new_vertex.colour}"
                        )
                        current_vertex_index += 1

                limit_index = num_indices_in_face - 1
                vertex_0_data = indices_data[0]
                for i in range(1, limit_index):
                    vertex_1_data = indices_data[i]
                    vertex_2_data = indices_data[i + 1]
                    triangle = (
                        obj_to_b3d_vertex_dict[vertex_0_data].id,
                        obj_to_b3d_vertex_dict[vertex_1_data].id,
                        obj_to_b3d_vertex_dict[vertex_2_data].id
                    )
                    triangles.append(triangle)
                    logging.debug(f"      Saved triangle {triangle}")

                face_count += 1
                indices_count += num_indices_in_face

    logging.info(f"  Closed input file '{in_file}'")

    logging.info(
        f"  Summary for input file '{in_file}' "
        f"({os.stat(in_file).st_size} bytes): "
    )
    logging.info(f"    Vertices = {len(vertices)}")
    logging.info(f"    Normals  = {len(normals)}")
    logging.info(f"    UVs      = {len(textures)}")
    logging.info(f"    Faces    = {face_count}")
    logging.info(f"      Index count = {indices_count}")

    b3d_data = B3DUtilities.B3DData(b3d_vertex_data, triangles)
    b3d_data.write_to_file(out_file, use_hint)

    logging.info(
        f"  Summary for output file '{out_file}' "
        f"({os.stat(out_file).st_size} bytes): "
    )
    with open(out_file, 'rb') as infile:
        b3d_header = B3DUtilities.B3DHeader.from_deserialization(
            infile.read(B3DUtilities.B3D_HEADER_SIZE)
        )
        logging.debug(f"    B3D header = {b3d_header}")
        num_vertices = b3d_header.number_of_vertices
        num_indices = b3d_header.number_of_indices
        num_triangles = int(num_indices / B3DUtilities.B3D_INTS_PER_TRIANGLE)
        logging.info(f"    Vertices = {num_vertices}")
        if has_normals:
            logging.info(f"        Normals   = {num_vertices}")
        if has_uv:
            logging.info(f"        UVs       = {num_vertices}")
        logging.info(f"    Indices  = {num_indices}")
        logging.info(f"        Triangles = {num_triangles}")

    logging.info('ObjToB3D.py - End')


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
