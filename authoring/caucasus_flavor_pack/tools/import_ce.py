#!/usr/bin/env python3
"""Rebuild the selected CE imports from explicit installed source directories."""
import argparse,json,re,hashlib
from pathlib import Path
from ck3_script import entries,registry,files,canonical,write,find_entry
ROOT=Path(__file__).resolve().parents[1]
ENTRY=re.compile(r'^\s*([^\s:#]+):\d*\s+"(.*)"\s*(?:#.*)?$')
CULTURES=('circassian','udi','dagestani','abkhaz','lazi','ce_svan','tat','alan')
def localization(root,lang):
 result={}
 for p in sorted((root/'localization').rglob('*.yml'),key=lambda p:('replace' in p.parts,str(p))):
  if not p.name.endswith('_l_'+lang+'.yml'):continue
  for line in p.read_text(encoding='utf-8-sig').splitlines():
   m=ENTRY.match(line)
   if m:result[m[1]]=m[2]
 return result

def main():
 ap=argparse.ArgumentParser()
 for name in ('game','ce','epe'):ap.add_argument('--'+name,type=Path,required=True)
 a=ap.parse_args();base=[a.game,a.epe];manifest=[];imported={};pending={}
 def select(category,key):
  if key in imported.setdefault(category,{}):return
  ce=registry([a.ce],category)
  if key not in ce:return
  p,b,raw=ce[key];imported[category][key]=(p,b,raw)
  B=registry(base,category)
  if key in B:
   filename=B[key][0].name
   if filename not in pending.setdefault(category,{}):pending[category][filename]=files(base,category)[filename].read_text(encoding='utf-8-sig')
   s=pending[category][filename]
   for k,_,start,end in entries(s):
    if k==key:s=s[:start]+raw+s[end:];break
   pending[category][filename]=s
  else:
   filename='CAUC_CE_'+category.replace('/','_')+'.txt'
   pending.setdefault(category,{}).setdefault(filename,'# Selected Culture Expanded content. See research/ce-import-manifest.json.\n')
   pending[category][filename]+='\n'+raw+'\n'
  manifest.append({'category':category,'key':key,'source':p.relative_to(a.ce).as_posix(),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'target':category+'/'+filename,'adaptations':[]})
 for k in CULTURES:select('common/culture/cultures',k)
 # Import the pillars and name lists used by the cultures, including CE's
 # Armenian/Georgian runtime changes. Existing vanilla keys retain vanilla text.
 for p,b,raw in list(imported['common/culture/cultures'].values()):
  for f,v,_,_ in entries(b):
   if f in ('heritage','language'):select('common/culture/pillars',v)
   if f=='name_list':select('common/culture/name_lists',v)
 for k in ('heritage_armenian','language_armenian','language_georgian'):select('common/culture/pillars',k)
 select('common/culture/name_lists','name_list_georgian')
 select('common/culture/traditions','tradition_armenian_resilience')
 select('common/culture/pillars','language_alani')
 select('common/game_concepts','bp_monolithic_culture_tradition')
 # CCU pillar AI-choice expressions require their scalar script values. Import
 # referenced values only; do not import CE's global acceptance overwrites.
 values=registry([a.ce],'common/script_values')
 wanted=set(t for defs in imported.values() for _,b,_ in defs.values() for t in canonical(b) if t in values)
 while wanted:
  k=sorted(wanted)[0];wanted.remove(k)
  if k in imported.get('common/script_values',{}):continue
  select('common/script_values',k)
  wanted.update(t for t in canonical(values[k][1]) if t in values and t not in imported['common/script_values'])
 for category,by_name in pending.items():
  for name,s in by_name.items():write(ROOT/category/name,s)
 # Select only Caucasus actions from CE's regional setup effects. Character
 # changes are guarded; CE adds no Caucasus history/characters records.
 setup=registry([a.ce],'common/scripted_effects')
 records=[];history=[];county_changes=[]
 allowed=set(CULTURES)|{'armenian','georgian'}
 base_cultures=set(registry(base,'common/culture/cultures'))
 for year in (867,1066,1178):
  keep=[]
  for group in ('byzantine','iranian','mid_east'):
   key=f'ce_{group}_{year}_setup_effect';p,b,raw=setup[key]
   for k,body,start,end in entries(b):
    refs=re.findall(r'culture:([A-Za-z0-9_]+)',body)
    selected=None
    if k.startswith('culture:') and k.split(':')[1] in allowed:
     if any(r not in allowed|base_cultures for r in refs):continue
     selected=b[start:end]
    elif k.startswith('character:') and any(r in allowed for r in refs):
     selected='if = { limit = { exists = '+k+' } '+b[start:end]+' }'
     history.append({'start':year,'character':k.split(':')[1],'action':canonical(body)})
    elif k.startswith('title:') and refs and all(r in allowed for r in refs):
     selected=b[start:end];county_changes.append({'start':year,'title':k.split(':')[1],'action':canonical(body)})
    if selected:
     selected=re.sub(r'get_all_innovations_from = scope:([A-Za-z0-9_]+)',r'get_all_innovations_from = culture:\1',selected)
     keep.append(selected)
   manifest.append({'category':'common/scripted_effects','key':key,'source':p.relative_to(a.ce).as_posix(),'target':'common/scripted_effects/CAUC_CE_setup_effects.txt','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'adaptations':['Caucasus cultures and Armenian distribution only','Guard existing character scopes','Resolve innovation inheritance through explicit culture scopes','Startup can be disabled by game rule']})
  records.append('CAUC_CE_setup_'+str(year)+'_effect = {\n'+'\n'.join(keep)+'\n}')
 write(ROOT/'common/scripted_effects/CAUC_CE_setup_effects.txt','\n\n'.join(records))
 # CE's Transcaucasia flavor, kept in a separate namespace. The CE compatibility
 # overlay hides this copy when the original CE decision is available.
 substitutions={'establish_transcaucasia_decision':'CAUC_establish_transcaucasia_decision','establish_transcaucasia_scripted_effect':'CAUC_establish_transcaucasia_effect','DE_decision_event.0025':'CAUC_CE.0025','e_transcaucasia':'e_CAUC_transcaucasia','establish_transcaucasia_trigger':'CAUC_establish_transcaucasia_trigger','custom_transcaucasia':'CAUC_transcaucasia_region','ce_transcaucasia_has_been_established':'CAUC_transcaucasia_has_been_established','de_imperial_pretender_opinions':'CAUC_imperial_pretender'}
 def adapt(s):
  for old,new in sorted(substitutions.items(),key=lambda x:len(x[0]),reverse=True):s=s.replace(old,new)
  return s
 for category,key,target in [('common/decisions','establish_transcaucasia_decision','common/decisions/CAUC_CE_decisions.txt'),('common/scripted_effects','establish_transcaucasia_scripted_effect','common/scripted_effects/CAUC_CE_flavor_effects.txt'),('events','DE_decision_event.0025','events/CAUC_CE_events.txt'),('common/landed_titles','e_transcaucasia','common/landed_titles/CAUC_CE_titles.txt'),('common/landed_titles','k_shirvan','common/landed_titles/CAUC_CE_titles.txt'),('common/coat_of_arms/coat_of_arms','e_transcaucasia','common/coat_of_arms/coat_of_arms/CAUC_CE_coa.txt'),('common/opinion_modifiers','de_imperial_pretender_opinions','common/opinion_modifiers/CAUC_CE_opinions.txt'),('common/trigger_localization','establish_transcaucasia_trigger','common/trigger_localization/CAUC_CE_trigger_loc.txt'),('map_data/geographical_regions','custom_transcaucasia','map_data/geographical_regions/CAUC_CE_regions.txt')]:
  p,b,raw=find_entry(a.ce,category,key);s=adapt(raw)
  if category=='common/decisions':
   s=s.replace('is_shown = {','is_shown = {\n CAUC_ce_present_trigger = no',1)
   # Guard non-dynastic rulers; empire-creation remains a dynastic ruler choice.
   s=s.replace('is_independent_ruler = yes','is_independent_ruler = yes\n exists = dynasty',1)
  if category=='events':s='namespace = CAUC_CE\n'+s.replace('= {', '= {\n type = character_event',1)
  if category=='common/landed_titles' and '@better_than_the_alternatives_score' in s:s='@better_than_the_alternatives_score = 100\n'+s
  q=ROOT/target
  previous=q.read_text(encoding='utf-8-sig') if q.exists() and key=='k_shirvan' else ''
  write(q,previous+'\n'+s)
  manifest.append({'category':category,'key':key,'source':p.relative_to(a.ce).as_posix(),'target':target,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'adaptations':['Namespace isolation']+(['Hide duplicate decision with CE adapter; require dynasty'] if category=='common/decisions' else [])})
 # Rebase the CE tradition's monolithic restrictions onto the current vanilla
 # rules. Whole-file overlays preserve other vanilla records token for token.
 for category,key in [('common/scripted_rules','can_diverge_culture'),('common/scripted_rules','can_hybridize_culture'),('common/scripted_triggers','is_valid_for_hybridising_trigger')]:
  cp,cb,cr=find_entry(a.ce,category,key);vp,vb,vr=find_entry(a.game,category,key)
  custom=[]
  for field,body,start,end in entries(cb):
   if field=='custom_description' and 'monolithic_culture_feature' in body:custom.append(cb[start:end])
   if field=='$CHARACTER$':
    for f,b,start,end in entries(body):
     if f=='trigger_if' and 'monolithic_culture_feature' in b:custom.append(body[start:end])
  if category=='common/scripted_rules':replacement=key+' = {'+vb+'\n'+'\n'.join(custom)+'\n}'
  else:
   parts=entries(vb);body=vb
   for f,b,start,end in parts:
    if f=='$CHARACTER$':body=vb[:start]+f+' = {'+b+'\n'+'\n'.join(custom)+'\n}'+vb[end:];break
   replacement=key+' = {'+body+'}'
  target=ROOT/category/vp.name
  text=target.read_text(encoding='utf-8-sig') if target.exists() else vp.read_text(encoding='utf-8-sig')
  for k,b,start,end in entries(text):
   if k==key:text=text[:start]+replacement+text[end:];break
  write(target,text)
  imported.setdefault(category,{})[key]=(cp,cb,cr)
  manifest.append({'category':category,'key':key,'source':cp.relative_to(a.ce).as_posix(),'target':category+'/'+vp.name,'source_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'adaptations':['Insert only CE monolithic-culture restriction into current vanilla 1.20 implementation']})
 # English dependency closure: prefer vanilla values for vanilla keys, then CE.
 V=localization(a.game,'english');C=localization(a.ce,'english');selected={}
 terms=set(t.strip('"') for category in pending for defs in imported.get(category,{}).values() for t in canonical(defs[1]))
 terms.update(imported.get('common/culture/pillars',{}));terms.update(CULTURES)
 terms.update(['tati','tati_prefix','tati_collective_noun','game_concept_bp_monolithic_culture_tradition','game_concept_bp_monolithic_culture_tradition_desc','ESTABLISH_TRANSCAUCASIA_TRIGGER','must_not_be_under_culture_head_tradition','must_have_duchy_or_better_to_hybridize'])
 for k in CULTURES:terms.update([k+'_prefix',k+'_collective_noun'])
 for category in ('common/decisions','events','common/landed_titles','common/opinion_modifiers','common/trigger_localization','common/scripted_rules','common/scripted_triggers'):
  for p in (ROOT/category).glob('*.txt'):
   terms.update(t.strip('"') for t in canonical(p.read_text(encoding='utf-8-sig')))
 # Select CE display strings with namespaced equivalents.
 for old,new in substitutions.items():
  for key,value in C.items():
   if key==old or key.startswith(old+'.') or key.startswith(old+'_'):
    if old in ('establish_transcaucasia_decision','DE_decision_event.0025','e_transcaucasia','establish_transcaucasia_trigger','de_imperial_pretender_opinions'):
     selected[adapt(key)]=adapt(value)
 for key in imported.get('common/culture/traditions',{}):terms.update([key+'_name',key+'_desc'])
 for key in imported.get('common/culture/pillars',{}):terms.update([key+'_name'])
 for category in imported.values():
  for _,body,_ in category.values():
   params=re.search(r'parameters\s*=\s*\{([^}]*)\}',body)
   if params:
    terms.update('culture_parameter_'+k for k,_,_,_ in entries(params[1]))
 while terms:
  k=terms.pop()
  if k in selected or k in V:continue
  if k in C:
   selected[k]=C[k];terms.update(re.findall(r'\$([A-Za-z0-9_.-]+)(?:\|[^$]*)?\$',C[k]))
 # Preserve CE content but repair clear English typos and unsupported claim of
 # historical uniqueness, following vanilla's concise voice.
 selected['CAUC_CE.0025.desc']='For generations, rulers from beyond these mountains have contested the lands between the Black Sea and the Caspian. I have united the heartlands of Transcaucasia under my rule. My successors will inherit an empire with its own crown and obligations, as well as the attention of the powers on our borders.'
 selected['CAUC_CE.0025.a']='Let our neighbors recognize the new crown.'
 # Standalone labels describe CCU group metadata without promising bonuses
 # from CE's global acceptance overhaul, which this regional pack does not import.
 for k,v in list(selected.items()):
  if k.startswith('culture_parameter_') and 'cultural_acceptance_baseline' in v:
   m=re.search(r'sharing the (.+?) \[([a-z_]+)\|E\]',v)
   if m:selected[k]='Shares the '+m[1]+' '+m[2].replace('_',' ')+'.'
 selected['game_concept_bp_monolithic_culture_tradition_desc']='A culture with this tradition requires a duke or higher-ranking ruler to create a hybrid culture. A ruler cannot diverge or hybridize while subject to their culture head or to the liege of their culture head.'
 selected['alan_history_loc']='Diverged from Sarmatian culture around the year [DATE.GetYear]'
 selected['tati_history_loc']='The Caucasianized [CULTURE.GetName] culture of the local Iranian population'
 selected['CAUC_establish_transcaucasia_decision_desc']='I control the heartlands of Transcaucasia and can establish an imperial crown of my own. My realm will claim a place beside the empires whose rulers have contested these lands. The new crown will bring obligations to my successors and rivals at our borders.'
 selected['CAUC_establish_transcaucasia_decision_confirm']='Establish the imperial crown'
 # Isolate imported AI-choice values from the original CE registry.
 value_map={k:'CAUC_CE_'+k for k in imported.get('common/script_values',{})}
 for category in ('common/script_values','common/culture/pillars'):
  for p in (ROOT/category).glob('*.txt'):
   text=p.read_text(encoding='utf-8-sig')
   for old,new in value_map.items():text=re.sub(r'\b'+re.escape(old)+r'\b',new,text)
   write(p,text)
 for item in manifest:
  if item['category'] in ('common/script_values','common/culture/pillars'):
   item.setdefault('adaptations',[]).append('Namespace imported CCU AI-choice values; retain group metadata')
 text='l_english:\n'+'\n'.join(' '+k+':0 "'+v+'"' for k,v in sorted(selected.items()))
 write(ROOT/'localization/english/CAUC_CE_l_english.yml',text)
 # Explicit replace entries keep vanilla terminology even with CE enabled.
 vanilla_names=['alan','armenian','georgian','c_derbent','b_derbent','c_lori','c_svaneti','b_kutaisi']
 write(ROOT/'localization/english/replace/CAUC_vanilla_names_l_english.yml',
       'l_english:\n'+'\n'.join(' '+k+':0 "'+V[k]+'"' for k in vanilla_names))
 # Vanilla-derived terminology per language for future translations. No automatic
 # translated gameplay files are produced in the English-first build.
 terms_report={}
 for lang in ['english','simp_chinese','french','german','spanish','russian','polish','japanese','korean']:
  d=localization(a.game,lang)
  terms_report[lang]={k:d[k] for k in ('c_derbent','b_derbent','c_svaneti','c_lori','armenian','georgian','alan') if k in d}
 (ROOT/'research/vanilla-terminology.json').write_text(json.dumps(terms_report,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'research/ce-import-manifest.json').write_text(json.dumps({'source_workshop_id':'2829397295','cultures':CULTURES,'entries':manifest,'historical_character_changes':history,'county_setup_changes':county_changes,'new_caucasus_character_records':0,'note':'CE history/characters contains only unrelated fictional Balkans/Pannonia records. Existing Caucasus character corrections are imported from CE startup effects. CCU metadata and referenced scalar values are preserved; global CCU GUI and acceptance overhaul are not imported.'},ensure_ascii=False,indent=2)+'\n')
 # Optional CE overlay masks imported registry keys without deleting CE's other
 # regional content. Use the same source filenames to make overlays explicit.
 adapter=ROOT.parent/'caucasus_flavor_pack_ce_compat'
 for category,defs in imported.items():
  if category=='common/script_values':continue # values use namespaced subset below
  for filename,p in files([a.ce],category).items():
   s=p.read_text(encoding='utf-8-sig');changed=False
   for k,b,start,end in reversed(entries(s)):
    if k in defs:s=s[:start]+'# '+k+' is supplied by Caucasus: Passes and Sanctuaries.\n'+s[end:];changed=True
   if changed:write(adapter/category/filename,s)
 # k_shirvan is the one unrenamed CE title copied into core.
 for filename,p in files([a.ce],'common/landed_titles').items():
  s=p.read_text(encoding='utf-8-sig');changed=False
  for k,b,start,end in reversed(entries(s)):
   if k=='k_shirvan':s=s[:start]+'# k_shirvan is supplied by the Caucasus package.\n'+s[end:];changed=True
  if changed:write(adapter/'common/landed_titles'/filename,s)
 write(adapter/'common/scripted_triggers/CAUC_compatibility_triggers.txt','CAUC_ce_present_trigger = { always = yes }')
 print(json.dumps({'cultures':len(CULTURES),'imported_entries':len(manifest),'english_keys':len(selected),'historical_character_changes':len(history)},indent=2))
if __name__=='__main__':main()
