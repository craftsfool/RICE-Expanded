#!/usr/bin/env python3
"""Static package validation. Does not run CK3 or claim engine verification."""
import argparse,collections,json,re,hashlib
from pathlib import Path
from ck3_script import entries,registry,files,canonical,find_entry
from import_ce import localization,CULTURES,ENTRY
AUTHOR=Path(__file__).resolve().parents[1]
ROOT=AUTHOR
VISUALS={'ethnicities','coa_gfx','building_gfx','clothing_gfx','unit_gfx','house_coa_frame','house_coa_mask_offset','house_coa_mask_scale'}

def main():
 global ROOT
 ap=argparse.ArgumentParser()
 for k in ('game','rice','epe','ce'):ap.add_argument('--'+k,type=Path,required=True)
 ap.add_argument('--expanded',type=Path)
 ap.add_argument('--mod',type=Path)
 ap.add_argument('--profile',choices=['base','epe','ce-epe'])
 ap.add_argument('--rice-epe-patch',type=Path)
 ap.add_argument('--rice-ce-patch',type=Path)
 ap.add_argument('--output',type=Path,default=ROOT/'research/static-validation.json')
 a=ap.parse_args()
 if a.mod:ROOT=a.mod
 adapter=AUTHOR.parent/'caucasus_flavor_pack_ce_compat';errors=[];warnings=[]
 manifest=json.loads((AUTHOR/'research/ce-import-manifest.json').read_text())
 for root in ([ROOT] if a.mod else [ROOT,adapter]):
  for p in root.rglob('*.txt'):
   if 'research' in p.relative_to(root).parts or p.relative_to(root).parts[0] not in ('common','events','map_data','history'):continue
   if a.mod and not (p.name.startswith('CAUC') or p.name in ('00_iranian.txt','00_byzantine.txt','00_language.txt','00_heritage.txt','00_rules.txt','00_cultural_triggers.txt') or (adapter/p.relative_to(root)).exists()):continue
   try:entries(p.read_text(encoding='utf-8-sig'))
   except ValueError as e:errors.append({'structure':str(p.relative_to(root)),'error':str(e)})
  for p in (root/'localization').rglob('*.yml'):
   if not p.name.endswith('_l_english.yml') or (a.mod and not p.name.startswith('CAUC')):continue
   b=p.read_bytes();lines=b.decode('utf-8-sig').splitlines()
   if not b.startswith(b'\xef\xbb\xbf') or not lines or lines[0]!='l_english:':errors.append({'localization_encoding':p.name})
   seen=set()
   for n,line in enumerate(lines[1:],2):
    if not line.strip() or line.lstrip().startswith('#'):continue
    m=ENTRY.match(line)
    if not m:errors.append({'malformed_localization':p.name,'line':n});continue
    if m[1] in seen:errors.append({'duplicate_localization':m[1],'file':p.name})
    seen.add(m[1])
    unescaped=re.findall(r'(?<!\\)"',m[2])
    if unescaped:errors.append({'unescaped_localization_quote':m[1]})
    if m[2].count('[')!=m[2].count(']'):errors.append({'localization_brackets':m[1]})
  if not (root/'descriptor.mod').exists():continue
  desc=(root/'descriptor.mod').read_text()
  if 'remote_file_id' in desc:errors.append({'workshop_id_in_descriptor':root.name})
  external=(root.parent/(root.name+'.mod')).read_text()
  if 'path="mod/'+root.name+'"' not in external:errors.append({'descriptor_path':root.name})
 profiles={}
 categories=['common/culture/cultures','common/culture/pillars','common/culture/name_lists','common/culture/traditions','common/ethnicities','common/script_values','common/scripted_effects','common/scripted_triggers','common/scripted_rules','common/modifiers','common/opinion_modifiers','common/game_concepts','common/event_themes','events']
 copies=[i for i in manifest['entries'] if i['category'] in categories and i['category'] not in ('events','common/scripted_effects')]
 bases=[(a.profile or 'local_modified',a.rice)]
 if a.expanded and not a.mod:bases.append(('expanded',a.expanded))
 for name,rice in bases:
  for with_ce in ([a.profile=='ce-epe'] if a.mod else [False,True]):
   layers=[a.game,rice,a.epe]+([a.ce] if with_ce else [])+([a.rice_epe_patch] if a.rice_epe_patch else [])+([a.rice_ce_patch] if with_ce and a.rice_ce_patch else [])+[ROOT]+([adapter] if with_ce else [])
   if a.mod:layers=[a.game]+([a.epe] if a.profile!='base' else [])+([a.ce] if with_ce else [])+[ROOT]
   regs={cat:registry(layers,cat) for cat in categories};pe=[]
   # Unlike a last-value dictionary, this counts duplicate keys in every
   # effective file after filenames are overlaid.
   for cat in ('common/culture/cultures','common/culture/pillars','common/culture/name_lists','common/culture/traditions','common/scripted_rules','common/scripted_triggers','common/game_concepts'):
    counts=collections.defaultdict(list)
    for p in files(layers,cat).values():
     try:defs=entries(p.read_text(encoding='utf-8-sig'))
     except ValueError:continue
     for k,_,_,_ in defs:counts[k].append(p.name)
    tracked={i['key'] for i in copies if i['category']==cat}
    for k in tracked:
     if len(counts[k])!=1:pe.append({'duplicate_or_missing_import':k,'category':cat,'files':counts[k]})
   titles=set()
   for p in files(layers,'common/landed_titles').values():
    text=' '.join(canonical(p.read_text(encoding='utf-8-sig')))
    titles.update(re.findall(r'\b([hekdcb]_[A-Za-z0-9_-]+)\s*=\s*\{',text))
   faiths=set(registry(layers,'common/religion/faith_types'))
   for p,body,_ in registry(layers,'common/religion/religion_types').values():
    # Legacy inline-faith definitions in modified local sources.
    for k,b,_,_ in entries(body):
     if k=='faiths':faiths.update(k for k,_,_,_ in entries(b))
   chars=set()
   for p in files(layers,'history/characters').values():
    try:chars.update(k for k,_,_,_ in entries(p.read_text(encoding='utf-8-sig')))
    except ValueError:continue
   regions=set(registry(layers,'map_data/geographical_regions'))
   checked_scripts=[]
   for p in (ROOT/'common').rglob('*.txt'):
    if p.name.startswith('CAUC') or p.name in ('00_rules.txt','00_cultural_triggers.txt'):checked_scripts.append(p)
   checked_scripts+=list((ROOT/'events').glob('CAUC*.txt'))
   for p in checked_scripts:
    text=' '.join(canonical(p.read_text(encoding='utf-8-sig')))
    for scope,known in [('culture',set(regs['common/culture/cultures'])),('title',titles),('faith',faiths),('religion',set(registry(layers,'common/religion/religion_types'))),('character',chars)]:
     for ref in set(re.findall(r'\b'+scope+r':([A-Za-z0-9_-]+)',text)):
      if ref not in known:pe.append({'unresolved_scope':scope+':'+ref,'file':p.name})
    for ref in set(re.findall(r'\bgeographical_region\s*=\s*(CAUC_[A-Za-z0-9_]+)',text)):
     if ref not in regions:pe.append({'unresolved_region':ref,'file':p.name})
    for key in set(re.findall(r'\b(CAUC_[A-Za-z0-9_]+)\s*=\s*yes',text)):
     if key not in regs['common/scripted_effects'] and key not in regs['common/scripted_triggers']:pe.append({'unresolved_custom_script':key,'file':p.name})
    for event in set(re.findall(r'\b(?:id\s*=\s*|\d+\s*=\s*)(CAUC(?:_CE)?\.[0-9]+)',text)):
     if event not in regs['events']:pe.append({'unresolved_event':event,'file':p.name})
    for image in re.findall(r'"(gfx/[^"\n]+)"',text):
     if not any((root/image).exists() for root in layers):pe.append({'missing_image':image,'file':p.name})
   # Culture dependency closure, including ethnicity names with adjacent '='.
   for key in CULTURES:
    if key not in regs['common/culture/cultures']:pe.append({'missing_culture':key});continue
    for field,value,_,_ in entries(regs['common/culture/cultures'][key][1]):
     category=None;refs=[]
     if field in ('heritage','language','ethos','martial_custom'):category='common/culture/pillars';refs=[value]
     elif field=='name_list':category='common/culture/name_lists';refs=[value]
     elif field=='traditions':category='common/culture/traditions';refs=canonical(value)
     elif field=='ethnicities':category='common/ethnicities';refs=[v for _,v,_,_ in entries(value)]
     elif field=='dlc_tradition':category='common/culture/traditions';refs=[v for k,v,_,_ in entries(value) if k in ('trait','fallback')]
     for ref in refs:
      if ref not in regs[category]:pe.append({'culture':key,'field':field,'unresolved':ref})
   known_loc={}
   for root in layers:known_loc.update(localization(root,'english'))
   actual_loc=localization(ROOT,'english')
   package_loc={k:actual_loc.get(k,v) for k,v in localization(AUTHOR,'english').items()}
   for k,v in package_loc.items():
    for ref in re.findall(r'\$([A-Za-z0-9_.-]+)(?:\|[^$]*)?\$',v):
     if ref not in known_loc:pe.append({'localization_key':k,'unresolved_reference':ref})
    for ref in re.findall(r"ScriptValue\('([^']+)'\)",v):
     if ref not in regs['common/script_values']:pe.append({'localization_key':k,'unresolved_script_value':ref})
    for ref in re.findall(r'\[([a-z_]+)\|E\]',v):
     if ref not in regs['common/game_concepts']:pe.append({'localization_key':k,'unresolved_concept':ref})
   for p in checked_scripts:
    text=' '.join(canonical(p.read_text(encoding='utf-8-sig')))
    for k in re.findall(r'\b(?:title|desc|selection_tooltip|confirm_text|custom_tooltip|text)\s*=\s*(CAUC[A-Za-z0-9_.]+|ESTABLISH_TRANSCAUCASIA_TRIGGER)',text):
     if k not in known_loc:pe.append({'missing_english_key':k,'file':p.name})
   for key,(p,b,raw) in regs['events'].items():
    if not p.is_relative_to(ROOT):continue
    if key=='namespace' or not key.startswith('CAUC'):continue
    for field,v,_,_ in entries(b):
     if field=='theme' and v not in regs['common/event_themes']:pe.append({'event':key,'invalid_theme':v})
     if field=='option':
      for f,val,_,_ in entries(v):
       if f=='name' and val not in known_loc:pe.append({'event':key,'missing_option_name':val})
   for cat in ('common/modifiers','common/opinion_modifiers'):
    for key,(p,b,raw) in regs[cat].items():
     if p.is_relative_to(ROOT) and key.startswith('CAUC') and key not in known_loc:pe.append({'missing_modifier_localization':key})
   # Imported culture content must be identical to CE, with its own name list,
   # traditions and appearance. Vanilla names remain vanilla names.
   ce_cultures=registry([a.ce],'common/culture/cultures')
   for key in CULTURES:
    actual=regs['common/culture/cultures'][key][1];expected=ce_cultures[key][1]
    if a.profile=='base':
     def gameplay(body):return [(k,canonical(v)) for k,v,_,_ in entries(body) if k not in VISUALS]
     same=gameplay(actual)==gameplay(expected)
    else:same=canonical(actual)==canonical(expected)
    if not same:pe.append({'changed_ce_culture':key})
   vanilla_loc=localization(a.game,'english')
   for key in ('alan','armenian','georgian','c_derbent','b_derbent'):
    if known_loc.get(key)!=vanilla_loc.get(key):pe.append({'vanilla_terminology_changed':key})
   profiles[name+('_ce_overlay' if with_ce else '_standalone')]={'errors':pe,'layers':[r.name for r in layers],'cultures_checked':len(CULTURES),'character_corrections_checked':len(manifest['historical_character_changes']),'english_keys':len(package_loc)}
 # Concrete behavior checks in a small interpreter for this pack's effect subset.
 behavior=check_behavior()
 errors+=behavior
 report={'errors':errors,'profiles':profiles,'counts':{'decisions':sum(k.startswith('CAUC') for k in registry([ROOT],'common/decisions')),'events':sum(k.startswith('CAUC.') or k.startswith('CAUC_CE.') for k in registry([ROOT],'events')),'imported_cultures':len(CULTURES),'english_keys':len(localization(AUTHOR,'english'))},'behavior_checks':['each passage choice leaves one county policy','policy effects target county scope','review cost is charged once','10-year repair/5-year policy expiry','Gelati threshold: 1106-01-01','all paid annual options gate their costs'],'limitations':['No CK3 process was started. This validates file overlays, references, selected source preservation and a script-subset behavior model, not engine scopes or UI rendering.','Built into RICE Expanded; Base has vanilla visual fallbacks. EPE presets require EPE; CE-EPE also requires CE. Compatibility files are embedded, with no external compatibility mod required.','CE compatibility overlay is for the fingerprinted local CE source; unrelated CE 1.20 issues remain outside this pack.','Exact historical distribution corrections follow CE and are optional; copying does not independently authenticate CE historical claims.']}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 count=len(errors)+sum(len(p['errors']) for p in profiles.values())
 print(json.dumps({'errors':count,'profiles':{k:len(v['errors']) for k,v in profiles.items()},'counts':report['counts']},ensure_ascii=False,indent=2))
 return bool(count)

