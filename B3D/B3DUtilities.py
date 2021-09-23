#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : B3DUtilities.py
# SYNOPSIS : A module for common data structures and tasks for B3D files.
# LICENSE  : MIT
# NOTES    : A B3D header is 16 bytes at the start of the binary file where:
#                bytes[ 0..3  ] = identifier 'B3D\n'
#                bytes[ 4..7  ] = number of vertices (unsigned long)
#                bytes[ 8..11 ] = number indices (unsigned long)
#                byte[12]       = flag set to 1 if vertex normal data present
#                byte[13]       = flag set to 1 if vertex UV data present
#                byte[14]       = flag set to 1 if vertex colour data present
#                byte[15]       = type of indices data
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import collections
import struct


###############################################################################
# CONSTANTS
###############################################################################

B3D_HEADER_SIZE = 16

B3D_INDICES_TYPE_UCHAR = 1
B3D_INDICES_TYPE_USHORT = 2
B3D_INDICES_TYPE_UINT = 4

B3D_UCHAR_THRESHOLD = 256
B3D_USHORT_THRESHOLD = 65536

B3D_HEADER_ID_B0 = ord('B')
B3D_HEADER_ID_B1 = ord('3')
B3D_HEADER_ID_B2 = ord('D')
B3D_HEADER_ID_B3 = ord('\n')

B3D_HEADER_DATA_FORMAT = '4B2L4B'
B3D_ENDIAN_FORMAT = '<'
B3D_HEADER_FORMAT = B3D_ENDIAN_FORMAT + B3D_HEADER_DATA_FORMAT
B3D_OUTPUT_INTEGERS_TYPE_FORMAT = 'I'
B3D_OUTPUT_SHORTS_TYPE_FORMAT = 'H'
B3D_OUTPUT_BYTES_TYPE_FORMAT = 'B'
B3D_OUTPUT_FLOATS_TYPE_FORMAT = 'f'

B3D_INTS_PER_TRIANGLE = 3


###############################################################################
# CLASSES
###############################################################################

B3DVertex = collections.namedtuple(
    'B3DVertex',
    [
        'id',
        'coordinates',
        'normal',
        'uv',
        'colour'
    ]
)


class B3DHeader:
    """Holds all header data in a binary B3D file."""

    def __init__(
            self,
            num_verts,
            num_indices,
            has_normals,
            has_uvs,
            has_colours,
            indices_type_hint
    ):
        """
        Parameters
        ----------
        num_verts : int
            Number of vertices
        num_indices : int
            Number of indices
        has_normals : bool
            Vertex normal data is stored
        has_uvs : bool
            Vertex texture coordinates data is stored
        has_colours : bool
            Vertex colour data as RGBA is stored
        indices_type_hint : int
            Suggests indices type be unsigned char, short or int
        """

        self._num_verts = num_verts
        self._num_indices = num_indices
        self._has_normals = has_normals
        self._has_uvs = has_uvs
        self._has_colours = has_colours
        self._indices_type_hint = indices_type_hint

    def __repr__(self):
        v = self._num_verts
        i = self._num_indices
        n = self._has_normals
        u = self._has_uvs
        c = self._has_colours
        t = self._indices_type_hint
        return (
            f"<B3DHeader object: vertices={v}, indices={i}, normals?={n}, "
            f"UV?={u}, colours?={c}, indices type hint={t}>"
        )

    def serialize(self):
        """Creates the byte representation of the B3DHeader object."""

        data = struct.pack(
            B3D_HEADER_FORMAT,
            B3D_HEADER_ID_B0,
            B3D_HEADER_ID_B1,
            B3D_HEADER_ID_B2,
            B3D_HEADER_ID_B3,
            self._num_verts,
            self._num_indices,
            1 if self._has_normals else 0,
            1 if self._has_uvs else 0,
            1 if self._has_colours else 0,
            self._indices_type_hint
        )
        return data

    @property
    def number_of_vertices(self):
        return self._num_verts

    @property
    def number_of_indices(self):
        return self._num_indices

    @property
    def has_normals(self):
        return self._has_normals

    @property
    def has_uvs(self):
        return self._has_uvs

    @property
    def has_colours(self):
        return self._has_colours

    @property
    def indices_type_hint(self):
        return self._indices_type_hint

    @classmethod
    def from_arguments(
            cls,
            num_verts,
            num_indices,
            has_normals=False,
            has_uvs=False,
            has_colours=False,
            indices_type_hint=B3D_INDICES_TYPE_UINT
    ):
        """
        Creates a B3DHeader object from a complete set of arguments.

        Parameters
        ----------
        num_verts : int
            Number of vertices
        num_indices : int
            Number of indices
        has_normals : bool
            Vertex normal data is stored
        has_uvs : bool
            Vertex texture coordinates data is stored
        has_colours : bool
            Vertex colour data as RGBA is stored
        indices_type_hint : int
            Indices type suggestion
        """

        return cls(
            num_verts,
            num_indices,
            has_normals,
            has_uvs,
            has_colours,
            indices_type_hint
        )

    @classmethod
    def from_deserialization(cls, bytes_data):
        """
        Creates a B3DHeader object by deserialization of bytes.

        Parameters
        ----------
        bytes_data : array/tuple
            Bytes representing a B3DHeader
        """

        if len(bytes_data) == B3D_HEADER_SIZE:
            (
                b0,
                b1,
                b2,
                b3,
                num_verts,
                num_indices,
                has_normals,
                has_uvs,
                has_colours,
                indices_type_hint
            ) = struct.unpack(B3D_HEADER_FORMAT, bytes_data)
            if (
                b0 == B3D_HEADER_ID_B0
                and b1 == B3D_HEADER_ID_B1
                and b2 == B3D_HEADER_ID_B2
                and b3 == B3D_HEADER_ID_B3
            ):
                has_normals = True if has_normals == 1 else False
                has_uvs = True if has_uvs == 1 else False
                has_colours = True if has_colours == 1 else False
                return cls(
                    num_verts,
                    num_indices,
                    has_normals,
                    has_uvs,
                    has_colours,
                    indices_type_hint
                )
            else:
                msg = (
                    f"B3D identifier not found in first bytes ([0]={b0}, "
                    f"[1]={b1}, [2]={b2}, [3]={b3}) !"
                )
                raise Exception(msg)
        else:
            msg = (
                f"B3D header size is {B3D_HEADER_SIZE} bytes but data is "
                f"{len(bytes_data)} bytes !"
            )
            raise Exception(msg)


