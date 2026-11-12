# Server BMC、IPMI、Redfish、網路協定與 PMBus 自學講義｜Claude Code 製作需求

> **文件用途**：將本文件交給 Claude Code，請它依照下列課綱與規格，製作一份繁體中文、適合工程師從基礎循序學習到能實際 Debug 的完整自學講義。  
> **主要情境**：Lenovo Server、BMC／SMM／SMM3、PSU（伺服器電源供應器）驗證、Linux、Python 自動化、Redfish API、IPMI、PMBus、TFTP 與 Firmware Update。  
> **注意**：本文件是「講義製作規格＋完整知識清單＋初步範例」，不是宣稱所有廠牌、機型都有同樣的功能。請查閱官方規範及裝置文件確認細節。

---

## 0. 給 Claude Code 的工作指示（請先閱讀）

請根據本 Markdown 檔案製作一套**完整、深入但對初學者友善**的繁體中文自學教材。目標讀者為具備 PSU Validation、電力電子基本知識、Python 自動化與 Linux 操作經驗，但希望系統性補強電腦網路、Server BMC、Redfish／IPMI、I²C／SMBus／PMBus 的工程師。

### 請產生的成果

1. `README.md`：總覽、學習地圖、先備知識與索引。
2. `chapters/`：依下列章節建立獨立 Markdown 教材；每章包含概念、生活類比、嚴謹定義、圖解、操作例子、常見誤解、Debug 流程、練習題與詳解。
3. `labs/`：可在 Linux 執行的 Lab（以模擬環境、唯讀命令優先），註明前置條件、預期輸出與失敗排查。
4. `glossary.md`：中英文縮寫對照、英文常見唸法、所屬層級、使用情境。
5. `quiz.md`：至少 40 題，由初階到進階，附解答與解題說明。
6. `cheatsheet.md`：一頁式指令及協定速查表。
7. `references.md`：以官方來源為優先，附來源連結、對應章節及規範版本／查閱日期。

### 寫作規則

- 使用**繁體中文（台灣用語）**，專業名詞第一次出現須提供英文全名和中文說明。
- **從零說明網路概念**，但也要給工程師足夠底層深度；先直觀再技術。
- 圖解使用 Mermaid：架構圖、OSI/TCP-IP 分層圖、TCP 三向交握、HTTP Request/Response、BMC 至 PSU 的資料路徑、Firmware Update 流程、故障定位流程。
- 每個命令提供逐段拆解；區分「純示意」、「可直接執行（需參數）」、「需要特定設備或權限」；提供成功與失敗的輸出範例。
- **設備控制以唯讀為預設**；開關機、重啟、韌體更新、修改設定需醒目標示風險及前置確認，不要當作可任意執行的實驗。
- 密碼、Token 不得硬編碼到公開檔案。建議 `read -s`、環境變數、權限安全的設定檔；說明命令列參數可能洩漏憑證。
- 範例 IP `192.168.70.100` 只是示意／先前實驗情境，不是保證可連線的實機。請用佔位符 `<BMC_IP>`、`<USER>` 等給出可移植範例。
- `curl -k` 與 `requests(..., verify=False)` **只可做實驗測試**，並說明跳過 TLS 憑證驗證的風險；正式環境應正確配置 CA／憑證。
- 某些 BMC、SMM、PSU 不支援全部 API 或 PMBus Command；所有廠商特有功能、OEM 命令與路徑都應標示需查硬體文件。
- 章末加 5 題理解題與至少 1 題動手練習；每 3 章做一次整合題。
- 需要多補充重點：**I²C 7-bit vs 8-bit 位址、PMBus Read Word／Block Read、JSON 解析、FirmwareInventory、Redfish Session、TFTP 與 Linux Debug**。

---

## 1. 完整學習路徑與章節

### Part A｜Server 管理基礎

#### Chapter 01：Server、BMC、SMM、PSU 的角色
- Server 主機架構：CPU、OS、主機板、NIC、BMC、PSU、Fan、Sensor、CPLD、I²C MUX。
- BMC（Baseboard Management Controller）是什麼？帶外管理（Out-of-Band Management）與作業系統內管理（In-Band）的差異。
- 伺服器作業系統沒開機，BMC 為何仍可部分運作？管理電源與待機供電概念。
- Lenovo SMM／SMM3（System Management Module）與一般 BMC 的概念差異：依平台架構辨識，**不要武斷視為同一顆控制器**。
- PSU Telemetry、Presence、Health、Fault、Input／Output Voltage、Current、Power、Temperature。
- 外部 PC → 管理網路 → BMC／SMM → 硬體的完整路徑。

