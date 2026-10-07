#!/usr/bin/env python3
"""Static CK3 compatibility checks; never launches the game.

Model the file overlay first, then inspect registries. Duplicate keys in distinct
files remain ambiguous and are reported, rather than assuming a winning file.
"""
import argparse
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEX = re.compile(r'\s+|#[^\n]*|"(?:\\.|[^"\\])*"|[{}]|[=<>!]+|[^\s{}#"=<>!]+')
CATEGORIES = ('culture/cultures', 'culture/pillars', 'culture/name_lists',
              'culture/traditions', 'culture/innovations', 'ethnicities')
VISUALS = {'ethnicities', 'coa_gfx', 'building_gfx', 'clothing_gfx', 'unit_gfx',
           'house_coa_frame', 'house_coa_mask_offset', 'house_coa_mask_scale'}


def lex(source):
    return [m for m in LEX.finditer(source) if not m.group().isspace()
            and not m.group().startswith('#') and m.group() != '\ufeff']


def entries(source):
    """Return top-level assignments with exact spans, handling adjacent '='."""
    ts = lex(source)
    result = []
    i = 0
    while i < len(ts):
        if i + 2 >= len(ts) or ts[i + 1].group() != '=':
            raise ValueError(f'Expected assignment near {ts[i].group()!r}')
        key = ts[i].group()
        j = i + 2
        if ts[j].group() == '{':
            depth = 1
            j += 1
            body_start = ts[j - 1].end()
            while j < len(ts) and depth:
                if ts[j].group() == '{':
                    depth += 1
                elif ts[j].group() == '}':
                    depth -= 1
                j += 1
            if depth:
                raise ValueError(f'Unclosed block: {key}')
            body = source[body_start:ts[j - 1].start()]
        else:
            body = ts[j].group()
            j += 1
        result.append((key, body, ts[i].start(), ts[j - 1].end()))
        i = j
    return result


def canonical(source):
    return [m.group() for m in lex(source)]


def registry_files(layers, category):
    files = {}
    for root in layers:
        for p in sorted((root / 'common' / category).glob('*.txt')):
            files[p.name] = p
    return files


def registry(layers, category):
    result = collections.defaultdict(list)
    for p in registry_files(layers, category).values():
        for key, body, _, _ in entries(p.read_text(encoding='utf-8-sig')):
            result[key].append((p, body))
    return result


def audit(layers, patch_roots):
    errors = []
    regs = {c: registry(layers, c) for c in CATEGORIES}
    rice_cultures = set(registry([layers[1]], 'culture/cultures'))
    rice_pillars = set(registry([layers[1]], 'culture/pillars'))
    for category, relevant in [('culture/cultures', rice_cultures),
                               ('culture/pillars', rice_pillars)]:
        for key in sorted(relevant):
            definitions = regs[category].get(key, [])
            if len(definitions) != 1:
                errors.append({'registry': category, 'key': key,
                               'definitions': [str(p.relative_to(root)) if p.is_relative_to(root) else p.name
                                               for p, _ in definitions for root in [ROOT]]})
    count = 0
    for key, definitions in regs['culture/cultures'].items():
        for p, body in definitions:
            if not any(p.is_relative_to(root) for root in patch_roots):
                continue
            count += 1
            for field, value, _, _ in entries(body):
                cat = 'culture/pillars' if field in ('heritage', 'language', 'ethos', 'martial_custom') else 'culture/name_lists' if field == 'name_list' else None
                refs = [value] if cat else []
                if field == 'traditions':
                    cat, refs = 'culture/traditions', canonical(value)
                if field == 'ethnicities':
                    cat = 'ethnicities'
                    refs = [v for _, v, _, _ in entries(value)]
                if field == 'parents':
                    cat, refs = 'culture/cultures', canonical(value)
                if field == 'dlc_tradition':
                    cat = 'culture/traditions'
                    refs = [v for f, v, _, _ in entries(value) if f in ('trait', 'fallback')]
                for ref in refs:
                    if ref not in regs[cat]:
                        errors.append({'culture': key, 'field': field, 'unresolved': ref, 'file': p.name})
    # Restored Oceania pillars require the normal startup innovation grants.
    gates = registry(layers, 'scripted_triggers').get('is_RICE_CE_temp_compatch_loaded', [])
    if len(gates) != 1 or canonical(gates[0][1]) != ['always', '=', 'no']:
        errors.append({'startup_gate': 'is_RICE_CE_temp_compatch_loaded', 'error': 'legacy gate would suppress restored Oceania initialization'})
    innovation_count = 0
    for p in registry_files(layers, 'culture/innovations').values():
        if not any(p.is_relative_to(root) for root in patch_roots):
            continue
        innovation_count += 1
        for ref in re.findall(r'\bhas_cultural_pillar\s*=\s*([A-Za-z0-9_]+)', ' '.join(canonical(p.read_text(encoding='utf-8-sig')))):
            if ref not in regs['culture/pillars']:
                errors.append({'innovation_file': p.name, 'unresolved_pillar': ref})
    return {'errors': errors, 'patched_cultures_checked': count, 'innovation_files_checked': innovation_count,
            'rice_cultures': len(rice_cultures), 'rice_pillars': len(rice_pillars),
            'ethnicities': len(regs['ethnicities'])}


