#!/usr/bin/env python3
"""Embed authored Caucasus content in RICE; build complete compatibility presets."""
import argparse,json,os,shutil,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'authoring/caucasus_flavor_pack'
sys.path.insert(0,str(SOURCE/'tools'))
from ck3_script import entries,registry,canonical,write
from import_ce import localization,CULTURES
VISUALS={'ethnicities','coa_gfx','building_gfx','clothing_gfx','unit_gfx','house_coa_frame','house_coa_mask_offset','house_coa_mask_scale'}
PROFILE_DEPS={'base':[],'epe':['Ethnicities and Portraits Expanded'],'ce-epe':['Ethnicities and Portraits Expanded','Culture Expanded']}
VERSION='1.20.0-beta-1-expanded.2-caucasus-alpha'

def replace_record(text,key,raw):
 for k,b,a,z in entries(text):
  if k==key:return text[:a]+raw+text[z:]
 raise KeyError(key)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--game',type=Path,required=True)
 ap.add_argument('--embed',action='store_true')
 ap.add_argument('--profile',choices=list(PROFILE_DEPS))
 ap.add_argument('--output',type=Path,default=ROOT.parent/'caucasus-built-in')
 ap.add_argument('--zip',action='store_true')
 a=ap.parse_args()
 if a.embed:
  for folder in ['common','events','map_data','localization','gfx']:
   for p in (SOURCE/folder).rglob('*'):
    if p.is_file():
     q=ROOT/'RICE'/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True)
     if q.exists():q.unlink()
     shutil.copy2(p,q)
  # Preserve CE gameplay. Use installed vanilla appearance until the EPE preset
  # replaces these fields with the exact source CE definitions.
  original=registry([SOURCE],'common/culture/cultures');vanilla=registry([a.game],'common/culture/cultures')
  donors={'circassian':'georgian','udi':'armenian','dagestani':'georgian','abkhaz':'georgian','lazi':'georgian','ce_svan':'georgian','tat':'daylamite','alan':'alan'}
  converted={}
  for key in CULTURES:
   raw=original[key][2]
   donor={k:vanilla[donors[key]][1][x:z] for k,v,x,z in entries(vanilla[donors[key]][1]) if k in VISUALS}
   # Replace only CE visual assignments present in the culture, retaining all
   # gameplay tokens and preserving the absence of optional visual fields.
   start=raw.index('{')+1;body=raw[start:raw.rfind('}')]
   for field,value,x,z in reversed(entries(body)):
    if field in VISUALS:
     replacement=donor.get(field,'')
     body=body[:x]+replacement+body[z:]
   converted[key]=raw[:start]+body+'}'
  p=ROOT/'RICE/common/culture/cultures/CAUC_CE_common_culture_cultures.txt'
  text=p.read_text(encoding='utf-8-sig')
  for key in CULTURES:
   if key!='alan':text=replace_record(text,key,converted[key])
  write(p,text)
  p=ROOT/'RICE/common/culture/cultures/00_iranian.txt'
  write(p,replace_record((a.game/'common/culture/cultures/00_iranian.txt').read_text(encoding='utf-8-sig'),'alan',converted['alan']))
  # English-first fallback coverage is explicit; existing translations and
  # native vanilla place/culture terms are kept, rather than machine translated.
  en=localization(ROOT/'RICE','english');fallbacks={}
  for lang in ['simp_chinese','french','german','spanish','russian','polish','japanese']:
   fallback_path=ROOT/'RICE/localization'/lang/('CAUC_english_fallback_l_'+lang+'.yml')
   if fallback_path.exists():fallback_path.unlink()
   have=localization(ROOT/'RICE',lang);v=localization(a.game,lang)
   missing=sorted(set(en)-set(have))
   write(ROOT/'RICE/localization'/lang/('CAUC_english_fallback_l_'+lang+'.yml'),'l_'+lang+':\n'+'\n'.join(' '+k+':0 "'+v.get(k,en[k])+'"' for k in missing))
   fallbacks[lang]=missing
  (ROOT/'reports/caucasus-localization-fallbacks.json').write_text(json.dumps({'translation_status':'English gameplay complete; other languages have explicit English fallbacks and vanilla terms, not completed translations.','languages':fallbacks},ensure_ascii=False,indent=2)+'\n')
  manifest=json.loads((SOURCE/'research/ce-import-manifest.json').read_text())
  manifest['integration']='Built into RICE Expanded. Base uses vanilla visual fallbacks; EPE and CE+EPE install presets embed compatibility and exact CE appearance definitions.'
  for name in ['ce-import-manifest.json','authored-content.json','vanilla-terminology.json','art-validation.json']:
   target=ROOT/'reports'/('caucasus-'+name)
   if name=='ce-import-manifest.json':target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
   else:shutil.copy2(SOURCE/'research'/name,target)
  for p in [ROOT/'RICE/descriptor.mod',ROOT/'RICE.mod']:
   s=p.read_text();import re;s=re.sub(r'version="[^"]+"','version="'+VERSION+'"',s,count=1);write(p,s,False)
  print('Embedded Caucasus scripts, localization, vanilla visual fallbacks and artwork in RICE.')
 if a.profile:
  target=a.output/a.profile;mod=target/'RICE'
  if mod.exists():raise SystemExit('Output already exists; choose a fresh output directory.')
  # Hard-linked unchanged assets keep three build trees small. Overwrites unlink
  # their destinations first and never mutate shared source files.
  shutil.copytree(ROOT/'RICE',mod,copy_function=os.link,ignore=shutil.ignore_patterns('.DS_Store','__pycache__'))
  layers=[]
  if a.profile!='base':layers=[ROOT/'RICE-EPE-Compatch']
  if a.profile=='ce-epe':layers.append(ROOT/'RICE+CE Compatch for 1.19')
  if a.profile!='base':layers.append(SOURCE)
  if a.profile=='ce-epe':layers.append(ROOT/'authoring/caucasus_flavor_pack_ce_compat')
  for layer in layers:
   for folder in ['common','events','map_data','localization','gfx']:
    for p in (layer/folder).rglob('*'):
     if p.is_file():
      q=mod/p.relative_to(layer);q.parent.mkdir(parents=True,exist_ok=True)
      if q.exists():q.unlink()
      shutil.copy2(p,q)
  d=(ROOT/'RICE/descriptor.mod').read_text()
  d+='dependencies={ '+' '.join('"'+x+'"' for x in PROFILE_DEPS[a.profile])+' }\n'
  (mod/'descriptor.mod').unlink();write(mod/'descriptor.mod',d,False)
  write(target/'RICE.mod',d+'path="mod/RICE"\n',False)
  for filename in ['CAUCASUS-Expanded.md','CHANGELOG-Expanded.md']:
   shutil.copy2(ROOT/filename,target/filename)
  report={'profile':a.profile,'embedded_layers':[x.name for x in layers],'external_compatibility_mods':[],'required_base_mods':PROFILE_DEPS[a.profile],'version':VERSION}
  (target/'BUILT-IN-PROFILE.json').write_text(json.dumps(report,indent=2)+'\n')
  print(json.dumps(report))
  if a.zip:
   archive=a.output/('RICE-Expanded-'+a.profile+'-Caucasus-Alpha.zip')
   with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for p in sorted(target.rglob('*')):
     if p.is_file():z.write(p,p.relative_to(target))
   print('Package: '+str(archive))
if __name__=='__main__':main()
