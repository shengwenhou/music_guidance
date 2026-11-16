# 聽見馬勒｜全曲導聆

[開啟網站](https://shengwenhou.github.io/music_guidance/)

馬勒第二號交響曲《復活》五樂章的繁體中文互動導聆。原始YouTube演出搭配 **251段字幕**，通常每20秒更新，章節交界立即切換。背景故事與聆聽提醒交替，涵蓋創作、文本、曲式、音色及全曲關聯。

## 使用

按「開始全曲導聆」，或選擇樂章、拖動時間。字幕顯示在影片下方，使用網頁的「影片＋字幕全螢幕」一起放大；YouTube自己的全螢幕只放大影片。可重聽10秒、上一段／下一段、預覽字幕；展開完整背景後可查看資料來源，或暫停音樂聽瀏覽器TTS。中文聲音依裝置而異，朗讀結束後手動繼續。

| 樂章 | 官方影片起點 | 內容 |
| --- | --- | --- |
| I | 00:00 | 葬禮、六年創作歷程、器樂對比 |
| II | 22:18 | 蘭德勒、回望生活、聲部與舞步 |
| III | 31:39 | 向魚說教、少年魔號、諷刺與徒勞 |
| IV | 42:49 | 原光、次女高音Beth Taylor、歌詞與表達 |
| V | 48:06 | 復活、幕後樂團、Klopstock與馬勒的文字、獨唱與合唱 |

## 核對程度

五個樂章起點與演出資訊來自ARD Klassik官方影片說明。本片約82:56。章內的20秒是閱讀節奏，**未逐小節驗聽校準**；「當你聽見」「稍後」是段落預告，不是已驗證的樂器入點或逐句歌詞字幕。第四樂章開頭有人聲，其餘獨唱、鳥鳴、合唱與末段樂器以聆聽線索呈現。全曲版完成的是背景與區段導聆，不宣稱精確的主題辨識。

音樂由YouTube提供，廣告、緩衝、地區或裝置限制可能影響播放。本專案沒有下載或重製演出功能。TTS是裝置端瀏覽器功能，不包含預製同步MP3。

## 本機執行與驗證

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory dist
node --check dist/guide-data.js
node --check dist/app.js
node --test tests/guide.test.cjs
```

開啟 http://127.0.0.1:8765/ 。不要以file://直接開啟，缺少HTTP Referer可能導致YouTube錯誤153。GitHub Actions檢查腳本、執行互動測試，再發布dist至GitHub Pages。

## 檔案

- `dist/index.html`：介面、版面、授權與使用說明。
- `dist/guide-data.js`：251段原創字幕、五個樂章與資料來源。
- `dist/app.js`：YouTube時間同步、跳轉、預覽、TTS與全螢幕。
- `tests/guide.test.cjs`：播放器與導覽回歸檢查。
- `LICENSE`、`THIRD_PARTY_NOTICES.md`：授權與排除範圍；網站亦提供副本。

## 授權

Copyright (c) 2026 Sheng-Wen Hou。程式碼與原創導聆採[MIT License](LICENSE)，可使用、修改與散布，須保留授權及著作權聲明。演出影片、錄音、商標及第三方史料**不在MIT授權範圍**，見[第三方權利與來源](THIRD_PARTY_NOTICES.md)。