def compare(repo, local):
    if local is None:
        return {'installed': False, 'note': 'No installed CE patch was found; repository baseline audited instead.'}
    a = {p.relative_to(repo).as_posix(): p for p in repo.rglob('*') if p.is_file()}
    b = {p.relative_to(local).as_posix(): p for p in local.rglob('*') if p.is_file()}
    result = {'installed': True, 'repo_only': sorted(a.keys() - b.keys()),
              'local_only': sorted(b.keys() - a.keys()), 'byte_differences': [], 'script_differences': []}
    for key in sorted(a.keys() & b.keys()):
        if a[key].read_bytes() != b[key].read_bytes():
            result['byte_differences'].append(key)
            if a[key].suffix in ('.txt', '.mod', '.gui') and canonical(a[key].read_text(encoding='utf-8-sig')) != canonical(b[key].read_text(encoding='utf-8-sig')):
                result['script_differences'].append(key)
    return result


def fingerprint(root):
    digest = hashlib.sha256()
    count = 0
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.suffix in ('.txt', '.mod', '.gui', '.yml'):
            digest.update(p.relative_to(root).as_posix().encode())
            digest.update(p.read_bytes())
            count += 1
    return {'files': count, 'sha256': digest.hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('game', 'rice', 'ce', 'epe', 'local-epe-patch'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--local-ce-patch', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/compatch-validation.json')
    args = parser.parse_args()
    ce_patch, epe_patch = ROOT / 'RICE+CE Compatch for 1.19', ROOT / 'RICE-EPE-Compatch'
    structure = []
    for root in (ce_patch, epe_patch):
        for p in root.rglob('*.txt'):
            try:
                entries(p.read_text(encoding='utf-8-sig'))
            except ValueError as e:
                structure.append({'file': str(p.relative_to(ROOT)), 'error': str(e)})
    profiles = {}
    for name, rice in [('local_modified', args.rice), ('expanded', ROOT / 'RICE')]:
        profiles[name + '_epe'] = audit([args.game, rice, args.epe, epe_patch], [epe_patch])
        profiles[name + '_ce_epe'] = audit([args.game, rice, args.epe, args.ce, epe_patch, ce_patch], [epe_patch, ce_patch])
    # Appearance-only EPE overrides must not silently roll back local RICE gameplay.
    gameplay = []
    local_defs = registry([args.rice], 'culture/cultures')
    for key, defs in registry([epe_patch, ce_patch], 'culture/cultures').items():
        if key not in local_defs:
            gameplay.append({'culture': key, 'error': 'not in local RICE'})
            continue
        def fields(body):
            return [(k, canonical(v)) for k, v, _, _ in entries(body) if k not in VISUALS]
        if fields(defs[0][1]) != fields(local_defs[key][0][1]):
            gameplay.append({'culture': key, 'error': 'patch override changes local gameplay fields'})
    preservation = []
    ce_defs = {cat: registry([args.ce], cat) for cat in ('culture/cultures', 'culture/pillars')}
    effective = {cat: registry([args.game, args.rice, args.epe, args.ce, epe_patch, ce_patch], cat) for cat in ce_defs}
    for cat, definitions in ce_defs.items():
        for key in set(definitions) & set(registry([args.rice], cat)):
            actual = effective[cat].get(key, [])
            if len(actual) == 1 and not any(canonical(actual[0][1]) == canonical(b) for _, b in definitions[key]):
                preservation.append({'registry': cat, 'key': key, 'error': 'CE content/CCU metadata changed'})
    workshop_visuals = registry([args.local_epe_patch], 'culture/cultures')
    for key, defs in registry([epe_patch], 'culture/cultures').items():
        def appearance(body):
            return [(k, canonical(v)) for k, v, _, _ in entries(body) if k in VISUALS]
        if key in workshop_visuals and appearance(defs[0][1]) != appearance(workshop_visuals[key][0][1]):
            preservation.append({'culture': key, 'error': 'EPE appearance changed'})
    report = {'preservation_errors': preservation, 'structure_errors': structure, 'gameplay_errors': gameplay, 'profiles': profiles,
              'local_comparison': {'epe': compare(epe_patch, args.local_epe_patch), 'ce': compare(ce_patch, args.local_ce_patch)},
              'sources': {name: fingerprint(getattr(args, name)) for name in ('rice', 'ce', 'epe')},
              'limitations': ['No game was launched. Engine scopes, rendering, DNA genes and long campaigns are not runtime-verified.',
                              'Checks cover RICE culture/pillar uniqueness and references in effective patched cultures; unrelated CE/vanilla conflicts are outside this patch audit.',
                              'Installed CE still targets 1.19; these compatibility changes are not a full CE port to 1.20.']}
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    errors = len(preservation) + len(structure) + len(gameplay) + sum(len(p['errors']) for p in profiles.values())
    print(json.dumps({'errors': errors, 'profiles': {k: {'errors': len(v['errors']), 'cultures_checked': v['patched_cultures_checked']} for k,v in profiles.items()}, 'gameplay_errors': gameplay}, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
