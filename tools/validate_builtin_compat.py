#!/usr/bin/env python3
"""Check RICE-owned culture and pillar uniqueness in single-directory presets."""
import argparse,json
from pathlib import Path
import validate_compatches as v
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser()
 for key in ['game','epe','ce','builds']:ap.add_argument('--'+key,type=Path,required=True)
 a=ap.parse_args();owned={cat:set() for cat in ['culture/cultures','culture/pillars']}
 for cat in owned:
  for pattern in ['RICE*.txt','zzzzz_RICE*.txt']:
   for p in (ROOT/'RICE/common'/cat).glob(pattern):
    owned[cat].update(k for k,b,x,z in v.entries(p.read_text(encoding='utf-8-sig')))
 report={}
 for profile in ['base','epe','ce-epe']:
  target=a.builds/profile;mod=target/'RICE'
  layers=[a.game]+([a.epe] if profile!='base' else [])+([a.ce] if profile=='ce-epe' else [])+[mod];errors=[]
  for cat,keys in owned.items():
   reg=v.registry(layers,cat)
   for key in keys:
    if len(reg.get(key,[]))!=1:errors.append({'category':cat,'key':key,'count':len(reg.get(key,[]))})
  if sorted(p.name for p in target.glob('*.mod'))!=['RICE.mod']:errors.append({'extra_mod_registration':profile})
  report[profile]={'errors':errors,'rice_owned_cultures':len(owned['culture/cultures']),'rice_owned_pillars':len(owned['culture/pillars']),'mod_registrations':['RICE.mod']}
 (ROOT/'reports/caucasus-embedded-compatibility.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:len(r['errors']) for k,r in report.items()}));return any(r['errors'] for r in report.values())
if __name__=='__main__':raise SystemExit(main())