#### Chapter 02：IPMI 與 Redfish 的異同
- IPMI（Intelligent Platform Management Interface）：傳統遠端平台管理標準，命令式架構、NetFn、Command、Data、SDR、SEL、FRU、Sensor、Chassis Power。
- IPMI over LAN 常見 UDP 623、RMCP／RMCP+；IPMI 2.0 與安全注意事項。
- `ipmitool` 常用命令：`sensor list`、`sdr list`、`sel list`、`fru print`、`chassis power status`；命令的設備支援條件。
- Redfish（DMTF Redfish）：HTTPS、RESTful API、JSON、資源導向、Schema、OData、Service Root。
- Redfish 常見資源：`/redfish/v1/`、`Systems`、`Chassis`、`Managers`、`UpdateService`、`FirmwareInventory`、`SessionService`。
- 兩者共通功能與差異：感測器、事件、電源控制、Firmware Inventory／Update、自動化、權限、安全、OEM 擴充。
- IPMI **不等於** I²C；IPMI／Redfish 是遠端管理介面，PMBus 是設備端電源管理通訊協定。
- 決策建議：舊平台／基本管理可用 IPMI，較大型自動化優先評估 Redfish，但不能假設完全取代。

### Part B｜網路從零到 Redfish

#### Chapter 03：網路基本名詞與分層
- Client／Server、Request／Response。
- IP Address、Subnet Mask、Gateway、LAN、NIC、MAC Address、Port。
- IP 是尋址與路由；Port 協助識別同一主機上的服務。`192.168.70.100:443` 的意思。
- OSI 七層模型，TCP/IP 四層／五層模型與對照；Ethernet、ARP、IP、ICMP、TCP、UDP、TLS、HTTP、HTTPS、SSH、TFTP、Redfish 各在哪一層。
- 注意：**API 與 JSON 不應被誤畫成與 TCP、IP 完全對等的獨立傳輸層**；描述其在應用上的角色。

#### Chapter 04：TCP、UDP 與 Port
- TCP（Transmission Control Protocol）：連線導向、可靠、有序的位元組串流、序號、ACK、重傳、流量控制、壅塞控制。
- TCP 三向交握：SYN → SYN-ACK → ACK；連線關閉基本概念。
- UDP（User Datagram Protocol）：無連線、訊息資料報、較少內建保證；不等於「一定比較快」。
- Port 常見例子：TCP 22 SSH／SFTP；TCP 80 HTTP；TCP 443 HTTPS；UDP 69 TFTP 初始請求；UDP 623 IPMI RMCP。
- TFTP 資料傳輸不一定全程固定在 UDP 69：說明雙方後續使用傳輸識別埠（TID）的概念。
- TCP 連線成功不代表 API 授權成功；Ping 不通不一定代表 HTTPS 不通。

#### Chapter 05：HTTP、HTTPS 與 TLS
- HTTP（Hypertext Transfer Protocol）的 Request Line、Method、URI、Header、Body、Response Status、Content-Type。
- GET、POST、PATCH、DELETE；舉例讀取 Inventory、Reset Action、修改設定、Session 刪除。
- HTTP Status：200、201、202、204、400、401、403、404、405、409、500、503 等。
- HTTPS = HTTP 使用 TLS 保護，通常經 TCP 443（另說明 HTTP/3/QUIC 為較進階延伸例外）。
- TLS：加密、完整性、伺服器身分驗證、憑證、CA；自簽憑證與 `curl -k` 的風險。
- `curl -v`、`-i`、`-k`、`-u`、`-H`、`-X` 的意義與安全注意事項。
- 應用層錯誤與 TCP／TLS 層錯誤如何區分。

#### Chapter 06：API、REST API 與 URI
- API（Application Programming Interface）並不只限於網路：Python 函式庫 API、PyVISA 與 SCPI 的關係。
- Web API、REST API、Redfish API 的包含／應用關係。
- Resource、URI、Endpoint、HTTP Method、JSON Payload、Authentication、Authorization。
- URL 範例 `https://<BMC_IP>/redfish/v1/UpdateService/FirmwareInventory` 逐段拆解：scheme、host、port、path。
- RESTful 的資源概念與操作；何時使用 Actions（例如 Reset）。

