#!/usr/bin/env python3
"""Package complete RICE directories, with no separate compatibility mod."""
import argparse,concurrent.futures,hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--builds',type=Path,required=True);a=ap.parse_args()
 def package(profile):
  target=a.builds/profile
  (target/'reports').mkdir(exist_ok=True)
  for name in ['caucasus-integrated-'+profile+'.json','caucasus-embedded-compatibility.json','caucasus-art-validation.json','caucasus-ce-import-manifest.json','caucasus-authored-content.json','caucasus-localization-fallbacks.json']:
   shutil.copy2(ROOT/'reports'/name,target/'reports'/name)
  for name in ['CAUCASUS-Expanded.md','CHANGELOG-Expanded.md']:shutil.copy2(ROOT/name,target/name)
  archive=a.builds/('RICE-Expanded-'+profile+'-Caucasus-Alpha.zip')
  with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
   for p in sorted(target.rglob('*')):
    if p.is_file():z.write(p,p.relative_to(target))
  with zipfile.ZipFile(archive) as z:
   names=set(z.namelist())
   for required in ['RICE.mod','RICE/descriptor.mod','RICE/common/decisions/CAUC_regional_decisions.txt','RICE/events/CAUC_regional_events.txt','RICE/gfx/interface/illustrations/decisions/CAUC_derbent_pass.dds']:
    assert required in names,required
   assert not any(x.endswith('.mod') and x not in ['RICE.mod','RICE/descriptor.mod'] for x in names)
  h=hashlib.sha256()
  with archive.open('rb') as f:
   for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
  print(profile,archive.stat().st_size,'bytes',flush=True)
  return {'profile':profile,'filename':archive.name,'bytes':archive.stat().st_size,'sha256':h.hexdigest(),'mod_registrations':['RICE.mod']}
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:result=list(pool.map(package,['base','epe','ce-epe']))
 (a.builds/'packages.json').write_text(json.dumps(result,indent=2)+'\n')
 (a.builds/'SHA256SUMS.txt').write_text(''.join(r['sha256']+'  '+r['filename']+'\n' for r in result))
if __name__=='__main__':main()
