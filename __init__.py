"""
PyCAS - Python CAS File Reader

A pure Python library for reading and converting Atari 8-bit cassette (CAS) files.
"""

from cas_reader import (
    CASReader,
    Chunk,
    ChunkHeader,
    ChunkType,
    read_cas_file,
    parse_chunk_selection,
)

__version__ = "0.1.1"
__author__ = "Aykut Kılıç"
__license__ = "MIT"

__all__ = [
    "CASReader",
    "Chunk",
    "ChunkHeader",
    "ChunkType",
    "read_cas_file",
    "parse_chunk_selection",
]
