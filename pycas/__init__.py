"""
PyCAS - Python CAS File Reader

A pure Python library for reading and converting Atari 8-bit cassette (CAS) files.
"""

from pycas.cas_reader import (
    CASReader,
    Chunk,
    ChunkHeader,
    ChunkType,
    read_cas_file,
    parse_chunk_selection,
)

__version__ = "0.1.3"
__author__ = "Claude.ai Sonnet 4.5 - Prompted by Aykut Kılıç"
__license__ = "MIT"

__all__ = [
    "CASReader",
    "Chunk",
    "ChunkHeader",
    "ChunkType",
    "read_cas_file",
    "parse_chunk_selection",
]
