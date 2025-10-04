"""
CAS File Reader for Atari 8-bit Cassette Files
Pure Python implementation for reading CAS files and converting to byte arrays.
"""

import struct
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ChunkType(Enum):
    """CAS file chunk types"""
    FUJI = b'FUJI'  # Tape description
    BAUD = b'baud'  # Transmission baudrate
    DATA = b'data'  # Standard SIO record
    FSK = b'fsk '   # Non-standard signal lengths
    PWMS = b'pwms'  # Turbo transmission settings
    PWMC = b'pwmc'  # Turbo synchronization signals
    PWMD = b'pwmd'  # Turbo data block
    PWML = b'pwml'  # Raw PWM state sequence


@dataclass
class ChunkHeader:
    """CAS chunk header structure (8 bytes)"""
    chunk_type: bytes  # 4-byte chunk type
    length: int        # 2-byte chunk length (little-endian)
    aux_data: int      # 2-byte auxiliary data (little-endian)


@dataclass
class Chunk:
    """Complete CAS chunk with header and data"""
    header: ChunkHeader
    data: bytes


class CASReader:
    """Reader for CAS (Atari 8-bit cassette) files"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.chunks: List[Chunk] = []
        self.data_blocks: List[bytes] = []

    def read(self) -> None:
        """Read and parse the CAS file"""
        with open(self.filepath, 'rb') as f:
            file_data = f.read()

        offset = 0
        while offset < len(file_data):
            # Read chunk header (8 bytes)
            if offset + 8 > len(file_data):
                break

            chunk_type = file_data[offset:offset+4]
            length = struct.unpack('<H', file_data[offset+4:offset+6])[0]
            aux_data = struct.unpack('<H', file_data[offset+6:offset+8])[0]

            header = ChunkHeader(chunk_type, length, aux_data)
            offset += 8

            # Read chunk data
            if offset + length > len(file_data):
                break

            chunk_data = file_data[offset:offset+length]
            offset += length

            chunk = Chunk(header, chunk_data)
            self.chunks.append(chunk)

            # Extract data blocks from 'data' chunks
            if chunk_type == ChunkType.DATA.value:
                self.data_blocks.append(chunk_data)

    def to_byte_array(self) -> bytearray:
        """Convert all data chunks to a single byte array"""
        result = bytearray()

        for chunk in self.chunks:
            if chunk.header.chunk_type == ChunkType.DATA.value:
                result.extend(chunk.data)

        return result

    def get_all_chunks_as_bytes(self) -> bytearray:
        """Convert entire CAS file (all chunks) to byte array"""
        result = bytearray()

        for chunk in self.chunks:
            # Add header
            result.extend(chunk.header.chunk_type)
            result.extend(struct.pack('<H', chunk.header.length))
            result.extend(struct.pack('<H', chunk.header.aux_data))
            # Add data
            result.extend(chunk.data)

        return result

    def get_metadata(self) -> Dict:
        """Extract metadata from CAS file"""
        metadata = {
            'description': None,
            'baudrate': 600,  # default
            'chunk_count': len(self.chunks),
            'data_block_count': len(self.data_blocks)
        }

        for chunk in self.chunks:
            if chunk.header.chunk_type == ChunkType.FUJI.value:
                try:
                    metadata['description'] = chunk.data.decode('utf-8')
                except UnicodeDecodeError:
                    metadata['description'] = chunk.data.decode('latin-1', errors='ignore')
            elif chunk.header.chunk_type == ChunkType.BAUD.value:
                if len(chunk.data) >= 2:
                    metadata['baudrate'] = struct.unpack('<H', chunk.data[:2])[0]

        return metadata

    def get_data_blocks(self) -> List[bytes]:
        """Get list of all data blocks"""
        return self.data_blocks.copy()

    def get_chunk_info(self) -> List[Dict]:
        """Get information about all chunks"""
        info = []
        for i, chunk in enumerate(self.chunks):
            chunk_info = {
                'index': i,
                'type': chunk.header.chunk_type.decode('ascii', errors='ignore'),
                'length': chunk.header.length,
                'aux_data': chunk.header.aux_data
            }
            info.append(chunk_info)
        return info

    def to_bin_file(self, output_path: str) -> int:
        """
        Convert data chunks to binary file

        Args:
            output_path: Path to output .bin file

        Returns:
            Number of bytes written
        """
        byte_array = self.to_byte_array()
        with open(output_path, 'wb') as f:
            f.write(byte_array)
        return len(byte_array)

    def dump_chunks(self, chunk_indices: Optional[List[int]] = None,
                    show_hex: bool = True, show_ascii: bool = False) -> str:
        """
        Dump chunk contents in hex and/or ASCII format

        Args:
            chunk_indices: List of chunk indices to dump (None = all chunks)
            show_hex: Show hex output
            show_ascii: Show ASCII output

        Returns:
            Formatted dump string
        """
        if chunk_indices is None:
            chunk_indices = list(range(len(self.chunks)))

        output_lines = []

        for idx in chunk_indices:
            if idx < 0 or idx >= len(self.chunks):
                continue

            chunk = self.chunks[idx]
            chunk_type = chunk.header.chunk_type.decode('ascii', errors='replace')

            # Chunk header
            output_lines.append(f"Chunk [{idx}] Type: {chunk_type}, Length: {chunk.header.length}, Aux: {chunk.header.aux_data}")
            output_lines.append("-" * 80)

            # Dump data
            data = chunk.data
            if len(data) == 0:
                output_lines.append("  (empty)")
            else:
                for offset in range(0, len(data), 16):
                    line_data = data[offset:offset+16]

                    # Build line
                    line_parts = [f"{offset:04x}:"]

                    if show_hex:
                        hex_part = ' '.join(f'{b:02x}' for b in line_data)
                        # Pad to align ASCII section
                        hex_part = hex_part.ljust(48)
                        line_parts.append(hex_part)

                    if show_ascii:
                        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line_data)
                        if show_hex:
                            line_parts.append('|')
                        line_parts.append(ascii_part)

                    output_lines.append(' '.join(line_parts))

            output_lines.append("")  # Blank line between chunks

        return '\n'.join(output_lines)


def parse_chunk_selection(chunk_spec: str, max_chunks: int) -> List[int]:
    """
    Parse chunk selection specification into list of indices

    Args:
        chunk_spec: Chunk specification (e.g., "0", "1,3,5", "0-5", "1,3-7,10")
        max_chunks: Maximum number of chunks available

    Returns:
        List of chunk indices
    """
    if not chunk_spec:
        return list(range(max_chunks))

    indices = set()
    parts = chunk_spec.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            # Range: "0-5"
            start, end = part.split('-', 1)
            start_idx = int(start.strip())
            end_idx = int(end.strip())
            for i in range(start_idx, end_idx + 1):
                if 0 <= i < max_chunks:
                    indices.add(i)
        else:
            # Single index: "3"
            idx = int(part)
            if 0 <= idx < max_chunks:
                indices.add(idx)

    return sorted(list(indices))


def read_cas_file(filepath: str) -> Tuple[bytearray, Dict]:
    """
    Convenience function to read a CAS file and return byte array and metadata

    Args:
        filepath: Path to the CAS file

    Returns:
        Tuple of (byte_array, metadata_dict)
    """
    reader = CASReader(filepath)
    reader.read()
    return reader.to_byte_array(), reader.get_metadata()


def main():
    """Main entry point for console script"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description='CAS File Reader - Read and convert Atari 8-bit cassette files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show file info
  pycas file.cas --info

  # Convert to binary
  pycas file.cas --to-bin output.bin

  # Dump all chunks (hex only)
  pycas file.cas dump --hex

  # Dump all chunks (hex + ASCII)
  pycas file.cas dump --hex --ascii

  # Dump specific chunks
  pycas file.cas dump --chunk 0,2,5-7 --hex --ascii

  # Dump in ASCII only
  pycas file.cas dump --ascii
        """)

    parser.add_argument('input', help='Input CAS file')
    parser.add_argument('--info', action='store_true', help='Show file info and metadata (default if no other action)')
    parser.add_argument('--to-bin', metavar='OUTPUT', help='Convert data chunks to binary file')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Dump subcommand
    dump_parser = subparsers.add_parser('dump', help='Dump chunk contents')
    dump_parser.add_argument('--chunk', help='Chunk selection (e.g., "0", "1,3,5", "0-5", "1,3-7,10")')
    dump_parser.add_argument('--hex', action='store_true', help='Show hex output')
    dump_parser.add_argument('--ascii', action='store_true', help='Show ASCII output')

    args = parser.parse_args()

    # Read CAS file
    reader = CASReader(args.input)
    try:
        reader.read()
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle commands
    if args.command == 'dump':
        # Parse chunk selection
        chunk_indices = None
        if args.chunk:
            try:
                chunk_indices = parse_chunk_selection(args.chunk, len(reader.chunks))
            except ValueError as e:
                print(f"Error parsing chunk selection: {e}", file=sys.stderr)
                sys.exit(1)

        # Default to hex if neither specified
        show_hex = args.hex
        show_ascii = args.ascii
        if not show_hex and not show_ascii:
            show_hex = True

        # Dump chunks
        output = reader.dump_chunks(chunk_indices, show_hex, show_ascii)
        print(output)

    elif args.to_bin:
        # Convert to binary
        try:
            bytes_written = reader.to_bin_file(args.to_bin)
            print(f"Wrote {bytes_written} bytes to {args.to_bin}")
        except Exception as e:
            print(f"Error writing binary file: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        # Default: show info
        print(f"CAS File: {args.input}")
        print(f"\nMetadata:")
        metadata = reader.get_metadata()
        for key, value in metadata.items():
            print(f"  {key}: {value}")

        print(f"\nChunks:")
        for chunk_info in reader.get_chunk_info():
            print(f"  [{chunk_info['index']}] {chunk_info['type']}: {chunk_info['length']} bytes (aux: {chunk_info['aux_data']})")

        byte_array = reader.to_byte_array()
        print(f"\nTotal data bytes: {len(byte_array)}")


if __name__ == '__main__':
    main()
