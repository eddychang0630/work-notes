# 指令與協定速查表

> 🔴 標示 🔴 的操作會改變設備狀態；其餘為唯讀。`<...>` 為佔位符。密碼一律用互動輸入或環境變數，不寫在命令列。

## 層級總覽

| 層 | 協定 | 診斷指令 |
|---|---|---|
| 應用／API | Redfish、JSON | `curl ... \| python3 -m json.tool` |
| 應用 | HTTP／HTTPS、IPMI(RMCP)、TFTP、SSH | `curl -v`、`ipmitool`、`curl tftp://` |
| 安全 | TLS | `curl -v`、`openssl s_client -connect <IP>:443` |
| 傳輸 | TCP、UDP | `nc -vz`、`ss -tulpen` |
| 網路 | IP、ICMP | `ip addr`、`ip route get`、`ping` |
| 鏈結 | Ethernet、ARP | `ip link`、`ip neigh` |
| 板內 | PMBus → SMBus → I²C | `i2cdetect -l`、`i2cget` |

## 常用 Port

| Port | 傳輸 | 服務 |
|---|---|---|
| 22 | TCP | SSH／SFTP |
| 80 | TCP | HTTP |
| 443 | TCP | HTTPS／Redfish |
| 69 | UDP | TFTP（僅初始請求，之後用 TID 臨時埠） |
| 623 | UDP | IPMI RMCP／RMCP+ |

## HTTP 狀態碼

| 碼 | 意義 | 碼 | 意義 |
|---|---|---|---|
| 200 | 成功 | 401 | 未認證／認證失敗 |
| 201 | 已建立（Session） | 403 | 權限不足 |
| 202 | 已接受，背景執行（Task） | 404 | 資源不存在 |
| 204 | 成功無內容 | 405 | Method 不支援 |
| 400 | 請求格式／參數錯 | 409 | 狀態衝突 |
| 500 | BMC 內部錯誤 | 503 | 暫時無法服務 |

## 網路診斷

```bash
ip -br addr                      # 我的 IP
ip route get <BMC_IP>            # 走哪張網卡
ip neigh                         # ARP 表
ping -c 4 <BMC_IP>
nc -vz -w 3 <BMC_IP> 443         # TCP Port
sudo ss -tulpen                  # 本機在聽的 Port
curl -v --max-time 10 https://<BMC_IP>/redfish/v1/ -o /dev/null
sudo tcpdump -ni <IFACE> host <BMC_IP>
```

| 訊息 | 意義 |
|---|---|
| `Destination Host Unreachable` | ARP 失敗（第 2 層） |
| `Connection refused` | Port 沒服務 |
| `timed out` | 封包被丟／不可達 |
| `SSL certificate problem` | 憑證驗證失敗 |

## curl 選項

| 選項 | 意義 |
|---|---|
| `-v`／`-i`／`-s` | 詳細／含 Header／安靜 |
| `--cacert <檔>` | 指定 CA（正式做法） |
| `-k` | 跳過憑證驗證（**僅實驗**） |
| `-u '<USER>'` | Basic Auth，密碼互動輸入 |
| `-H 'K: V'` | 加 Header |
| `-X <M>`／`-d '<body>'` | 指定 Method／Body 🔴 |
| `--max-time <s>` | 逾時 |
| `-w '%{http_code}\n'` | 印狀態碼 |

## Redfish

```bash
B='https://<BMC_IP>'; C='--cacert <CA_CERT_PATH>'
curl $C -s      $B/redfish/v1/                                  | python3 -m json.tool
curl $C -s -u '<USER>' $B/redfish/v1/Chassis                    | python3 -m json.tool
curl $C -s -u '<USER>' $B/redfish/v1/Managers                   | python3 -m json.tool
curl $C -s -u '<USER>' $B/redfish/v1/UpdateService              | python3 -m json.tool
curl $C -s -u '<USER>' $B/redfish/v1/UpdateService/FirmwareInventory | python3 -m json.tool
```

| 資源 | 內容 |
|---|---|
| `Systems` | 邏輯系統、電源狀態、Reset Action |
| `Chassis` | PSU、功率、溫度、風扇（`Power`／`PowerSubsystem`／`Sensors`） |
| `Managers` | BMC／SMM 資訊 |
| `UpdateService` → `FirmwareInventory` | 韌體清單 |
| `SessionService` → `Sessions` | 登入／登出 |

Session 流程：`POST .../Sessions`（Body `UserName`／`Password`）→ 201 ＋ Header `X-Auth-Token`、`Location` → 後續帶 `X-Auth-Token` → `DELETE <Location>`。

**原則**：從 Service Root 跟 `@odata.id` 走；路徑與成員名稱依平台而異。

## Python requests

```python
import os, requests
s = requests.Session()
s.verify = os.environ.get("BMC_CA_BUNDLE", True)
r = s.get(base + "/redfish/v1/", auth=(user, pw), timeout=(5, 20))
r.raise_for_status()
data = r.json()
health = (data.get("Status") or {}).get("Health")
```

| 例外 | 層 |
|---|---|
| `ConnectTimeout`／`ConnectionError` | IP／TCP |
| `SSLError` | TLS |
| `HTTPError` | HTTP 4xx／5xx |
| `JSONDecodeError` | Body 非 JSON |

## JSON

| JSON | Python | | JSON | Python |
|---|---|---|---|---|
| `{}` | `dict` | | `true`／`false` | `True`／`False` |
| `[]` | `list` | | `null` | `None` |
| `"x"` | `str` | | `12.5` | `float` |

`json.loads(str)` 解析；`json.dumps(obj, indent=2, ensure_ascii=False)` 輸出；`response.json()` 解析回應。

