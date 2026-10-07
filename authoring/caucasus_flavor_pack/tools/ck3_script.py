"""Small lossless CK3 assignment reader for import and static checks."""
import re
from pathlib import Path
TOKEN = re.compile(r'\s+|#[^\n]*|"(?:\\.|[^"\\])*"|[{}]|[=<>!]+|[^\s{}#"=<>!\ufeff]+')
def lex(s):
 return [m for m in TOKEN.finditer(s) if not m.group().isspace() and not m.group().startswith('#')]
def canonical(s):return [m.group() for m in lex(s)]
def entries(s):
 ts=lex(s);result=[];i=0
 while i<len(ts):
  if i+2>=len(ts) or ts[i+1].group() not in ('=','>','<','>=','<=','!=','?='):
   raise ValueError(f'Expected assignment near {ts[i].group()!r}')
  key=ts[i].group();j=i+2
  if ts[j].group()=='{':
   depth=1;j+=1;body_start=ts[j-1].end()
   while j<len(ts) and depth:
    if ts[j].group()=='{':depth+=1
    elif ts[j].group()=='}':depth-=1
    j+=1
   if depth:raise ValueError(f'Unclosed block: {key}')
   body=s[body_start:ts[j-1].start()]
  else:
   body_start=ts[j].start();j+=1
   while j<len(ts) and not (j+1<len(ts) and ts[j+1].group() in ('=','>','<','>=','<=','!=','?=')):
    j+=1
   body=s[body_start:ts[j-1].end()]
  result.append((key,body,ts[i].start(),ts[j-1].end()));i=j
 return result
def files(layers,category):
 result={}
 for root in layers:
  for p in sorted((root/category).glob('*.txt')):result[p.name]=p
 return result
def registry(layers,category):
 result={}
 for p in files(layers,category).values():
  s=p.read_text(encoding='utf-8-sig')
  try:parsed=entries(s)
  except ValueError:continue # Ignore unrelated files with unsupported prototypes.
  for k,b,a,z in parsed:result[k]=(p,b,s[a:z])
 return result
def write(path,s,bom=True):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text('\n'.join(l.rstrip() for l in s.splitlines()).rstrip()+'\n',encoding='utf-8-sig' if bom else 'utf-8')


def find_entry(root,category,key):
 result=None
 for p in sorted((Path(root)/category).glob('*.txt')):
  s=p.read_text(encoding='utf-8-sig')
  m=re.search(r'^\s*'+re.escape(key)+r'\s*=\s*\{',s,re.M)
  if not m:continue
  start=m.start();ts=lex(s[start:]);depth=0;opening=None
  for t in ts:
   if t.group()=='{':
    if opening is None:opening=t.end()
    depth+=1
   elif t.group()=='}':
    depth-=1
    if depth==0:
     raw=s[start:start+t.end()].strip();body=s[start+opening:start+t.start()]
     result=(p,body,raw);break
 if result is None:raise KeyError(key)
 return result
