#!/usr/bin/env python3
"""Verify the rite's native tenets without overriding vanilla definitions."""
import argparse
import hashlib
import json
from pathlib import Path
from ck3_script import registry

ROOT = Path(__file__).resolve().parents[1]

def main():
 parser = argparse.ArgumentParser()
 parser.add_argument('--game', type=Path, required=True)
 args = parser.parse_args()
 native = registry([args.game], 'common/religion/tenet_types')
 required = {'tenet_aniconism', 'tenet_communal_possessions', 'tenet_asceticism', 'tenet_miaphysitism'}
 assert required <= set(native), sorted(required - set(native))
 assert not list((ROOT / 'common/religion/tenet_types').glob('*.txt')), 'Rite must not override native tenets'
 report = {
  'native_tenet_count': len(native),
  'required_native_tenets': sorted(required),
  'native_mechanics_unchanged': True,
  'native_tenet_overrides': [],
  'source_files_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((args.game / 'common/religion/tenet_types').glob('*.txt'))},
 }
 target = ROOT / 'research/tondrakian-tenet-validation.json'
 target.write_text(json.dumps(report, indent=2) + '\n')
 print(json.dumps({'native_tenet_count': len(native), 'native_tenet_overrides': []}))

if __name__ == '__main__':
 main()
