#!/usr/bin/env python3
"""Check one RICE directory alone and with optional mods, without CK3/UI."""
import argparse, json, re
from pathlib import Path
import validate_compatches as v
from build_unified_compat import records

ROOT=Path(__file__).resolve().parents[1]
OPTIONAL={'heritage_kemetic','heritage_kipchak','heritage_levantine',
          'heritage_on_oq','heritage_south_semitic','heritage_tatar'}

def effective(layers, relative):
    files={}
    for root in layers:
        for p in sorted((root/relative).glob('*.txt')): files[p.name]=p
    return files

def get(body,key):
    return next((value for field,value,_,_ in v.entries(body) if field==key),'')

def run(layers,mod,with_ce):
    errors=[];warnings=[]
    regs={cat:v.registry(layers,cat) for cat in v.CATEGORIES}
    for cat in ['culture/pillars','culture/cultures','culture/name_lists']:
        for key in records(mod,cat):
            if len(regs[cat].get(key,[]))!=1:
                errors.append({'duplicate_or_missing':key,'category':cat})
    cultures={key:body for key,rows in regs['culture/cultures'].items()
              if not key.startswith('@') for p,body in rows}
    for key,rows in regs['culture/cultures'].items():
        if key.startswith('@'):continue
        for p,body in rows:
            if not p.is_relative_to(mod):continue
            for field,value,_,_ in v.entries(body):
                cat='culture/pillars' if field in ['heritage','language','ethos','martial_custom'] else 'culture/name_lists' if field=='name_list' else None
                refs=[value] if cat else []
                if field=='traditions':cat='culture/traditions';refs=v.canonical(value)
                if field=='parents':cat='culture/cultures';refs=v.canonical(value)
                if field=='ethnicities':cat='ethnicities';refs=[val for f,val,_,_ in v.entries(value)]
                for ref in refs:
                    if ref not in regs[cat]:errors.append({'culture':key,'field':field,'missing':ref})
    regions={key:body for p in effective(layers,'map_data/geographical_regions').values()
             for key,body,_,_ in v.entries(p.read_text(encoding='utf-8-sig'))}
    missing_pillars={};missing_regions={}
    for folder in ['common','events','gfx']:
        for p in (mod/folder).rglob('*.txt'):
            code=' '.join(v.canonical(p.read_text(encoding='utf-8-sig')))
            for ref in re.findall(r'\bhas_cultural_pillar\s*=\s*(\w+)',code):
                if ref not in regs['culture/pillars']:
                    missing_pillars.setdefault(ref,set()).add(p.relative_to(mod).as_posix())
            for ref in re.findall(r'\bgeographical_region\s*=\s*([A-Za-z_][^\s{}]*)',code):
                if ':' in ref or '$' in ref:continue  # Parameterized scope target.
                if ref not in regions:missing_regions.setdefault(ref,set()).add(p.relative_to(mod).as_posix())
    for ref,files in missing_pillars.items():
        (warnings if ref in OPTIONAL else errors).append({'missing_pillar':ref,'files':sorted(files)})
    for ref,files in missing_regions.items():errors.append({'missing_region':ref,'files':sorted(files)})
    # Keep file-local constants intact when merging culture/army data.
    for cat in ['culture/cultures','culture/pillars','culture/traditions','men_at_arms_types']:
        for p in (mod/'common'/cat).glob('*.txt'):
            code=' '.join(v.canonical(p.read_text(encoding='utf-8-sig')))
            declarations=set(re.findall(r'(@[\w]+)\s*=',code))
            missing=set(re.findall(r'@[\w]+',code))-declarations
            if missing:errors.append({'file':str(p.relative_to(mod)),'missing_constants':sorted(missing)})
    triggers={key:body for name,p in sorted(effective(layers,'common/scripted_triggers').items())
              for key,body,_,_ in v.entries(p.read_text(encoding='utf-8-sig'))}
    ce_flag=get(triggers['CE_is_loaded'],'always')=='yes'
    if ce_flag!=with_ce:errors.append({'ce_probe':ce_flag,'expected':with_ce})
    if v.canonical(triggers['CAUC_ce_present_trigger'])!=['CE_is_loaded','=','yes']:
        errors.append({'ce_probe_adapter':'not dynamic'})
    def evaluate(body, culture, ancestors=None):
        values=[]
        for field,value,_,_ in v.entries(body):
            if field in ['OR','AND','NOT','NOR']:
                nested=evaluate_items(value,culture,ancestors)
                result=any(nested) if field=='OR' else all(nested) if field=='AND' else not all(nested) if field=='NOT' else not any(nested)
            elif field in ['culture','capital_county'] and not value.startswith('culture:'):
                result=evaluate(value,culture,ancestors)
            elif field=='culture':result=culture==value.removeprefix('culture:')
            elif field=='has_cultural_pillar':
                if value not in regs['culture/pillars']:raise ValueError('Missing pillar in evaluated gate: '+value)
                result=value in [get(cultures[culture],f) for f in ['heritage','language','ethos','martial_custom']]
            elif field=='has_cultural_tradition':result=value in v.canonical(get(cultures[culture],'traditions'))
            elif field in ['has_trait','has_character_modifier']:result=False
            elif field=='religion':result=False  # Control ruler has no Oceanic/Siberian religion.
            elif field=='always':result=value=='yes'
            elif field in triggers:result=evaluate(triggers[field],culture,ancestors)==(value=='yes')
            else:raise ValueError('Unsupported culture gate: '+field)
            values.append(result)
        return all(values)
    def evaluate_items(body,culture,ancestors):
        return [evaluate(body[s:e],culture,ancestors) for f,val,s,e in v.entries(body)]
    controls=[]
    for culture in ['bedouin','daylamite','armenian','georgian','french','greek']:
        for trigger in ['RICE_is_native_american_culture_trigger',
                        'RICE_culture_has_oceanic_and_austronesian_heritage_pillar_trigger',
                        'RICE_enjoys_betel_nuts_trigger','RICE_enjoys_kava_trigger']:
            allowed=evaluate(triggers[trigger],culture)
            controls.append({'culture':culture,'gate':trigger,'allowed':allowed})
            if allowed:errors.append({'unrelated_culture_passes':culture,'gate':trigger})
    positives=[]
    for culture,body in cultures.items():
        if get(body,'heritage') in ['heritage_algonquian','heritage_iroquoian','heritage_inuit','heritage_paleo_inuit']:
            if not evaluate(triggers['RICE_is_native_american_culture_trigger'],culture):errors.append({'native_american_rejected':culture})
            positives.append(culture)
        if get(body,'heritage') in ['heritage_austronesian','heritage_papuan','heritage_micronesian','heritage_melanesian','heritage_polynesian']:
            if not evaluate(triggers['RICE_culture_has_oceanic_and_austronesian_heritage_pillar_trigger'],culture):errors.append({'oceanic_rejected':culture})
            positives.append(culture)
    # Check all three migrated starts, including the actual county assignments.
    setup=(mod/'common/scripted_effects/CAUC_CE_setup_effects.txt').read_text(encoding='utf-8-sig')
    starts={}
    for key,body,_,_ in v.entries(setup):
        assignments={}
        for field,value,_,_ in v.entries(body):
            if field.startswith('title:') and 'set_county_culture' in value:
                assignments[field.removeprefix('title:')]=get(value,'set_county_culture').removeprefix('culture:')
        for county,culture in {'c_abkhazia':'abkhaz','c_odishi':'lazi','c_derbent':'dagestani','c_svaneti':'ce_svan','c_shirvan':'tat'}.items():
            if assignments.get(county)!=culture:errors.append({'start':key,'county':county,'expected':culture})
        starts[key]=assignments
    shown=get(v.registry([mod],'decisions')['CAUC_establish_transcaucasia_decision'][0][1],'is_shown')
    if 'CAUC_transcaucasia_region' not in shown:errors.append({'empire_decision':'lost regional restriction'})
    if not re.search(r'\bCAUC_ce_present_trigger\s*=\s*no',shown):errors.append({'empire_decision':'lost optional CE gate'})
    return {'errors':errors,'warnings':warnings,'culture_controls':controls,
            'regional_positive_cultures':len(set(positives)),'startup_county_assignments':starts,
            'ce_present':ce_flag,'standalone_startup_enabled':not ce_flag,
            'standalone_empire_decision_enabled':not ce_flag,
            'pillars':len(regs['culture/pillars']),'regions':len(regions)}

