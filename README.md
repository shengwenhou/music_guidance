# 聽見馬勒｜五分鐘導聆

馬勒第二號交響曲《復活》開頭五分鐘的互動導聆試作，以原始 YouTube 演出搭配繁體中文提示卡。

## 第 2 版：創作故事 × 聆聽

每張卡分成背景故事、聆聽提示、補充與史料。從1888年的《葬禮》、1891年試奏、1893年續寫，到1894年追思禮拜與1895年全曲首演，將創作歷程連回聲音。每30秒換卡，這是閱讀節奏，不是已驗證的樂譜事件入點。卡片附來源連結，並區分史實、馬勒事後的自述及聆聽比喻。

敘事方向參考使用者提供的 [Musecow 影片](https://www.youtube.com/watch?v=YChlv0nklJI)，未取得影片逐字稿，未轉錄原講稿。

## 目前狀態

**介面原型，尚非逐段校準的精準導聆。** 十張圖卡的時間是暫定聆聽區間；尚未逐段驗聽這支演出。請勿把區間時間當成已確認的主題或樂器入點。

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
| `dist/app.js` | 十張導聆卡、YouTube 同步與 TTS |
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
