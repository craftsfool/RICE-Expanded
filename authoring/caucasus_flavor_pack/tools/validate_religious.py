#!/usr/bin/env python3
"""Exhaust actual authored option paths in a strict, limited script model.

This is not a CK3 interpreter. Unknown commands fail rather than being ignored.
Also checks native registry dependencies, translations, and the generated DDS.
"""
import argparse, copy, hashlib, json, operator, re
from pathlib import Path
from PIL import Image
from ck3_script import canonical, entries, registry
from import_ce import localization

ROOT = Path(__file__).resolve().parents[1]
SCRIPTED = registry([ROOT],'common/scripted_effects')
OPS = {'=':operator.eq, '>=':operator.ge, '<=':operator.le, '>':operator.gt, '<':operator.lt, '!=':operator.ne}

def fields(text):
 for key,value,start,end in entries(text):
  op = re.match(r'\s*\S+?\s*(\?=|>=|<=|!=|=|>|<)',text[start:end])[1]
  yield key,value.strip(),op

def get(text,key,default=''):
 return next((value for name,value,_ in fields(text) if name==key),default)

def date(value):
 return tuple(map(int,value.split('.')))

def condition(text,s,scope='root'):
 results=[]
 for key,value,op in fields(text):
  if key in ('NOT','AND','OR'):
   bits=[condition(value[a:z],s,scope) for _,_,a,z in entries(value)]
   result=not all(bits) if key=='NOT' else (all(bits) if key=='AND' else any(bits))
  elif key.startswith(('title:','global_var:','var:','scope:')) and '=' in value or key=='root':
   if key.startswith(('global_var:','var:','scope:')):
    ident=resolve(key,s,scope)
    result=ident is not None and condition(value,s,ident)
   else:result=condition(value,s,key)
  elif key=='faith' and '=' in value:
   result=condition(value,s,'faith')
  elif key=='religion':result=s['religion']==value
  elif key=='faith':result=s['faith']==value
  elif key=='rite':result=s['rite_exists'] and s['rite']==value
  elif key=='exists':
   if value=='rite:CAUC_tondrakian_rite':result=s['rite_exists']
   elif value.startswith(('global_var:','scope:','var:')):result=resolve(value,s,scope) is not None
   else:raise AssertionError(value)
  elif key=='has_title':result=value in s['owns']
  elif key=='has_character_flag':result=value in s['flags']
  elif key=='has_county_modifier':result=value in s['mods'].get(scope,{})
  elif key=='has_variable':result=value in s['vars'].get(scope,{})
  elif key.startswith('var:'):
   stored=s['vars'].get(scope,{}).get(key[4:])
   result=stored is not None and OPS[op](stored,float(value))
  elif key in ('gold','short_term_gold','piety'):
   result=OPS[op](s['gold' if key=='short_term_gold' else key],float(value))
  elif key=='current_date':result=OPS[op](s['date'],date(value))
  elif key=='is_landed':result=bool(s['owns'])==(value=='yes')
  elif key in ('is_available_adult','is_imprisoned','is_at_war'):
   result=s[key]==(value=='yes')
  elif key in ('is_valid_to_hire_court_position_type','can_employ_court_position_type'):result=s['bodyguard_available']
  elif key=='is_courtier_of':result=s['characters'][scope].get('employer')==value
  elif key=='is_alive':result=s['characters'][scope]['alive']==(value=='yes')
  elif key=='game_start_date':result=OPS[op](s['start'],date(value))
  elif key=='has_global_variable':result=value in s['globals']
  elif key=='has_game_rule':result=False # Historical tooltip visibility has no mechanics.
  else:raise AssertionError(('unmodelled trigger',key,value))
  results.append(result)
 return all(results)

