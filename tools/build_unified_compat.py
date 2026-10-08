#!/usr/bin/env python3
"""Build self-contained compatibility data, without mandatory CE/EPE mods.

The CE files that share RICE keys are embedded under their original filenames.
That supplies each shared database key exactly once with or without CE loaded.
Files needed by those records are included transitively. Native appearance
definitions keep the same package usable without EPE's asset database.
"""
import argparse, collections, hashlib, json, os, re, shutil
from pathlib import Path
import validate_compatches as v
from validate_expanded import localization, LANGUAGES

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ['culture/pillars', 'culture/cultures', 'culture/name_lists',
              'culture/traditions', 'script_values', 'men_at_arms_types']
VISUALS = v.VISUALS

def records(root, cat):
    result = collections.defaultdict(list)
    for p in sorted((root/'common'/cat).glob('*.txt')):
        text = p.read_text(encoding='utf-8-sig')
        if cat=='script_values':
            starts=list(re.finditer(r'^([A-Za-z_]\w*)\s*=\s*',text,re.M))
            for i,m in enumerate(starts):
                end=starts[i+1].start() if i+1<len(starts) else len(text)
                result[m.group(1)].append((p.name,text[m.end():end],text[m.start():end]))
            continue
        for key, body, start, end in v.entries(text):
            if key.startswith('@'): continue  # File-local constants, not objects.
            result[key].append((p.name, body, text[start:end]))
    return result

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and v.canonical(path.read_text(encoding='utf-8-sig'))==v.canonical(text):
        return  # Preserve comments in unchanged user-modified RICE files.
    if path.exists(): path.unlink()  # Source assets may be hard linked.
    path.write_text('\ufeff'+text.rstrip()+'\n', encoding='utf-8')

def consolidate_script_collisions(out_root,ce_root,report):
    cases=[('scripted_rules','00_rules.txt','00_rules_ce_overwrite.txt',{'can_diverge_culture','can_hybridize_culture'}),
           ('scripted_triggers','00_cultural_triggers.txt','00_cultural_triggers_ce_overwrite.txt',{'is_valid_for_hybridising_trigger'}),
           ('game_concepts','CAUC_CE_common_game_concepts.txt','ce_game_concepts.txt',{'bp_monolithic_culture_tradition'})]
    for cat,old,new,keys in cases:
        original=out_root/'common'/cat/old
        text=original.read_text(encoding='utf-8-sig')
        owned={k:text[a:z] for k,b,a,z in v.entries(text) if k in keys}
        existing=out_root/'common'/cat/new
        if not owned and existing.exists():
            current=existing.read_text(encoding='utf-8-sig')
            owned={k:current[a:z] for k,b,a,z in v.entries(current) if k in keys}
        incoming=(ce_root/'common'/cat/new).read_text(encoding='utf-8-sig')
        for k,b,a,z in reversed(v.entries(incoming)):
            if k in owned:incoming=incoming[:a]+owned[k]+incoming[z:]
        for k,b,a,z in reversed(v.entries(text)):
            if k in keys:text=text[:a]+text[z:]
        write(original,text)
        write(existing,'# One authoritative definition with or without optional CE.\n'+incoming)
        report['files'][cat]=[old,new]

def original_localization(root,lang):
    values,_,_=localization(root,lang)
    # Generated output must not suppress its own source keys on the next build.
    return {key:item for key,item in values.items()
            if not Path(item['file']).name.startswith(('RICE_unified_compat_', 'CAUC_english_fallback_'))}

