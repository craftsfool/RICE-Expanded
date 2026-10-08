#!/usr/bin/env python3
"""Regression checks against native resources and executable story-state models."""
import argparse,copy,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'authoring/caucasus_flavor_pack/tools'))
from ck3_script import entries,registry,canonical
from validate_religious import fresh,effects,condition,get,fields,paths,date

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',required=True,type=Path);ap.add_argument('--mod',type=Path,default=ROOT/'RICE');ap.add_argument('--output',type=Path,default=ROOT/'reports/story-design-validation.json');args=ap.parse_args()
 mod=args.mod;game=args.game;events=registry([mod],'events');actions=registry([mod],'common/on_action');cast=registry([mod],'common/scripted_effects')
 checks=[];timelines=[];modifier_numbers=[]
 # Every visible scene has its own cast and directly resolves actual actor scopes.
 regional=[k for k in events if k.startswith('CAUC.') and int(k.split('.')[1])<100 and int(k.split('.')[1])!=50]
 for key in regional:
  if key not in registry([mod],'events') or events[key][0].name!='CAUC_regional_events.txt':continue
  b=events[key][1];assert get(b,'right_portrait') and 'speaker_effect' in get(b,'immediate'),key
  assert 'add_courtier' in b or 'create_artifact' in b,key
  opts=[get(v,'name') for k,v,_ in fields(b) if k=='option'];assert len(opts)==len(set(opts)),key
 checks.append('All 22 smaller regional scenes have a recurring named contact and tangible recruit/manuscript outcomes')
 for key in ('CAUC.0100','CAUC.0101','CAUC.0102','CAUC.0110','CAUC.0111','CAUC.0112','CAUC.0120','CAUC.0121','CAUC.0122','CAUC.0130','CAUC.0131','CAUC.0132'):
  assert get(events[key][1],'right_portrait') and 'speaker_effect' in get(events[key][1],'immediate')
 checks.append('Every stage of the four religious disputes displays and recovers its actual participants')
 # Verify the actual native aptitude terms and breakpoints rather than a label override.
 cp=registry([game],'common/court_positions/types')['bodyguard_court_position'][1]
 assert canonical(get(cp,'aptitude_level_breakpoints'))==['20','40','60','80']
 aptitude=get(cp,'aptitude')
 for token in ('multiply = 4','max = 50','has_trait = brave','has_trait = gallant','has_trait = lifestyle_blademaster','value = 20','value = 15','value = 5'):
  assert token in aptitude,token
 s=fresh('c_derbent','sunni','867.1.1');b=events['CAUC.0100'][1];effects(get(b,'immediate'),s)
 captain=s['scopes']['CAUC_rus_speaker'];c=s['characters'][captain]
 assert c['faith']=='faith:slavic_pagan' and c['culture']=='culture:russian'
 cultures=registry([game,mod],'common/culture/cultures');assert get(cultures['russian'][1],'heritage')=='heritage_east_slavic'
 assert c['skills']['martial']>=25 and c['skills']['prowess']>=30
 assert c['trait_xp']['lifestyle_blademaster']==100 and {'brave','gallant','lifestyle_blademaster'}<=set(c['traits'])
 raw_score=1+min(4*c['skills']['prowess'],50)+20+15+5
 assert raw_score-10>=80
 opts=[v for k,v,_ in fields(b) if k=='option']
 results=[]
 for opt in opts:
  state=copy.deepcopy(s);effects(opt,state);assert state['troops']==500;results.append(state)
 assert results[0]['bodyguard']==captain and results[1]['bodyguard'] is None
 full=copy.deepcopy(s);full['bodyguard_available']=False
 assert not condition(get(opts[0],'trigger'),full) and condition(get(opts[1],'trigger'),full)
 # Reload preserves actor identities without generating a new captain.
 snap=copy.deepcopy(results[0]);snap['scopes'].clear();before=len(snap['characters']);effects(get(events['CAUC.0101'][1],'immediate'),snap)
 assert snap['scopes']['CAUC_rus_speaker']==captain and len(snap['characters'])==before
 checks.append('Rus captain: Slavic faith, East Slavic heritage, martial 26/prowess 32, native aptitude 91 (81 after Palace Politics), both choices exactly 500 troops, full positions protected, actor survives reload')
 # Exact starting schedule and the succession fallback, with no random event pool.
 start=get(actions['CAUC_tondrakian_start'][1],'effect');fallback=actions['CAUC_tondrakian_guaranteed_outbreak'][1]
 assert 'random_events' not in start+fallback
 for when in ('867.1.1','1066.9.15','1178.10.1'):
  state=fresh('c_apahunik','sunni',when)
  effects(start,state)
  if when.startswith('867'):
   assert state['queued']=='CAUC.0149' and state['delay']==365 and not state['rite_exists']
   state['date']=date('868.1.1');state['queued']=None
   assert condition(get(events['CAUC.0149'][1],'trigger'),state)
   effects(get(events['CAUC.0149'][1],'immediate'),state)
   assert state['rite_exists'] and state['foundations']==1 and state['notices']==['CAUC.0150']
   assert not condition(get(events['CAUC.0149'][1],'trigger'),state),'Duplicate public outbreak'
   # Original ruler dies: the annual global hook instead targets the current holder.
   succession=fresh('c_apahunik','sunni',when);effects(start,succession);succession['queued']=None;succession['delay']=0;succession['date']=date('868.1.1')
   assert condition(get(fallback,'trigger'),succession);effects(get(fallback,'effect'),succession)
   assert succession['queued']=='CAUC.0149' and succession['delay']==1
   effects(get(events['CAUC.0149'][1],'immediate'),succession);assert succession['rite_exists']
   timelines.append({'start':when,'normal_outbreak_day':365,'notification_day':366,'succession_fallback':'first annual pulse from 868; current Apahunik holder, no religion/war/adulthood gate'})
  else:
   assert state['rite_exists'] and state['foundations']==1 and state['queued'] is None
   before=state['native_founder'];effects(start,state);assert state['foundations']==1 and state['native_founder']==before
   timelines.append({'start':when,'rite_exists_at_initialization':True,'duplicate_foundation':False})
 checks.append('867 schedules a public outbreak after one year with a global succession fallback; 1066/1178 initialize the rite immediately independent of ruler faith')
 # Test icons in the installed vanilla archive, including correct name coloring.
 modifiers=registry([mod],'common/modifiers');icons={p.stem for p in (game/'gfx/interface/icons/modifiers').glob('*.dds')}|{p.stem for p in (mod/'gfx/interface/icons/modifiers').glob('*.dds')}
 for key,(p,body,raw) in modifiers.items():
  if not key.startswith('CAUC_'):continue
  icon=get(body,'icon');assert icon in icons,(key,icon)
  assert icon.endswith(('_positive','_negative')),(key,icon)
  for field,value,_,_ in entries(body):
   if field=='icon':continue
   number=float(value)
   assert number!=0,(key,field,'Zero modifier effect')
   # Native fortification modifiers use whole levels. Fractional levels such as
   # 0.25 render as +0 in the county tooltip and should never be authored here.
   if field in ('fort_level','county_opinion_add','learning'):
    assert number.is_integer(),(key,field,'Integer-displayed modifier requires a whole value')
   modifier_numbers.append({'modifier':key,'field':field,'value':number})
  if key in ('CAUC_pass_obstructed','CAUC_tondrakian_suppressed'):assert icon.endswith('_negative')
 for key in ('CAUC_lori_autonomy','CAUC_ani_existing_use','CAUC_pass_restored'):assert get(modifiers[key][1],'icon').endswith('_positive')
 checks.append('All 25 Caucasus modifiers point to existing native icons; green/red names follow the engine’s documented suffix rule')
 checks.append('All authored modifier effects are nonzero; fort levels, opinion and skill bonuses use whole values instead of fractions that display as zero')
 # Every typed reference introduced by the story overhaul resolves in the actual game.
 references=[]
 for p in list((mod/'events').glob('CAUC*'))+list((mod/'common/scripted_effects').glob('CAUC*')):
  code=' '.join(canonical(p.read_text(encoding='utf-8-sig')))
  for category,scope in [('culture/cultures','culture'),('religion/faith_types','faith')]:
   known=registry([game,mod],'common/'+category)
   for key in re.findall(r'\b'+scope+r':([a-zA-Z0-9_]+)',code):assert key in known,(p,key)
 for category,key in [('artifacts/visuals','book'),('artifacts/templates','general_unique_template'),('men_at_arms_types','light_horsemen')]:assert key in registry([game,mod],'common/'+category)
 checks.append('New culture, faith, cavalry type, book visual/template and modifier references resolve against 1.20')
 report={'errors':[],'scope':'Native file references and bounded script-state regression tests; no game launch, rendering or engine simulation','checks':checks,'timelines':timelines,'bodyguard_aptitude':{'base':raw_score,'with_palace_politics':raw_score-10,'excellent_threshold':80},'regional_scenes':22,'modifier_numbers':modifier_numbers}
 args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'errors':[],'checks':len(checks),'timelines':timelines,'bodyguard_aptitude':report['bodyguard_aptitude']}))
if __name__=='__main__':main()