## ipmitool

```bash
I='ipmitool -I lanplus -H <BMC_IP> -U <USER> -E'    # 密碼在 $IPMI_PASSWORD
$I mc info
$I chassis power status
$I sensor list
$I sdr elist
$I sdr type "Power Supply"
$I sel elist
$I fru print
$I lan print
```

| 🔴 高風險 | 作用 |
|---|---|
| `chassis power off／cycle／reset` | 強制斷電／重啟主機 |
| `mc reset cold` | 重啟 BMC |
| `sel clear` | 清除事件紀錄 |
| `raw <NetFn> <Cmd> ...` | 送任意 bytes；OEM 命令不可猜 |

## I²C／i2c-tools

| 7-bit | 寫 byte | 讀 byte | | 換算 |
|---|---|---|---|---|
| `0x58` | `0xB0` | `0xB1` | | 8-bit = 7-bit << 1 (\| R/W) |
| `0x68` | `0xD0` | `0xD1` | | 7-bit = 8-bit >> 1 |

```bash
i2cdetect -l                           # 列出 bus（安全）
i2cdetect -y <BUS>                     # 🟡 掃描
i2cget -y <BUS> <ADDR7> <CMD> b        # Read Byte
i2cget -y <BUS> <ADDR7> <CMD> w        # Read Word（已組成 word）
i2ctransfer -y <BUS> w1@<ADDR7> <CMD> r2   # 原始 bytes（低位元組在前）
# 🔴 i2cset / i2ctransfer 寫入：可能改變輸出或設定
```

| 交易 | 線上格式 |
|---|---|
| Read Byte | `S Addr+W A Cmd A Sr Addr+R A Data N P` |
| Read Word | `S Addr+W A Cmd A Sr Addr+R A Low A High N P` |
| Block Read | `S Addr+W A Cmd A Sr Addr+R A Count A D1 … Dn N P` |
| ＋PEC | 最後多 1 byte CRC-8（poly 0x07，涵蓋含位址在內的所有 byte） |

## PMBus 命令碼

| 碼 | 命令 | 交易 | 格式 |
|---|---|---|---|
| `0x03` | CLEAR_FAULTS 🔴 | Send Byte | — |
| `0x19` | CAPABILITY | Byte | bit7 = PEC |
| `0x20` | VOUT_MODE | Byte | 模式[7:5]＋指數[4:0] |
| `0x78` | STATUS_BYTE | Byte | 位元 |
| `0x79` | STATUS_WORD | Word | 位元 |
| `0x7A`–`0x7E` | STATUS_VOUT／IOUT／INPUT／TEMPERATURE／CML | Byte | 位元 |
| `0x81` | STATUS_FANS_1_2 | Byte | 位元 |
| `0x88` | READ_VIN | Word | Linear11 |
| `0x89` | READ_IIN | Word | Linear11 |
| `0x8B` | READ_VOUT | Word | Linear16 |
| `0x8C` | READ_IOUT | Word | Linear11 |
| `0x8D` | READ_TEMPERATURE_1 | Word | Linear11 |
| `0x90` | READ_FAN_SPEED_1 | Word | Linear11 |
| `0x96` | READ_POUT | Word | Linear11 |
| `0x97` | READ_PIN | Word | Linear11 |
| `0x98` | PMBUS_REVISION | Byte | — |
| `0x99`／`0x9A`／`0x9B`／`0x9E` | MFR_ID／MODEL／REVISION／SERIAL | Block | ASCII |

是否支援與格式依 PSU 規格為準。

## 解碼公式

| 格式 | 公式 | 例 |
|---|---|---|
| **Linear11** | N = bits[15:11] 有號；Y = bits[10:0] 有號；值 = Y × 2ᴺ | `0xF398` → 920 × 2⁻² = 230.0 |
| **Linear16** | 值 = word（無號）× 2ᴺ；N = VOUT_MODE[4:0] 有號 | `0x1800`、mode `0x17`（N=−9）→ 12.0 V |
| **DIRECT** | X = (Y × 10⁻ᴿ − b) ÷ m | m=100,b=0,R=0,Y=1205 → 12.05 |

二補數：5-bit ≥16 減 32；11-bit ≥1024 減 2048。

## STATUS_WORD 位元

| 15 | 14 | 13 | 12 | 11 | 10 | 9 | 8 |
|---|---|---|---|---|---|---|---|
| VOUT | IOUT/POUT | INPUT | MFR | PGOOD# | FANS | OTHER | UNKNOWN |

| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|---|
| BUSY | OFF | VOUT_OV | IOUT_OC | VIN_UV | TEMP | CML | NONE_ABOVE |

## TFTP

```bash
sudo ss -ulpn | grep ':69'                                   # 服務在聽？
curl -o test.bin tftp://<TFTP_SERVER_IP>/<FILE>              # 從另一台實測
sha256sum test.bin
sudo tcpdump -ni <IFACE> udp and host <BMC_IP>               # 看 RRQ／DATA／ACK
```

| 發行版 | 套件 | 根目錄（常見預設） |
|---|---|---|
| Ubuntu | `tftpd-hpa` | `/srv/tftp` |
| CentOS 7／RHEL | `tftp-server` | `/var/lib/tftpboot` |

BMC 要填**實體網路可達的 IP**（不是 WSL 的 172.x、不是 127.0.0.1）。

## 韌體更新前（🔴）

授權 → 型號／檔案對應 → 雜湊驗證 → 版本相依 → 備援與 Health → 順序 → Recovery → 不中斷電源 → 存檔紀錄 → 更新後驗證。**命令以官方文件為準。**