def resolve(value,s,scope):
 if value=='this':return scope
 if value=='root.faith':return s['faith']
 if value=='root.culture':return s['culture']
 if value=='current_year':return s['date'][0]
 if value=='title:c_apahunik.holder':return 'root'
 if value.startswith('title:'):return value
 if value.startswith('scope:'):return s['scopes'].get(value[6:])
 if value.startswith('global_var:'):return s['globals'].get(value[11:])
 if value.startswith('var:'):return s['vars'].get(scope,{}).get(value[4:])
 try:return float(value)
 except ValueError:return value

def effects(text,s,scope='root'):
 previous_if=None
 for key,value,_ in fields(text):
  if key in SCRIPTED:
   assert value=='yes';effects(SCRIPTED[key][1],s,scope)
  elif key.startswith(('title:','scope:','global_var:','var:')) or key=='root':
   target=resolve(key,s,scope) if key!='root' else 'root'
   assert target is not None,('Missing effect scope',key)
   effects(value,s,target)
  elif key=='if':
   previous_if=condition(get(value,'limit'),s,scope)
   if previous_if:
    effects(' '.join(value[start:end] for field,arg,start,end in entries(value) if field!='limit'),s,scope)
  elif key=='else':
   assert previous_if is not None
   if not previous_if:effects(value,s,scope)
  elif key in ('name','trigger','ai_chance','custom_tooltip'):pass
  elif key=='set_variable':
   if '=' not in value:s['vars'].setdefault(scope,{})[value]=True
   else:s['vars'].setdefault(scope,{})[get(value,'name')]=resolve(get(value,'value'),s,scope)
  elif key=='set_global_variable':s['globals'][get(value,'name')]=resolve(get(value,'value'),s,scope)
  elif key=='save_scope_as':s['scopes'][value]=scope
  elif key=='create_character':
   ident='character:'+str(len(s['characters'])+1)
   s['characters'][ident]={'alive':True,'name':get(value,'name'),'culture':resolve(get(value,'culture'),s,scope),'dynasty':get(value,'dynasty'),'faith':resolve(get(value,'faith'),s,scope),'rite':None,'historical':False,'traits':[arg for field,arg,_ in fields(value) if field=='trait'],'flags':[],'employer':None,'skills':{field:float(get(value,field,'0')) for field in ('martial','prowess','learning','stewardship','diplomacy')},'trait_xp':{}}
   s['scopes'][get(value,'save_scope_as')]=ident
  elif key=='add_trait_xp':s['characters'][scope].setdefault('trait_xp',{})[get(value,'trait')]=float(get(value,'value'))
  elif key=='add_visiting_courtier':s['characters'][resolve(value,s,scope)]['guest']='root'
  elif key=='remove_courtier_or_guest':s['characters'][resolve(value,s,scope)].pop('guest',None)
  elif key=='add_courtier':s['characters'][resolve(value,s,scope)]['employer']='root'
  elif key=='appoint_court_position':
   assert s['bodyguard_available']
   ident=resolve(get(value,'recipient'),s,scope);assert s['characters'][ident]['employer']=='root'
   assert get(value,'court_position')=='bodyguard_court_position'
   s['bodyguard']=ident;s['bodyguard_available']=False
  elif key=='spawn_army':
   levies=int(get(value,'levies','0'));maa=get(value,'men_at_arms')
   assert get(value,'inheritable')=='no'
   if maa:assert get(maa,'type')=='light_horsemen' and get(maa,'stacks')=='2'
   s['troops']+=levies;s['cavalry']+=100 if maa else 0
  elif key=='add_opinion':
   assert get(value,'modifier')=='friendliness_opinion' and get(value,'target')=='root'
   s['opinions'][scope]=s['opinions'].get(scope,0)+float(get(value,'opinion'))
  elif key=='create_artifact':
   assert get(value,'type')=='book' and get(value,'visuals')=='book'
   assert get(value,'modifier')=='CAUC_scholarly_book_modifier'
   assert resolve(get(value,'creator'),s,scope) in s['characters']
   s['artifacts'].append(get(value,'name'))
  elif key=='imprison':
   ident=resolve(get(value,'target'),s,scope);assert ident in s['characters']
   s['characters'][ident]['imprisoned']=True
  elif key=='set_character_faith':
   assert value=='faith:orthodox';s['faith']=value;s['religion']='religion:christianity_religion'
  elif key=='historical_character_finalization_effect':s['characters'][scope]['historical']=True
  elif key=='add_trait':s['characters'][scope]['traits'].append(value)
  elif key=='add_county_modifier':
   assert scope.startswith('title:')
   s['mods'].setdefault(scope,{})[get(value,'modifier')]=int(get(value,'years'))
  elif key=='remove_county_modifier':s['mods'].setdefault(scope,{}).pop(value,None)
  elif key=='change_county_control':
   assert scope.startswith('title:')
   s['control'][scope]=s['control'].get(scope,50)+float(value)
  elif key in ('add_gold','add_piety','add_prestige','add_learning_lifestyle_xp','add_learning_skill','add_martial_lifestyle_xp'):
   metric={'add_gold':'gold','add_piety':'piety','add_prestige':'prestige','add_learning_lifestyle_xp':'learning','add_learning_skill':'learning_skill','add_martial_lifestyle_xp':'martial_xp'}[key]
   if key=='add_gold':assert float(value)>=0,'Native add_gold does not accept negative amounts'
   s[metric]+=float(value)
   if metric=='gold':assert s['gold']>=0,('unfunded option',s['gold'])
  elif key=='remove_short_term_gold':
   assert float(value)>=0
   s['gold']-=float(value)
   assert s['gold']>=0,('unfunded option',s['gold'])
  elif key=='add_character_flag':
   if '=' not in value:s['characters'][scope]['flags'].append(value)
   else:
    assert int(get(value,'years'))==1
    s['flags'].add(get(value,'flag'))
  elif key=='remove_character_flag':s['flags'].discard(value)
  elif key=='every_player':
   assert get(value,'trigger_event')
   s.setdefault('notices',[]).append(get(get(value,'trigger_event'),'id'))
  elif key=='trigger_event':
   assert s['queued'] is None, 'Two follow-ups scheduled by one choice'
   s['queued']=get(value,'id');s['delay']+=int(get(value,'days'))
  elif key=='create_rite_from_type':
   assert not s['rite_exists'],'Attempted duplicate foundation'
   assert get(value,'type')=='CAUC_tondrakian_rite' and get(value,'convert')=='yes'
   assert scope!='root' and s['characters'][scope]['faith']=='faith:armenian_apostolic'
   assert s['characters'][scope]['culture']=='culture:armenian'
   assert s['characters'][scope]['dynasty']=='none'
   assert s['characters'][scope]['name']=='CAUC_smbat_zarehavantsi_name'
   s['rite_exists']=True;s['foundations']+=1;s['native_founder']=scope
   s['characters'][scope]['rite']='rite:CAUC_tondrakian_rite'
  elif key=='set_character_rite':
   assert s['rite_exists']
   if scope=='root':s['rite']=value
   else:s['characters'][scope]['rite']=value
  elif key=='set_county_rite':
   assert s['rite_exists'] and scope in s['owns']
   s['county_rites'][scope]=value
  else:raise AssertionError(('unmodelled effect',key,value))

