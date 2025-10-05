# PyCAS - Python CAS File Reader

A pure Python library for reading and converting Atari 8-bit cassette (CAS) files. This library provides comprehensive support for the CAS file format as defined in the [A8CAS specification](https://a8cas.sourceforge.net/format-cas.html).

## Features

- **Pure Python**: Compatible with Python 3.x, no external dependencies
- **Complete CAS format support**: Handles all chunk types (FUJI, baud, data, fsk, pwms, pwmc, pwmd, pwml)
- **Binary conversion**: Extract data chunks to binary (.bin) files
- **Flexible dumping**: View chunk contents in hex, ASCII, or both formats
- **Chunk selection**: Dump specific chunks or ranges
- **Metadata extraction**: Read tape descriptions and baudrate information
- **CLI tool**: Command-line interface for file inspection and conversion

## Installation

### From PyPI

```bash
pip install atari-cas-reader
```

### From source

```bash
git clone https://github.com/yourusername/pycas.git
cd pycas
pip install -e .
```

## Quick Start

### As a Library

```python
from pycas import CASReader, read_cas_file

# Simple usage - get data and metadata
byte_array, metadata = read_cas_file('tape.cas')
print(f"Description: {metadata['description']}")
print(f"Baudrate: {metadata['baudrate']}")
print(f"Data size: {len(byte_array)} bytes")

# Advanced usage with CASReader class
reader = CASReader('tape.cas')
reader.read()

# Get metadata
metadata = reader.get_metadata()
print(f"Chunks: {metadata['chunk_count']}")

# Get chunk information
for chunk_info in reader.get_chunk_info():
    print(f"[{chunk_info['index']}] {chunk_info['type']}: {chunk_info['length']} bytes")

# Extract data to byte array
data = reader.to_byte_array()

# Convert to binary file
reader.to_bin_file('output.bin')

# Get individual data blocks
for i, block in enumerate(reader.get_data_blocks()):
    print(f"Block {i}: {len(block)} bytes")

# Dump chunks in hex format
print(reader.dump_chunks(chunk_indices=[0, 1], show_hex=True, show_ascii=True))
```

### Command-Line Interface

#### Show file information (default)

```bash
python -m pycas tape.cas
```

Output:
```
CAS File: tape.cas

Metadata:
  description: My Atari Program
  baudrate: 600
  chunk_count: 5
  data_block_count: 3

Chunks:
  [0] FUJI: 16 bytes (aux: 0)
  [1] baud: 2 bytes (aux: 0)
  [2] data: 132 bytes (aux: 0)
  [3] data: 132 bytes (aux: 0)
  [4] data: 64 bytes (aux: 0)

Total data bytes: 328
```

#### Convert to binary file

```bash
python -m pycas tape.cas --to-bin output.bin
```

#### Dump chunks in hex format

```bash
# Dump all chunks (hex only, default)
python -m pycas tape.cas dump

# Dump all chunks with both hex and ASCII
python -m pycas tape.cas dump --hex --ascii

# Dump specific chunk
python -m pycas tape.cas dump --chunk 0 --hex --ascii

# Dump chunk range
python -m pycas tape.cas dump --chunk 2-4 --hex --ascii

# Dump multiple chunks and ranges
python -m pycas tape.cas dump --chunk 0,2,5-7 --hex --ascii

# Dump ASCII only
python -m pycas tape.cas dump --ascii
```

Example dump output:
```
Chunk [2] Type: data, Length: 132, Aux: 0
--------------------------------------------------------------------------------
0000: 55 55 55 55 55 55 55 55 55 55 55 55 55 55 55 55 | UUUUUUUUUUUUUUUU
0010: 7f 7f 7f 00 01 02 03 04 05 06 07 08 09 0a 0b 0c | ................
0020: 48 45 4c 4c 4f 20 57 4f 52 4c 44 21 9b 00 00 00 | HELLO WORLD!....
```

## CAS File Format

The CAS format stores Atari 8-bit cassette data as a series of chunks. Each chunk has:

- **Header** (8 bytes):
  - Chunk type (4 bytes, ASCII)
  - Length (2 bytes, little-endian)
  - Auxiliary data (2 bytes, little-endian)
- **Data** (variable length)

### Supported Chunk Types

- `FUJI`: Tape description (UTF-8 text)
- `baud`: Transmission baudrate (default: 600 baud)
- `data`: Standard SIO record (typically 132 bytes)
- `fsk `: Non-standard FSK signal lengths
- `pwms`: Turbo transmission settings
- `pwmc`: Turbo synchronization signals
- `pwmd`: Turbo data block
- `pwml`: Raw PWM state sequence

## API Reference

### CASReader Class

#### Methods

- `read()`: Parse the CAS file and load all chunks
- `to_byte_array() -> bytearray`: Extract all data chunks into a single byte array
- `to_bin_file(output_path: str) -> int`: Write data chunks to binary file, returns bytes written
- `get_all_chunks_as_bytes() -> bytearray`: Convert entire CAS file (including headers) to byte array
- `get_metadata() -> dict`: Extract metadata (description, baudrate, chunk counts)
- `get_data_blocks() -> List[bytes]`: Get list of all data chunk contents
- `get_chunk_info() -> List[dict]`: Get information about all chunks
- `dump_chunks(chunk_indices=None, show_hex=True, show_ascii=False) -> str`: Format chunk contents for display

#### Properties

- `filepath`: Path to the CAS file
- `chunks`: List of parsed Chunk objects
- `data_blocks`: List of data chunk contents

### Chunk Class

Dataclass representing a CAS chunk:

- `header: ChunkHeader`: Chunk header information
- `data: bytes`: Chunk data payload

### ChunkHeader Class

Dataclass representing chunk header:

- `chunk_type: bytes`: 4-byte chunk type identifier
- `length: int`: Length of chunk data
- `aux_data: int`: Auxiliary/metadata value

### Utility Functions

- `read_cas_file(filepath: str) -> Tuple[bytearray, dict]`: Convenience function returning data and metadata
- `parse_chunk_selection(chunk_spec: str, max_chunks: int) -> List[int]`: Parse chunk selection string

## Examples

### Extract program data

```python
from pycas import CASReader

reader = CASReader('program.cas')
reader.read()

# Save just the data chunks to binary
reader.to_bin_file('program.bin')
print(f"Extracted {len(reader.to_byte_array())} bytes")
```

### Analyze tape structure

```python
from pycas import CASReader

reader = CASReader('tape.cas')
reader.read()

print("Tape Analysis")
print("=" * 60)

metadata = reader.get_metadata()
print(f"Description: {metadata['description']}")
print(f"Baudrate: {metadata['baudrate']}")
print(f"\nChunk Structure:")

for info in reader.get_chunk_info():
    print(f"  [{info['index']:2d}] {info['type']:4s} - "
          f"{info['length']:4d} bytes (aux: {info['aux_data']})")

total_size = sum(chunk.header.length for chunk in reader.chunks)
print(f"\nTotal payload: {total_size} bytes")
```

### Dump specific chunks

```python
from pycas import CASReader, parse_chunk_selection

reader = CASReader('tape.cas')
reader.read()

# Parse user input like "0,2-5,7"
chunks = parse_chunk_selection("0,2-5,7", len(reader.chunks))

# Dump with hex and ASCII
output = reader.dump_chunks(chunks, show_hex=True, show_ascii=True)
print(output)
```

## Development

### Building from source

```bash
# Clone repository
git clone https://github.com/yourusername/pycas.git
cd pycas

# Install in development mode
pip install -e .

# Run tests (if available)
python -m pytest
```

### Building for PyPI

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Upload to PyPI (requires credentials)
python -m twine upload dist/*
```

## Requirements

- Python >= 3.6
- No external dependencies

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## References

- [A8CAS File Format Specification](https://a8cas.sourceforge.net/format-cas.html)
- [Atari 8-bit Cassette System](https://en.wikipedia.org/wiki/Atari_8-bit_family)

## Author

Aykut Kılıç

## Changelog

### 0.1.0 (2025-01-XX)

- Initial release
- CAS file reading and parsing
- Binary conversion support
- Hex/ASCII dump functionality
- Command-line interface
- Complete chunk type support
