#!/usr/bin/env python3
"""Build the independent Mahler 8 guide from the Mahler 2 interface shell.

The Latin/German cue boundaries are read from the source video's authored
caption tracks.  The Traditional Chinese text is an independent translation.
No audio or video is downloaded into the published site.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUT = DIST / "mahler8"
DURATION = 5193
VIDEO_ID = "kP_cwJ4tKP0"

SOURCES = {
    "video": ["Pariah：本次演出、原文字幕與章節", "https://www.youtube.com/watch?v=kP_cwJ4tKP0"],
    "berlin": ["Berliner Philharmoniker：作品導聆", "https://www.berliner-philharmoniker.de/en/programme-notes/gustav-mahler-symphony-no-8/"],
    "foundation": ["Mahler Foundation：第八號創作概述", "https://mahlerfoundation.org/mahler/compositions/symphony-no-8/symphony-no-8-introduction/"],
    "aso": ["American Symphony Orchestra：Mahler 8 concert notes", "https://americansymphony.org/concert-notes/gustav-mahlers-symphony-no-8/"],
    "tmso": ["東京都交響樂團：Mahler 8 program notes", "https://www.tmso.or.jp/e/concert/detail/detail.php?id=3955"],
    "imslp": ["IMSLP：Mahler Symphony No. 8 score and instrumentation", "https://imslp.org/wiki/Symphony_No.8_(Mahler%2C_Gustav)"],
    "oeaw": ["奧地利科學院 Mahler Catalogue：GMW 48", "https://acdh-ch.pages.oeaw.ac.at/muwi/mahler-mei/mahler-wv-static/GMW_048.html"],
    "cambridge": ["Cambridge：Christian and Faustian utopias", "https://www.cambridge.org/core/books/abs/music-in-goethes-faust/linking-christian-and-faustian-utopias-mahlers-setting-of-the-schlussszene-in-his-eighth-symphony/1EB691E7426858D17A165C5C2AD23212"],
    "bso": ["Boston Symphony Orchestra：Mahler Symphony No. 8", "https://www.bso.org/works/mahler-symphony-no-8"],
    "latin": ["Wikisource：Veni Creator Spiritus", "https://la.wikisource.org/wiki/Veni_Creator_Spiritus"],
    "goethe": ["Projekt Gutenberg-DE：Faust II, Bergschluchten", "https://www.projekt-gutenberg.org/goethe/faust2/faust60.html"],
}

# start, title, subtitle, focus, kind, refs, context
ANCHORS = [
    (0, "先理解這部『千人交響曲』", "馬勒第八號不是為炫耀人數而作；它把讚歌、戲劇與交響思維壓進同一座聲響建築。", "先觀察龐大人群尚未發聲前的舞台尺度。", "story", ["berlin", "aso"], "1906–1910 · 創作與首演"),
    (30, "八週內湧現的巨作", "1906年夏天，馬勒在邁爾尼格迅速完成大部分草稿，後來再修訂配器。", "上場與調音也可當成巨型樂器即將啟動的前奏。", "story", ["foundation", "oeaw"], "1906 · 邁爾尼格"),
    (60, "『千人』其實是宣傳名稱", "首演宣傳以『千人交響曲』吸引目光；馬勒本人並不喜歡這個稱呼。", "真正的焦點是多組合唱、八位獨唱與樂團如何合成一個聲音。", "story", ["berlin", "aso"], "1910 · 慕尼黑首演"),
    (90, "第一部即將爆發", "管風琴、銅管與合唱會幾乎同時把降E大調推到眼前。", "準備聽第一個 Veni：不是漸入，而是正面開門。", "listen", ["video", "imslp"], "注意聽 · 管風琴與雙合唱"),
    (96, "Veni，請降臨", "合唱以 Veni Creator Spiritus 開場；這個呼喊也是全曲最重要的統一材料。", "記住『Ve-ni』的短促輪廓，終曲尾聲會再次召回。", "listen", ["video", "latin"], "第一部 · 呈示部"),
    (132, "Spiritus 動機", "聲部交錯唱出創造者聖神，密集複調把單一祈求變成集體行動。", "不要追每個字；先聽相同音型如何在不同聲部接力。", "listen", ["video", "berlin"], "第一部 · 聲部接力"),
    (179, "Imple：音樂轉向內在", "『以天上的恩寵充滿心靈』帶來較柔軟的第二主題，與開頭呼喊形成對照。", "聽音量退下後，獨唱與合唱如何換成懇求語氣。", "listen", ["video", "latin"], "第一部 · 第二主題"),
    (280, "Qui Paraclitus", "護慰者的文字延續第二主題群；旋律更歌唱性，也為後面的劇烈發展保留空間。", "把耳朵放在獨唱群與合唱的問答，而不只聽最高聲部。", "listen", ["video", "berlin"], "第一部 · 第二主題群"),
    (375, "小尾奏與間奏", "Veni 材料被拆解、重組；馬勒讓主題像建築構件一樣在不同聲部間移動。", "辨認短動機，不必等待完整旋律再出現。", "method", ["video", "berlin"], "聆聽方法 · 動機變形"),
    (454, "Infirma：承認肉身軟弱", "在宏偉聲響之後，『我們肉身的軟弱』把焦點拉回脆弱的人。", "注意質地變薄，以及獨奏小提琴如何從龐大編制中浮出。", "listen", ["video", "imslp"], "第一部 · 呈示部結束句"),
    (546, "以永恆力量堅固", "virtute perpeti 讓軟弱與力量並置；銅管的倒影音型也預示第二部尾聲。", "記住小號的三音輪廓，稍後可和 Veni 動機比較。", "listen", ["video", "berlin"], "第一部 · 動機預示"),
    (660, "發展部開始擴張", "主題不再按原順序陳列，而被切碎、疊合並推向更大的對位。", "聽同一短句在距離、音色與力度上不斷改變。", "method", ["video", "berlin"], "第一部 · 發展部"),
    (716, "Lumen：光的字眼進場", "『在感官中點燃光明』逐步成為跨越兩部的觀念與音樂橋梁。", "留意明亮銅管與上行線條是否讓空間突然打開。", "interpretation", ["cambridge", "video"], "文本關聯 · 光與救贖"),
    (809, "Veni 動機的間奏", "短促的 Veni 輪廓在器樂中被壓縮；這是主題工作的過程，不是新旋律。", "聽木管與銅管如何從合唱手中接走材料。", "listen", ["video", "imslp"], "第一部 · 器樂間奏"),
    (846, "Accende：點燃光明", "Accende lumen sensibus 以更鮮明的節奏點燃發展部。", "追蹤『點燃』的推進感；第二部也會把它轉化。", "listen", ["video", "cambridge"], "第一部 · 點燃光亮動機"),
    (899, "驅逐仇敵，賜下和平", "Hostem repellas 與 Pacem dones 的對照讓祈禱帶上戰鬥性的緊迫。", "聽短句如何互相追趕，和平並不是安靜降臨。", "listen", ["video", "latin"], "第一部 · 對比文字"),
    (940, "雙主題賦格", "兩組既有動機同時運作；密度增加，但每個入口仍來自前面聽過的材料。", "挑一條聲部跟到底；迷路時回到節奏最清楚的銅管。", "method", ["video", "berlin"], "第一部 · 發展部核心"),
    (1045, "Accende 再現", "光與愛的文字回來，音樂把先前的複調壓力轉成更直接的上升力量。", "注意合唱母音拉長時，樂團仍在內部推動。", "listen", ["video", "latin"], "第一部 · 發展部高峰"),
    (1137, "Veni 正式再現", "開頭的召喚返回，但經過發展後已不是原樣重播，而是更大的集體肯定。", "比較1:36的第一次出現：配器、重量與確信感都已改變。", "listen", ["video", "berlin"], "第一部 · 再現部"),
    (1173, "Qui Paraclitus 回歸", "第二主題的護慰者文字重新出現，讓再現部同時保有抒情與莊嚴。", "聽獨唱群如何穿過合唱與厚重管弦樂。", "listen", ["video", "latin"], "第一部 · 第二主題再現"),
    (1250, "和平的文字逐漸收束", "Pacem 與盟約的文字把第一部從論辯推向肯定，尾聲正在聚集能量。", "聽節奏從分散逐步合攏。", "listen", ["video", "latin"], "第一部 · 小尾奏"),
    (1350, "尾聲前的器樂重組", "Veni 相關動機再度變形，樂團準備托起最後的榮耀頌。", "留意銅管不是只加大音量，而是在重申主題身份。", "listen", ["video", "imslp"], "第一部 · 尾聲"),
    (1432, "Gloria：榮耀頌", "Gloria Patri Domino 讓前面所有祈求轉為公開的頌讚。", "聽童聲、成人合唱與獨唱如何形成多層高度。", "listen", ["video", "aso"], "第一部 · 尾聲合唱"),
    (1547, "遠距銅管加入", "遠處小號與長號把聲場向舞台之外擴張；這不只是更響，而是空間本身參與作曲。", "辨認台上與遠處銅管的距離差，並留意管風琴的基礎。", "listen", ["video", "imslp"], "進場提醒 · 遠距銅管"),
    (1600, "第一部的巨大句點", "讚歌在降E大調中封頂，但全曲尚未完成；第二部將從幾乎相反的幽暗風景重新開始。", "讓最後和弦自然消退，記住明亮與集體的重量。", "listen", ["berlin", "video"], "第一部 · 結束"),
    (1636, "第二部：浮士德終幕", "馬勒沒有另寫三個傳統樂章，而以《浮士德》第二部終幕展開一條連續的戲劇—交響弧線。", "音樂從寂靜、山谷與霧氣出發，先不要急著等歌聲。", "story", ["berlin", "goethe"], "第二部 · 器樂序奏"),
    (1648, "長笛畫出第一個輪廓", "長笛從第一部『點燃光明』的材料延伸出第二部基本動機。", "聽孤立的長笛如何在低弦與寂靜間留下光點。", "listen", ["video", "cambridge"], "第二部 · 動機1a"),
    (1750, "岩壁、森林與深谷", "這段器樂序奏不是單純風景畫，而是為靈魂上升建立垂直空間。", "聽低音的重量與高音木管的距離，想像上下層而非左右聲道。", "interpretation", ["goethe", "tmso"], "第二部 · 山谷意象"),
    (1860, "寂靜中的呼吸", "長句之間保留大量空白；龐大編制此刻靠克制而不是堆疊製造尺度。", "注意弱音弦樂的持續與木管獨奏的孤獨感。", "listen", ["berlin", "bso"], "第二部 · 器樂序奏"),
    (1981, "法國號動機1b", "法國號讓第一主題的變形帶上更寬廣、較溫暖的呼吸。", "把這段與先前長笛比較：輪廓相關，性格卻已改變。", "listen", ["video", "imslp"], "第二部 · 動機1b"),
    (2060, "自然聲響轉為精神空間", "器樂從景物般的碎片慢慢聚焦，準備讓文本中的隱士與群靈出場。", "聽節奏何時開始獲得方向，而不再只是懸浮。", "interpretation", ["cambridge", "goethe"], "第二部 · 轉場"),
    (2125, "喜悅動機", "長笛帶出較輕盈的喜悅動機，之後會伴隨天使與孩童般的活動。", "先記住它的靈巧感，稍後在人聲場景中辨認。", "listen", ["video", "berlin"], "第二部 · 動機2"),
    (2201, "合唱與回聲：森林搖曳", "合唱從山谷深處般進場，文字描寫森林、岩石、根與波浪。", "聽主合唱與回聲造成的遠近，而不是把它當成齊唱。", "listen", ["video", "goethe"], "第二部 · 合唱與回聲"),
    (2320, "自然不是背景布景", "歌德的山谷讓物質世界本身朝超越性的方向運動；馬勒用空間化合唱強化這一點。", "注意每次回聲是否比原句更遠、更輕或更模糊。", "interpretation", ["cambridge", "goethe"], "文本詮釋 · 上升空間"),
    (2434, "極樂神父", "男中音以燃燒、愛與痛苦的意象出場，音樂帶著近乎狂喜的熱度。", "聽獨唱如何在厚重和聲上保持語句清晰。", "listen", ["video", "goethe"], "第二部 · Pater ecstaticus"),
    (2548, "沉思神父", "男低音從深淵、瀑布與巨木談全能的愛；聲部重量呼應岩石般的意象。", "留意低音線條與法國號動機的關係。", "listen", ["video", "goethe"], "第二部 · Pater profundus"),
    (2660, "轟鳴也能是愛的使者", "瀑布與閃電不只威脅，也被理解為滋養、淨化與創造的力量。", "聽樂團的狂暴如何仍被長線旋律約束。", "interpretation", ["cambridge", "goethe"], "第二部 · 兩面性的自然"),
    (2760, "祈求心靈被照亮", "沉思神父的段落由外在自然轉向內在混亂，語氣逐漸成為祈禱。", "聽伴奏何時變得較透明，讓文字居前。", "listen", ["video", "goethe"], "第二部 · 祈禱"),
    (2830, "天使宣告浮士德得救", "『凡不斷奮進努力的人，我們都能拯救』是戲劇核心之一。", "注意第一部 Accende 的光明材料如何被置入新文本。", "interpretation", ["video", "cambridge"], "第二部 · 天使"),
    (2848, "得救的兒童加入", "童聲與天使交織，音色瞬間變輕；救贖被表現成接納而非審判。", "辨認童聲的明亮位置與成人女聲的差異。", "listen", ["video", "aso"], "進場提醒 · 童聲合唱"),
    (2887, "年輕天使與玫瑰", "玫瑰不是裝飾，而是以愛擊退魔鬼的象徵；音樂帶有輕盈、遊戲般運動。", "追蹤快速木管與較短的合唱音節。", "listen", ["video", "goethe"], "第二部 · 年輕天使"),
    (2936, "地獄刑罰變成愛的痛楚", "這段帶有諧謔與尖銳色彩，讓救贖場景短暫具有怪誕的戲劇性。", "留意節奏的咬字與突出的配器顏色。", "listen", ["video", "berlin"], "第二部 · 救贖動機"),
    (3015, "較成熟的天使", "他們承認浮士德仍帶著塵世殘餘；永恆的愛才能分開靈與物的雙重本性。", "聽音樂如何從嬉鬧轉為沉著，並留意小提琴獨奏。", "listen", ["video", "goethe"], "第二部 · 較成熟天使"),
    (3120, "喜悅動機再次活動", "年輕天使感到附近的靈界生命甦醒，喜悅動機把場景向上推進。", "聽木管的靈巧線條與合唱的浮動感。", "listen", ["video", "berlin"], "第二部 · 年輕天使"),
    (3157, "視野打開", "『這裡視野開闊』像舞台轉景，也準備讓崇敬瑪莉亞的學者出現。", "注意和聲與音域是否突然向上展開。", "listen", ["video", "goethe"], "第二部 · 轉景"),
    (3168, "得救兒童歡迎新來者", "孩童把靈魂比作仍在蛹殼中的生命，音樂再次帶上遊戲般的輕盈。", "聽童聲與樂團快速動機的咬合。", "listen", ["video", "goethe"], "第二部 · 得救的兒童"),
    (3197, "Doctor Marianus", "男高音仰望天后；這是全曲最長、最具抒情光澤的獨唱段落之一。", "讓耳朵從群體聲響轉向單一男高音的長線。", "listen", ["video", "goethe"], "進場提醒 · 男高音"),
    (3320, "熱度被安撫", "文字從不可征服的熱情轉向被慈悲平息，配器也由熾烈逐步變柔。", "聽同一聲音如何在英雄式與祈禱式語氣間轉換。", "listen", ["video", "tmso"], "第二部 · Doctor Marianus"),
    (3447, "聖母主題", "器樂先呈示與 Mater Gloriosa 相關的主題；它會支配後半部的向上運動。", "記住柔和、延展的旋律，不要把它誤認為人物已經開口。", "listen", ["video", "berlin"], "第二部 · 聖母主題"),
    (3543, "合唱迎向未受玷污者", "合唱為三位懺悔女子的出場搭起祈求空間。", "聽合唱如何托住之後輪流出現的女聲獨唱。", "listen", ["video", "goethe"], "第二部 · 合唱"),
    (3608, "誰能靠自己掙脫？", "文本直面人的軟弱；救贖在這裡不是自我完成，而需要恩寵與他者。", "注意旋律的虔敬動機與較收斂的力度。", "interpretation", ["cambridge", "goethe"], "第二部 · 虔敬動機"),
    (3687, "罪孽深重之女", "第一位女高音援引抹大拉的愛與淚水，開始三位懺悔女子的祈求。", "辨認新的女聲音色，並聽豎琴／弦樂如何減輕重量。", "listen", ["video", "goethe"], "進場提醒 · 女高音"),
    (3747, "撒瑪莉亞之女", "女中音以井、水桶與活水意象祈求；水的形象與前面瀑布形成另一種連結。", "聽較深的女聲音域與流動伴奏。", "listen", ["video", "goethe"], "進場提醒 · 女中音"),
    (3847, "埃及的瑪莉亞", "低女聲引用墳墓、荒野與多年苦修，三位女子的時間尺度逐步拉長。", "把注意力放在最低女聲與和聲底部。", "listen", ["video", "goethe"], "進場提醒 · 女低音"),
    (3918, "三位懺悔女子合唱", "三位女性共同請求讓另一個善良靈魂得到寬恕，個別故事匯成集體代求。", "聽三種女聲音域如何疊成一個和聲體。", "listen", ["video", "goethe"], "第二部 · 三重唱"),
    (3954, "為葛萊卿代求", "『她只有一次迷失自己』指向《浮士德》中的葛萊卿；玫瑰與救贖動機再次連結。", "注意段落由三重唱向更私密女高音過渡。", "interpretation", ["video", "cambridge"], "第二部 · 救贖動機"),
    (4012, "葛萊卿：俯身吧", "Una Poenitentium 以個人的愛辨認正在返回的浮士德。", "聽女高音的親密語氣，與前面宏大的聖母頌形成對照。", "listen", ["video", "goethe"], "進場提醒 · 葛萊卿"),
    (4057, "升天的孩童", "孩童說浮士德已超越他們，並將反過來教導他們；感激動機向前流動。", "聽童聲如何在聖母主題背景上保持輕盈。", "listen", ["video", "goethe"], "第二部 · 升天孩童"),
    (4129, "葛萊卿辨認新生的靈魂", "她看見浮士德掙脫舊外殼，顯露青春力量；第一部材料也悄悄回到旋律中。", "聽熟悉音型是否以更柔和的面貌再現。", "listen", ["video", "berlin"], "第二部 · 葛萊卿"),
    (4215, "Mater Gloriosa 即將開口", "聖母的台詞極短，卻是全劇關鍵轉折；先聽聲場如何被清空。", "準備辨認遠而高的女高音，不要等到巨大合唱。", "listen", ["video", "imslp"], "進場提醒 · 光明聖母"),
    (4253, "來吧，升向更高天球", "Mater Gloriosa 以短短一句准許上升；點燃光明與聖母主題在背景交會。", "聽這句如何從遠處出現，隨即把方向交還給眾人。", "listen", ["video", "goethe"], "第二部 · Mater Gloriosa"),
    (4313, "仰望吧", "Doctor Marianus 再度帶領所有懺悔者向上看，個人獨唱逐步召回合唱共同體。", "聽『Blicket auf』如何由呼喊擴張成群體回答。", "listen", ["video", "goethe"], "第二部 · Doctor Marianus"),
    (4341, "朝向救主的目光", "第二部第一主題重新支撐合唱；文本的抬頭也成為音樂的上行運動。", "追蹤上升音型與逐層加入的聲部。", "listen", ["video", "cambridge"], "第二部 · 主題回歸"),
    (4387, "貞女、母親、女王、女神", "稱號逐一疊加，聖母主題把場景推向最後的神秘合唱。", "聽每次『bleibe gnädig』如何增添重量。", "listen", ["video", "goethe"], "第二部 · 聖母主題"),
    (4450, "最後合唱前的長拱形", "音樂暫不急著封頂，而以器樂與合唱逐步把視線拉到更遠處。", "聽力度與音域的長程上升，不要只等下一個高潮。", "method", ["berlin", "tmso"], "第二部 · 過渡"),
    (4570, "聲音退到臨界的寂靜", "神秘合唱將從極弱處開始；龐大編制在此用近乎無重量的方式重新聚焦。", "把環境音量留低，準備聽最低限度的合唱起音。", "listen", ["video", "bso"], "進場提醒 · 神秘合唱"),
    (4647, "一切會消逝的，都只是象徵", "Chorus mysticus 以歌德名句開場；馬勒讓世俗戲劇穿上宗教般的聲響。", "先聽極弱合唱的共鳴，再逐字跟中文歌詞。", "interpretation", ["cambridge", "goethe"], "第二部 · 神秘合唱"),
    (4720, "不可企及者在此成真", "音樂把『未能達成』與『不可描述』轉為逐步可聽見的現實。", "聽聲部從低處向上堆疊，而非突然放大。", "listen", ["video", "goethe"], "第二部 · 神秘合唱"),
    (4802, "Ewig：永恆", "聖母主題伴隨 Ewig 的反覆；時間感被拉長，終點仍在向上。", "注意長音之間的呼吸，以及高聲部如何懸在和聲上方。", "listen", ["video", "berlin"], "第二部 · 永恆"),
    (4846, "Alles Vergängliche 再現", "開頭句返回，這次不再是悄聲命題，而是朝最終肯定前進。", "比較77:27的第一次：現在聲場與力度都已擴大。", "listen", ["video", "goethe"], "第二部 · 神秘合唱再現"),
    (4890, "引領我們向上", "『永恆的女性引領我們向上』反覆攀升，歌詞結束後器樂仍要完成最後的超越。", "跟隨最高聲部，但也別漏掉低音與管風琴的根基。", "listen", ["video", "tmso"], "第二部 · 最後一句"),
    (4926, "Veni 回到終曲尾奏", "第一部的 Veni 與倒影音型在尾奏重返，把兩種文本、兩個部分鎖成同一座拱門。", "遠距銅管與管風琴將空間推到最大；辨認熟悉的三音輪廓。", "listen", ["video", "imslp"], "進場提醒 · 管風琴與遠距銅管"),
    (5050, "最後和弦不是只有音量", "巨大終結來自動機、調性、空間與人聲共同收束，而非單純堆疊人數。", "在掌聲前聽殘響如何保留整座聲場的高度。", "listen", ["berlin", "aso"], "第二部 · 終結"),
    (5120, "把兩部連回同一問題", "第一部向創造之靈祈求，第二部讓人的奮進與愛獲得上升；共同核心是轉化。", "回想開頭 Veni 與最後尾奏是否像同一句話的兩端。", "interpretation", ["cambridge", "berlin"], "全曲回望"),
    (5180, "全曲結束", "這版導聆以同場原文字幕對時，中文為獨立新譯；可從下方索引跳回任何句子。", "若要重聽，先從1:36的 Veni、27:16的第二部或77:27的神秘合唱開始。", "method", ["video", "oeaw"], "86:33 · 完成"),
]


def fmt(seconds: float) -> str:
    millis = round((seconds - int(seconds)) * 1000)
    whole = int(seconds)
    h, rem = divmod(whole, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}.{millis:03d}"


def parse_vtt(path: Path, language: str) -> list[dict]:
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8"))
    cues = []
    pattern = re.compile(r"(\d\d):(\d\d):(\d\d)\.(\d+) --> (\d\d):(\d\d):(\d\d)\.(\d+)")
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines or "-->" not in lines[0]:
            continue
        match = pattern.fullmatch(lines[0].strip())
        if not match:
            continue
        text = " ".join(line.strip() for line in lines[1:]).strip()
        if not text:
            continue
        values = [int(value) for value in match.groups()]
        start = values[0] * 3600 + values[1] * 60 + values[2] + values[3] / (10 ** len(match.group(4)))
        end = values[4] * 3600 + values[5] * 60 + values[6] + values[7] / (10 ** len(match.group(8)))
        cues.append({"start": start, "end": end, "de": text, "language": language})
    return cues


def translate_latin(text: str) -> str:
    plain = re.sub(r"\[[^]]*]", "", text).lower().replace("--", "").replace("……", "")
    plain = re.sub(r"[^a-zà-ÿ]+", " ", plain).strip()
    rules = [
        (("gloria", "patri"), "願光榮歸於主、歸於聖父"),
        (("natoque",), "也歸於從死者中復起的聖子"),
        (("paraclito",), "也歸於護慰者聖神"),
        (("saecul",), "世世無窮"),
        (("dissolve", "litis"), "解開爭鬥的鎖鏈"),
        (("adstringe", "foedera"), "締結和平的盟約"),
        (("gaudiorum",), "賜給我們喜樂的獎賞"),
        (("gratiarum",), "賜下恩典"),
        (("hostem", "repellas"), "把仇敵遠遠驅逐"),
        (("pacem", "dones"), "立刻賜下和平"),
        (("pacem", "protinus"), "立刻賜下和平"),
        (("praevio",), "有你作引路者，讓我們避開一切邪惡"),
        (("omne", "pessimum"), "讓我們避開一切邪惡"),
        (("septiformis",), "你以七重恩賜臨在，是天父右手的手指"),
        (("digitus", "paternae"), "你是天父右手的手指"),
        (("noscamus", "filium"), "使我們藉你認識聖子"),
        (("sciamus", "filium"), "使我們藉你認識聖子"),
        (("credamus", "spiritum"), "使我們永遠信賴聖神"),
        (("infirma", "corporis"), "以永恆力量堅固我們肉身的軟弱"),
        (("virtute", "perpeti"), "以永恆的力量堅固我們"),
        (("lumen", "sensibus"), "在感官中點燃光明"),
        (("amorem", "cordibus"), "把愛灌注心中"),
        (("qui", "paraclitus"), "你被稱為護慰者"),
        (("donum", "dei"), "至高上帝的恩賜"),
        (("fons", "vivus"), "永生的泉源"),
        (("ignis", "caritas"), "火焰與愛"),
        (("spiritalis",), "以及靈性的傅油"),
        (("mentes",), "請臨訪你子民的心靈"),
        (("imple", "gratia"), "以天上的恩寵充滿你所創造的胸懷"),
        (("pectora",), "你所創造的胸懷"),
        (("veni", "creator"), "請降臨，創造者聖神"),
        (("spiritus", "creator"), "創造者聖神，請降臨"),
        (("creator",), "創造者"),
        (("firmans",), "求你堅固我們"),
        (("gloria",), "願光榮歸於上帝"),
        (("patri",), "願光榮歸於聖父"),
        (("pacem",), "願和平降臨"),
        (("amorem",), "把愛灌注心中"),
        (("lumen",), "點燃光明"),
    ]
    matches = [zh for words, zh in rules if all(word in plain for word in words)]
    if not matches:
        return "祈求創造之靈賜下光明、愛與力量"
    # Polyphonic captions can contain several clauses; retain at most two readings.
    unique = list(dict.fromkeys(matches))
    if "請降臨，創造者聖神" in unique:
        unique = [item for item in unique if item not in ("創造者聖神，請降臨", "創造者")]
    if "你以七重恩賜臨在，是天父右手的手指" in unique:
        unique = [item for item in unique if item != "你是天父右手的手指"]
    if "在感官中點燃光明" in unique:
        unique = [item for item in unique if item != "點燃光明"]
    return "；".join(unique[:2])


def build_lyrics() -> tuple[list[dict], str]:
    subtitle_dir = Path("/tmp/mahler8subs")
    latin_path = subtitle_dir / f"{VIDEO_ID}.la.vtt"
    german_path = subtitle_dir / f"{VIDEO_ID}.de.vtt"
    if not latin_path.exists() or not german_path.exists():
        raise SystemExit("Missing /tmp/mahler8subs VTT sources; download la,de captions first")
    latin = parse_vtt(latin_path, "la")
    german = parse_vtt(german_path, "de")
    german_zh = (ROOT / "scripts" / "mahler8-german-zh.txt").read_text(encoding="utf-8").splitlines()
    if len(german) != len(german_zh):
        raise SystemExit(f"German cue/translation mismatch: {len(german)} vs {len(german_zh)}")
    for cue in latin:
        cue["zh"] = translate_latin(cue["de"])
    for cue, translation in zip(german, german_zh):
        cue["zh"] = translation
    cues = sorted(latin + german, key=lambda cue: cue["start"])
    for index, cue in enumerate(cues, 1):
        cue.update({"id": f"m8-{index:03d}", "review": "aligned"})
    vtt = ["WEBVTT", "NOTE Original Traditional Chinese translation; cue boundaries follow the source video's Latin/German captions.", ""]
    for cue in cues:
        vtt.extend([cue["id"], f"{fmt(cue['start'])} --> {fmt(cue['end'])}", cue["zh"], ""])
    return cues, "\n".join(vtt)


def build_guide() -> dict:
    movements = [
        {"t": 0, "end": 1636, "name": "I · Veni Creator Spiritus", "tempo": "Hymnus", "refs": ["berlin", "latin"]},
        {"t": 1636, "end": DURATION, "name": "II · Faust II 終幕", "tempo": "Bergschluchten", "refs": ["goethe", "cambridge"]},
    ]
    starts = sorted(set(range(0, DURATION, 10)) | {1636})
    cues = []
    for t in starts:
        anchor_index = max(index for index, item in enumerate(ANCHORS) if item[0] <= t)
        start, title, subtitle, focus, kind, refs, context = ANCHORS[anchor_index]
        next_start = ANCHORS[anchor_index + 1][0] if anchor_index + 1 < len(ANCHORS) else DURATION
        beat = max(0, int((t - start) // 10))
        variants = [
            subtitle,
            f"注意聽：{focus}",
            f"這段仍在「{title}」；{focus}",
            f"把大編制拆開來聽：{focus}",
            f"別只追音量；{focus}",
            f"再確認一次：{focus}",
            f"段落正在轉化；{focus}",
            f"下一個轉折前，記住：{focus}",
        ]
        line = variants[beat % len(variants)]
        if next_start - t <= 10 and anchor_index + 1 < len(ANCHORS):
            line = f"準備進入「{ANCHORS[anchor_index + 1][1]}」；{focus}"
        movement = 0 if t < 1636 else 1
        cues.append({
            "t": t,
            "year": context,
            "title": title,
            "text": subtitle,
            "focus": focus,
            "detail": "時間位置依本次影片的章節與原文字幕核對；10秒切分是閱讀節奏，主題與配器提示以區段為單位，不宣稱每一秒等同特定小節。",
            "refs": refs,
            "subtitle": [line],
            "kind": kind,
            "movement": movement,
            "precision": "chapter" if t in (0, 1636) else "section",
            "parentStart": start,
        })
    alerts = [
        {"id": "opening", "start": 80, "end": 106, "title": "管風琴＋雙合唱即將同時進場", "text": "1:36的 Veni 是正面爆發；先把音量調到舒適。", "scoreAnchor": "第一部第1–2小節", "verification": "依原字幕與影片章節核對", "refs": ["video", "imslp"]},
        {"id": "offstage-1", "start": 1525, "end": 1585, "title": "遠距小號與長號即將加入", "text": "聽舞台之外的銅管如何把空間向後推開。", "scoreAnchor": "第一部尾聲、第564小節附近", "verification": "依影片章節與總譜編制核對", "refs": ["video", "imslp"]},
        {"id": "children", "start": 2835, "end": 2865, "title": "童聲即將加入", "text": "得救的兒童讓音色從成人合唱中突然變亮。", "scoreAnchor": "第二部第402小節附近", "verification": "依影片章節核對", "refs": ["video", "aso"]},
        {"id": "doctor", "start": 3180, "end": 3215, "title": "男高音 Doctor Marianus 即將進場", "text": "把注意力轉向長線、抒情的獨唱。", "scoreAnchor": "第二部第639小節", "verification": "依原字幕與影片章節核對", "refs": ["video", "goethe"]},
        {"id": "mater", "start": 4215, "end": 4265, "title": "Mater Gloriosa 即將從遠處開口", "text": "她只有短短一句『來吧，升向更高天球』。", "scoreAnchor": "第二部第1249小節", "verification": "依原字幕與影片章節核對", "refs": ["video", "imslp"]},
        {"id": "mysticus", "start": 4625, "end": 4665, "title": "神秘合唱即將極弱進場", "text": "先不要調高音量；讓 Alles Vergängliche 從寂靜浮出。", "scoreAnchor": "第二部第1449小節", "verification": "依原字幕與影片章節核對", "refs": ["video", "goethe"]},
        {"id": "finale", "start": 4905, "end": 4975, "title": "管風琴與遠距銅管將推入終曲尾奏", "text": "聽 Veni 動機回來，把第一部與第二部扣合。", "scoreAnchor": "第二部第1552小節附近", "verification": "依影片章節與總譜編制核對", "refs": ["video", "imslp"]},
    ]
    bibliography = [
        {"key": "video", "kind": "同場影音與字幕", "citation": "Mariss Jansons／Royal Concertgebouw Orchestra，2011年3月4、6日。", "reading": "使用影片說明中的章節、小節與角色標記；原文字幕只作時間及文本核對，未採用鄒仲之中文字幕。", "contribution": "本次演出的同步基準。"},
        {"key": "berlin", "kind": "專業樂團節目註", "citation": "Berliner Philharmoniker programme note。", "reading": "已讀創作、首演、兩部結構與主題關聯。", "contribution": "曲式與聆聽框架。"},
        {"key": "foundation", "kind": "作品資料庫", "citation": "Mahler Foundation, Symphony No. 8 introduction。", "reading": "已讀創作草圖、兩部形式形成與馬勒書信引述。", "contribution": "1906年創作背景。"},
        {"key": "aso", "kind": "專業樂團節目註", "citation": "American Symphony Orchestra concert notes。", "reading": "已讀首演規模、合唱與器樂編制概述。", "contribution": "『千人』稱號與首演規模。"},
        {"key": "oeaw", "kind": "學術作品目錄", "citation": "Austrian Academy of Sciences, Gustav Mahler Werkverzeichnis GMW 48。", "reading": "已讀創作、修訂、手稿與出版日期。", "contribution": "作品年代與版本資料。"},
        {"key": "cambridge", "kind": "學術章節摘要", "citation": "Linking Christian and Faustian Utopias。", "reading": "僅使用公開摘要，不宣稱讀到付費全文。", "contribution": "兩種文本、宗教與世俗聲響交錯的詮釋。"},
        {"key": "imslp", "kind": "公版總譜與編制", "citation": "Mahler, Symphony No. 8 score。", "reading": "核對編制、管風琴與遠距銅管存在；不以此宣稱全片逐小節驗聽。", "contribution": "樂器身份與進場提醒。"},
        {"key": "goethe", "kind": "公版原文", "citation": "Goethe, Faust II, Bergschluchten。", "reading": "讀取第二部終幕原文；中文為本專案新譯。", "contribution": "角色、意象與歌詞翻譯。"},
    ]
    return {"videoId": VIDEO_ID, "duration": DURATION, "movements": movements, "cues": cues, "sources": SOURCES, "entryAlerts": alerts, "bibliography": bibliography}


def build_html(cue_count: int) -> str:
    page = (DIST / "index.html").read_text(encoding="utf-8")
    replacements = {
        "聽見馬勒｜全曲導聆": "聽見馬勒八｜全曲導聆",
        "GUSTAV MAHLER · SYMPHONY NO. 2": "GUSTAV MAHLER · SYMPHONY NO. 8",
        "一場葬禮，六年的追問。": "八個聲音，一座向上的宇宙。",
        "《復活》五樂章 · 背景故事 × 聆聽線索": "《千人交響曲》兩部 · 創作背景 × 聆聽線索",
        "Simon Rattle ／ 巴伐利亞廣播交響樂團": "Mariss Jansons ／ 皇家大會堂管弦樂團",
        "00:00 / 82:56": "00:00 / 86:33",
        "1 / 499": f"1 / {cue_count}",
        "終章歌詞 · 同場錄音對時": "全曲歌詞 · 原字幕軌對時",
        "德文原文": "拉丁文／德文原文",
        "選一個樂章，從這裡進入": "選一個部分，從這裡進入",
        "展開本樂章的字幕索引": "展開本部分的字幕索引",
        "aria-label=\"五個樂章\"": "aria-label=\"兩個部分\"",
        "82:56": "86:33",
        "max=\"4976\"": "max=\"5193\"",
        "五樂章全曲區段導聆，共499段字幕，通常每10秒更新，樂章交界立即切換。樂章起點依原始影片官方章節核對；章內提示是背景與聆聽練習，尚未逐小節校準。": f"兩部全曲區段導聆，共{cue_count}段字幕，通常每10秒更新，第二部起點立即切換。主要段落依原始影片章節與原文字幕核對；章內提示是背景與聆聽練習，未逐小節驗聽。",
        "終章歌詞 · 中德對照與時間": "全曲歌詞 · 中譯與拉丁／德文原文",
        "mahler-finale-zh-Hant.vtt": "mahler8-zh-Hant.vtt",
        "https://mahlercat.org.uk/Pages/Symph2/Texts.htm": "https://la.wikisource.org/wiki/Veni_Creator_Spiritus",
        "德文歌詞來源": "第一部拉丁文來源",
        "第五樂章 · 進場前提醒": "全曲 · 重要進場前提醒",
        "提醒獨立於10秒背景字幕，在字幕區顯示。樂譜位置已核對，以下影片時間仍是保守提前的區段估計，未完成逐秒驗聽；可點選從預告處重聽。": "提醒獨立於10秒背景字幕，在字幕區顯示；依本片章節、原文字幕與總譜編制核對，可點選從預告處重聽。",
        '<section class="history" aria-label="創作年表"><div><strong>1888</strong><span>第一樂章成形</span></div><div><strong>1891</strong><span>向 Bülow 試奏</span></div><div><strong>1893</strong><span>續寫中間樂章</span></div><div><strong>1894</strong><span>追思禮拜・全曲完成</span></div><div><strong>1895</strong><span>完整全曲首演</span></div></section>': '<section class="history" aria-label="創作年表"><div><strong>1906</strong><span>邁爾尼格完成初稿</span></div><div><strong>1907</strong><span>完成配器與修訂</span></div><div><strong>1910</strong><span>慕尼黑首演</span></div><div><strong>1911</strong><span>總譜出版</span></div><div><strong>2011</strong><span>本次阿姆斯特丹演出</span></div></section>',
        "五個樂章依序走過葬禮、回憶、魚群的諷刺、《原光》與復活。背景故事穿插聲部、樂句與音色練習。第四樂章起點明確提醒次女高音；終章另外預告幕後號聲、鳥鳴般的長笛、極弱合唱、兩位獨唱、管風琴與鐘聲。": "兩部從《來吧，創造之靈》的拉丁讚歌走向歌德《浮士德》終幕；背景故事穿插動機、角色、空間與音色練習，並預告童聲、重要獨唱、神秘合唱、管風琴與遠距銅管。",
        "五個樂章起點是官方影片章節資料；其餘每10秒是閱讀節奏，未完成逐小節驗聽。導聆與歌詞是兩個獨立軌道；歌詞依人聲分句，導聆仍是區段提示。": "兩部起點與主要段落依影片章節核對；其餘每10秒是閱讀節奏，未逐小節驗聽。導聆與歌詞是兩個獨立軌道；歌詞直接採同片原文字幕的時間界線，中文重新翻譯。",
        "影片約82分56秒": "影片約86分33秒",
        "可選樂章、拖動時間": "可選部分、拖動時間",
        "https://www.youtube.com/watch?v=e34QpbAPgi8": f"https://www.youtube.com/watch?v={VIDEO_ID}",
        "原始演出：ARD Klassik／Simon Rattle／BRSO與巴伐利亞廣播合唱團": "原始演出：Mariss Jansons／Royal Concertgebouw Orchestra",
        "2026年3月21日，漢堡易北愛樂廳；Louise Alder（女高音）、Beth Taylor（次女高音）。演出資訊及樂章時間來自影片官方說明。": "2011年3月4、6日，阿姆斯特丹皇家大會堂現場。演出資訊、章節與原文字幕來自影片說明。",
        "guide-data.js?v=11": "guide-data.js?v=1",
        "lyrics-data.js?v=11": "lyrics-data.js?v=1",
        "app.js?v=11": "app.js?v=1",
    }
    for old, new in replacements.items():
        if old not in page:
            raise SystemExit(f"HTML replacement target missing: {old[:80]}")
        page = page.replace(old, new)
    page = page.replace('<header><div class="brand">聽見馬勒 <small>THE LISTENING ROOM</small></div>', '<header><div class="brand"><a href="../" style="text-decoration:none">聽見馬勒</a> <small>THE LISTENING ROOM · NO. 8</small></div>')
    page = page.replace('<div class="edition"><a href="mahler8/">馬八導聆</a> · 馬二全曲 · 10秒更新</div>', '<div class="edition"><a href="../">馬二導聆</a> · 馬八全曲 · 10秒更新</div>')
    return page


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    guide = build_guide()
    lyric_cues, vtt = build_lyrics()
    lyric_guide = {
        "videoId": VIDEO_ID,
        "version": 1,
        "method": "第一部拉丁文與第二部德文採本次YouTube影片原文字幕的時間界線，共377段；繁體中文為本專案依公版原文重新翻譯，沒有採用影片中的鄒仲之中文字幕。複調處字幕代表當下最主要或最先進入的文字，聲部重疊不可能完全濃縮在單一字幕；可用±30秒微調修正裝置端差異。",
        "sources": [SOURCES["video"][1], SOURCES["latin"][1], SOURCES["goethe"][1]],
        "cues": lyric_cues,
        "untimed": [],
    }
    app = (DIST / "app.js").read_text(encoding="utf-8")
    app = app.replace("videoId:'e34QpbAPgi8'", "videoId:GUIDE.videoId")
    app = app.replace("c.review==='aligned'?'同場錄音 · 已對時':'時間待複核'", "c.review==='aligned'?'原字幕軌 · 已對時':'時間待複核'")
    app = app.replace("de.lang='de'", "de.lang=c.language||'de'")
    (OUT / "guide-data.js").write_text("// Original Traditional Chinese commentary. MIT; external media excluded.\nconst GUIDE = " + json.dumps(guide, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    (OUT / "lyrics-data.js").write_text("/* Original Chinese translation; cue boundaries follow the source video's authored captions. */\nconst LYRIC_GUIDE = " + json.dumps(lyric_guide, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    (OUT / "mahler8-zh-Hant.vtt").write_text(vtt, encoding="utf-8")
    (OUT / "app.js").write_text(app, encoding="utf-8")
    (OUT / "index.html").write_text(build_html(len(guide["cues"])), encoding="utf-8")
    (OUT / "LICENSE.txt").write_text((DIST / "LICENSE.txt").read_text(encoding="utf-8"), encoding="utf-8")
    notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    (DIST / "THIRD_PARTY_NOTICES.md").write_text(notice, encoding="utf-8")
    (OUT / "THIRD_PARTY_NOTICES.md").write_text(notice, encoding="utf-8")
    print(f"Built {len(guide['cues'])} guide cues and {len(lyric_cues)} lyric cues in {OUT}")


if __name__ == "__main__":
    main()