class B3DData:
    """Holds all data to describe a 3D object."""

    def __init__(self, vertices, triangles):
        """
        Parameters
        ----------
        vertices : list
            A list of B3DVertex in ascending ID order
        triangles : list
            A list of triples of integers for vertex indices making a triangle
        """

        self._b3dvertices = vertices
        self._triangles = triangles

    def write_to_file(self, filename, use_hint=False):
        """
        Creates a binary B3D file for the data.

        Parameters
        ----------
        filename : str
            Full name and path of the output file
        use_hint : bool
            Save indices as a type suggested by the amount of vertex data
        """

        with open(filename, 'wb') as out_file:

            vertex_old_id_to_new_id_dict = {}
            vertex_data_to_new_id_dict = {}
            current_new_vertex_id = 0
            new_vertices = []
            for v in self._b3dvertices:
                key = (v.coordinates, v.normal, v.uv, v.colour)
                if key not in vertex_data_to_new_id_dict:
                    vertex_data_to_new_id_dict[key] = current_new_vertex_id
                    new_vertices.append(v)
                    current_new_vertex_id += 1
                vertex_old_id_to_new_id_dict[v.id] = (
                    vertex_data_to_new_id_dict[key]
                )

            num_vertices = len(new_vertices)
            num_indices = len(self._triangles) * B3D_INTS_PER_TRIANGLE
            examine_vertex = new_vertices[0]
            has_normals = True if examine_vertex.normal else False
            has_uvs = True if examine_vertex.uv else False
            has_colours = True if examine_vertex.colour else False
            indices_type_hint = None
            if num_vertices <= B3D_UCHAR_THRESHOLD:
                indices_type_hint = B3D_INDICES_TYPE_UCHAR
            elif num_vertices <= B3D_USHORT_THRESHOLD:
                indices_type_hint = B3D_INDICES_TYPE_USHORT
            else:
                indices_type_hint = B3D_INDICES_TYPE_UINT
            b3d_header = B3DHeader.from_arguments(
                num_vertices,
                num_indices,
                has_normals,
                has_uvs,
                has_colours,
                indices_type_hint
            )
            out_file.write(b3d_header.serialize())

            pack_data_vertices = []
            pack_data_normals = []
            pack_data_uvs = []
            pack_data_colours = []
            for v in new_vertices:
                pack_data_vertices.extend(v.coordinates)
                if has_normals:
                    pack_data_normals.extend(v.normal)
                if has_uvs:
                    pack_data_uvs.extend(v.uv)
                if has_colours:
                    pack_data_colours.append(v.colour)

            pack_format_vertices = (
                B3D_ENDIAN_FORMAT
                + (B3D_OUTPUT_FLOATS_TYPE_FORMAT * len(pack_data_vertices))
            )
            out_file.write(
                struct.pack(
                    pack_format_vertices,
                    *pack_data_vertices
                )
            )

            if has_normals:
                pack_format_normals = (
                    B3D_ENDIAN_FORMAT
                    + (B3D_OUTPUT_FLOATS_TYPE_FORMAT * len(pack_data_normals))
                )
                out_file.write(
                    struct.pack(
                        pack_format_normals,
                        *pack_data_normals
                    )
                )

            if has_uvs:
                pack_format_uvs = (
                    B3D_ENDIAN_FORMAT
                    + (B3D_OUTPUT_FLOATS_TYPE_FORMAT * len(pack_data_uvs))
                )
                out_file.write(struct.pack(pack_format_uvs, *pack_data_uvs))

            if has_colours:
                pack_format_colours = (
                    B3D_ENDIAN_FORMAT
                    + (
                        B3D_OUTPUT_INTEGERS_TYPE_FORMAT
                        * len(pack_data_colours)
                    )
                )
                out_file.write(
                    struct.pack(
                        pack_format_colours,
                        *pack_data_colours
                    )
                )

            pack_data_triangles = [
                vertex_old_id_to_new_id_dict[i]
                for t in self._triangles
                for i in t
            ]
            output_index_type = B3D_OUTPUT_INTEGERS_TYPE_FORMAT
            if use_hint:
                if indices_type_hint == B3D_INDICES_TYPE_UCHAR:
                    output_index_type = B3D_OUTPUT_BYTES_TYPE_FORMAT
                elif indices_type_hint == B3D_INDICES_TYPE_USHORT:
                    output_index_type = B3D_OUTPUT_SHORTS_TYPE_FORMAT
            pack_format_triangles = (
                B3D_ENDIAN_FORMAT
                + (output_index_type * len(pack_data_triangles))
            )
            out_file.write(
                struct.pack(
                    pack_format_triangles,
                    *pack_data_triangles
                )
            )


###############################################################################
# END
###############################################################################
# Local variables:
# mode: python
# End:
