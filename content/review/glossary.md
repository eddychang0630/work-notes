# 名詞與縮寫對照

> 💡 「唸法」為工程師間常見的口語唸法，僅供溝通參考。「層級」對應本筆記的分層：管理介面／網路／板內匯流排。

## 伺服器與管理

| 縮寫 | 英文全名 | 中文 | 常見唸法 | 層級 | 使用情境 |
|---|---|---|---|---|---|
| BMC | Baseboard Management Controller | 基板管理控制器 | B-M-C | 管理控制器 | 帶外管理、讀感測器、電源控制 |
| SMM | System Management Module | 系統管理模組 | S-M-M | 管理控制器（機箱層級） | Lenovo 部分多節點機箱的共用 PSU／風扇管理 |
| XCC | XClarity Controller | Lenovo 的 BMC 實作 | X-C-C | 管理控制器 | Lenovo ThinkSystem 節點管理 |
| PSU | Power Supply Unit | 電源供應器 | P-S-U | 硬體 | AC／DC 轉換、Telemetry 來源 |
| OOB | Out-of-Band | 帶外（管理） | O-O-B／out of band | 概念 | 不依賴主機 OS 的管理 |
| CPLD | Complex Programmable Logic Device | 複雜可程式邏輯元件 | C-P-L-D | 硬體 | 上電時序、Presence、訊號轉接 |
| MUX | Multiplexer | 多工器 | mux（ㄇㄚˋ克斯） | 硬體 | I²C 分支切換 |
| NIC | Network Interface Card | 網路卡 | nick | 硬體 | 主機／管理網路介面 |
| FRU | Field Replaceable Unit | 現場可更換單元 | fru（ㄈㄨˋ）／F-R-U | IPMI 資料 | 料號、序號、製造資訊 |
| SDR | Sensor Data Record | 感測器資料紀錄 | S-D-R | IPMI 資料 | 感測器定義與門檻 |
| SEL | System Event Log | 系統事件日誌 | sel（ㄙㄟˋ歐）／S-E-L | IPMI 資料 | 事件歷史 |
| KCS | Keyboard Controller Style | 主機與 BMC 的帶內介面 | K-C-S | 帶內通道 | 本機 `ipmitool` |
| OEM | Original Equipment Manufacturer | 原廠／廠商自訂 | O-E-M | — | 廠商特有命令與擴充 |
| Telemetry | — | 遙測資料 | te-LE-me-try | — | 電壓、電流、功率、溫度等讀值 |
| OVP／OCP／OTP／UVP | Over-Voltage／Over-Current／Over-Temperature／Under-Voltage Protection | 過壓／過流／過溫／欠壓保護 | 逐字母 | PSU 保護 | Fault 類型 |

## 管理介面

| 縮寫 | 英文全名 | 中文 | 常見唸法 | 層級 | 使用情境 |
|---|---|---|---|---|---|
| IPMI | Intelligent Platform Management Interface | 智慧平台管理介面 | I-P-M-I | 管理介面（UDP 623） | `ipmitool sensor list` |
| RMCP／RMCP+ | Remote Management Control Protocol | 遠端管理控制協定 | R-M-C-P (plus) | IPMI 的網路封裝 | IPMI over LAN |
| NetFn | Network Function | 網路功能碼 | net function | IPMI 訊息 | 命令群組 |
| Redfish | DMTF Redfish | — | red-fish | 管理介面（HTTPS 之上） | `/redfish/v1/` |
| DMTF | Distributed Management Task Force | 分散式管理任務組 | D-M-T-F | 標準組織 | Redfish 制定者 |
| OData | Open Data Protocol | 開放資料協定 | oh-data | Redfish 慣例 | `@odata.id` |
| Schema | — | 綱要（資料結構定義） | skee-ma | Redfish | 定義資源欄位 |
| OneCLI | Lenovo XClarity Essentials OneCLI | Lenovo 命令列管理工具 | one C-L-I | 廠商工具 | 盤點、設定、韌體更新 |

## 網路

| 縮寫 | 英文全名 | 中文 | 常見唸法 | 層級 | 使用情境 |
|---|---|---|---|---|---|
| IP | Internet Protocol | 網際網路協定 | I-P | 第 3 層 | `192.168.70.100` |
| MAC | Media Access Control | 媒體存取控制（位址） | mac | 第 2 層 | 網卡硬體位址 |
| ARP | Address Resolution Protocol | 位址解析協定 | arp | 2–3 層間 | IP → MAC |
| ICMP | Internet Control Message Protocol | 網際網路控制訊息協定 | I-C-M-P | 第 3 層 | `ping` |
| LAN | Local Area Network | 區域網路 | lan | — | 實驗室網路 |
| VLAN | Virtual LAN | 虛擬區域網路 | V-lan | 第 2 層 | 網路隔離 |
| NAT | Network Address Translation | 網路位址轉譯 | nat | 第 3 層 | WSL2 預設網路模式 |
| TCP | Transmission Control Protocol | 傳輸控制協定 | T-C-P | 第 4 層 | HTTPS、SSH |
| UDP | User Datagram Protocol | 使用者資料報協定 | U-D-P | 第 4 層 | IPMI、TFTP |
| Port | — | 連接埠／埠號 | port | 第 4 層 | 443、623 |
| TID | Transfer Identifier | 傳輸識別碼 | T-I-D | TFTP | TFTP 資料傳輸用的臨時埠 |
| TLS | Transport Layer Security | 傳輸層安全性 | T-L-S | TCP 與 HTTP 之間 | HTTPS 加密 |
| CA | Certificate Authority | 憑證授權單位 | C-A | TLS | 簽發憑證 |
| MITM | Man-in-the-Middle | 中間人攻擊 | M-I-T-M | 安全 | `-k` 的風險 |
| HTTP | Hypertext Transfer Protocol | 超文字傳輸協定 | H-T-T-P | 第 7 層 | `GET /redfish/v1/` |
| HTTPS | HTTP over TLS | 安全的 HTTP | H-T-T-P-S | 第 7 層＋TLS | TCP 443 |
| URI／URL | Uniform Resource Identifier／Locator | 統一資源識別碼／定位符 | U-R-I／U-R-L | 應用層 | 資源位址 |
| SSH | Secure Shell | 安全殼層 | S-S-H | 第 7 層（TCP 22） | 遠端登入 |
| SFTP | SSH File Transfer Protocol | SSH 檔案傳輸協定 | S-F-T-P | 第 7 層（TCP 22） | 安全傳檔 |
| TFTP | Trivial File Transfer Protocol | 簡易檔案傳輸協定 | T-F-T-P | 第 7 層（UDP 69） | 韌體檔傳送 |
| WSL | Windows Subsystem for Linux | Windows 的 Linux 子系統 | W-S-L | 環境 | 在 Windows 跑 Linux 工具 |