def main():
    ap=argparse.ArgumentParser()
    for name in ['game','ce','epe','mod']:ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--output',type=Path,default=ROOT/'reports/unified-validation.json')
    ap.add_argument('--extra-mod',type=Path,action='append',default=[])
    a=ap.parse_args()
    if re.search(r'\bdependencies\s*=',(a.mod/'descriptor.mod').read_text()):
        raise SystemExit('The unified package still declares mandatory optional mods.')
    # Resolve actual pillar display names too; definitions alone cannot detect _name placeholders.
    from validate_expanded import localization as display_localization
    names={**display_localization(a.game/'localization','english')[0],**display_localization(a.mod/'localization','english')[0]}
    for key,rows in v.registry([a.mod],'culture/pillars').items():
        kind=get(rows[-1][1],'type')
        if kind in ('heritage','language') and key+'_name' not in names:
            raise SystemExit('Missing cultural pillar display name: '+key+'_name')
    profiles={}
    for name,extra in [('alone',[]),('epe',[a.epe]),('ce',[a.ce]),('ce-epe',[a.epe,a.ce])]:
        profiles[name]=run([a.game]+extra+[a.mod],a.mod,a.ce in extra)
    if a.extra_mod:
        profiles['epe-extra-mods']=run([a.game,a.epe]+a.extra_mod+[a.mod],a.mod,False)
        profiles['ce-epe-extra-mods']=run([a.game,a.epe,a.ce]+a.extra_mod+[a.mod],a.mod,True)
    report={'profiles':profiles,'same_directory':str(a.mod),'game_launched':False,
            'limitations':['Static file overlays and a limited culture-condition model; not engine execution.',
                          'Six existing optional ROA/TFE pillar references remain behind their integration guards.']}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({name:{'errors':len(r['errors']),'warnings':len(r['warnings'])} for name,r in profiles.items()}))
    return any(p['errors'] for p in profiles.values())

if __name__=='__main__':raise SystemExit(main())
