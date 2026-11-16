const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../dist/app.js'), 'utf8');
function setup() {
  const elements = {}, buttons = [], listeners = {};
  const state = {time:0, playback:2, pauses:0, cancelCount:0, speech:null};
  const element = () => ({textContent:'',value:0,style:{},classList:{add(){},toggle(){}},append(){},replaceChildren(...children){this.children=children},setAttribute(k,v){this[k]=v}});
  const document = {
    body:{style:{overflow:''}},
    getElementById:id=>elements[id]??=element(),
    createElement:tag=>{const e=element();if(tag==='button')buttons.push(e);return e},
    createTextNode:s=>s,querySelectorAll:()=>buttons,head:{append(){}},
    addEventListener:(name,callback)=>listeners[name]=callback
  };
  let events, tick;
  const context={document,location:{origin:'https://example.org'},window:{addEventListener(){},speechSynthesis:{cancel(){state.cancelCount++},getVoices:()=>[],speak:u=>state.speech=u}},setInterval:f=>tick=f,setTimeout:()=>1,clearTimeout(){},SpeechSynthesisUtterance:function(text){this.text=text},YT:{Player:function(id,options){events=options.events;return {getCurrentTime:()=>state.time,getPlayerState:()=>state.playback,seekTo:v=>state.time=v,pauseVideo(){state.playback=2;state.pauses++},playVideo(){state.playback=1}}}}};
  vm.createContext(context);vm.runInContext(source,context);
  return {elements,buttons,state,document,listeners,ready(){context.window.onYouTubeIframeAPIReady();events.onReady()},event(data){events.onStateChange({data})},tick(){tick()}};
}
test('captions, sources, preview and boundary navigation',()=>{
  const s=setup(),e=s.elements;
  assert.equal(s.buttons.length,15);assert.match(e.subtitleLine1.textContent,/1888/);assert.equal(e.sources.children.length,2);
  e.preview.onclick();e.nextCue.onclick();assert.equal(e.clock.textContent,'00:20');assert.equal(e.subtitleCount.textContent,'2 / 15');
  e.previousCue.onclick();assert.equal(e.previousCue.disabled,true);
  for(let i=0;i<14;i++)e.nextCue.onclick();assert.equal(e.nextCue.disabled,true);assert.match(e.subtitleLine1.textContent,/完整聽/);
});
test('real playback position controls captions and preview is isolated',()=>{
  const s=setup(),e=s.elements;s.ready();e.start.onclick();s.tick();s.state.time=101;s.tick();assert.match(e.subtitleLine1.textContent,/1891/);
  e.preview.onclick();e.nextCue.onclick();assert.equal(s.state.time,101);s.state.time=150;s.tick();assert.equal(e.clock.textContent,'02:00');
  e.preview.onclick();assert.equal(e.clock.textContent,'02:30');
});
test('offset, buffering pause and five-minute stop',()=>{
  const s=setup(),e=s.elements;s.ready();s.state.time=12;e.align.onclick();e.start.onclick();s.tick();assert.equal(s.state.time,12);
  s.state.playback=3;e.toggle.onclick();assert.equal(s.state.playback,2);s.state.playback=1;s.state.time=312;s.tick();assert.equal(s.state.playback,2);assert.equal(e.clock.textContent,'05:00');
  s.event(2);assert.match(e.status.textContent,/結束/);e.toggle.onclick();assert.equal(s.state.time,12);assert.equal(s.state.playback,1);
});
test('narration survives delayed pause and ignores stale speech callbacks',()=>{
  const s=setup(),e=s.elements;s.ready();e.speak.onclick();const old=s.state.speech,count=s.state.cancelCount;
  assert.match(old.text,/現在可以這樣聽/);s.event(2);assert.equal(s.state.cancelCount,count);assert.match(e.speak.textContent,/停止/);
  e.nextCue.onclick();const status=e.status.textContent;old.onerror();assert.equal(e.status.textContent,status);
  e.speak.onclick();s.event(1);assert.match(e.speak.textContent,/暫停並聽/);
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
  assert.equal(e.subtitleCount.textContent,'15 / 15');assert.equal(e.clock.textContent,'04:40');
  s.state.time=280;s.tick();assert.equal(e.clock.textContent,'04:40');
});

test('20-second cadence and listening hints have distinct labels',()=>{
  const s=setup(),e=s.elements;e.preview.onclick();
  for(let i=0;i<15;i++){
    const mm=String(Math.floor(i*20/60)).padStart(2,'0'),ss=String(i*20%60).padStart(2,'0');
    assert.equal(e.clock.textContent,mm+':'+ss);
    if([1,3,8,12,14].includes(i))assert.ok(e.year.textContent.startsWith('注意聽'));
    if(i<14)e.nextCue.onclick();
  }
});