#### Chapter 07：JSON 全面理解
- JSON（JavaScript Object Notation）的英文唸法：**Jason（傑森）**，一般不是逐一唸 J-S-O-N。
- JSON 與 JavaScript 的歷史關係，但並非只供 JavaScript 使用。
- Object `{}`、Array `[]`、key/value、String、Number、Boolean、null、nested object。
- JSON 與 Python `dict`／`list` 的對應；`json.loads()`／`json.dumps()`／`response.json()` 的差異。
- `Content-Type: application/json`；JSON 解析失敗、不存在欄位、數值型別、`null` 的處理。
- Redfish PSU／Firmware Inventory 模擬 JSON；`Members`、`@odata.id`；如何追蹤下一層資源。

### Part C｜Redfish 與 IPMI 實作

#### Chapter 08：Redfish 從 curl 到 Python
- Service Root 探查：`GET /redfish/v1/`。
- Systems、Chassis、Managers、UpdateService、FirmwareInventory 的關係；如何跟隨 `@odata.id`。
- Basic Auth 與 Redfish Session Token (`X-Auth-Token`)；建立、使用、刪除 Session 的觀念及版本差異。
- Python `requests`：timeout、status code、`raise_for_status()`、`json()`、例外處理、安全存放 Token。
- 列出 PSU 相關資源／FirmwareInventory 的示範程式，**不可假設所有平台的資源路徑或欄位固定**。
- 處理 `401`、`403`、`404`、`405`、`500`，還有回傳空集合、不支援欄位。
- 簡易流程：取得 BMC 韌體資訊 → 匯出 CSV → 依 PSU 編號建立報告。

#### Chapter 09：IPMI 實作與限制
- 安裝 `ipmitool`、Local vs LAN／LANPlus。
- `ipmitool -I lanplus -H <BMC_IP> -U <USER> ...` 的每個選項意義。
- 常見感測器資訊與 PSU Presence／Fault 的差異；SDR／SEL／FRU。
- OEM 命令、RAW command 的風險；廠商專有格式不能猜。
- IPMI 與 Redfish 同一項 PSU Telemetry 的交叉核對策略。

### Part D｜硬體底層通訊與 PMBus

#### Chapter 10：I²C、SMBus、PMBus 的關係
- I²C：SDA（Data）、SCL（Clock）、Controller／Target、ACK／NACK、START／STOP、Repeated START、7-bit／10-bit 位址。
- SMBus（System Management Bus）：基於兩線式匯流排的較具體系統管理規範，與 I²C 互通性及差異（timeout、電氣特性、交易類型等）。
- PMBus（Power Management Bus）：定義電源管理命令、資訊格式與行為，常使用 SMBus 實體／交易機制。
- **關鍵區分**：I²C／SMBus 管傳輸、PMBus 定義電源命令、Redfish／IPMI 是管理端介面。
- BMC／SMM 可能直接連 PSU，也可能經 CPLD、I²C MUX、Bridge、其他管理控制器。

#### Chapter 11：I²C Address 與 Linux 指令
- 7-bit 位址 `0x68` 對應寫入方向位元組 `0xD0`（`0x68 << 1 | 0`）、讀取方向位元組 `0xD1`（`0x68 << 1 | 1`）；注意 Linux 工具通常接受 **7-bit address**。
- 位址、R/W bit、Register／Command Code、Bus Number、裝置節點 `/dev/i2c-*` 的不同。
- `i2cdetect`、`i2cget`、`i2cset`、`i2ctransfer` 的用途與風險；掃描和寫入可能造成設備問題。
- Byte／Word／Block Read，Repeated START、SMBus Read Word 的格式。
- 範例：`i2cget -y 8 0x68 0x8B w` 僅在確定 bus/address/command 與回應格式符合時可用；**不得直接將 raw word 當電壓值**。
- 解析 Byte Order、PEC（Packet Error Checking）、不同回傳長度、Block Read 多一個 count byte 等常見疑問。
- 把過去工程實作中的 I²C Bus 8、PSU 7-bit 地址 0x68 當成**待驗證的案例**，勿宣稱所有 Lenovo 平台相同。

#### Chapter 12：PMBus Command 與資料解碼
- 常見 Command Code（是否支援及數值定義仍須依規格與設備核對）：
  - `READ_VIN` `0x88`
  - `READ_IIN` `0x89`
  - `READ_VOUT` `0x8B`
  - `READ_IOUT` `0x8C`
  - `READ_TEMPERATURE_1` `0x8D`
  - `READ_POUT` `0x96`
  - `READ_PIN` `0x97`
  - `STATUS_WORD` `0x79`
  - `VOUT_MODE` `0x20`
