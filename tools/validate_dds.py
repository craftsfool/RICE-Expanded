#!/usr/bin/env python3
"""Check DDS header dimensions, mip counts and minimum payload lengths."""
import argparse
import json
import struct
from pathlib import Path

BLOCK_BYTES = {b'DXT1': 8, b'DXT3': 16, b'DXT5': 16}
DXGI_BLOCK_BYTES = {71: 8, 72: 8, 74: 16, 75: 16, 77: 16, 78: 16,
                    80: 8, 81: 8, 83: 16, 84: 16, 95: 16, 96: 16,
                    98: 16, 99: 16}
DXGI_PIXEL_BYTES = {28: 4, 29: 4, 87: 4, 91: 4}


def check_file(path):
    with path.open('rb') as stream:
        header = stream.read(148)
    if len(header) < 128 or header[:4] != b'DDS ':
        raise ValueError('Missing DDS header')
    field = lambda offset: struct.unpack_from('<I', header, offset)[0]
    if field(4) != 124 or field(76) != 32:
        raise ValueError('Invalid DDS header or pixel-format size')
    height, width = field(12), field(16)
    depth = max(1, field(24)) if field(112) & 0x200000 else 1
    mips = max(1, field(28))
    if not width or not height:
        raise ValueError('Zero texture dimension')
    maximum = max(width, height, depth).bit_length()
    if mips > maximum:
        raise ValueError(f'{mips} mip levels declared; dimensions allow only {maximum}')
    fourcc = header[84:88]
    block_bytes = BLOCK_BYTES.get(fourcc)
    pixel_bytes = None
    header_bytes, copies = 128, 6 if field(112) & 0x200 else 1
    if fourcc == b'DX10':
        if len(header) < 148:
            raise ValueError('Missing DX10 header')
        header_bytes = 148
        dxgi, dimension, misc, array_size, _ = struct.unpack_from('<5I', header, 128)
        if not array_size:
            raise ValueError('Zero DX10 array size')
        copies = array_size * (6 if misc & 4 else 1)
        block_bytes = DXGI_BLOCK_BYTES.get(dxgi)
        pixel_bytes = DXGI_PIXEL_BYTES.get(dxgi)
        if dimension != 4:
            depth = 1
    elif fourcc == b'\0\0\0\0':
        bits = field(88)
        if not bits or bits % 8:
            raise ValueError(f'Unsupported RGB bit count: {bits}')
        pixel_bytes = bits // 8
    if block_bytes is None and pixel_bytes is None:
        raise ValueError(f'Unsupported DDS format: {fourcc!r}')
    payload = 0
    for level in range(mips):
        w, h, d = max(1, width >> level), max(1, height >> level), max(1, depth >> level)
        if block_bytes:
            payload += max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * d * block_bytes
        else:
            payload += w * h * d * pixel_bytes
    required = header_bytes + payload * copies
    actual = path.stat().st_size
    if actual < required:
        raise ValueError(f'Truncated DDS: {actual} bytes available; {required} required')
    return {'width': width, 'height': height, 'mips': mips, 'bytes': actual}


def audit(root):
    errors = []
    paths = sorted(root.rglob('*.dds'))
    for path in paths:
        try:
            check_file(path)
        except (ValueError, struct.error) as error:
            errors.append({'file': str(path.relative_to(root)), 'error': str(error)})
    return {'checked': len(paths), 'errors': errors,
            'limitations': ['Header and payload checks do not validate GPU decoding or engine behavior.']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit(args.root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return bool(report['errors'])


if __name__ == '__main__':
    raise SystemExit(main())
