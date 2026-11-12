# 工作專業知識庫 — 維護說明

這是一個部署在 GitHub Pages 的純靜態筆記 App（PWA，手機優先）。使用者會持續丟新的資料（通常是 `.md` 需求或原始筆記）進來，請依下列規則**新增／歸類**，不要重寫既有架構。

## 結構

- `index.html`、`assets/app.css`、`assets/app.js`：App 外殼（hash 路由、搜尋、進度、目錄、Mermaid／highlight.js 由 CDN 載入）。
- `content/index.json`：**唯一的目錄來源**——`categories`（分類）、`stages`（學習路徑）、`docs`（每篇文章的 id／cat／title／summary／file）。
- `content/<分類 id>/*.md`：文章本體（Markdown，由 marked 在瀏覽器端轉成 HTML）。
- `labs/`：可執行的範例程式。
- `sw.js`：Service Worker（離線快取）。改了外殼檔案時把 `CACHE` 版本號加一。
- 根目錄的 `*_需求.md` 等是使用者提供的原始資料，保留不動。

## 新增內容的流程

1. 讀使用者給的資料，判斷屬於哪個既有分類；沒有合適的才在 `index.json` 的 `categories` 新增一個（id 用英文小寫、選一個 emoji icon、寫一句 desc），並建立 `content/<id>/` 資料夾。「複習工具」(`review`) 分類保持在最後。
2. 在 `content/<分類>/` 新增 `.md`，並在 `index.json` 的 `docs` 加一筆（`added` 填當天日期，首頁「最近新增」會用到）。`docs` 陣列順序就是「上一篇／下一篇」的順序。
3. 需要的話更新 `stages`、`content/review/` 下的名詞表、速查表、測驗、參考資料。
4. 本機預覽：`python -m http.server 8123` 後開 `http://127.0.0.1:8123/`（不能直接雙擊 index.html）。
5. commit 並 push 到 `main`，GitHub Pages 會自動更新。

## 文章寫作慣例

- 繁體中文（台灣用語）；專有名詞第一次出現附英文全名。
- 每篇結構：`# 標題` → `> 📌 一句話重點` → 概念／類比 → 嚴謹定義 → 圖解 → 範例 → 常見誤解 → Debug → 練習題（`<details><summary>看解答</summary>` 前後要空行）。
- 提示框用 blockquote 並以 emoji 開頭：`> 📌`（重點）、`> 💡`（提示）、`> ⚠️`（注意）、`> 🔴`（危險）、`> ✅`（建議）。
- 圖解：流程／時序用 ```` ```mermaid ````（節點文字用雙引號包起來）；位元欄位與封包格式用 `assets/app.css` 裡的 `.bits`、`.frame`、`.layers` HTML 區塊（HTML 區塊內不可有空行）。
- 指令範例標示風險：🟢 可執行／唯讀、🟡 需設備或權限、⚪ 純示意、🔴 會改變設備狀態。設備操作以唯讀為預設。
- 不寫死密碼／Token；IP、帳號用 `<BMC_IP>`、`<USER>` 佔位符。
- 與特定機型、韌體、廠商工具參數有關的內容標示「需依實機驗證」，不可猜測或杜撰命令。
- 文章間連結用 `[第 5 章](#/doc/ch05)`。
- 數值例題要用程式驗算（參考 `labs/test_pmbus_decode.py`）。
