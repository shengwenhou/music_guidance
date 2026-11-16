const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const guideSource = fs.readFileSync(path.join(__dirname, '../dist/guide-data.js'), 'utf8');
const source = fs.readFileSync(path.join(__dirname, '../dist/app.js'), 'utf8');
function setup() {
  const elements = {}, buttons = [], listeners = {};
  const state = {time:0, playback:2, pauses:0};
  const element = () => ({textContent:'',value:0,style:{},dataset:{},classList:{add(){},toggle(){}},append(){},replaceChildren(...children){this.children=children},setAttribute(k,v){this[k]=v}});
  const document = {
    body:{style:{overflow:''}},
    getElementById:id=>elements[id]??=Object.assign(element(),{checked:id==='lyricsToggle'}),
    createElement:tag=>{const e=element();if(tag==='button')buttons.push(e);return e},
    createTextNode:s=>s,querySelectorAll:selector=>buttons.filter(b=>selector==='.movement'?b.className==='movement':b.className?.startsWith('cue')),head:{append(){}},
    addEventListener:(name,callback)=>listeners[name]=callback
  };
  let events, tick;
  const context={document,location:{origin:'https://example.org'},window:{addEventListener(){}},setInterval:f=>tick=f,setTimeout:()=>1,clearTimeout(){},YT:{Player:function(id,options){events=options.events;return {getCurrentTime:()=>state.time,getPlayerState:()=>state.playback,seekTo:v=>state.time=v,pauseVideo(){state.playback=2;state.pauses++},playVideo(){state.playback=1}}}}};
  vm.createContext(context);vm.runInContext(guideSource,context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../dist/lyrics-data.js'),'utf8'),context);vm.runInContext(source,context);
  return {elements,buttons,state,document,listeners,guide:vm.runInContext('GUIDE',context),ready(){context.window.onYouTubeIframeAPIReady();events.onReady()},event(data){events.onStateChange({data})},tick(){tick()}};
}
test('captions, sources, preview and boundary navigation',()=>{
  const s=setup(),e=s.elements;
  assert.equal(e.movements!==undefined,true);assert.equal(s.guide.cues.length,499);assert.match(e.subtitleLine1.textContent,/1888/);assert.equal(e.sources.children.length,s.guide.cues[0].refs.length);
  e.preview.onclick();e.nextCue.onclick();assert.equal(e.clock.textContent,'00:10');assert.equal(e.subtitleCount.textContent,'2 / 499');
  e.previousCue.onclick();assert.equal(e.previousCue.disabled,true);
  e.seek.value=4975;e.seek.onchange();assert.equal(e.nextCue.disabled,true);assert.match(e.subtitleLine1.textContent,/最後|需要重聽|全曲/);
});
test('real playback position controls captions and preview is isolated',()=>{
  const s=setup(),e=s.elements;s.ready();e.start.onclick();s.tick();s.state.time=101;s.tick();assert.match(e.subtitleLine1.textContent,/1891/);
  e.preview.onclick();e.nextCue.onclick();assert.equal(s.state.time,101);s.state.time=150;s.tick();assert.equal(e.clock.textContent,'01:50');
  e.preview.onclick();assert.equal(e.clock.textContent,'02:30');
});
test('offset, buffering pause and full-work stop',()=>{
  const s=setup(),e=s.elements;s.ready();s.state.time=12;e.align.onclick();e.start.onclick();s.tick();assert.equal(s.state.time,12);
  s.state.playback=3;e.toggle.onclick();assert.equal(s.state.playback,2);s.state.playback=1;s.state.time=4988;s.tick();assert.equal(s.state.playback,2);assert.equal(e.clock.textContent,'82:56');
  s.event(2);assert.match(e.status.textContent,/結束/);e.toggle.onclick();assert.equal(s.state.time,12);assert.equal(s.state.playback,1);
});
test('fullscreen API, fallback and Escape exit restore the page',async()=>{
  const s=setup(),e=s.elements;
  await e.fullscreen.onclick();assert.equal(e.fullscreen['aria-pressed'],'true');assert.equal(s.document.body.style.overflow,'hidden');
  s.listeners.keydown({key:'Escape'});assert.equal(e.fullscreen['aria-pressed'],'false');assert.equal(s.document.body.style.overflow,'');
  e.stage.requestFullscreen=async()=>{s.document.fullscreenElement=e.stage;s.listeners.fullscreenchange()};
  s.document.exitFullscreen=async()=>{s.document.fullscreenElement=null;s.listeners.fullscreenchange()};
  await e.fullscreen.onclick();assert.equal(e.fullscreen['aria-pressed'],'true');await e.fullscreen.onclick();assert.equal(e.fullscreen['aria-pressed'],'false');
});
test('all script UI references exist in the page',()=>{
  const s=setup();const html=fs.readFileSync(path.join(__dirname,'../dist/index.html'),'utf8');
  for(const id of Object.keys(s.elements))assert.ok(html.includes(`id="${id}"`),id);
});

test('stale player time during seek cannot rewind rapid subtitle navigation',()=>{
  const s=setup(),e=s.elements;s.ready();e.start.onclick();
  for(let i=0;i<14;i++){e.nextCue.onclick();s.state.time=0;s.tick()}
  assert.equal(e.subtitleCount.textContent,'15 / 499');assert.equal(e.clock.textContent,'02:20');
  s.state.time=140;s.tick();assert.equal(e.clock.textContent,'02:20');
});

test('10-second cadence and listening hints have distinct labels',()=>{
  const s=setup(),e=s.elements;e.preview.onclick();
  for(let i=0;i<30;i++){
    const mm=String(Math.floor(i*10/60)).padStart(2,'0'),ss=String(i*10%60).padStart(2,'0');
    assert.equal(e.clock.textContent,mm+':'+ss);
    if([2,3,6,7,16,17,24,25,28,29].includes(i))assert.ok(e.year.textContent.startsWith('注意聽'));
    if(i<29)e.nextCue.onclick();
  }
});


test('all five chapters navigate in preview without moving the video',()=>{
 const s=setup(),e=s.elements;s.ready();s.state.time=120;e.preview.onclick();
 const chapters=s.buttons.filter(b=>b.className==='movement');assert.equal(chapters.length,5);
 const times=[0,1338,1899,2569,2886];
 chapters.forEach((b,i)=>{b.onclick();assert.equal(e.clock.textContent,fmt(times[i]));assert.equal(s.state.time,120);assert.equal(e.precision.textContent,'官方樂章起點');assert.equal(e.chapters.children[0].dataset.cue,s.guide.cues.findIndex(c=>c.t===times[i]));});
});
function fmt(t){return String(Math.floor(t/60)).padStart(2,'0')+':'+String(t%60).padStart(2,'0')}
test('full guide covers the video with no gap longer than ten seconds',()=>{
 const {guide:g}=setup();assert.equal(g.duration,4976);
 assert.equal(g.cues[0].t,0);assert.ok(g.duration-g.cues.at(-1).t<=10);
 const seen=new Set();
 g.cues.forEach((c,i)=>{
  if(i)assert.ok(c.t>g.cues[i-1].t&&c.t-g.cues[i-1].t<=10);
  assert.equal(c.subtitle.length,1);assert.ok(c.subtitle.every(Boolean));
  assert.ok(c.t>=g.movements[c.movement].t&&c.t<g.movements[c.movement].end);
  c.refs.forEach(key=>assert.ok(g.sources[key]?.[1].startsWith('https://')));
  const text=c.subtitle.join(' ');assert.ok(!seen.has(text));seen.add(text);
 });
 assert.match(g.cues.find(c=>c.t===2569).subtitle.join(' '),/次女高音/);
 assert.ok(g.cues.filter(c=>c.precision==='chapter').every(c=>g.movements.some(m=>m.t===c.t)));
});
test('chapter boundaries follow real playback and slider uses calibrated time',()=>{
 const s=setup(),e=s.elements;s.ready();e.start.onclick();s.tick();
 for(const t of [1338,1899,2569,2886]){s.state.time=t;s.tick();assert.equal(e.clock.textContent,fmt(t));assert.equal(e.precision.textContent,'官方樂章起點')}
 e.offset.value=5;e.offset.onchange();e.seek.value=2569;e.seek.onchange();assert.equal(s.state.time,2574);s.tick();assert.equal(e.clock.textContent,'42:49');
 assert.match(e.subtitleLine1.textContent,/次女高音/);
});
test('MIT license is published with explicit media exclusions',()=>{
 const root=path.join(__dirname,'..');const license=fs.readFileSync(path.join(root,'LICENSE'),'utf8');
 assert.match(license,/MIT License/);assert.match(license,/Copyright \(c\) 2026 Sheng-Wen Hou/);
 assert.equal(license,fs.readFileSync(path.join(root,'dist/LICENSE.txt'),'utf8'));
 assert.match(fs.readFileSync(path.join(root,'dist/THIRD_PARTY_NOTICES.md'),'utf8'),/影片、錄音/);
});

test('YouTube ended event completes guide even when duration rounding differs',()=>{const s=setup(),e=s.elements;s.ready();s.state.time=4975.5;s.event(0);assert.equal(e.clock.textContent,'82:56');assert.match(e.status.textContent,/結束/);e.toggle.onclick();assert.equal(s.state.time,0)});

test('entry reminders update between background cues and clear after seeking',()=>{
 const s=setup(),e=s.elements;s.ready();e.start.onclick();s.tick();
 const alert=s.guide.entryAlerts[0];s.state.time=alert.start-0.1;s.tick();const line=e.subtitleLine1.textContent;
 assert.equal(e.entryAlert.hidden,true);s.state.time=alert.start;s.tick();
 assert.equal(e.entryAlert.hidden,false);assert.match(e.entryAlertTitle.textContent,/圓號/);assert.equal(e.subtitleLine1.textContent,line);
 s.state.time=alert.end;s.tick();assert.equal(e.entryAlert.hidden,true);
 e.preview.onclick();const organ=s.guide.entryAlerts.find(a=>a.id==='organ');e.seek.value=organ.start;e.seek.onchange();assert.equal(e.entryAlert.hidden,false);assert.match(e.entryAlertTitle.textContent,/管風琴/);
 e.seek.value=100;e.seek.onchange();assert.equal(e.entryAlert.hidden,true);
});
test('all entry reminders state timing uncertainty and link valid musical evidence',()=>{
 const {guide:g}=setup();for(const a of g.entryAlerts){assert.ok(a.start>=g.movements[4].t&&a.end<=g.duration&&a.end>a.start);assert.match(a.verification,/估計/);assert.ok(a.scoreAnchor);a.refs.forEach(k=>assert.ok(g.sources[k]));}
});

test('lyrics follow their own boundaries, clear gaps and remain independent of guide cadence',()=>{
 const s=setup(),e=s.elements;s.ready();e.start.onclick();s.tick();
 s.state.time=4145.1;s.tick();assert.equal(e.lyricsBand.hidden,false);assert.match(e.lyricChinese.textContent,/塵土/);assert.match(e.lyricTiming.textContent,/草稿/);
 const first=e.lyricChinese.textContent;s.state.time=4150;s.tick();assert.equal(e.lyricChinese.textContent,first);
 s.state.time=4202;s.tick();assert.equal(e.lyricsBand.hidden,true);
 s.state.time=4145.1;s.tick();e.lyricsToggle.checked=false;e.lyricsToggle.onchange();assert.equal(e.lyricsBand.hidden,true);assert.equal(s.state.time,4145.1);
 e.lyricsToggle.checked=true;e.lyricsToggle.onchange();assert.equal(e.lyricsBand.hidden,false);
 e.germanToggle.checked=true;e.germanToggle.onchange();assert.equal(e.lyricGerman.hidden,false);assert.match(e.lyricGerman.textContent,/Aufersteh/);
 e.lyricShift.value=10;e.lyricShift.onchange();assert.equal(e.lyricsBand.hidden,true);assert.equal(s.state.time,4145.1);
 s.state.time=4155.1;s.tick();assert.equal(e.lyricsBand.hidden,false);
 e.offset.value=5;e.offset.onchange();assert.equal(e.lyricsBand.hidden,true);
});
test('published lyric times and VTT are valid and failed phrases stay explicitly untimed',()=>{
 const context=vm.createContext({});vm.runInContext(fs.readFileSync(path.join(__dirname,'../dist/lyrics-data.js'),'utf8'),context);const g=vm.runInContext('LYRIC_GUIDE',context);
 assert.equal(g.cues.length,18);assert.equal(g.untimed.length,4);assert.match(g.method,/失敗/);
 let end=0;for(const c of g.cues){assert.ok(c.start>=end&&c.end>c.start&&c.end<=4976);assert.ok(c.zh&&c.de);assert.equal(c.review,'machine-draft');end=c.end}
 for(const c of g.untimed)assert.equal(c.start,undefined);
 const vtt=fs.readFileSync(path.join(__dirname,'../dist/mahler-finale-zh-Hant.vtt'),'utf8');assert.equal((vtt.match(/ --> /g)||[]).length,g.cues.length);assert.match(vtt,/manual review pending/);
});
