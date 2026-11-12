# 25 個核心問題速答

> 💡 用法：先遮住答案自己講一遍（目標每題 30 秒內），再點開對照。每題後面附延伸章節。

## Server 與管理介面

**1. BMC 是什麼，跟 Server CPU 和 OS 有什麼差異？**

<details><summary>看答案</summary>

BMC 是主機板上獨立的管理控制器，有自己的處理器、韌體與網路介面，由**待機電源**供電。它負責監控感測器、控制電源、記錄事件並提供 IPMI／Redfish。主機 CPU＋OS 執行使用者工作負載，需要主電源。OS 當機或關機時 BMC 仍可運作。→ [第 1 章](#/doc/ch01)

</details>

**2. SMM3 和一般 Server BMC 一樣嗎？何時需要分開看？**

<details><summary>看答案</summary>

不應視為相同。BMC（Lenovo 稱 XCC）管理**單一節點**；SMM 系列是部分 Lenovo 多節點／高密度機箱的**機箱層級**管理模組，管理共用的 PSU、風扇等。查共用 PSU 的 Telemetry／韌體時，要確認該問的是 SMM 還是節點 BMC。支援的 API 需依實機驗證。→ [第 1 章](#/doc/ch01)

</details>

**3. IPMI 跟 Redfish 是什麼，為什麼可以管理同一台 Server？**

<details><summary>看答案</summary>

兩者都是 BMC 對外的管理介面：IPMI 是較早的二進位命令式協定；Redfish 是 DMTF 的 HTTPS＋JSON RESTful API。它們是同一顆 BMC 的兩個「窗口」，背後是同一份感測器資料與控制邏輯。→ [第 2 章](#/doc/ch02)

</details>

**4. IPMI、Redfish 與 PMBus 哪個是在管理網路、哪個是在硬體匯流排？**

<details><summary>看答案</summary>

IPMI（over LAN）與 Redfish 在**管理網路**（PC ↔ BMC）；PMBus 在**板上的 SMBus／I²C 匯流排**（BMC ↔ PSU）。→ [第 2 章](#/doc/ch02)、[第 10 章](#/doc/ch10)

</details>

**5. IPMI 為何常見 UDP 623，Redfish 為何常見 HTTPS TCP 443？**

<details><summary>看答案</summary>

IPMI over LAN 以 RMCP／RMCP+ 封裝，規範指定 UDP 623，可靠性由 IPMI 自己的序號與重試處理。Redfish 建立在 HTTPS 上，HTTPS 的預設埠是 TCP 443，由 TCP 提供可靠傳輸、TLS 提供加密。→ [第 2 章](#/doc/ch02)、[第 4 章](#/doc/ch04)

</details>

## 網路

**6. TCP 和 UDP 根本差別為何？**

<details><summary>看答案</summary>

TCP：連線導向，可靠、有序的**位元組串流**，有重傳、流量與壅塞控制。UDP：無連線的**資料報**，不保證送達與順序，可靠性交給應用層。UDP 不等於一定比較快。→ [第 4 章](#/doc/ch04)

</details>

**7. TCP 三向交握各階段在做什麼？**

<details><summary>看答案</summary>

① SYN：Client 要求連線並送出初始序號。② SYN-ACK：Server 同意、確認 Client 序號並送出自己的序號。③ ACK：Client 確認 Server 序號。完成後雙方確認彼此收發正常。→ [第 4 章](#/doc/ch04)

</details>

**8. IP Address 與 Port 有何不同？**

<details><summary>看答案</summary>

IP 識別**哪一台主機**（第 3 層，用於路由）；Port 識別主機上的**哪個服務**（第 4 層）。`192.168.70.100:443` = 那台機器上的 HTTPS 服務。→ [第 3 章](#/doc/ch03)

</details>

**9. HTTP 是什麼？Request 與 Response 包含哪些欄位？**

<details><summary>看答案</summary>

HTTP 是應用層的請求／回應協定。Request：Request Line（Method、URI、版本）＋Headers＋空行＋Body。Response：Status Line（版本、狀態碼、原因）＋Headers＋空行＋Body。→ [第 5 章](#/doc/ch05)

</details>

**10. HTTP 與 HTTPS 差異，TLS 保護什麼？**

<details><summary>看答案</summary>

HTTPS 是把 HTTP 放在 TLS 通道中傳輸（通常 TCP 443）。TLS 提供**加密**、**完整性**、**伺服器身分驗證**。→ [第 5 章](#/doc/ch05)

</details>

**11. `curl -k` 到底略過了什麼安全檢查？**

<details><summary>看答案</summary>

略過**伺服器憑證驗證**：不檢查簽發 CA 是否受信任、主機名稱是否相符、是否過期。連線仍加密，但無法確認對方身分，可能遭中間人攻擊。只能用於隔離實驗環境。→ [第 5 章](#/doc/ch05)

</details>

**12. GET、POST、PATCH、DELETE 差在哪裡？**

<details><summary>看答案</summary>

GET 讀取（唯讀）；POST 建立資源或執行 Action；PATCH 修改部分欄位；DELETE 刪除。例：讀 Inventory／建立 Session 或 Reset／改設定／刪除 Session。→ [第 5 章](#/doc/ch05)

</details>

**13. HTTP 401、403、404、500 分別表示什麼？**

<details><summary>看答案</summary>

401 未認證或認證失敗；403 已認證但權限不足；404 資源不存在；500 伺服器內部錯誤。4xx 是 Client 端問題、5xx 是 Server 端問題。→ [第 5 章](#/doc/ch05)

</details>

**14. API、REST API、Redfish API 是什麼關係？**

<details><summary>看答案</summary>

API 泛指程式介面（含函式庫、PyVISA）；Web API 是透過 HTTP 的 API；REST API 是以「資源＋HTTP Method」風格設計的 Web API；Redfish 是 DMTF 以 REST 風格定義的伺服器管理 API 規範。層層包含。→ [第 6 章](#/doc/ch06)

</details>

**15. JSON 如何唸？`{}`、`[]`、字串、數字、布林、null 是什麼？**

<details><summary>看答案</summary>

唸「Jason」。`{}` 物件（key/value，對應 dict）；`[]` 陣列（對應 list）；字串必須雙引號；數字不加引號；布林為小寫 `true`／`false`；`null` 表示空值（對應 None）。→ [第 7 章](#/doc/ch07)

</details>

**16. `response.json()` 如何轉成 Python dict/list？**

<details><summary>看答案</summary>

它把 HTTP 回應 Body 的 JSON 文字解析成 Python 物件（等同 `json.loads(response.text)`）：最外層是 `{}` 就得到 dict，是 `[]` 就得到 list。Body 不是合法 JSON 時會丟例外。→ [第 7 章](#/doc/ch07)

</details>

## Redfish

**17. `/redfish/v1/`、Systems、Chassis、Managers 有何不同？**

<details><summary>看答案</summary>

`/redfish/v1/` 是 Service Root（入口與目錄）。Systems＝邏輯上的電腦系統；Chassis＝實體機箱（PSU、風扇、溫度）；Managers＝BMC／SMM 本身。→ [第 2 章](#/doc/ch02)、[第 8 章](#/doc/ch08)

</details>

**18. FirmwareInventory、UpdateService、SessionService 是什麼？**

<details><summary>看答案</summary>

UpdateService 是韌體更新服務入口；FirmwareInventory 是其下的韌體清單集合（各元件版本）；SessionService 管理登入 Session（POST 建立取得 `X-Auth-Token`、DELETE 登出）。→ [第 8 章](#/doc/ch08)

</details>

**19. Redfish 查得到 FirmwareVersion 就代表一定能刷 Firmware 嗎？**

<details><summary>看答案</summary>

不代表。Inventory 只是清單；能否更新要看 `Updateable`、UpdateService 是否提供對應 Action／協定，以及廠商是否支援該途徑。→ [第 8 章](#/doc/ch08)、[第 15 章](#/doc/ch15)

</details>

## 硬體匯流排與 PMBus

**20. BMC 如何讀到 PSU Input/Output Voltage、Current、Power、Fault？**

<details><summary>看答案</summary>

BMC 作為 I²C Controller，透過 SMBus 交易向 PSU 發 PMBus 命令（`READ_VIN`、`READ_VOUT`、`READ_IOUT`、`READ_POUT`、`STATUS_WORD`…），取得原始值後解碼並快取；中間可能經 MUX、CPLD 或其他控制器。Presence／Alert 常是獨立腳位。→ [第 10 章](#/doc/ch10)、[第 13 章](#/doc/ch13)

</details>

**21. I²C、SMBus、PMBus 差在哪裡？**

<details><summary>看答案</summary>

I²C 定義兩線式實體與基本傳輸；SMBus 在其上規定固定交易格式、逾時、PEC 等；PMBus 使用 SMBus 作為傳輸，定義電源管理命令碼與資料格式。→ [第 10 章](#/doc/ch10)

</details>

**22. 為何 PSU 7-bit Address `0x68` 會和 `0xD0/0xD1` 扯上關係？**

<details><summary>看答案</summary>

線上第一個 byte ＝ 7-bit 位址左移 1 位＋R/W 位元：`0x68<<1|0 = 0xD0`（寫）、`0x68<<1|1 = 0xD1`（讀）。Linux 工具用 7-bit（0x68）。→ [第 11 章](#/doc/ch11)

</details>

**23. Read Byte、Read Word、Block Read 有何差異？**

<details><summary>看答案</summary>

Read Byte 回 1 byte；Read Word 回 2 bytes（低位元組先）；Block Read 先回 1 byte 長度再回 N bytes 資料。三者都是「寫命令碼 → Repeated START → 讀」。→ [第 11 章](#/doc/ch11)

</details>

**24. PMBus READ_VOUT／READ_POUT 的 Raw Data 如何解碼？**

<details><summary>看答案</summary>

READ_POUT 用 **Linear11**：高 5 bit 有號指數 N、低 11 bit 有號尾數 Y，值＝Y×2ᴺ（`0x0AEE` → 750×2 = 1500 W）。READ_VOUT 用 **Linear16**：word 為無號尾數，指數取自 `VOUT_MODE` 低 5 bit（`0x17` → −9；`0x1800` → 12.0 V）。實際格式依 PSU 規格確認。→ [第 12 章](#/doc/ch12)

</details>

## 整合

**25. 如果 BMC 連線正常但 PSU Telemetry 為空，如何逐層定位？**

<details><summary>看答案</summary>

① 確認連的是管理該 PSU 的控制器（節點 BMC vs SMM）；② 路徑正確（Power vs PowerSubsystem，從 Chassis 跟連結）；③ BMC 已開機完成並輪詢；④ 用 IPMI 交叉確認；⑤ PSU 在位、有 AC；⑥ 查 BMC Log／SEL 的 I²C 錯誤；⑦ 授權下以唯讀方式確認 PSU 位址是否 ACK；⑧ 交換法判斷問題跟 PSU 或槽位。→ [第 13 章](#/doc/ch13)

</details>