def supply_localization(rice_root,out_root,ce_root,game_root,files):
    # Supply labels and names referenced by the borrowed dependency records.
    # Existing authored translations and native terminology take precedence.
    ce_en,_,_=localization(ce_root/'localization','english')
    rice_en=original_localization(rice_root/'localization','english')
    native_en,_,_=localization(game_root/'localization','english')
    symbols=set()
    for cat,files in files.items():
        for filename in files:
            code=' '.join(v.canonical((out_root/'common'/cat/filename).read_text(encoding='utf-8-sig')))
            symbols.update(re.findall(r'\b[A-Za-z_]\w*\b',code))
    potential=set(symbols)
    for key in symbols:
        potential.update([key+'_name',key+'_desc',key+'_adj',key+'_prefix',key+'_collective_noun','culture_parameter_'+key,'game_concept_'+key,'game_concept_'+key+'_desc'])
    needed=(potential & set(ce_en))-set(rice_en)-set(native_en)
    for _ in range(10):
        refs={ref for key in needed for ref in re.findall(r'\$([A-Za-z_]\w*)\$',ce_en[key]['value'])}
        expanded=needed|((refs & set(ce_en))-set(rice_en)-set(native_en))
        if expanded==needed:break
        needed=expanded
    result={}
    for lang in LANGUAGES:
        ce_loc,_,_=localization(ce_root/'localization',lang)
        native_loc,_,_=localization(game_root/'localization',lang)
        rice_loc=original_localization(rice_root/'localization',lang)
        lines=['l_'+lang+':'];fallback=[]
        for key in sorted(needed):
            if key in rice_loc: continue
            item=native_loc.get(key) or ce_loc.get(key) or ce_en[key]
            lines.append(' '+key+':0 "'+item['value']+'"')
            if key not in ce_loc and key not in native_loc:fallback.append(key)
        write(out_root/'localization'/lang/('RICE_unified_compat_l_'+lang+'.yml'),'\n'.join(lines))
        result[lang]={'added_keys':len(lines)-1,'english_fallbacks':fallback}
    return result

