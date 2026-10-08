#!/usr/bin/env python3
"""One unified update against expanded.1; retired preset scripts are masked."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--builds',type=Path,required=True);ap.add_argument('--baseline',default='8b2b5193');a=ap.parse_args()
 raw=subprocess.check_output(['git','ls-tree','-rz',a.baseline,'RICE'],cwd=ROOT);old={}
 for line in raw.split(b'\0'):
  if line:
   meta,name=line.split(b'\t',1);old[name.decode()[len('RICE/'):]]=meta.split()[-1].decode()
 target=a.builds/'unified';mod=target/'RICE';delta=[]
 for p in sorted(mod.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(mod).as_posix();data=p.read_bytes()
  sha=hashlib.sha1(('blob '+str(len(data))+'\0').encode()+data).hexdigest()
  if sha!=old.get(rel):delta.append(rel)
 # Legacy overlays cannot keep defining superseded objects after an update.
 retired=set()
 for layer in [ROOT/'RICE-EPE-Compatch',ROOT/'RICE+CE Compatch for 1.19',ROOT/'authoring/caucasus_flavor_pack_ce_compat']:
  for folder in ['common','events','map_data','localization']:
   retired.update(p.relative_to(layer).as_posix() for p in (layer/folder).rglob('*') if p.is_file() and not (mod/p.relative_to(layer)).exists() and p.suffix in ('.txt','.yml'))
 archive=a.builds/'RICE-Expanded-Unified-1.20-expanded.3.3-Update.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for rel in delta:z.write(mod/rel,'RICE/'+rel)
  # Removing a retired file is different from masking a file supplied by CE.
  # Empty title files would suppress CE's legitimate database on an update.
  z.writestr('RETIRED-FILES.txt',''.join(rel+'\n' for rel in sorted(retired)))
  z.writestr('finish-unified-update.py',"""from pathlib import Path
import argparse,shutil
p=argparse.ArgumentParser();p.add_argument('--mod-dir',type=Path,default=Path(__file__).resolve().parent/'RICE');a=p.parse_args()
root=a.mod_dir.resolve()
if 'RICE Expanded' not in (root/'descriptor.mod').read_text():raise SystemExit('Choose an existing RICE Expanded directory.')
backup=root.parent/'RICE-Unified-3.3-Retired-Backup'
for line in (Path(__file__).resolve().parent/'RETIRED-FILES.txt').read_text().splitlines():
 rel=Path(line)
 if rel.is_absolute() or '..' in rel.parts:raise SystemExit('Invalid retired-file path.')
 target=root/rel
 if target.exists():
  saved=backup/rel;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved);target.unlink();print('Backed up and removed:',rel)
print('Unified update cleanup complete. CE and EPE source mods are unchanged.')
""")
  for name in ['RICE.mod','CAUCASUS-Expanded.md','CHANGELOG-Expanded.md']:z.write(target/name,name)
  for p in (target/'reports').glob('*.json'):z.write(p,'reports/'+p.name)
  z.writestr('UPDATE-INSTRUCTIONS.txt','This is an update for an existing RICE Expanded expanded.1–expanded.3.2 installation. Extract over the same RICE folder. Remove RICE/common/landed_titles/00_decisions_expanded_titles.txt from the old RICE installation if present; do not remove it from the CE mod. Alternatively run finish-unified-update.py with Python 3 and --mod-dir pointing to the updated RICE Expanded directory; the retired file is backed up before removal. CE and EPE are optional. Disable old separate RICE compatibility patches and load Expanded after culture/portrait/map mods. The Full archive is available for fresh installations. Starting culture assignments require a new campaign. Native reference and script-state checks only; no engine run. Keep a backup.\n')
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  for rel in delta:assert z.read('RICE/'+rel)==(mod/rel).read_bytes()
 row={'profile':'unified','filename':archive.name,'bytes':archive.stat().st_size,'changed_files':len(delta),'retired_files_to_remove':sorted(retired),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
 (a.builds/'updates.json').write_text(json.dumps([row],indent=2)+'\n')
 with (a.builds/'SHA256SUMS.txt').open('a') as f:f.write(row['sha256']+'  '+row['filename']+'\n')
 print(json.dumps(row),flush=True)
if __name__=='__main__':main()