def fresh(county,faith,when,created=False,gold=1000):
 state={'faith':'faith:'+faith,'religion':'religion:' + ('islam_religion' if faith=='sunni' else 'christianity_religion'),
 'rite':'rite:armenian_rite','rite_exists':created,'foundations':0,'county_rites':{},
 'owns':{'title:'+county},'gold':gold,'piety':1000,'prestige':0,'learning':0,
 'start':date(when),'date':date(when),'flags':set(),'mods':{},'vars':{},'control':{},'queued':None,'delay':0,
 'bodyguard_available':True,'bodyguard':None,'troops':0,'cavalry':0,'artifacts':[],'opinions':{},'culture':'culture:armenian','learning_skill':0,'martial_xp':0,
 'is_available_adult':True,'is_imprisoned':False,'is_at_war':False,'globals':{},'characters':{'root':{'alive':True,'traits':[],'flags':[]}},'scopes':{},'native_founder':None}
 if created:
  state['characters']['character:1']={'alive':False,'name':'CAUC_smbat_zarehavantsi_name','culture':'culture:armenian','dynasty':'none','faith':'faith:armenian_apostolic','rite':'rite:CAUC_tondrakian_rite','historical':True,'traits':['historical_character'],'flags':[]}
  state['native_founder']='character:1'
  state['globals']={'CAUC_tondrakian_founder':'character:1','CAUC_tondrakian_origin':'title:c_apahunik','CAUC_tondrakian_founding_year':867}
 return state

