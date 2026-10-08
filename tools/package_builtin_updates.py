#!/usr/bin/env python3
"""Build in-place RICE update ZIPs against expanded.1; no extra mod registration."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--builds',type=Path,required=True);ap.add_argument('--baseline',default='8b2b5193');a=ap.parse_args()
 raw=subprocess.check_output(['git','ls-tree','-rz',a.baseline,'RICE'],cwd=ROOT);old={}
 for line in raw.split(b'\0'):
  if not line:continue
  meta,name=line.split(b'\t',1);old[name.decode()[len('RICE/'):]]=meta.split()[-1].decode()
 candidates={'descriptor.mod'}
 for layer in [ROOT/'authoring/caucasus_flavor_pack',ROOT/'RICE-EPE-Compatch',ROOT/'RICE+CE Compatch for 1.19',ROOT/'authoring/caucasus_flavor_pack_ce_compat']:
  for folder in ['common','events','map_data','localization','gfx']:
   candidates.update(p.relative_to(layer).as_posix() for p in (layer/folder).rglob('*') if p.is_file())
 candidates.update(p.relative_to(ROOT/'RICE').as_posix() for p in (ROOT/'RICE/localization').rglob('CAUC_english_fallback_*.yml'))
 manifest=[]
 for profile in ['base','epe','ce-epe']:
  target=a.builds/profile;delta=[]
  for rel in sorted(candidates):
   p=target/'RICE'/rel
   if not p.is_file():continue
   data=p.read_bytes();sha=hashlib.sha1(('blob '+str(len(data))+'\0').encode()+data).hexdigest()
   if sha!=old.get(rel):delta.append(rel)
  archive=a.builds/('RICE-Expanded-'+profile+'-Caucasus-Built-In-Update.zip')
  with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for rel in delta:z.write(target/'RICE'/rel,'RICE/'+rel)
   z.write(target/'RICE.mod','RICE.mod');z.write(ROOT/'CAUCASUS-Expanded.md','CAUCASUS-Expanded.md')
   for p in (target/'reports').glob('*.json'):z.write(p,'reports/'+p.name)
   z.writestr('UPDATE-INSTRUCTIONS.txt','Requires an existing RICE Expanded expanded.1 or expanded.2 installation. Extract over its RICE folder. Caucasus gameplay and compatibility are built into RICE itself. Select one preset, load RICE Expanded after its required base mods, and disable old separate compatibility mods. Caucasus localization is complete in English, Simplified Chinese and French; five other languages retain fallbacks. This update adds five religious stories and the Tondrakian rite. It replaces the native tenet definitions file only to extend name/description selection for that rite, preserving native mechanics from the recorded 1.20 source. Keep a backup.\n')
  with zipfile.ZipFile(archive) as z:
   assert z.testzip() is None
   assert sorted(n for n in z.namelist() if n.endswith('.mod'))==['RICE.mod','RICE/descriptor.mod']
   for rel in delta:assert z.read('RICE/'+rel)==(target/'RICE'/rel).read_bytes()
  manifest.append({'profile':profile,'name':archive.name,'bytes':archive.stat().st_size,'changed_files':len(delta),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()})
 (a.builds/'updates.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (a.builds/'SHA256SUMS-updates.txt').write_text(''.join(r['sha256']+'  '+r['name']+'\n' for r in manifest))
 print(json.dumps(manifest));return 0
if __name__=='__main__':raise SystemExit(main())