def main():
    ap=argparse.ArgumentParser()
    for name in ['game','ce','rice-source','output']:
        ap.add_argument('--'+name, type=Path, required=True)
    ap.add_argument('--localization-only',action='store_true')
    a=ap.parse_args()
    if a.localization_only:
        report=json.loads((ROOT/'reports/unified-compatibility-build.json').read_text())
        consolidate_script_collisions(a.output,a.ce,report)
        report['localization']=supply_localization(a.rice_source,a.output,a.ce,a.game,report['files'])
        (ROOT/'reports/unified-compatibility-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({lang:row['added_keys'] for lang,row in report['localization'].items()}))
        return 0
    if a.output.exists(): raise SystemExit('Choose a new output directory.')
    shutil.copytree(a.rice_source, a.output, copy_function=os.link)
    base={cat:records(a.rice_source,cat) for cat in CATEGORIES}
    native={cat:records(a.game,cat) for cat in CATEGORIES}
    ce={cat:records(a.ce,cat) for cat in CATEGORIES}
    included={cat:set() for cat in CATEGORIES}
    # Start only with files that would collide with RICE's own keys.
    for cat in CATEGORIES[:3]:
        for key in set(base[cat]) & set(ce[cat]):
            included[cat].update(x[0] for x in ce[cat][key])
    report={'source':'Culture Expanded installed snapshot', 'files':{},
            'appearance_fallbacks':[], 'unresolved':[]}
    selected={}
    def select():
        for cat in CATEGORIES:
            current={key:rows[-1] for key,rows in native[cat].items()}
            for key,rows in ce[cat].items():
                active=[x for x in rows if x[0] in included[cat]]
                if active: current[key]=active[-1]
            # RICE gameplay and authored Caucasus definitions remain authoritative.
            for key,rows in base[cat].items():
                current[key]=rows[-1]
                if cat=='culture/pillars' and key in ce[cat]:
                    active=[x for x in ce[cat][key] if x[0] in included[cat]]
                    if active: current[key]=active[-1]
            selected[cat]=current
    def require(cat,key):
        if key in selected[cat]: return
        if key in ce[cat]: included[cat].update(x[0] for x in ce[cat][key])
        else: report['unresolved'].append({'category':cat,'key':key})
    for iteration in range(20):
        select();before={cat:set(files) for cat,files in included.items()}
        for cat in CATEGORIES[:3]:
            touched=set(included[cat])|{x[0] for rows in base[cat].values() for x in rows}
            for key,row in selected[cat].items():
                if row[0] in included[cat]: touched.update(x[0] for x in native[cat].get(key,[]))
            for key,rows in ce[cat].items():
                own=selected[cat].get(key)
                if own and own[0] in touched:
                    included[cat].update(x[0] for x in rows)
        for key,(filename,body,raw) in list(selected['culture/cultures'].items()):
            if key.startswith('@'): continue
            if filename not in included['culture/cultures'] and key not in base['culture/cultures']: continue
            for field,value,_,_ in v.entries(body):
                if field in ['heritage','language','ethos','martial_custom']:
                    require('culture/pillars',value)
                elif field=='name_list': require('culture/name_lists',value)
                elif field=='traditions':
                    for token in v.canonical(value): require('culture/traditions',token)
                elif field=='parents':
                    for token in v.canonical(value): require('culture/cultures',token)
                elif field=='dlc_tradition':
                    for f,token,_,_ in v.entries(value):
                        if f in ['trait','fallback']: require('culture/traditions',token)
        unlocks=set()
        for key,(filename,body,raw) in selected['culture/traditions'].items():
            if filename in included['culture/traditions'] or key in base['culture/traditions']:
                unlocks.update(re.findall(r'\bunlock_maa_\w+\b',' '.join(v.canonical(body))))
        for key,rows in ce['men_at_arms_types'].items():
            if key.startswith('@'): continue
            code=set(v.canonical(rows[-1][1]))
            if code & unlocks: require('men_at_arms_types',key)
        for cat in ['culture/pillars','culture/traditions','script_values','men_at_arms_types']:
            for key,(filename,body,raw) in list(selected[cat].items()):
                if filename not in included[cat]: continue
                code=' '.join(v.canonical(body))
                for ref in re.findall(r'\bhas_cultural_pillar\s*=\s*(\w+)',code):
                    require('culture/pillars',ref)
                for ref in re.findall(r'\b(?:multiply|add|subtract|divide|value|base)\s*=\s*([A-Za-z_]\w*)',code):
                    if ref in ce['script_values']: require('script_values',ref)
        if before==included: break
    else: raise SystemExit('Dependency closure did not converge.')
    select()
    optional_aliases={'culture/cultures':{'evenk':'evenk.txt'},'culture/name_lists':{'name_list_evenk':'00_evenk.txt'}}
    for cat,aliases in optional_aliases.items():
        for key,filename in aliases.items():
            if key in selected[cat]:
                row=selected[cat][key];selected[cat][key]=(filename,row[1],row[2])
    ethnicity=set(records(a.game,'ethnicities'))|set(records(a.rice_source,'ethnicities'))
    donors={k:row[-1][1] for k,row in native['culture/cultures'].items()}
    def safe_appearance(key,body,raw):
        if key.startswith('@'): return raw
        fields=v.entries(body);by_field={f:value for f,value,_,_ in fields}
        refs={value for _,value,_,_ in v.entries(by_field.get('ethnicities',''))}
        if refs<=ethnicity and key not in donors: return raw
        parent=next((p for p in v.canonical(by_field.get('parents','')) if p in donors),None)
        donor=(key if key in donors else None) or parent or next((k for k,b in donors.items() if any(f=='heritage' and value==by_field.get('heritage') for f,value,_,_ in v.entries(b))),None)
        donor=donor or next((k for k,b in donors.items() if any(f=='language' and value==by_field.get('language') for f,value,_,_ in v.entries(b))),None)
        donor=donor or 'armenian'
        safe={f:donors[donor][s:e] for f,value,s,e in v.entries(donors[donor]) if f in VISUALS}
        for field,value,s,e in reversed(fields):
            if field in VISUALS: body=body[:s]+safe.get(field,'')+body[e:]
        report['appearance_fallbacks'].append({'culture':key,'donor':donor})
        return key+' = {\n'+body+'\n}'
    # Place each record in its chosen source file. Mask other definitions using
    # whole files; do not leave a missing CE-owned object behind a dependency.
    for cat in CATEGORIES:
        touched=set(included[cat])|{p.name for p in (a.rice_source/'common'/cat).glob('*.txt')}
        touched.update(optional_aliases.get(cat,{}).values())
        # An embedded CE definition may override a native record in another file.
        for key,row in selected[cat].items():
            if row[0] in included[cat]: touched.update(x[0] for x in native[cat].get(key,[]))
        output=collections.defaultdict(list)
        for key,(filename,body,raw) in selected[cat].items():
            if filename not in touched: continue
            if cat=='culture/cultures': raw=safe_appearance(key,body,raw)
            if cat=='men_at_arms_types' and filename in included[cat]:
                raw=re.sub(r'\bicon\s*=\s*archers\b','icon = bowmen',raw)
            output[filename].append(raw)
        for filename in sorted(touched):
            constants={}
            for source in [a.game,a.ce,a.rice_source]:
                p=source/'common'/cat/filename
                if not p.exists():continue
                text=p.read_text(encoding='utf-8-sig')
                if cat=='script_values':
                    for m in re.finditer(r'^(@[A-Za-z_]\w*)\s*=[^\r\n]*',text,re.M):
                        constants[m.group(1)]=m.group(0)
                    continue
                for key,body,s,e in v.entries(text):
                    if key.startswith('@'): constants[key]=text[s:e]
            write(a.output/'common'/cat/filename,
                  '# RICE Expanded unified built-in compatibility; CE/EPE are optional.\n\n'+'\n'.join(constants.values())+'\n\n'+'\n\n'.join(output[filename]))
        report['files'][cat]=sorted(touched)
    report['unresolved']=sorted({(r['category'],r['key']) for r in report['unresolved'] if r['key'] not in selected[r['category']]})
    for cat in CATEGORIES[:3]:
        for layers in [[a.game,a.output],[a.game,a.ce,a.output]]:
            reg=v.registry(layers,cat)
            for key in records(a.output,cat):
                if len(reg[key])!=1: raise SystemExit(f'Duplicate {cat}: {key}')
    # All CE-only geography lives in this distinct file. Include it so borrowed
    # tradition requirements have real regions even when CE is disabled.
    geo=a.ce/'map_data/geographical_regions/CE_geographical_region.txt'
    write(a.output/'map_data/geographical_regions'/geo.name,
          '# Culture Expanded geography used by built-in compatibility.\n'+geo.read_text(encoding='utf-8-sig'))
    report['geography_source_sha256']=hashlib.sha256(geo.read_bytes()).hexdigest()
    # CE already exposes this loader probe in test_celticus_trigger.txt. The
    # early default mirrors RICE's existing optional-mod trigger convention.
    early=a.output/'common/scripted_triggers/00000000_compatibility_triggers.txt'
    text=early.read_text(encoding='utf-8-sig')
    if not re.search(r'\bCE_is_loaded\s*=',text): text+='\nCE_is_loaded = { always = no }\n'
    write(early,text)
    write(a.output/'common/scripted_triggers/CAUC_compatibility_triggers.txt',
          'CAUC_ce_present_trigger = { CE_is_loaded = yes }')
    descriptor=a.output/'descriptor.mod'
    text=re.sub(r'\s*dependencies\s*=\s*\{[^}]*\}','',descriptor.read_text())
    if descriptor.exists(): descriptor.unlink()
    descriptor.write_text(text,encoding='utf-8')
    consolidate_script_collisions(a.output,a.ce,report)
    # Native 1.20 renamed the administrative government rule to a mechanic.
    traditions=a.output/'common/culture/traditions/new_realm_traditions.txt'
    if traditions.exists():
        write(traditions, traditions.read_text(encoding='utf-8-sig').replace('government_allows = administrative', 'government_has_mechanic = administrative'))
    # CE concepts use bare icon names; their textures are also needed standalone.
    report['concept_icons']={}
    for p in sorted((a.ce/'gfx/interface/icons/culture_pillars').glob('*.dds')):
        q=a.output/p.relative_to(a.ce)
        q.parent.mkdir(parents=True,exist_ok=True)
        if q.exists(): q.unlink()
        shutil.copy2(p,q)
        report['concept_icons'][str(p.relative_to(a.ce))]=hashlib.sha256(p.read_bytes()).hexdigest()
    report['localization']=supply_localization(a.rice_source,a.output,a.ce,a.game,report['files'])
    report['source_hashes']={str(p.relative_to(a.ce)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for cat,files in included.items() for filename in files
                             for p in [a.ce/'common'/cat/filename]}
    (ROOT/'reports/unified-compatibility-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'files':sum(len(x) for x in included.values()),'fallbacks':len(report['appearance_fallbacks']),'unresolved':report['unresolved']}))
    return bool(report['unresolved'])

if __name__=='__main__': raise SystemExit(main())