def paths(key,state,events,flow,results,depth=0):
 assert depth<10,'Cyclic story'
 body=events[key][1]
 assert condition(get(body,'trigger'),state),('Unexpected blocked continuation',key)
 lost=copy.deepcopy(state);lost['owns'].clear()
 assert not condition(get(body,'trigger'),lost),('Event survives ownership loss',key)
 effects(get(body,'immediate'),state)
 options=[arg for field,arg,_ in fields(body) if field=='option']
 available=[arg for arg in options if condition(get(arg,'trigger'),state)]
 assert available,('No affordable option',key)
 for option in available:
  successor=copy.deepcopy(state);successor['queued']=None
  effects(option,successor)
  assert successor['delay']<365,'Story outlasts its active flag'
  target=successor['queued']
  if target:paths(target,successor,events,flow,results,depth+1)
  else:
   assert 'CAUC_'+flow['flow']+'_active' not in successor['flags']
   mods=set(successor['mods'].get('title:'+flow['county'],{}))&set(flow['policy_modifiers'])
   assert len(mods)==1,('Policy count',mods)
   assert successor['foundations']<=1
   if flow['flow']=='ani_sanctuary':assert not successor['county_rites']
   if successor['county_rites']:
    assert set(successor['county_rites'])=={'title:c_apahunik'}
    assert successor['rite']=='rite:CAUC_tondrakian_rite'
   results.append(successor)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,required=True)
 ap.add_argument('--mod',type=Path,default=ROOT);ap.add_argument('--output',type=Path,default=ROOT/'research/religious-validation.json')
 args=ap.parse_args();mod=args.mod
 events=registry([mod],'events');decisions=registry([mod],'common/decisions')
 manifest=json.loads((ROOT/'research/religious-content.json').read_text())
 scenarios=[]
 for flow in manifest['flows']:
  body=decisions[flow['decision']][1]
  assert get(get(body,'cooldown'),'years')=='10'
  assert float(get(get(body,'cost'),'gold'))==flow['cost']
  assert 'add_gold' not in canonical(get(body,'effect')),'Decision charges outside its cost block'
  for faith,when in [('armenian_apostolic','1080.1.1'),('catholic','1180.1.1'),('sunni','1080.1.1')]:
   for created in (False,True):
    s=fresh(flow['county'],faith,when,created)
    allowed=condition(get(body,'is_shown'),s) and condition(get(body,'is_valid'),s)
    if not allowed:continue
    assert condition(get(body,'is_valid_showing_failures_only'),s)
    at_war=copy.deepcopy(s);at_war['is_at_war']=True
    assert not condition(get(body,'is_valid_showing_failures_only'),at_war)
    s['gold']-=flow['cost'];effects(get(body,'effect'),s)
    assert not condition(get(body,'is_valid'),s),'Can restart while active'
    terminals=[];paths(s['queued'],s,events,flow,terminals)
    assert terminals
    for result in terminals:
     assert not condition(get(body,'is_valid'),result),'Can bypass current county policy'
    scenarios.append({'flow':flow['flow'],'faith':faith,'existing_rite':created,'completed_paths':len(terminals),'founding_paths':sum(x['foundations'] for x in terminals),'adopting_paths':sum(bool(x['county_rites']) for x in terminals)})
  # The final option in every event is free; verify zero-gold continuation too.
  for key,(_,event_body,_) in events.items():
   if not key.startswith('CAUC.') or get(event_body,'trigger').find('title:'+flow['county'])<0:continue
   if int(key.split('.')[1])<100 or int(key.split('.')[1])>=149:continue
   s=fresh(flow['county'],'sunni' if flow['flow']=='derbent_guards' else 'armenian_apostolic','1180.1.1',gold=0)
   if flow['flow'] in ('lori_council','ani_sanctuary','alan_mission'):s['vars'].setdefault('title:'+flow['county'],{})['CAUC_'+flow['flow']+'_choice']=1
   available=[arg for field,arg,_ in fields(event_body) if field=='option' and condition(get(arg,'trigger'),s)]
   assert available,('No zero-gold option',key)
   for opt in available:
    if flow['flow']=='tondrakian_inquiry':effects('CAUC_tondrakian_prepare_inquiry_effect = yes',s)
    effects(get(event_body,'immediate'),s)
    effects(opt,copy.deepcopy(s))
  # Exercise policy replacement against all possible stale policies at once.
  for key,(_,event_body,_) in events.items():
   if not key.startswith('CAUC.'):continue
   for field,opt,_ in fields(event_body):
    if field!='option' or not any('modifier = '+name in opt for name in flow['policy_modifiers']):continue
    s=fresh(flow['county'],'sunni' if flow['flow']=='derbent_guards' else 'armenian_apostolic','1180.1.1')
    s['mods']['title:'+flow['county']]={name:5 for name in flow['policy_modifiers']}
    if flow['flow']=='tondrakian_inquiry':effects('CAUC_tondrakian_prepare_inquiry_effect = yes',s)
    effects(get(event_body,'immediate'),s)
    effects(opt,s)
    assert len(set(s['mods']['title:'+flow['county']])&set(flow['policy_modifiers']))==1

 # Native mechanics and doctrine references, including absence of faith duplication.
 native=registry([args.game],'common/religion/tenet_types')
 actual=registry([args.game,mod],'common/religion/tenet_types')
 for key,(p,body,_) in native.items():
  amended=actual[key][1]
  if key=='tenet_unrelenting_faith':
   mechanical=lambda b:[(k,canonical(v)) for k,v,_ in fields(b) if k not in ('name','desc')]
   assert mechanical(body)==mechanical(amended)
   assert amended.count('desc = tenet_unrelenting_faith_zandik_')==body.count('desc = tenet_unrelenting_faith_zandik_')+2
  else:assert canonical(body)==canonical(amended),('Changed native tenet',key)
 rite=registry([mod],'common/religion/rite_types')['CAUC_tondrakian_rite'][1]
 assert get(rite,'faith')=='armenian_apostolic' and get(rite,'create')=='no'
 assert canonical(get(rite,'tenets'))==['tenet_aniconism','tenet_communal_possessions','tenet_unrelenting_faith']
 doctrines=registry([args.game],'common/religion/doctrine_types')
 # Doctrine definitions are nested in groups; compare against actual native tokens.
 doctrine_text=' '.join(p.read_text(encoding='utf-8-sig') for p in (args.game/'common/religion/doctrine_types').glob('*.txt'))
 for key in canonical(get(rite,'doctrines')):assert re.search(r'\b'+key+r'\s*=\s*\{',doctrine_text),key
 assert 'doctrine_gender_equal' in canonical(get(rite,'doctrines'))
 assert 'doctrine_clerical_gender_either' in canonical(get(rite,'doctrines'))
 assert 'doctrine_adultery_men_accepted' in canonical(get(rite,'doctrines'))
 assert 'doctrine_adultery_women_accepted' in canonical(get(rite,'doctrines'))

 source={lang:localization(ROOT,lang) for lang in ('english','simp_chinese','french')}
 assert len(source['english'])>=838
 marks=lambda v: sorted(re.findall(r'\$[^$]+\$|\[[^\]]+\]|#[A-Za-z_!]+|@[^!\s]+!',v))
 for lang,values in source.items():
  assert set(values)==set(source['english']),('Source key coverage',lang)
  for key,value in values.items():assert marks(value)==marks(source['english'][key]),('Changed interpolation',lang,key)
  installed=localization(mod,lang)
  for key,value in values.items():assert installed[key]==value,('Installed translation differs',lang,key)
 # Founder death, movement and a serialization round trip must not change the
 # historical link or create a second Smbat. Speaker replacement is independent.
 s=fresh('c_apahunik','armenian_apostolic','867.1.1')
 effects('CAUC_tondrakian_prepare_inquiry_effect = yes',s)
 founder=s['native_founder'];snap=copy.deepcopy(s['globals'])
 assert founder==snap['CAUC_tondrakian_founder']
 assert s['characters'][founder]['historical']
 s['characters'][founder]['alive']=False
 s['date']=date('1000.1.1');s['scopes'].clear()
 preserved=json.loads(json.dumps({'characters':s['characters'],'globals':s['globals'],'vars':s['vars']}))
 for field in preserved:s[field]=preserved[field]
 effects('CAUC_tondrakian_recover_speaker_effect = yes',s)
 speaker=s['scopes']['CAUC_tondrakian_speaker']
 assert speaker!=founder and s['characters'][speaker]['alive']
 assert s['characters'][speaker]['rite']=='rite:CAUC_tondrakian_rite'
 assert s['globals']==snap and s['foundations']==1
 assert s['globals']['CAUC_tondrakian_founder'] in s['characters']
 assert s['characters'][s['globals']['CAUC_tondrakian_founder']]['name']=='CAUC_smbat_zarehavantsi_name'
 founder_desc=get(rite,'desc')
 assert 'is_alive' not in canonical(founder_desc),'Description must not lose a dead founder'
 for lang in source:
  text=source[lang]['CAUC_tondrakian_rite_founded_desc']
  assert "GetGlobalVariable('CAUC_tondrakian_founder').Char.GetFullName]" in text
  assert 'GetFullNameNoTooltip' not in text
  assert "GetGlobalVariable('CAUC_tondrakian_origin')" in text
  assert "GetGlobalVariable('CAUC_tondrakian_founding_year')" in text
  assert "Custom('GetGenericRiteTenetSentence')" in text
 image=Image.open(mod/'gfx/interface/icons/faith/CAUC_tondrakian.dds')
 assert image.size==(100,100) and image.mode=='RGBA' and image.getchannel('A').getextrema()==(0,255)
 report={'errors':[],'scope':'Static model and assets only; no engine or UI execution','scenarios':scenarios,'completed_paths':sum(x['completed_paths'] for x in scenarios),'native_tenets_preserved':len(native),'localization_keys_per_language':len(source['english']),'languages':list(source),'icon':{'size':list(image.size),'mode':image.mode,'alpha':list(image.getchannel('A').getextrema()),'sha256':hashlib.sha256((mod/'gfx/interface/icons/faith/CAUC_tondrakian.dds').read_bytes()).hexdigest()},'checks':['Ownership loss blocks every delayed stage','Every stage has an option at zero gold','Paid branches cannot overspend gold','No simultaneous policies even with stale modifiers','No duplicate rite foundation; existing rite is reused','Named Armenian historical founder creates and adopts the rite; ruler and Apahunik may join; Ani never converts its county','Ten-year decision cooldown and one-year timed active lock','All native tenet mechanics unchanged','English/French/Chinese source and installed text match, including interpolation markers']}
 report['checks'].extend(['Founder is Armenian, complete name is retained and no noble dynasty is fabricated','Founder death and serialization preserve the original character, place and year references','Living follower replaces a dead speaker without recreating or replacing the founder','Native generic tenet sentence and tooltip-enabled GetFullName used in all three foundation descriptions'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({key:report[key] for key in ('completed_paths','native_tenets_preserved','localization_keys_per_language','errors')}))

if __name__=='__main__':main()