- 各命令的 Byte／Word／Block 回傳方式，不能一概而論。
- Linear11、Linear16、DIRECT 等資料表示方式：signed exponent／mantissa、two's complement、VOUT_MODE，附可手算的例題、Python 解碼程式與測試案例。
- STATUS_BYTE／STATUS_WORD、Fault／Warning、不同 PSU 的 OEM 擴充。
- 實測 PMBus 功率與 Redfish 顯示值可能不同的原因：更新頻率、四捨五入、快取、校正、不同感測位置。

### Part E｜完整應用與 Debug

#### Chapter 13：從 PSU 到 Python 的端到端資料流
- 以 `PSU1 READ_POUT` 為例：PSU 內部控制器 → PMBus → BMC／SMM → Redfish 或 IPMI → HTTPS／網路 → Python → CSV／Dashboard。
- PMBus 原始值的解碼位置、Redfish JSON 的資料呈現、取樣頻率與延遲。
- 不同協定層級與對應的可能故障點。
- 以 Lenovo 4 PSU／SMM3／FirmwareInventory (PCS1～PCS4) 作為案例，明確聲明**名稱及內容依硬體平台而異**。

#### Chapter 14：Linux 網路診斷與常用指令
- `ip addr`、`ip route`、`ping`、`nc -vz`、`ss -tulpen`、`curl -v`、`journalctl`、`tcpdump`（依權限）。
- TCP/IP、TCP 443、UDP 623、UDP 69、TLS、HTTP、JSON、PMBus 各階段的故障判讀。
- IP 固定設定、同子網路、路由與防火牆、Windows／WSL／Linux 差異。
- 排查矩陣：ping 不通、TCP connection refused、timeout、TLS certificate error、HTTP 401／403／404、HTTP 200 但缺欄位、I²C NACK。

#### Chapter 15：TFTP、OneCLI 與 Firmware Update（進階且需謹慎）
- TFTP（Trivial File Transfer Protocol）如何運作：UDP 69、讀取請求、資料／ACK、後續 TID Port。
- Ubuntu／CentOS 7.9／RHEL 環境下的套件與服務差異；先查版本再操作。
- TFTP Root Directory、Firmware 檔案放置、權限、服務啟動、確認設備能否取得檔案。
- WSL NAT／Mirrored Networking、Windows 與 Linux IP 的區別與網路可達性。
- OneCLI、SMM3、PSU FirmwareInventory、Redfish UpdateService 之間的關係：哪些是標準、哪些可能是 Lenovo/OEM 特有。
- Firmware Update 的安全檢查：硬體型號、正確韌體、備援電源狀態、更新順序、rollback／recovery、測試設備授權、維護時段、Log 保留。
- 僅提供**已經由裝置文件確認**的實際更新命令，不能憑空杜撰 OneCLI 參數。

#### Chapter 16：整合實作專題
- Project A：在模擬 Redfish 伺服器上讀取 FirmwareInventory，輸出 CSV，完成例外處理及 pytest。
- Project B：解析 PMBus Linear11／Linear16 raw sample，繪製電壓／功率趨勢。
- Project C：比較同台設備在 IPMI 與 Redfish 取得的 PSU Health／功率資訊（需設備支援）。
- Project D：建立「BMC／SMM／PSU 通訊故障 Debug Checklist」，例如 PSU I²C NACK、BMC 連線逾時、API 401、FirmwareInventory 空值。

---

## 2. 核心對照表（講義必須詳細擴寫）

