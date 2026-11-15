const cues = [
 {t:0,title:'先把注意力交給低音',text:'開頭先別急著尋找一條好唱的旋律。留意低音弦樂的起音、快速音群與它們留下的重量：音樂如何在很短的時間內建立緊張感？',focus:'大提琴・低音提琴 ／ 起音與重量',detail:'低音聲部不只是和聲背景；在這個開頭，它直接參與音樂的戲劇。試著把快速音群聽成一個完整手勢。'},
 {t:20,title:'音符之間，也有戲',text:'留意每一個樂句如何停止。聲音收住之後，張力是消失了，還是仍然懸在空中？可以連同指揮的動作一起觀察。',focus:'樂句尾端 ／ 休止與餘響',detail:'休止不等於鬆懈。前一個音的力度、收音方式與音樂廳的餘響，都會改變下一次進入的感受。'},
 {t:45,title:'尋找音樂裡的步伐',text:'試著感覺音樂的重心：哪些音像向前踏步，哪些音像突然的衝撞？不用數拍，也可以先感受長短音和重音帶來的身體感。',focus:'節奏重心 ／ 長短與重音',detail:'第一樂章與葬禮的構想有關，但並不是從頭到尾維持同一種整齊步伐。觀察步伐如何受到激烈手勢的干擾。'},
 {t:75,title:'換一個聲部聽',text:'這一小段，試著暫時不追最響的聲音。找出一條比較輕、比較高，或比較細的線條：它是在回應，還是在和主線同時說話？',focus:'背景聲部 ／ 回應與對位',detail:'不必立即辨認每一種樂器。先區分音域、音色與角色，往往比猜樂器名稱更能聽出配器的層次。'},
 {t:105,title:'力度不只是一個音量鈕',text:'注意聲音變強時，是更多樂器加入，還是原本的樂器奏得更用力？也留意音域是否拉開、節奏是否變密。',focus:'音量・密度・音域',detail:'音樂的強烈感來自多種因素。即使音量相近，厚重和弦和稀疏獨奏仍會帶來很不同的壓力。'},
 {t:140,title:'留一隻耳朵給低音',text:'如果上方的旋律開始變得柔和，請同時聽下面的聲部。伴奏是否也放鬆了？還是仍保留原本的步伐或緊張？',focus:'上方旋律 ↔ 下方伴奏',detail:'第一樂章的抒情材料，會與開頭的激烈性格形成對比。聽旋律和低音的關係，可以避免只用「現在變好聽了」來理解轉折。'},
 {t:175,title:'情緒變了，哪裡先變？',text:'留意讓你覺得音樂比較溫暖或比較明亮的因素。是旋律拉長、弦樂連奏，還是和聲與音色改變？如果此刻仍緊張，也記下這個感受。',focus:'旋律線條 ／ 音色與和聲',detail:'「明亮」是聆聽比喻。真正值得追問的是，哪些可聽見的變化讓你產生這個感受；精確轉折時間仍待此版本校準。'},
 {t:210,title:'認出一個曾聽過的手勢',text:'現在試著回想開頭的性格。如果熟悉的節奏或起音再次出現，它和第一次有什麼不同？也可以注意熟悉材料是否交給了別的樂器。',focus:'記憶 ／ 相似與差異',detail:'這是一個主動聆聽練習，並非宣告此秒數一定發生主題再現。相似材料在不同和聲或配器裡，可能具有不同作用。'},
 {t:250,title:'音樂往哪裡去？',text:'把注意力放到整個樂句。它像是一直累積、遲遲不落地，還是已經得到暫時的安定？觀察你何時開始期待下一個音。',focus:'累積 ／ 期待與落點',detail:'不懂和聲名稱也能感受方向。先用自己的聽覺判斷「還沒結束」或「暫時落地」，再回頭學習它的結構。'},
 {t:285,title:'帶著一個問題重聽',text:'五分鐘快到了。回想你剛才最清楚聽見的對比：低與高、短與長、激烈與柔和。重聽時只選其中一組，看看能否聽出更多層次。',focus:'一次只追一個線索',detail:'導聆的目的是讓你更能聽見音樂。這次先熟悉介面與聆聽方式，下一版再逐段核實這個演出的時間與樂譜位置。'}
];
const $=id=>document.getElementById(id), fmt=s=>{s=Math.max(0,Math.floor(s));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')};
let player,ready=false,preview=false,index=-1,finished=false,speaking=false,apiTimer;
const status=t=>$('status').textContent=t;
function offset(){return Math.max(0,Number($('offset').value)||0)}
function cancelSpeech(){if('speechSynthesis'in window)window.speechSynthesis.cancel();speaking=false;$('speak').textContent='◉ 暫停並聽解說'}
function render(t){t=Math.max(0,Math.min(300,t));let i=cues.findLastIndex(c=>c.t<=t);$('clock').textContent=fmt(t);$('progress').style.width=(t/3)+'%';if(i===index)return;index=i;const c=cues[i];$('title').textContent=c.title;$('prompt').textContent=c.text;$('tags').textContent=c.focus;$('detail').textContent=c.detail;$('count').textContent=String(i+1).padStart(2,'0')+' / '+cues.length;$('window').textContent=fmt(c.t)+' — '+fmt(cues[i+1]?.t??300);document.querySelectorAll('.cue').forEach((b,j)=>{b.classList.toggle('active',j===i);b.setAttribute('aria-current',j===i?'step':'false')})}
function setPreview(value){preview=value;$('mode').textContent=value?'CARD PREVIEW · 圖卡預覽':'LISTENING NOTE';$('railLabel').textContent=value?'圖卡預覽 · 未跟隨影片':'五分鐘聆聽路線';$('preview').textContent=value?'返回影片同步':'預覽圖卡'}
function jump(t){cancelSpeech();finished=false;if(preview||!ready){if(!preview)setPreview(true);render(t);return}player.seekTo(offset()+t,true);render(t)}
cues.forEach((c,i)=>{const b=document.createElement('button');b.className='cue';const s=document.createElement('span');s.textContent=fmt(c.t);b.append(s,document.createTextNode(c.title));b.onclick=()=>jump(c.t);$('chapters').append(b)});
$('preview').onclick=()=>{cancelSpeech();if(!preview){if(ready)player.pauseVideo();setPreview(true);status('圖卡預覽：點選下方時間卡，影片不會跟著播放。')}else{setPreview(false);if(ready){render(player.getCurrentTime()-offset());status('已返回影片同步；按繼續播放。')}else status('播放器尚未就緒，可再次開啟圖卡預覽。')}};
$('start').onclick=()=>{cancelSpeech();setPreview(false);finished=false;player.seekTo(offset(),true);player.playVideo();render(0)};
$('toggle').onclick=()=>{cancelSpeech();setPreview(false);if(finished){finished=false;player.seekTo(offset(),true)}player.getPlayerState()===1?player.pauseVideo():player.playVideo()};
$('back').onclick=()=>{setPreview(false);jump(Math.max(0,player.getCurrentTime()-offset()-10))};
$('align').onclick=()=>{cancelSpeech();$('offset').value=player.getCurrentTime().toFixed(1);finished=false;setPreview(false);render(0);status('已將目前影片位置設為音樂起點。')};
$('offset').onchange=()=>{cancelSpeech();finished=false;$('offset').value=offset();if(ready&&!preview)render(player.getCurrentTime()-offset())};
$('speak').onclick=()=>{if(!('speechSynthesis'in window)){status('此瀏覽器未支援語音朗讀；仍可閱讀圖卡。');return}if(speaking){cancelSpeech();return}if(ready)player.pauseVideo();cancelSpeech();const c=cues[index];const u=new SpeechSynthesisUtterance(c.title+'。'+c.text);u.lang='zh-TW';u.rate=.9;const voices=window.speechSynthesis.getVoices();u.voice=voices.find(v=>/zh[-_]TW/i.test(v.lang))||voices.find(v=>/^zh/i.test(v.lang))||null;speaking=true;$('speak').textContent='■ 停止解說';u.onend=()=>{cancelSpeech();status('解說結束；按「繼續」回到音樂。')};u.onerror=()=>{cancelSpeech();status('語音未能播放，可閱讀圖卡後繼續。')};window.speechSynthesis.speak(u)};
window.onYouTubeIframeAPIReady=()=>{clearTimeout(apiTimer);player=new YT.Player('player',{videoId:'e34QpbAPgi8',playerVars:{playsinline:1,rel:0,origin:location.origin},events:{onReady:()=>{ready=true;$('loading').classList.add('hidden');['start','toggle','back','align'].forEach(id=>$(id).disabled=false);status('播放器已就緒。按「開始五分鐘導聆」，從音樂起點播放。')},onStateChange:e=>{if(e.data!==1)cancelSpeech();$('toggle').textContent=e.data===1?'暫停':'繼續';if(!preview)status(e.data===1?'正在跟隨影片時間 · 提示入點待逐段校準':e.data===2?'已暫停 · 圖卡停留在目前位置':'播放器已就緒')},onError:e=>{ready=false;['start','toggle','back','align'].forEach(id=>$(id).disabled=true);$('loading').classList.add('hidden');status('YouTube 無法播放（代碼 '+e.data+'）。可開啟原始影片，或用「預覽圖卡」查看內容。')}}})};
setInterval(()=>{if(!ready||preview||speaking)return;const t=player.getCurrentTime()-offset();render(t);if(t>=300&&player.getPlayerState()===1){player.pauseVideo();finished=true;status('五分鐘試聽結束。可點選時間卡重聽，或按繼續從頭開始。')}},200);
apiTimer=setTimeout(()=>{status('YouTube 連線較久。可先預覽圖卡，或從下方連結開啟原始影片。');$('loading').innerHTML='<div>YouTube 尚未載入<p>可先使用「預覽圖卡」瀏覽導聆內容。</p></div>'},15000);
const script=document.createElement('script');script.src='https://www.youtube.com/iframe_api';script.onerror=()=>{clearTimeout(apiTimer);status('無法連接 YouTube。可先預覽圖卡，或從下方連結開啟原始影片。');$('loading').innerHTML='<div>暫時無法連接 YouTube<p>可先預覽圖卡。</p></div>'};document.head.append(script);render(0);
window.addEventListener('pagehide',cancelSpeech);
