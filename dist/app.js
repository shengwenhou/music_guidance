const {cues,sources,movements,duration:END}=GUIDE;
const $=id=>document.getElementById(id), fmt=s=>{s=Math.max(0,Math.floor(s));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')};
let player,ready=false,preview=false,index=-1,finished=false,apiTimer,pendingSeek=null;
const status=t=>$('status').textContent=t;
function offset(){return Math.min(7200,Math.max(0,Number($('offset').value)||0))}
function updateCueKind(){const listening=cues[index]?.kind==='listen';$('captionMode').textContent=preview?'字幕預覽':listening?'🎧 注意聽':cues[index]?.kind==='method'?'聆聽方法':cues[index]?.kind==='interpretation'?'學者觀點':'創作背景';$('subtitleBand').classList.toggle('listening',listening)}
let shownEntry;
function renderEntryAlert(t){const e=(GUIDE.entryAlerts||[]).find(e=>t>=e.start&&t<e.end);const key=e?.id||null;if(key===shownEntry)return;shownEntry=key;$('entryAlert').hidden=!e;$('entryAlertTitle').textContent=e?.title||'';$('entryAlertText').textContent=e?.text||''}
function render(t){t=Math.max(0,Math.min(END,t));renderEntryAlert(t);let i=cues.findLastIndex(c=>c.t<=t);$('clock').textContent=fmt(t);$('seek').value=t;$('seek').setAttribute('aria-valuetext',fmt(t));$('subtitleTime').textContent=fmt(t)+' / '+fmt(END);$('progress').style.width=(t/END*100)+'%';if(i===index)return;index=i;const c=cues[i];drawCueList(c.movement);$('currentMovement').textContent=movements[c.movement].name;$('precision').textContent=c.precision==='chapter'?'官方樂章起點':'區段導聆 · 非逐小節標記';document.querySelectorAll('.movement').forEach((b,j)=>{b.setAttribute('aria-current',j===c.movement?'step':'false')});$('subtitleYear').textContent=c.year;$('subtitleLine1').textContent=c.subtitle[0];$('subtitleLine2').textContent=c.subtitle[1];$('subtitleCount').textContent=(i+1)+' / '+cues.length;$('previousCue').disabled=i===0;$('nextCue').disabled=i===cues.length-1;updateCueKind();$('year').textContent=c.year;$('title').textContent=c.title;$('prompt').textContent=c.text;$('tags').textContent=c.focus;$('detail').textContent=c.detail;$('sources').replaceChildren(...c.refs.map(key=>{const a=document.createElement('a');a.textContent=sources[key][0];a.href=sources[key][1];a.target='_blank';a.rel='noopener';return a}));$('count').textContent=String(i+1).padStart(2,'0')+' / '+cues.length;$('window').textContent=fmt(c.t)+' — '+fmt(cues[i+1]?.t??END);document.querySelectorAll('.cue').forEach(b=>{const active=Number(b.dataset.cue)===i;b.classList.toggle('active',active);b.setAttribute('aria-current',active?'step':'false')})}
function setPreview(value){preview=value;$('mode').textContent=value?'CARD PREVIEW · 字幕預覽':'背景故事 × 聆聽';$('railLabel').textContent=value?'字幕預覽 · 未跟隨影片':'全曲故事導聆';$('preview').textContent=value?'返回影片同步':'預覽字幕';updateCueKind()}
function seekGuide(t){const target=offset()+t;pendingSeek={target,until:Date.now()+8000};player.seekTo(target,true)}
function jump(t){finished=false;if(preview||!ready){if(!preview)setPreview(true);render(t);return}seekGuide(t);render(t)}
let shownMovement=-1;
function drawCueList(mi){
  if(mi===shownMovement)return;shownMovement=mi;
  const nodes=cues.map((c,i)=>({c,i})).filter(({c})=>c.movement===mi).map(({c,i})=>{
    const b=document.createElement('button');b.className=c.kind==='listen'?'cue listening':'cue';b.dataset.cue=i;
    const s=document.createElement('span');s.textContent=fmt(c.t);b.append(s,document.createTextNode(c.title));b.onclick=()=>jump(c.t);return b;
  });$('chapters').replaceChildren(...nodes);
}
movements.forEach((m,i)=>{const b=document.createElement('button');b.className='movement';b.dataset.movement=i;b.textContent=fmt(m.t)+' · '+m.name;b.onclick=()=>jump(m.t);$('movements').append(b)});
(GUIDE.bibliography||[]).forEach(ref=>{
 const section=document.createElement('section');section.className='reference-entry';
 const heading=document.createElement('h4');const link=document.createElement('a');link.textContent=sources[ref.key][0];link.href=sources[ref.key][1];link.target='_blank';link.rel='noopener';heading.append(link);
 const cite=document.createElement('p');cite.textContent=ref.kind+' · '+ref.citation;
 const reading=document.createElement('p');reading.textContent=ref.reading;
 const use=document.createElement('p');use.textContent='放進導聆：'+ref.contribution;
 const links=document.createElement('div');links.className='reference-cues';
 cues.filter(c=>c.refs.includes(ref.key)).forEach(c=>{const b=document.createElement('button');b.textContent=fmt(c.t);b.onclick=()=>jump(c.t);links.append(b)});
 section.append(heading,cite,reading,use,links);$('bibliography').append(section);
});
(GUIDE.entryAlerts||[]).forEach(e=>{
 const wrap=document.createElement('div'),b=document.createElement('button');b.textContent=fmt(e.start)+' · '+e.title;b.onclick=()=>jump(e.start);
 const note=document.createElement('small');note.textContent=e.scoreAnchor+'。'+e.verification;b.append(note);wrap.append(b);
 e.refs.forEach(key=>{const a=document.createElement('a');a.textContent=sources[key][0];a.href=sources[key][1];a.target='_blank';a.rel='noopener';a.style.fontSize='11px';a.style.display='block';wrap.append(a)});$('entryIndex').append(wrap);
});
$('seek').max=END;$('totalTime').textContent=fmt(END);
$('seek').onchange=()=>jump(Number($('seek').value));
$('preview').onclick=()=>{if(!preview){if(ready)player.pauseVideo();setPreview(true);status('字幕預覽：點選下方時間卡，影片不會跟著播放。')}else{setPreview(false);if(ready){render(player.getCurrentTime()-offset());status('已返回影片同步；按繼續播放。')}else status('播放器尚未就緒，可再次開啟字幕預覽。')}};
$('start').onclick=()=>{setPreview(false);finished=false;seekGuide(0);player.playVideo();render(0)};
$('toggle').onclick=()=>{setPreview(false);if(finished){finished=false;seekGuide(0)}[1,3].includes(player.getPlayerState())?player.pauseVideo():player.playVideo()};
$('back').onclick=()=>{setPreview(false);jump(Math.max(0,player.getCurrentTime()-offset()-10))};
$('align').onclick=()=>{$('offset').value=player.getCurrentTime().toFixed(1);finished=false;setPreview(false);render(0);status('已將目前影片位置設為音樂起點。')};
$('offset').onchange=()=>{pendingSeek=null;finished=false;$('offset').value=offset();if(ready&&!preview)render(player.getCurrentTime()-offset())};
window.onYouTubeIframeAPIReady=()=>{clearTimeout(apiTimer);player=new YT.Player('player',{videoId:'e34QpbAPgi8',playerVars:{playsinline:1,rel:0,origin:location.origin},events:{onReady:()=>{ready=true;$('loading').classList.add('hidden');['start','toggle','back','align'].forEach(id=>$(id).disabled=false);status('播放器已就緒。按「開始全曲導聆」，從音樂起點播放。')},onStateChange:e=>{if(e.data===0&&!preview){finished=true;render(END)}$('toggle').textContent=[1,3].includes(e.data)?'暫停':'繼續';if(!preview)status(finished?'全曲導聆結束。可點選時間卡重聽，或按繼續從頭開始。':e.data===1?'背景導聆進行中 · 字幕跟隨影片時間':e.data===2?'已暫停 · 字幕停留在目前位置':e.data===3?'影片緩衝中 · 字幕跟隨實際播放位置':'播放器已就緒')},onError:e=>{ready=false;['start','toggle','back','align'].forEach(id=>$(id).disabled=true);$('loading').classList.add('hidden');status('YouTube 無法播放（代碼 '+e.data+'）。可開啟原始影片，或用「預覽字幕」查看內容。')}}})};
setInterval(()=>{if(!ready||preview)return;const videoTime=player.getCurrentTime();if(pendingSeek){if(Math.abs(videoTime-pendingSeek.target)<=1.5||Date.now()>=pendingSeek.until)pendingSeek=null;else return}const t=videoTime-offset();render(t);if(t>=END&&player.getPlayerState()===1){finished=true;player.pauseVideo();status('全曲導聆結束。可點選時間卡重聽，或按繼續從頭開始。')}},200);
apiTimer=setTimeout(()=>{status('YouTube 連線較久。可先預覽字幕，或從下方連結開啟原始影片。');$('loading').innerHTML='<div>YouTube 尚未載入<p>可先使用「預覽字幕」瀏覽導聆內容。</p></div>'},15000);
const script=document.createElement('script');script.src='https://www.youtube.com/iframe_api';script.onerror=()=>{clearTimeout(apiTimer);status('無法連接 YouTube。可先預覽字幕，或從下方連結開啟原始影片。');$('loading').innerHTML='<div>暫時無法連接 YouTube<p>可先預覽字幕。</p></div>'};$('loading').classList.add('hidden');document.head.append(script);render(0);

$('previousCue').onclick=()=>jump(cues[Math.max(0,index-1)].t);
$('nextCue').onclick=()=>jump(cues[Math.min(cues.length-1,index+1)].t);
let fallbackFocus=false,oldOverflow='';
function updateFullscreen(){const active=document.fullscreenElement===$('stage')||document.webkitFullscreenElement===$('stage')||fallbackFocus;$('fullscreen').textContent=active?'↙ 離開專注畫面':'⛶ 影片＋字幕全螢幕';$('fullscreen').setAttribute('aria-pressed',String(active))}
function fallbackFullscreen(){fallbackFocus=!fallbackFocus;$('stage').classList.toggle('focus-mode',fallbackFocus);if(fallbackFocus){oldOverflow=document.body.style.overflow;document.body.style.overflow='hidden'}else document.body.style.overflow=oldOverflow;updateFullscreen()}
$('fullscreen').onclick=async()=>{const stage=$('stage');if(fallbackFocus){fallbackFullscreen();return}try{if(document.fullscreenElement===stage){await document.exitFullscreen()}else if(document.webkitFullscreenElement===stage){document.webkitExitFullscreen()}else if(stage.requestFullscreen){await stage.requestFullscreen()}else if(stage.webkitRequestFullscreen){stage.webkitRequestFullscreen()}else fallbackFullscreen()}catch{fallbackFullscreen()}updateFullscreen()};
document.addEventListener('fullscreenchange',updateFullscreen);document.addEventListener('webkitfullscreenchange',updateFullscreen);document.addEventListener('keydown',e=>{if(e.key==='Escape'&&fallbackFocus)fallbackFullscreen()});