| 名詞 | 英文全名 | 核心用途 | 示例 |
|---|---|---|---|
| BMC | Baseboard Management Controller | 伺服器帶外管理控制器 | 讀感測器、電源管理 |
| SMM | System Management Module | 特定平台的系統／機箱管理模組 | Lenovo 部分平台 SMM3 |
| PSU | Power Supply Unit | 電源供應器 | 輸入、輸出、Fault |
| IPMI | Intelligent Platform Management Interface | 傳統平台管理介面 | `ipmitool sensor list` |
| Redfish | DMTF Redfish | RESTful Server Management API | `/redfish/v1/` |
| API | Application Programming Interface | 程式操作介面 | Redfish API、PyVISA API |
| REST | Representational State Transfer | Web API 架構風格 | 資源 URI + HTTP methods |
| JSON | JavaScript Object Notation | 結構化文字資料格式 | `{"Health":"OK"}` |
| HTTP | Hypertext Transfer Protocol | 應用層請求／回應協定 | GET /redfish/v1/ |
| HTTPS | HTTP over TLS | 受 TLS 保護的 HTTP | TCP 443 常見 |
| TLS | Transport Layer Security | 安全通訊 | 憑證、加密 |
| TCP | Transmission Control Protocol | 可靠、有序位元組串流 | HTTPS 常見傳輸 |
| UDP | User Datagram Protocol | 無連線資料報傳輸 | TFTP／IPMI |
| IP | Internet Protocol | 封包尋址與路由 | 192.168.70.100 |
| I²C | Inter-Integrated Circuit | 兩線式序列匯流排 | SDA、SCL |
| SMBus | System Management Bus | 系統管理匯流排規範 | Read Word |
| PMBus | Power Management Bus | 電源管理命令與資料規範 | READ_VOUT |
| TFTP | Trivial File Transfer Protocol | 簡易檔案傳輸 | Firmware 傳送 |
| SSH | Secure Shell | 安全遠端 Shell | TCP 22 |
| SFTP | SSH File Transfer Protocol | SSH 上的檔案傳輸 | TCP 22 |
| SCPI | Standard Commands for Programmable Instruments | 儀器控制命令 | `*IDN?` |
| PyVISA | Python VISA binding | Python 儀器通訊介面 | `inst.write(...)` |

---

## 3. 必須有的程式及指令範例

> 這些範例是**教學情境**，請在正式教材補充前置條件、帳密保護、預期回應、錯誤處理與機型差異。

### 3.1 Redfish Service Root（唯讀）

```bash
curl --cacert <CA_CERT_PATH> -u '<USER>' \
  'https://<BMC_IP>/redfish/v1/'
```

如果 lab 使用自簽憑證且尚未建立信任，可在隔離測試環境暫時使用 `curl -k`，並特別標示風險。

### 3.2 Redfish FirmwareInventory（唯讀）

```bash
curl --cacert <CA_CERT_PATH> -u '<USER>' \
  'https://<BMC_IP>/redfish/v1/UpdateService/FirmwareInventory'
```

必須先讀 `/redfish/v1/UpdateService` 並確認實際連結，勿假定此 URL 一定存在。

### 3.3 Python requests（唯讀、使用環境變數）

```python
import os
import requests

base = os.environ["BMC_BASE_URL"].rstrip("/")
user = os.environ["BMC_USER"]
password = os.environ["BMC_PASSWORD"]
ca_bundle = os.environ.get("BMC_CA_BUNDLE", True)

response = requests.get(
    f"{base}/redfish/v1/",
    auth=(user, password),
    timeout=10,
    verify=ca_bundle,
)
response.raise_for_status()
print(response.json())
```

### 3.4 JSON 基本結構（純模擬資料）

```json
{
  "Name": "PSU1",
  "FirmwareVersion": "00.51",
  "PowerOutputWatts": 1500,
  "Status": {
    "State": "Enabled",
    "Health": "OK"
  }
}
```

以上為教學自訂 JSON，**不是保證符合某一 Redfish PowerSupply Schema 的原始回應**。

```python
firmware = data["FirmwareVersion"]
health = data["Status"]["Health"]
```

### 3.5 IPMI 查詢（唯讀）

```bash
# 建議正式教材介紹更安全的密碼輸入選項，避免直接 -P <password>
ipmitool -I lanplus -H <BMC_IP> -U <USER> sensor list
ipmitool -I lanplus -H <BMC_IP> -U <USER> chassis power status
```

### 3.6 I²C／PMBus 讀取（僅確認後、授權測試設備）

```bash
# 示意：Linux I2C bus 8、7-bit address 0x68，PMBus READ_VOUT 0x8B
# 只有確定總線拓樸與裝置支援時才可執行
i2cget -y 8 0x68 0x8B w
```

需要完整介紹交易格式、PEC、Byte Order、Linear11／Linear16、VOUT_MODE，不能把回傳 16-bit Raw 值直接當伏特數。

### 3.7 網路診斷（唯讀）

```bash
ip addr
ip route
ping -c 4 <BMC_IP>
nc -vz <BMC_IP> 443
curl -v 'https://<BMC_IP>/redfish/v1/'
```

---

## 4. 必須解答的 25 個問題

