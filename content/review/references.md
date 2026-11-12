# 參考資料與查證狀態

> ⚠️ **查證狀態說明（製作日期 2026-11-12）**：本筆記依據各公開規範中長期穩定的通用內容整理（分層模型、TCP／HTTP／TLS 行為、JSON 語法、I²C 位址換算、PMBus 常用命令碼與 Linear 格式等），其中數值例題已用程式驗算。**製作時並未逐條對照最新版規範原文，也沒有連接任何實機**。凡涉及特定機型、韌體版本、廠商工具參數的內容，文中皆標示「需依實機驗證」，使用前請以下列官方來源為準。

## 官方與權威來源

| 主題 | 來源 | 連結 | 對應章節 |
|---|---|---|---|
| Redfish 標準總覽 | DMTF Redfish | https://www.dmtf.org/standards/redfish | 2、8、15 |
| Redfish 規格（DSP0266）、Schema（DSP8010）、資料模型指南（DSP0268） | DMTF | https://www.dmtf.org/dsp/DSP0266 | 2、6、8 |
| Redfish 開發者資源、Mockup、Schema 瀏覽 | Redfish Developer Hub | https://redfish.dmtf.org/ | 8、16 |
| IPMI 2.0 規格 | Intel（IPMI 由 Intel、HP、NEC、Dell 等推動，**並非 DMTF 標準**） | https://www.intel.com/content/www/us/en/products/docs/servers/ipmi/ipmi-second-gen-interface-spec-v2-rev1-1.html | 2、9 |
| ipmitool | 專案原始碼與 man page | https://codeberg.org/IPMITool/ipmitool | 9 |
| HTTP Semantics | IETF RFC 9110 | https://www.rfc-editor.org/rfc/rfc9110 | 5 |
| TCP | IETF RFC 9293 | https://www.rfc-editor.org/rfc/rfc9293 | 4 |
| UDP | IETF RFC 768 | https://www.rfc-editor.org/rfc/rfc768 | 4 |
| TLS 1.3 | IETF RFC 8446 | https://www.rfc-editor.org/rfc/rfc8446 | 5 |
| JSON | IETF RFC 8259 | https://www.rfc-editor.org/rfc/rfc8259 | 7 |
| URI 通用語法 | IETF RFC 3986 | https://www.rfc-editor.org/rfc/rfc3986 | 6 |
| TFTP | IETF RFC 1350（選項延伸：RFC 2347／2348／2349） | https://www.rfc-editor.org/rfc/rfc1350 | 4、15 |
| I²C | NXP UM10204 *I²C-bus specification and user manual* | https://www.nxp.com/docs/en/user-guide/UM10204.pdf | 10、11 |
| SMBus | System Management Interface Forum | http://smbus.org/specs/ | 10、11 |
| PMBus | PMBus Implementers Forum（Part I 傳輸、Part II 命令語言） | https://pmbus.org/ | 10、12 |
| i2c-tools | Linux kernel wiki／man pages（`i2cdetect(8)`、`i2cget(8)`、`i2cset(8)`、`i2ctransfer(8)`） | https://i2c.wiki.kernel.org/index.php/I2C_Tools | 11 |
| Linux I²C／SMBus 子系統 | kernel.org 文件 | https://docs.kernel.org/i2c/ | 11 |
| curl | 官方手冊 | https://curl.se/docs/manpage.html | 5、8、14 |
| Python requests | 官方文件 | https://requests.readthedocs.io/ | 8 |
| WSL 網路模式 | Microsoft Learn | https://learn.microsoft.com/windows/wsl/networking | 14、15 |
| Lenovo 機型文件、XCC／SMM Redfish 說明、OneCLI User Guide、韌體更新說明 | Lenovo Docs／Lenovo Support | https://pubs.lenovo.com/ | 1、13、15 |

> 📌 連結為各組織的常用入口；若網址變動，請以組織名稱與文件編號搜尋。規範版本請在查閱時記錄（例如「PMBus 1.3.1 Part II」「Redfish 2024.x」），並把查閱日期寫回本表。

## 需依實機／官方文件驗證的項目清單

| 項目 | 出現章節 | 為什麼不能通用 |
|---|---|---|
| SMM／SMM2／SMM3 適用機型、與節點 BMC 的分工 | 1、13 | 依 Lenovo 平台架構 |
| Redfish 資源路徑、Chassis／Manager ID、成員命名（如 `PCS1`–`PCS4`） | 8、13 | 依廠商與韌體版本 |
| PSU 資料在 `Power` 或 `PowerSubsystem`、有哪些欄位 | 8 | 依 Schema 版本與實作 |
| Session 逾時、數量上限 | 8 | 依 BMC 設定 |
| ipmitool 所需 Cipher Suite（`-C`）、支援的命令 | 9 | 依 BMC |
| 任何 IPMI OEM／raw 命令 | 9 | 廠商私有 |
| I²C bus 編號、PSU 位址（例：Bus 8、0x68）、MUX 配置 | 10、11 | 依平台硬體與 BMC 韌體 |
| PSU 支援的 PMBus 命令、資料格式（Linear／DIRECT）、PEC | 11、12 | 依 PSU 規格書 |
| `MFR_SPECIFIC` 命令與 `STATUS_MFR_SPECIFIC` 位元 | 12 | PSU 廠商自訂 |
| BMC 輪詢週期、PSU 讀值更新週期與精度 | 12、13 | 依韌體與 PSU 規格 |
| TFTP 套件名稱、設定檔位置、預設根目錄 | 15 | 依發行版與版本 |
| WSL Mirrored Networking 的 UDP 入站行為 | 15 | 依 Windows 版本 |
| OneCLI 命令語法與參數 | 15 | 依工具版本，**本筆記刻意未列** |
| `SimpleUpdate` 支援的協定與目標、PSU 更新流程 | 15 | 依機型官方更新說明 |

## 已驗算的數值例題

以下例題已由 `labs/test_pmbus_decode.py` 以程式驗算：

| 例題 | 結果 |
|---|---|
| Linear11 `0xF398` | 230.0 |
| Linear11 `0x0AEE` | 1500.0 |
| Linear11 `0xD1F4` | 7.8125 |
| Linear11 `0xE7B0` | −5.0 |
| Linear11 `0xF3C8` | 242.0 |
| Linear16 `0x1800`，VOUT_MODE `0x17` | 12.0 |
| Linear16 `0x3600`，VOUT_MODE `0x18` | 54.0 |
| Linear16 `0x1866`，VOUT_MODE `0x17` | 12.199… |
| `0x68` ↔ `0xD0`／`0xD1`；`0xB0` → `0x58` | 位址換算 |
| STATUS_WORD `0x0848` | POWER_GOOD#、OFF、VIN_UV_FAULT |

## 筆記更新紀錄

| 日期 | 內容 |
|---|---|
| 2026-11-12 | 建立：Server BMC／IPMI／Redfish／網路協定／PMBus 共 16 章＋複習工具 |
