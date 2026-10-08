#!/usr/bin/env python3
"""Keep native tenet mechanics; select the vanilla Righteous Rebellion label for this rite."""
import argparse, hashlib, json
from pathlib import Path
from ck3_script import entries, canonical, write
ROOT = Path(__file__).resolve().parents[1]

def main():
 ap = argparse.ArgumentParser()
 ap.add_argument('--game', type=Path, required=True)
 args = ap.parse_args()
 source = args.game/'common/religion/tenet_types/00_tenet_types.txt'
 text = source.read_text(encoding='utf-8-sig')
 original = {key: canonical(body) for key, body, _, _ in entries(text)}
 for key, body, start, end in entries(text):
  if key != 'tenet_unrelenting_faith':
   continue
  for field, value, a, z in reversed(entries(body)):
   if field not in ('name', 'desc'):
    continue
   label = 'tenet_unrelenting_faith_zandik_' + field
   insertion = '\n triggered_desc = { trigger = { exists = rite:CAUC_tondrakian_rite this ?= rite:CAUC_tondrakian_rite } desc = ' + label + ' }\n'
   assert value.count('first_valid') == 1
   marker = value.index('{', value.index('first_valid')) + 1
   value = value[:marker] + insertion + value[marker:]
   body = body[:a] + field + ' = {' + value + '}' + body[z:]
  text = text[:start] + key + ' = {' + body + '}' + text[end:]
  break
 else:
  raise ValueError('Native Unrelenting Faith tenet is missing')
 actual = {key: canonical(body) for key, body, _, _ in entries(text)}
 assert set(original) == set(actual)
 assert all(original[key] == actual[key] for key in original if key != 'tenet_unrelenting_faith')
 # All mechanical fields on this tenet must remain byte-equivalent in tokens.
 before = next(body for k, body, _, _ in entries(source.read_text(encoding='utf-8-sig')) if k == 'tenet_unrelenting_faith')
 after = next(body for k, body, _, _ in entries(text) if k == 'tenet_unrelenting_faith')
 fields = lambda s: [(k, canonical(v)) for k, v, _, _ in entries(s) if k not in ('name', 'desc')]
 assert fields(before) == fields(after)
 target = ROOT/'common/religion/tenet_types/00_tenet_types.txt'
 write(target, '# Vanilla tenets, with a rite-specific name/description selection only.\n' + text)
 report = {'source': str(source), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'modified_tenet': 'tenet_unrelenting_faith', 'changed_fields': ['name', 'desc'], 'native_mechanics_unchanged': True, 'other_native_tenets_unchanged': True, 'native_tenet_count': len(original)}
 (ROOT/'research/tondrakian-tenet-validation.json').write_text(json.dumps(report, indent=2) + '\n')
 print(json.dumps(report))

if __name__ == '__main__':
 main()