1. BMC 是什麼，跟 Server CPU 和 OS 有什麼差異？
2. SMM3 和一般 Server BMC 一樣嗎？何時需要分開看？
3. IPMI 跟 Redfish 是什麼，為什麼可以管理同一台 Server？
4. IPMI、Redfish 與 PMBus 哪個是在管理網路、哪個是在硬體匯流排？
5. IPMI 為何常見 UDP 623，Redfish 為何常見 HTTPS TCP 443？
6. TCP 和 UDP 根本差別為何？
7. TCP 三向交握各階段在做什麼？
8. IP Address 與 Port 有何不同？
9. HTTP 是什麼？Request 與 Response 包含哪些欄位？
10. HTTP 與 HTTPS 差異，TLS 保護什麼？
11. `curl -k` 到底略過了什麼安全檢查？
12. GET、POST、PATCH、DELETE 差在哪裡？
13. HTTP 401、403、404、500 分別表示什麼？
14. API、REST API、Redfish API 是什麼關係？
15. JSON 如何唸？JSON 的 `{}`、`[]`、字串、數字、布林、null 是什麼？
16. `response.json()` 如何轉成 Python dict/list？
17. Redfish `/redfish/v1/`、Systems、Chassis、Managers 有何不同？
18. FirmwareInventory、UpdateService、SessionService 是什麼？
19. Redfish 查得到 FirmwareVersion 就代表一定能刷 Firmware 嗎？
20. BMC 如何讀到 PSU Input/Output Voltage、Current、Power、Fault？
21. I²C、SMBus、PMBus 差在哪裡？
22. 為何 PSU 7-bit Address `0x68` 會和 `0xD0/0xD1` 扯上關係？
23. Read Byte、Read Word、Block Read 有何差異？
24. PMBus READ_VOUT／READ_POUT 的 Raw Data 如何解碼？
25. 如果 BMC 連線正常但 PSU Telemetry 為空，如何逐層定位？

---

## 5. 自學課程的教學與驗收標準

### 建議的學習階段

- **第 1 階段（基礎）**：BMC／PSU 架構、IP／Port、TCP／UDP、HTTP／HTTPS、API、JSON。
- **第 2 階段（應用）**：Redfish API、curl、Python requests、IPMI 指令、Firmware Inventory。
- **第 3 階段（底層）**：I²C、SMBus、PMBus、Address、Transaction、資料格式解碼。
- **第 4 階段（整合）**：PSU Telemetry 全鏈路、Linux Debug、TFTP／韌體更新、安全及自動化專題。

### 完成後應能做到

- 能向同事清楚解釋 BMC、IPMI、Redfish、TCP、HTTPS、API、JSON、PMBus 的關係。
- 能看懂 Redfish JSON Response 與 HTTP Status Code。
- 能以 Python 安全地查詢 Redfish 資料，追蹤 `@odata.id`，輸出 CSV。
- 能判讀基本 IPMI sensor／SEL／FRU 輸出。
- 能區分 I²C Address、Bus Number、PMBus Command Code。
- 能理解 PMBus 的 Byte／Word／Block、PEC 與數據編碼。
- 能根據症狀辨別網路連線、TLS、HTTP、權限、API、BMC、I²C、PSU 層級的問題。
- 能設計一個 PSU Monitoring／Firmware Inventory 的簡單自動化系統。

---

## 6. 官方與權威資料查閱方向

請 Claude Code **實際核對後**引用，別只根據本文件生成技術細節：

- DMTF Redfish：`https://www.dmtf.org/standards/redfish`
- Redfish Developer Hub：`https://redfish.dmtf.org/`
- DMTF IPMI 規格與 IPMItool 官方文件／原始碼。
- IETF RFC：HTTP Semantics（RFC 9110）、TCP（RFC 9293）、UDP（RFC 768）、TLS 1.3（RFC 8446）、JSON（RFC 8259）。
- NXP I²C-bus specification and user manual。
- SMBus 官方規範與 PMBus Implementers Forum 規範。
- Linux `i2c-tools` 官方 man pages／原始碼。
- Lenovo 官方的機型文件、OneCLI User Guide、SMM3／BMC Redfish API 說明、PSU Firmware Update 流程。

**最後要求**：寫完所有講義後，進行技術正確性檢查，特別確認各協定的層級、指令語法、HTTP／TLS／TCP 關係、I²C 地址、PMBus Command Code 與資料編碼。對機型不確定的地方標記「需依實機驗證」，不可猜測。