def check_behavior():
 errors=[];events=registry([ROOT],'events');decisions=registry([ROOT],'common/decisions')
 policy_names={'CAUC_pass_trade','CAUC_pass_guard','CAUC_pass_compact'}
 options=[v for k,v,_,_ in entries(events['CAUC.0001'][1]) if k=='option']
 # Apply actual parsed title effects to a county state with previous policies.
 for body in options:
  state={k:5 for k in policy_names}
  for field,value,_,_ in entries(body):
   if field=='title:c_derbent':
    for effect,arg,_,_ in entries(value):
     if effect=='remove_county_modifier':state.pop(arg,None)
     elif effect=='add_county_modifier':
      d={k:v for k,v,_,_ in entries(arg)};state[d['modifier']]=int(d['years'])
  if len(set(state)&policy_names)!=1:errors.append({'policy_exclusivity':state})
  # Verify these effects use the county scope rather than a holder modifier.
  if 'add_character_modifier' in body:errors.append({'policy_wrong_scope':body})
 review=dict((k,v) for k,v,_,_ in entries(decisions['CAUC_manage_derbent_pass'][1]))
 costs={k:v for k,v,_,_ in entries(review['cost'])}
 actual_effect=' '.join(canonical(review['effect']))
 if costs!={'gold':'25'} or 'add_gold' in actual_effect or actual_effect.count('CAUC.0001')!=1:errors.append({'review_payment':'must charge exactly once'})
 repair=dict((k,v) for k,v,_,_ in entries(decisions['CAUC_repair_derbent_pass'][1]))
 if not re.search(r'modifier\s*=\s*CAUC_pass_restored\s+years\s*=\s*10',repair['effect']):errors.append({'repair_duration':'expected ten years'})
 # Check expiry from parsed policy values, independent of holder.
 for body in options:
  for _,v,_,_ in entries(body):
   if 'add_county_modifier' in v:
    if 'years = 5' not in v:errors.append({'policy_duration':'expected five years'})
 gelati=dict((k,v) for k,v,_,_ in entries(decisions['CAUC_support_gelati'][1]))
 for field in ('is_shown','is_valid'):
  if 'current_date >= 1106.1.1' not in gelati[field]:errors.append({'gelati_date_gate':field})
 # Every paid option needs enough gold before the player can choose it.
 for key,(p,b,raw) in events.items():
  if not key.startswith('CAUC.'):continue
  for f,opt,_,_ in entries(b):
   if f!='option':continue
   charge=sum(float(x) for x in re.findall(r'add_gold\s*=\s*(-[0-9.]+)',opt))
   if charge<0:
    trigger=next((v for k,v,_,_ in entries(opt) if k=='trigger'),'')
    gates=[float(x) for x in re.findall(r'gold\s*>=\s*([0-9.]+)',trigger)]
    if not gates or max(gates)<-charge:errors.append({'unguarded_option_cost':key,'gold':charge})
 return errors
if __name__=='__main__':raise SystemExit(main())
