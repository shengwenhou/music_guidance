const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const base = path.join(__dirname, '../dist/mahler8');
const context = vm.createContext({});
vm.runInContext(fs.readFileSync(path.join(base, 'guide-data.js'), 'utf8'), context);
vm.runInContext(fs.readFileSync(path.join(base, 'lyrics-data.js'), 'utf8'), context);
const guide = vm.runInContext('GUIDE', context);
const lyrics = vm.runInContext('LYRIC_GUIDE', context);

test('Mahler 8 guide covers the complete source video at ten-second cadence', () => {
  assert.equal(guide.videoId, 'kP_cwJ4tKP0');
  assert.equal(guide.duration, 5193);
  assert.equal(guide.cues.length, 521);
  assert.deepEqual(Array.from(guide.movements, movement => movement.t), [0, 1636]);
  assert.equal(guide.cues[0].t, 0);
  assert.ok(guide.duration - guide.cues.at(-1).t <= 10);
  for (let index = 0; index < guide.cues.length; index += 1) {
    const cue = guide.cues[index];
    if (index) {
      assert.ok(cue.t > guide.cues[index - 1].t);
      assert.ok(cue.t - guide.cues[index - 1].t <= 10);
    }
    assert.equal(cue.subtitle.length, 1);
    assert.ok(cue.subtitle[0]);
    assert.ok(cue.text && cue.focus && cue.detail);
    assert.ok(cue.t >= guide.movements[cue.movement].t);
    assert.ok(cue.t < guide.movements[cue.movement].end);
    cue.refs.forEach(key => assert.match(guide.sources[key][1], /^https:\/\//));
  }
  assert.equal(guide.cues.find(cue => cue.t === 1636).precision, 'chapter');
  assert.match(guide.cues.find(cue => cue.parentStart === 4926).subtitle[0], /Veni|管風琴|遠距銅管/);
});

test('entry reminders include the requested large-scale and vocal landmarks', () => {
  const ids = new Set(guide.entryAlerts.map(alert => alert.id));
  for (const id of ['opening', 'offstage-1', 'children', 'doctor', 'mater', 'mysticus', 'finale']) {
    assert.ok(ids.has(id), id);
  }
  assert.match(guide.entryAlerts.find(alert => alert.id === 'finale').text, /Veni/);
  assert.match(guide.entryAlerts.find(alert => alert.id === 'finale').title, /管風琴.*遠距銅管/);
});

test('all Latin and German lyric cues are independently translated and timed', () => {
  assert.equal(lyrics.videoId, 'kP_cwJ4tKP0');
  assert.equal(lyrics.cues.length, 377);
  assert.equal(lyrics.untimed.length, 0);
  assert.equal(lyrics.cues.filter(cue => cue.language === 'la').length, 128);
  assert.equal(lyrics.cues.filter(cue => cue.language === 'de').length, 249);
  assert.equal(lyrics.cues[0].start, 96.03);
  assert.equal(lyrics.cues.at(-1).end, 4890.38);
  let lastStart = -1;
  for (const cue of lyrics.cues) {
    assert.ok(cue.start >= lastStart);
    assert.ok(cue.end > cue.start);
    assert.ok(cue.zh && cue.de);
    assert.equal(cue.review, 'aligned');
    assert.match(cue.zh, /[\u3400-\u9fff]/);
    lastStart = cue.start;
  }
  assert.match(lyrics.cues[0].zh, /降臨/);
  assert.match(lyrics.cues.find(cue => cue.start === 4647).zh, /消逝/);
  assert.match(lyrics.method, /沒有採用.*鄒仲之/);
});

test('published VTT and interface expose the same lyric set without TTS', () => {
  const vtt = fs.readFileSync(path.join(base, 'mahler8-zh-Hant.vtt'), 'utf8');
  const html = fs.readFileSync(path.join(base, 'index.html'), 'utf8');
  const app = fs.readFileSync(path.join(base, 'app.js'), 'utf8');
  assert.equal((vtt.match(/ --> /g) || []).length, lyrics.cues.length);
  assert.match(vtt, /一切會消逝的/);
  assert.match(html, /馬勒八/);
  assert.match(html, /拉丁文／德文原文/);
  assert.match(html, /mahler8-zh-Hant\.vtt/);
  assert.match(app, /videoId:GUIDE\.videoId/);
  assert.doesNotMatch(`${html}\n${app}`, /speechSynthesis|TTS|語音播放/);
  for (const id of app.matchAll(/\$\('([^']+)'\)/g)) {
    assert.ok(html.includes(`id="${id[1]}"`), id[1]);
  }
});

test('Mahler 8 rights notice excludes the source video and caption tracks from MIT', () => {
  const notice = fs.readFileSync(path.join(base, 'THIRD_PARTY_NOTICES.md'), 'utf8');
  assert.match(notice, /馬勒第八號頁面/);
  assert.match(notice, /原字幕軌不在MIT授權範圍/);
  assert.match(notice, /鄒仲之中文字幕未被複製/);
});