## API 與資料

| 縮寫 | 英文全名 | 中文 | 常見唸法 | 層級 | 使用情境 |
|---|---|---|---|---|---|
| API | Application Programming Interface | 應用程式介面 | A-P-I | 概念 | Redfish API、PyVISA API |
| REST | Representational State Transfer | 表現層狀態轉移 | rest | 架構風格 | 資源＋HTTP Method |
| JSON | JavaScript Object Notation | JavaScript 物件表示法 | **Jason（傑森）** | 資料格式 | `{"Health":"OK"}` |
| CSV | Comma-Separated Values | 逗號分隔值 | C-S-V | 資料格式 | 報表輸出 |
| SCPI | Standard Commands for Programmable Instruments | 可程式儀器標準命令 | skippy（斯基批） | 儀器命令 | `*IDN?` |
| VISA | Virtual Instrument Software Architecture | 虛擬儀器軟體架構 | visa | 儀器 I/O API | PyVISA 的底層標準 |
| PyVISA | Python VISA binding | Python 的 VISA 介面 | pie-visa | 程式庫 API | `inst.query(...)` |
| Token | — | 權杖 | token | 認證 | `X-Auth-Token` |
| Session | — | 工作階段 | session | 認證 | Redfish 登入狀態 |

## 板內匯流排與 PMBus

| 縮寫 | 英文全名 | 中文 | 常見唸法 | 層級 | 使用情境 |
|---|---|---|---|---|---|
| I²C | Inter-Integrated Circuit | 積體電路間匯流排 | I-squared-C／I-two-C | 實體／鏈結 | SDA、SCL |
| SDA／SCL | Serial Data／Serial Clock | 序列資料／序列時脈 | S-D-A／S-C-L | I²C 訊號 | 兩條線 |
| ACK／NACK | Acknowledge／Not Acknowledge | 確認／未確認 | ack／nack | I²C | 第 9 個時脈 |
| SMBus | System Management Bus | 系統管理匯流排 | S-M-bus | 交易層 | Read Word、PEC |
| PEC | Packet Error Checking | 封包錯誤檢查 | P-E-C／peck | SMBus | CRC-8 |
| PMBus | Power Management Bus | 電源管理匯流排 | P-M-bus | 命令層 | `READ_VOUT` |
| VR／VRM | Voltage Regulator (Module) | 電壓調節器（模組） | V-R／V-R-M | 硬體 | 也使用 PMBus |
| Linear11／Linear16 | — | PMBus 線性資料格式 | linear eleven／sixteen | PMBus 資料 | 讀值解碼 |
| DIRECT | — | PMBus 直接格式（m、b、R） | direct | PMBus 資料 | 讀值解碼 |
| MSB／LSB | Most／Least Significant Bit(Byte) | 最高／最低有效位元（位元組） | M-S-B／L-S-B | — | Byte Order |
| CRC | Cyclic Redundancy Check | 循環冗餘檢查 | C-R-C | — | PEC 的演算法 |

## 容易混淆的成對名詞

| A | B | 差別 |
|---|---|---|
| BMC | SMM | 節點層級 vs 機箱層級管理 |
| In-Band | Out-of-Band | 經主機 OS vs 經 BMC 管理通道 |
| IP | MAC | 邏輯位址（可路由）vs 硬體位址（同 LAN） |
| IP | Port | 哪台主機 vs 哪個服務 |
| TCP | UDP | 可靠串流 vs 盡力而為的資料報 |
| HTTP | HTTPS | 明文 vs TLS 保護 |
| Authentication | Authorization | 你是誰（401）vs 你能做什麼（403） |
| URI | Endpoint | 資源位址 vs API 存取點（口語常混用） |
| JSON | dict | 文字格式 vs Python 記憶體物件 |
| Sensor | SDR | 當下讀值 vs 感測器的描述紀錄 |
| 7-bit 位址 | 8-bit 位址 | `0x68` vs `0xD0`／`0xD1`（含 R/W） |
| Bus Number | Address | 哪條匯流排 vs 匯流排上的哪顆裝置 |
| Command Code | Address | 裝置內的哪個命令 vs 哪顆裝置 |
| Read Word | Block Read | 固定 2 bytes vs 長度 byte＋N bytes |
| Linear11 | Linear16 | 指數在 word 內 vs 指數在 VOUT_MODE |
| Warning | Fault | 僅通知 vs 通常伴隨保護動作 |
| FirmwareInventory | UpdateService | 版本清單 vs 更新服務入口 |
