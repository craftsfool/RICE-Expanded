#!/usr/bin/env python3
"""Package one complete, self-contained RICE directory."""
import argparse,hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--builds',type=Path,required=True);a=ap.parse_args()
 target=a.builds/'unified';(target/'reports').mkdir(exist_ok=True)
 for p in (ROOT/'reports').glob('*.json'):
  if p.name.startswith(('unified-','caucasus-','story-design-')) and '-integrated-' not in p.name and p.name!='caucasus-embedded-compatibility.json':shutil.copy2(p,target/'reports'/p.name)
 for name in ['CAUCASUS-Expanded.md','CHANGELOG-Expanded.md']:shutil.copy2(ROOT/name,target/name)
 archive=a.builds/'RICE-Expanded-Unified-1.20-expanded.3.3-Full.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
  for p in sorted(target.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(target))
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  names=set(z.namelist())
  for required in ['RICE.mod','RICE/descriptor.mod','RICE/common/on_action/CAUC_tondrakian_start_on_actions.txt','RICE/events/CAUC_religious_events.txt','RICE/gfx/interface/illustrations/decisions/CAUC_derbent_pass.dds']:assert required in names
  assert sorted(x for x in names if x.endswith('.mod'))==['RICE.mod','RICE/descriptor.mod']
  assert 'dependencies' not in z.read('RICE/descriptor.mod').decode()
 h=hashlib.sha256()
 with archive.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 row={'profile':'unified','filename':archive.name,'bytes':archive.stat().st_size,'sha256':h.hexdigest(),'required_external_mods':[],'mod_registrations':['RICE.mod']}
 (a.builds/'packages.json').write_text(json.dumps([row],indent=2)+'\n');(a.builds/'SHA256SUMS.txt').write_text(row['sha256']+'  '+row['filename']+'\n')
 print(json.dumps(row),flush=True)
if __name__=='__main__':main()
