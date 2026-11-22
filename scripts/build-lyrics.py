"""Build the independent finale lyric track from reviewed phrase timing.

The timing file contains phrase boundaries reviewed against the official ARD
recording of the same performance. Audio is analysis-only and is never copied
into the repository or deployed site.
"""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
rows = {row["id"]: row for row in json.loads((root / "scripts/finale-translation.json").read_text())}
timing = json.loads((root / "scripts/finale-timing.json").read_text())

cues = []
for item in timing:
    source_ids = item.get("sourceIds", [item["id"]])
    words = [rows[source_id] for source_id in source_ids]
    cue = {
        "id": item["id"],
        "start": item["start"],
        "end": item["end"],
        "zh": " ".join(dict.fromkeys(word["zh"] for word in words)),
        "de": " ".join(dict.fromkeys(word["de"] for word in words)),
        "review": "aligned",
    }
    if item.get("note"):
        cue["note"] = item["note"]
    cues.append(cue)

out = {
    "videoId": "e34QpbAPgi8",
    "version": 12,
    "method": (
        "終章合唱與獨唱的原創中譯；德文依Klopstock與馬勒原詞。"
        "時間以ARD同場官方錄音的強制對齊初稿為底，逐句對照頻譜、長音、休止與樂句重新修正。"
        "五個樂章起點與YouTube相同；ARD在82:04左右音樂收束、82:16左右開始掌聲，"
        "YouTube多出的約10秒位於尾端，歌詞無須整體平移。複調合唱以最先可辨識的聲部換句，"
        "長音和聲部重疊仍可能有約1–2秒差異；可用歌詞微調做裝置端修正。"
    ),
    "sources": [
        "https://mahlercat.org.uk/Pages/Symph2/Texts.htm",
        "https://ard-pd.ard-mcdn.de/klassik/2325609.avc-360.mp4",
    ],
    "vocalRanges": [
        {"start": cues[0]["start"], "end": cues[-1]["end"]},
    ],
    "cues": cues,
    "untimed": [],
}

(root / "dist/lyrics-data.js").write_text(
    "/* Original Chinese translation; phrase timing reviewed against the same performance. */\n"
    "const LYRIC_GUIDE = " + json.dumps(out, ensure_ascii=False, indent=2) + ";\n"
)

def stamp(seconds):
    milliseconds = round(seconds * 1000)
    return (
        f"{milliseconds // 3600000:02}:"
        f"{milliseconds // 60000 % 60:02}:"
        f"{milliseconds // 1000 % 60:02}."
        f"{milliseconds % 1000:03}"
    )

(root / "dist/mahler-finale-zh-Hant.vtt").write_text(
    "WEBVTT\n\nNOTE Phrase timing reviewed against the official recording.\n\n"
    + "\n\n".join(
        f"{cue['id']}\n{stamp(cue['start'])} --> {stamp(cue['end'])}\n{cue['zh']}"
        for cue in cues
    )
    + "\n"
)
print(len(cues), "aligned lyric phrases")
