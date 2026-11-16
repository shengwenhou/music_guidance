# 聽見馬勒｜五分鐘導聆

馬勒第二號交響曲《復活》開頭五分鐘的互動導聆試作，以原始 YouTube 演出搭配繁體中文提示卡。

## 第 3 版：影片下方同步字幕

影片下方顯示每段兩句精簡字幕，完整故事與史料改為可展開區域。支援上一段／下一段、字幕預覽，以及「影片＋字幕全螢幕」。字幕位於 YouTube 播放器範圍之外，不覆蓋影片或控制項。若瀏覽器不支援 Fullscreen API，改用頁內專注模式，可按退出或 Esc 離開。YouTube 內建全螢幕只會放大影片，請使用網頁提供的按鈕。

## 第 2 版：創作故事 × 聆聽

每張卡分成背景故事、聆聽提示、補充與史料。從1888年的《葬禮》、1891年試奏、1893年續寫，到1894年追思禮拜與1895年全曲首演，將創作歷程連回聲音。每20秒換卡，這是閱讀節奏，不是已驗證的樂譜事件入點。卡片附來源連結，並區分史實、馬勒事後的自述及聆聽比喻。

敘事方向參考使用者提供的 [Musecow 影片](https://www.youtube.com/watch?v=YChlv0nklJI)，未取得影片逐字稿，未轉錄原講稿。

## 目前狀態

**五分鐘創作背景導聆。** 十五段字幕跟隨影片時間，每20秒帶入一個背景故事與聆聽線索。本版完成的是背景導聆與字幕播放器，不是逐小節音樂分析；時間不代表特定主題或樂器的精確入點。

- YouTube 播放位置同步圖卡，支援暫停、跳轉與音樂起點校正。
- 五分鐘結束自動暫停，支援重聽十秒及圖卡預覽。
- 瀏覽器 TTS：先暫停音樂再朗讀，語音結束後手動繼續。
- 音樂由原始影片提供，本專案不包含演出音訊、影片或下載功能。

## 本機執行

需要 Python 3。在專案目錄執行：

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory dist
```

開啟 <http://127.0.0.1:8765/>。用完後按 Control+C。

請勿直接雙擊 HTML 使用 `file://` 開啟，YouTube 可能因缺少 HTTP Referer 而回報錯誤 153。瀏覽器或擴充功能阻擋來源資訊時，也可能出現相同錯誤。

## GitHub Pages

專案已啟用 GitHub Pages：[觀看網站](https://shengwenhou.github.io/music_guidance/)。部署流程支援 main 分支變更後發布，也保留手動執行。

1. 確認希望網站對外公開，且帳號方案支援該儲存庫的 Pages。
2. 在儲存庫 Settings → Pages，將 Source 設為 GitHub Actions。
3. 到 Actions → Deploy listening guide → Run workflow。
4. 部署成功後，以 Pages 顯示的網址開啟。原始影片是否允許嵌入，以及實際同步效果，仍須在部署環境驗證。

## 檔案

| 路徑 | 用途 |
| --- | --- |
| `dist/index.html` | 畫面、樣式、使用說明 |
| `dist/app.js` | 十五段導聆字幕、YouTube 同步與 TTS |
| `.github/workflows/pages.yml` | 手動發布至 GitHub Pages |

## 下一步

- 逐段驗聽並以本次演出的樂譜位置校準提示。
- 在 Safari、Chrome 與行動裝置驗證播放器、跳轉與語音。
- 增加真正對應段落的配器圖卡與主題比較。

## 參考

- [原始演出：ARD Klassik／Simon Rattle／BRSO](https://www.youtube.com/watch?v=e34QpbAPgi8)
- [Mahler Foundation：第一樂章](https://mahlerfoundation.org/mahler/compositions/symphony-no-2/symphony-no-2-movement-1-allegro-maestoso/)
- [Utah Symphony：導聆](https://usuo.org/explore/2014/11/mahler-2-listening-guide/)
- [YouTube IFrame Player API](https://developers.google.com/youtube/iframe_api_reference)

導聆中的情緒描述是聆聽比喻，不是唯一詮釋。演出及相關標誌權利屬原權利人。

## 驗證與限制

- 互動回歸檢查：`node --test tests/guide.test.cjs`，部署前自動執行。
- 已以瀏覽器實際測試影片播放、字幕跳轉、暫停、字幕預覽及影片＋字幕共同全螢幕。
- 全螢幕字幕維持在播放器下方，桌面、手機直式與橫式均有專用版面。
- 中文語音依裝置可用聲音而異。TTS先暫停音樂；結束後手動繼續。
- 創作背景有來源可查；逐小節／配器精確入點並未校準，未宣稱完成。

## 第 5 版：20秒更新與聆聽提醒

- 00:00至04:40共十五段，每20秒更新；「創作背景」與金色「🎧 注意聽」提示交替。
- 聆聽提醒：00:20低音弦樂、01:00木管哀歌、02:40弦樂長線條、04:00聲部層次、04:40完整樂句。
- 先查樂曲結構，並以指定影片核對約一分鐘木管及兩分半弦樂區間；區間提示不等於逐小節起音校準。
- 不把鏡頭特寫直接當成獨奏證據。這五分鐘沒有獨唱，因此不加虛構的獨唱提醒。
