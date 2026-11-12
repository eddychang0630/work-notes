# 工作專業知識庫

手機優先的複習筆記 App（純靜態網頁，可「加入主畫面」當 App 使用並離線閱讀）。

## 目前內容

**Server BMC・IPMI・Redfish・網路協定・PMBus**（16 章＋複習工具）

| 分類 | 章節 |
|---|---|
| 🖥️ 伺服器管理 | 01 角色、02 IPMI vs Redfish、08 Redfish 實作、09 IPMI 實作 |
| 🌐 電腦網路與 Web API | 03 分層、04 TCP／UDP、05 HTTP／TLS、06 API／REST、07 JSON |
| 🔌 硬體匯流排與 PMBus | 10 I²C／SMBus／PMBus、11 位址與 Linux 指令、12 PMBus 解碼 |
| 🛠️ Linux 診斷與 Debug | 13 端到端資料流、14 Linux 網路診斷 |
| 📦 韌體更新 | 15 TFTP／OneCLI／Firmware Update |
| 🚀 實作專題與 Lab | 16 專題；`labs/` 內有模擬 Redfish 伺服器與 PMBus 解碼程式 |
| 📚 複習工具 | 25 問速答、40 題測驗、速查表、名詞表、參考資料 |

## 本機預覽

```bash
python -m http.server 8123
```

開啟 <http://127.0.0.1:8123/>。

## 新增內容

見 [CLAUDE.md](CLAUDE.md)：新增 Markdown 到 `content/<分類>/`，並在 `content/index.json` 登記。

## 聲明

筆記為個人學習整理，範例資料皆為模擬；與特定機型、韌體、廠商工具有關的內容請以官方文件與實機為準。
