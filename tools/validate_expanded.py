#!/usr/bin/env python3
"""Validate CK3 script structure, religion registries and localization coverage.

This checks structural release invariants, not all CK3 scope semantics. Pass the
installed vanilla game directory to resolve faith/rite and localization references.
"""
import argparse, collections, json, re, subprocess
from pathlib import Path
from validate_dds import audit as audit_dds
ROOT=Path(__file__).resolve().parents[1]
TOKEN=re.compile(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}]|[^\s{}#"]+')
ENTRY=re.compile(r'^\s*([^\s:#]+):\d*\s+"(.*)"\s*(?:#.*)?$')
LANGUAGES=('english','simp_chinese','french','german','spanish','russian','polish','japanese')
def tokens(text):
 return [m.group() for m in TOKEN.finditer(text) if not m.group().startswith('#')]
def blocks(text):
 ts=tokens(text);depth=0;result=[];start=None
 for i,t in enumerate(ts):
  if t=='{':
   if depth==0 and i>=2 and ts[i-1]=='=':start=(ts[i-2],i)
   depth+=1
  elif t=='}':
   depth-=1
   if depth<0:raise ValueError('unmatched closing brace')
   if depth==0 and start:result.append((start[0],ts[start[1]+1:i]));start=None
 if depth:raise ValueError(f'unclosed braces: {depth}')
 return result

def localization(root,language):
 result={};dups=[];malformed=[];files=sorted(root.rglob('*_l_'+language+'.yml'),key=lambda p:('replace' in p.parts,str(p)))
 for p in files:
  seen=set()
  for n,line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(),1):
   m=ENTRY.match(line)
   if m:
    k,v=m.groups()
    if k in seen:dups.append({'file':str(p.relative_to(root)),'key':k,'line':n})
    seen.add(k);result[k]={'value':v,'file':str(p.relative_to(root)),'line':n}
   elif line.strip() and not line.lstrip().startswith('#') and not re.fullmatch(r'\s*l_[a-z_]+:\s*',line):
    malformed.append({'file':str(p.relative_to(root)),'line':n,'text':line[:160]})
 return result,dups,malformed

def registry(root,kind):
 d=collections.defaultdict(list)
 for p in (root/'common/religion'/kind).glob('*.txt'):
  for k,b in blocks(p.read_text(encoding='utf-8-sig')):d[k].append(str(p.relative_to(root)))
 return d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path);ap.add_argument('--output',type=Path,default=ROOT/'reports/static-validation.json');args=ap.parse_args()
 errors=[];warnings=[];mod=ROOT/'RICE'
 dds=audit_dds(mod)
 errors.extend({'dds': item} for item in dds['errors'])
 for p in mod.rglob('*'):
  if p.suffix not in ('.txt','.gui'):continue
  try:blocks(p.read_text(encoding='utf-8-sig'))
  except (UnicodeError,ValueError) as e:errors.append({'file':str(p.relative_to(ROOT)),'error':str(e)})
 registries={k:registry(mod,k) for k in ('faith_types','rite_types','religion_types')}
 for kind,defs in registries.items():
  for key,paths in defs.items():
   if len(paths)>1:errors.append({'duplicate_definition':key,'kind':kind,'files':paths})
 for p in (mod/'common/decisions').glob('*.txt'):
  for k,ts in blocks(p.read_text(encoding='utf-8-sig')):
   depth=0;widgets=0
   for i,t in enumerate(ts):
    if depth==0 and t=='widget' and ts[i+1:i+3]==['=','{']:widgets+=1
    if t=='{':depth+=1
    elif t=='}':depth-=1
   if widgets>1:errors.append({'decision':k,'widgets':widgets,'file':str(p.relative_to(ROOT))})
 vanilla={kind:registry(args.game,kind) if args.game else {} for kind in registries}
 if args.game:
  known={kind:set(defs)|set(vanilla[kind]) for kind,defs in registries.items()}
  for p in mod.rglob('*.txt'):
   s=' '.join(tokens(p.read_text(encoding='utf-8-sig')))
   for scope,kind in [('faith','faith_types'),('rite','rite_types'),('religion','religion_types')]:
    for key in sorted(set(re.findall(r'\b'+scope+r':([A-Za-z0-9_]+)',s))-known[kind]):
     warnings.append({'unresolved_scope':scope+':'+key,'file':str(p.relative_to(ROOT))})
 languages={};en,_,_=localization(mod/'localization','english')
 vanilla_loc={}
 if args.game:
  vanilla_loc,_,_=localization(args.game/'localization','english')
 known_loc=set(en)|set(vanilla_loc)|{"EFFECT_LIST_BULLET","VALUE","ORDER"}
 for language in LANGUAGES:
  values,dups,bad=localization(mod/'localization',language)
  missing=sorted(set(en)-set(values))
  if missing:errors.append({'language':language,'missing_keys':missing})
  errors.extend(dict(language=language,malformed_localization=x) for x in bad)
  if dups:warnings.append({'language':language,'duplicate_keys_within_file':dups})
  for p in (mod/'localization').rglob('*_l_'+language+'.yml'):
   b=p.read_bytes();lines=b.decode('utf-8-sig').splitlines()
   headers=[line.strip() for line in lines if re.fullmatch(r'\s*l_[a-z_]+:\s*',line)]
   if not b.startswith(b'\xef\xbb\xbf') or headers!=['l_'+language+':']:errors.append({'localization_encoding_or_header':str(p.relative_to(ROOT)),'headers':headers})
  invalid=[];unresolved=[];known_language_loc=known_loc|set(values)
  for k,v in values.items():
   if re.search(r'Get(?:Faith|Rite)Doctrine\(',v['value']):invalid.append(k)
   if v['value'].count('[')!=v['value'].count(']'):errors.append({'language':language,'unbalanced_localization_brackets':k})
   refs=set(re.findall(r'\$([A-Za-z0-9_.-]+)(?:\|[^$]*)?\$',v['value']))
   for ref in sorted(refs-known_language_loc):
    if args.game:unresolved.append({'key':k,'reference':ref,'file':v['file']})
  if invalid:errors.append({'language':language,'removed_localization_accessors':invalid})
  if unresolved:warnings.append({'language':language,'unresolved_localization_references':unresolved})
  languages[language]={'keys':len(values),'missing_keys':len(missing),'malformed_entries':len(bad),'unresolved_references':len(unresolved)}
 baseline=subprocess.check_output(['git','show','f2aa2c7ae50294407f0aca7f154dfdbd2dc28d46:README.md'],cwd=ROOT)
 if (ROOT/'README.md').read_bytes()!=baseline:errors.append({'README':'changed from starting fork'})
 report={'errors':errors,'warnings':warnings,'languages':languages,'dds':dds,'registries':{k:len(v) for k,v in registries.items()},'limitations':['Structural checks do not validate every engine function, scope, or gameplay path.']}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'errors':len(errors),'warnings':len(warnings),'languages':languages,'registries':report['registries']},ensure_ascii=False,indent=2));return bool(errors)
if __name__=='__main__':raise SystemExit(main())
