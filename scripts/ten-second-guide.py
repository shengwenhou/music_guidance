from pathlib import Path
from copy import deepcopy
import json
r=Path(__file__).resolve().parents[1];p=r/'dist/guide-data.js';head,raw=p.read_text().split('const GUIDE = ',1);g=json.loads(raw.rsplit(';',1)[0]);old=g['cues'];new=[]
if g.get('cadence')!=10:
 for i,c in enumerate(old):
  end=old[i+1]['t'] if i+1<len(old) else g['duration']
  for part,t in enumerate(range(c['t'],end,10)):
   n=deepcopy(c);n['t']=t;n['parentStart']=c['t'];n['subtitle']=[c['subtitle'][min(part,len(c['subtitle'])-1)]]
   if part:n['title']+=' · 續';n['precision']='section'
   new.append(n)
 g['cues']=new;g['cadence']=10
s=json.dumps(g,ensure_ascii=False,indent=2).replace('每20秒','每10秒').replace('每 20 秒','每 10 秒').replace('二十秒','十秒')
p.write_text(head+'const GUIDE = '+s+';\n');print('captions',len(g['cues']))
p=r/'dist/index.html';s=p.read_text().replace('20秒更新','10秒更新').replace('20秒背景','10秒背景').replace('每20秒','每10秒').replace('每20秒','每10秒').replace('每 20 秒','每 10 秒').replace('共251段字幕','每段最長10秒的字幕').replace('1 / 251',f"1 / {len(g['cues'])}").replace('app.js?v=9.1','app.js?v=10').replace('guide-data.js?v=9','guide-data.js?v=10');p.write_text(s)
p=r/'dist/app.js';s=p.read_text().replace("$('subtitleLine2').textContent=c.subtitle[1]","$('subtitleLine2').textContent=c.subtitle[1]||''");p.write_text(s)
p=r/'README.md';s=p.read_text().replace('251段','499段').replace('每20秒','每10秒').replace('20秒背景','10秒背景');p.write_text(s)
