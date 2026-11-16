"""Build the independent finale lyric track from archived alignment results.

Input is an internal stable-ts alignment JSON, never performance audio.
This is machine alignment for review, not a claim of human-verified timing.
"""
from pathlib import Path
import json,sys
r=Path(__file__).resolve().parents[1]
a=json.load(open(sys.argv[1]))['segments']
rows=json.loads((r/'scripts/finale-translation.json').read_text())
# Group uncertain word boundaries and polyphonic repeats into complete phrases.
groups=[(0,1),(2,3),(4,4),(5,7),(8,9),(10,10),(11,11),(12,12),(13,13),(14,14),(15,15),(16,16),(17,17),(18,19),(20,21),(22,25),(26,27),(28,29)]
cues=[]
for lo,hi in groups:
 start=round(4140+a[lo]['start'],2);end=round(4140+a[hi]['end'],2)
 if lo==8:start=4423.9 # first nonzero aligned 'glaube'; do not bridge instrumental silence
 words=rows[lo:hi+1]
 # Repeated overlapping texts share one translation, rather than stacking duplicates.
 zh=' '.join(dict.fromkeys(x['zh'] for x in words));de=' '.join(dict.fromkeys(x['de'] for x in words))
 cues.append(dict(id=rows[lo]['id'],start=start,end=end,zh=zh,de=de,review='machine-draft'))
# Failed closing phrases are readable but must not acquire invented timestamps.
untimed=[dict(rows[30]),dict(rows[31]),dict(rows[32]),dict(rows[34])]
out={'videoId':'e34QpbAPgi8','version':10,'method':'終章合唱與獨唱的原創中譯；德文依Klopstock與馬勒原詞。時間用ARD同場官方錄影音訊，依已知德文歌詞做機器對齊初稿；五個樂章起點與YouTube相符，但片長相差約10秒，尚未完成人工逐句及跨版本影音複核。複調與長音已合併分句，字幕入點仍可能有明顯誤差，結尾四句對齊失敗，僅列文字、暫不自動顯示；請視為可測試的對時草稿。正值微調會延後歌詞。','sources':['https://mahlercat.org.uk/Pages/Symph2/Texts.htm','https://ard-pd.ard-mcdn.de/klassik/2325609.avc-360.mp4'],'cues':cues,'untimed':untimed}
(r/'dist/lyrics-data.js').write_text('/* Original Chinese translation; machine-aligned timing draft, not manually verified. */\nconst LYRIC_GUIDE = '+json.dumps(out,ensure_ascii=False,indent=2)+';\n')
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'
(r/'dist/mahler-finale-zh-Hant.vtt').write_text('WEBVTT\n\nNOTE Timing draft: machine alignment; manual review pending.\n\n'+'\n\n'.join(f"{c['id']}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['zh']}" for c in cues)+'\n')
print(len(cues),'lyric phrases')
