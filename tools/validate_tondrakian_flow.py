#!/usr/bin/env python3
"""Native integration references and bounded regional/old-save regressions.

This does not execute CK3, calculate engine divergence, or check rendered UI.
"""
import argparse,copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'authoring/caucasus_flavor_pack/tools'))
from ck3_script import entries,registry,canonical
from validate_religious import fresh,effects,condition,get,fields

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,required=True);ap.add_argument('--mod',type=Path,default=ROOT/'RICE');ap.add_argument('--output',type=Path,default=ROOT/'reports/tondrakian-flow-validation.json');a=ap.parse_args()
 mod=a.mod;triggers=registry([mod],'common/scripted_triggers');events=registry([mod],'events');actions=registry([mod],'common/on_action');scripted=registry([mod],'common/scripted_effects');native=registry([a.game/'events/religion_events'],'');native_effects=registry([a.game],'common/scripted_effects')
 regions=registry([a.game,mod],'map_data/geographical_regions')
 def duchies(key):
  body=regions[key][1];result=set(canonical(get(body,'duchies')))
  for child in canonical(get(body,'regions')):result.update(duchies(child))
  return result
 area=duchies('CAUC_caucasus_broadcast_region')
 assert {'d_alania','d_ciscaucasia','d_azov','d_khazaria','d_shirvan','d_abkhazia','d_georgia','d_greater_armenia'}<=area
 titles=registry([a.game],'common/landed_titles') # Nested titles checked against native tokens.
 native_titles=' '.join(p.read_text(encoding='utf-8-sig') for p in (a.game/'common/landed_titles').glob('*.txt'))
 for title in area:assert title+' = {' in native_titles,title
 def evaluate(text,c):
  bits=[]
  for key,value,op in fields(text):
   if key in triggers and key.startswith('CAUC_tondrakian_'):b=evaluate(triggers[key][1],c)
   elif key in ('OR','AND','NOT'):
    xs=[evaluate(value[x:z],c) for _,_,x,z in entries(value)];b=any(xs) if key=='OR' else (not all(xs) if key=='NOT' else all(xs))
   elif key=='is_landed':b=bool(c.get('lands'))==(value=='yes')
   elif key=='faith':b=evaluate(value,{'religion':c['religion']})
   elif key=='religion':b=c['religion']==value
   elif key=='capital_province':b=evaluate(value,{'duchy':c.get('capital')})
   elif key=='any_held_title':b=any(evaluate(value,{'tier':'tier_county','duchy':d}) for d in c.get('lands',[]))
   elif key=='title_province':b=evaluate(value,c)
   elif key=='geographical_region':b=c.get('duchy') in duchies(value)
   elif key=='tier':b=c['tier']==value
   elif key=='any_liege_or_above':b=any(evaluate(value,liege) for liege in c.get('lieges',[]))
   elif key=='has_title':b=value.removeprefix('title:') in c.get('titles',[])
   elif key in ('highest_held_title_tier','culture'):b=c.get(key)==value
   else:raise AssertionError(('Unmodelled regional predicate',key,value))
   bits.append(b)
  return all(bits)
 cases=[]
 for religion,cap,lands,expected in [('christianity','d_alania',['d_alania'],True),('christianity','d_ciscaucasia',['d_ciscaucasia'],True),('christianity','d_abkhazia',['d_abkhazia'],True),('christianity','d_greater_armenia',['d_greater_armenia'],True),('christianity','d_latium',['d_shirvan'],True),('christianity','d_latium',['d_latium'],False),('islam','d_shirvan',['d_shirvan'],False),('christianity','d_alania',[],False)]:
  c={'religion':'religion:'+religion+'_religion','capital':cap,'lands':lands};actual=evaluate(triggers['CAUC_tondrakian_broadcast_recipient_trigger'][1],c);assert actual==expected,(c,actual);cases.append({**c,'receives_followups':actual})
 join=next(v for k,v,_ in fields(events['CAUC.0151'][1]) if k=='option' and get(v,'name')=='CAUC.0150.b')
 ai=get(join,'ai_chance');base=float(get(ai,'base'));modifier=get(ai,'modifier');factor=float(get(modifier,'factor'))
 for title,expected in [('k_armenia',True),('k_armenian_principality',True),('k_france',False)]:
  c={'lieges':[{'titles':[title],'highest_held_title_tier':'tier_kingdom','culture':'culture:french'}]};actual=evaluate(get(modifier,'CAUC_tondrakian_armenian_crown_vassal_trigger') and 'CAUC_tondrakian_armenian_crown_vassal_trigger = yes',c);assert actual==expected
 assert base*factor>base and factor==8
 # The engine-native notification requires all four saved scopes.
 s=fresh('c_apahunik','armenian_apostolic','867.1.1');effects('CAUC_tondrakian_prepare_inquiry_effect = yes CAUC_tondrakian_notification_scopes_effect = yes',s)
 assert condition(get(native['faith_creation.1021'][1],'trigger'),s)
 for name in ('rite_growth_resolve_differences_effect','pam_heresy_convert_ruler_to_new_rite_effect','pam_convert_court_to_faith_effect'):assert name in native_effects
 assert 'set_character_rite_with_conversion' in native_effects['pam_heresy_convert_ruler_to_new_rite_effect'][1]
 assert 'every_held_title' in native_effects['pam_heresy_convert_ruler_to_new_rite_effect'][1] and 'rite_growth_convert_court_to_new_rite_effect' in native_effects['pam_heresy_convert_ruler_to_new_rite_effect'][1]
 # Population spreads once, respects non-Armenian counties and foreign rulers,
 # and cannot repaint a province that was intentionally reconverted afterwards.
 effects('CAUC_tondrakian_seed_counties_effect = yes',s)
 assert set(s['county_rites'])=={'title:c_apahunik','title:c_bagrevand'}
 assert s['rite']=='rite:armenian_rite' and s['faith']=='faith:armenian_apostolic'
 s['county_rites']['title:c_apahunik']='rite:armenian_rite';before=copy.deepcopy(s['county_rites']);effects('CAUC_tondrakian_seed_counties_effect = yes',s);assert s['county_rites']==before
 suppressed=fresh('c_apahunik','armenian_apostolic','868.1.1',created=True);suppressed['vars']['title:c_apahunik']={'CAUC_tondrakian_inquiry_choice':5};effects('CAUC_tondrakian_seed_counties_effect = yes',suppressed);assert not suppressed['county_rites']
 old=fresh('c_apahunik','armenian_apostolic','868.1.1',created=True);old['globals'].update(CAUC_tondrakian_scheduled=True,CAUC_tondrakian_outbreak_announced=True);old['rite_parent']='faith:detached_tondrakian';founder=old['native_founder'];effects(get(actions['CAUC_tondrakian_start'][1],'effect'),old)
 assert old['rite_parent']=='faith:armenian_apostolic' and old['native_founder']==founder and old['foundations']==0 and old['county_rites']
 # Cross-denomination acceptance converts matching old-faith domain counties.
 convert=fresh('c_apahunik','orthodox','868.1.1',created=True);convert['counties']['title:c_apahunik']['faith']='faith:orthodox';effects('CAUC_tondrakian_join_effect = yes',convert);assert convert['faith']=='faith:armenian_apostolic' and convert['rite']=='rite:CAUC_tondrakian_rite' and convert['county_rites']['title:c_apahunik']==convert['rite']
 # Each actual investigation stage forwards its saved stage to regional rulers.
 for n in range(141,145):
  immediate=get(events[f'CAUC.{n:04d}'][1],'immediate');assert f'value = {n}' in immediate and 'CAUC_tondrakian_broadcast_followup_effect = yes' in immediate
 assert get(events['CAUC.0151'][1],'trigger').find('CAUC_tondrakian_broadcast_recipient_trigger')>=0
 assert 'has_title' not in get(events['CAUC.0151'][1],'trigger')
 # A Muslim/minor/imprisoned origin ruler must not block the public sequel.
 fallback=fresh('c_apahunik','sunni','868.1.1',created=True)
 for n in range(152,156):
  body=events[f'CAUC.{n:04d}'][1];assert get(body,'scope')=='faith' and condition(get(body,'trigger'),fallback)
  effects(get(body,'immediate'),fallback,'faith:armenian_apostolic')
  assert fallback['broadcasts'][-1]['stage']==n-11
 fallback['globals']['CAUC_tondrakian_inquiry_started']=True
 assert not condition(get(events['CAUC.0152'][1],'trigger'),fallback)
 # On-action registrations are additive; registry() keeps only the last same-key
 # declaration, so inspect this registration rather than an unrelated RICE one.
 registrations={k:v for k,v,_,_ in entries((mod/'common/on_action/CAUC_tondrakian_start_on_actions.txt').read_text(encoding='utf-8-sig'))}
 assert 'CAUC_tondrakian_keep_parent' in get(registrations['on_faith_created'],'on_actions')
 assert 'include_derived = no' in scripted['CAUC_tondrakian_restore_parent_effect'][1]
 report={'errors':[],'scope':'Native source references and bounded script models only; no engine, UI or calculated divergence verification','region_duchies':sorted(area),'broadcast_cases':cases,'ai_join_weights':{'ordinary':base,'armenian_crown_vassal':base*factor,'decline':100},'checks':['Native rite notification scopes resolve','Native domain and court conversion helpers exist','County seed, neighbor exclusions and no forced player conversion','Old-save reparenting retains original founder','No repeated seed after deliberate reconversion or suppression','Cross-denomination acceptance stays in Armenian parent faith','All four follow-up stages broadcast to regional rulers','Public sequel survives an ineligible local host; an actual investigation takes over','Only the authored rite is repaired; derived rites are excluded']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'errors':[],'checks':len(report['checks']),'broadcast_cases':len(cases),'ai_join_weights':report['ai_join_weights']}))

if __name__=='__main__':main()
