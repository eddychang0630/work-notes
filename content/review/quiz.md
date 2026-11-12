# 總測驗 40 題

> 💡 由初階到進階。先自己作答，再點開看解答與說明。建議每次做 10 題，錯的題目回到對應章節重讀。

## 初階（1–15）

**1.** 伺服器關機（AC 仍插著）時，下列何者通常仍可使用？ (A) SSH 到主機 OS (B) BMC 的 Redfish (C) 主機上的資料庫 (D) 以上皆非

<details><summary>解答</summary>

**(B)**。BMC 由待機電源供電，獨立於主機 OS。（第 1 章）

</details>

**2.** 「帶外管理」的定義是？

<details><summary>解答</summary>

不依賴主機作業系統、透過 BMC 的管理通道（通常為管理網路）進行的管理。（第 1 章）

</details>

**3.** 下列哪個是 DMTF 制定的標準？ (A) IPMI (B) Redfish (C) PMBus (D) I²C

<details><summary>解答</summary>

**(B)**。IPMI 由 Intel 等廠商主導；PMBus 由 PMBus Implementers Forum；I²C 源自 Philips／NXP。（第 2 章）

</details>

**4.** IPMI over LAN 與 Redfish 預設各使用什麼傳輸與 Port？

<details><summary>解答</summary>

IPMI：UDP 623；Redfish：TCP 443（HTTPS）。（第 2、4 章）

</details>

**5.** `192.168.70.100:443` 中，`:443` 代表什麼？

<details><summary>解答</summary>

Port 編號，識別該主機上的 HTTPS 服務。（第 3 章）

</details>

**6.** PC 為 `192.168.70.50/24`，下列哪個位址與它同子網路？ (A) 192.168.71.100 (B) 192.168.70.200 (C) 192.169.70.50 (D) 10.168.70.50

<details><summary>解答</summary>

**(B)**。`/24` 表示前三段相同才同網段。（第 3 章）

</details>

**7.** ping 使用哪個協定？它有 Port 嗎？

<details><summary>解答</summary>

ICMP（第 3 層），沒有 Port 的概念。（第 3 章）

</details>

**8.** TCP 三向交握的三個封包依序為？

<details><summary>解答</summary>

SYN → SYN-ACK → ACK。（第 4 章）

</details>

**9.** 下列敘述何者正確？ (A) UDP 一定比 TCP 快 (B) TCP 保證訊息邊界 (C) UDP 不保證送達 (D) TCP 不需要建立連線

<details><summary>解答</summary>

**(C)**。TCP 是位元組串流不保留訊息邊界；UDP 開銷小但不等於一定較快。（第 4 章）

</details>

**10.** HTTP 的哪個 Method 是唯讀的？

<details><summary>解答</summary>

GET（以及 HEAD）。（第 5 章）

</details>

**11.** HTTP 401 與 403 的差別？

<details><summary>解答</summary>

401：未認證或認證失敗（你是誰？）；403：已認證但無權限（你不能做）。（第 5 章）

</details>

**12.** JSON 如何唸？它有哪六種型別？

<details><summary>解答</summary>

唸「Jason」。Object、Array、String、Number、Boolean、null。（第 7 章）

</details>

**13.** 下列何者是合法 JSON？ (A) `{'a': 1}` (B) `{"a": 1,}` (C) `{"a": True}` (D) `{"a": null}`

<details><summary>解答</summary>

**(D)**。(A) 單引號；(B) 尾端逗號；(C) 應為小寫 `true`。（第 7 章）

</details>

**14.** Redfish 的入口 URI 是？

<details><summary>解答</summary>

`/redfish/v1/`（Service Root）。（第 2、8 章）

</details>

**15.** I²C 的兩條線叫什麼？

<details><summary>解答</summary>

SDA（資料）與 SCL（時脈）。（第 10 章）

</details>

## 中階（16–30）

**16.** `nc -vz <BMC_IP> 443` 顯示 `Connection refused`，最可能的原因？

<details><summary>解答</summary>

主機可達，但 443 沒有服務在聽（收到 RST）：服務未啟動、BMC 仍在開機、或 HTTPS 被停用。與 timeout（無回應）不同。（第 4、14 章）

</details>

**17.** TFTP 傳輸時，為什麼防火牆只開 UDP 69 可能不夠？

<details><summary>解答</summary>

只有初始 RRQ／WRQ 送到 69；Server 之後用新的臨時埠（TID）傳資料，回程封包可能被擋。（第 4、15 章）

</details>

**18.** `curl -k` 之下，連線是否仍加密？缺少了什麼？

<details><summary>解答</summary>

仍加密；缺少伺服器憑證驗證（身分驗證），無法防止中間人攻擊。（第 5 章）

</details>

**19.** 看到 HTTP 404 時，可以確定哪些層是正常的？

<details><summary>解答</summary>

IP 可達、TCP 連線、TLS 握手、HTTP 服務都正常；問題在 URI 路徑／資源不存在。（第 5 章）

</details>

**20.** Redfish 中「重開機」為什麼用 POST 到 Action 而不是 PATCH？

<details><summary>解答</summary>

重開機是動作而非屬性修改；Redfish 以 `Actions/ComputerSystem.Reset` 的 target 搭配 POST 與參數（ResetType）表達。（第 6 章）

</details>

**21.** 以下 Python 會印出什麼？

```python
import json
d = json.loads('{"Status": {"Health": null}, "Members": []}')
print(d["Status"]["Health"] is None, len(d["Members"]), d.get("Name", "N/A"))
```

<details><summary>解答</summary>

`True 0 N/A`。JSON `null` → `None`；空陣列長度 0；`get` 取不到回傳預設值。（第 7 章）

</details>

**22.** Redfish 集合資源的成員清單在哪個欄位？每個成員通常只包含什麼？

<details><summary>解答</summary>

`Members` 陣列；每個成員通常只有 `@odata.id`（連結），需再 GET 才能取得完整內容。（第 7、8 章）

</details>

**23.** 建立 Redfish Session 成功後，回應的狀態碼與兩個重要 Header 是？

<details><summary>解答</summary>

201 Created；`X-Auth-Token`（之後請求要帶）與 `Location`（Session 的 URI，登出時 DELETE）。（第 8 章）

</details>

**24.** 為什麼自動化程式結束時要 DELETE Session？

<details><summary>解答</summary>

BMC 的 Session 數量有限，不登出會佔用到逾時，累積後導致後續登入失敗。（第 8 章）

</details>

**25.** `ipmitool -I lanplus -H <BMC_IP> -U <USER> -E sdr list` 中 `-E` 的作用？

<details><summary>解答</summary>

從環境變數 `IPMI_PASSWORD` 讀取密碼，避免密碼出現在命令列。（第 9 章）

</details>

**26.** IPMI 的 SDR、SEL、FRU 各是什麼？

<details><summary>解答</summary>

SDR：感測器描述紀錄；SEL：系統事件日誌；FRU：可更換元件的料號／序號等資訊。（第 2、9 章）

</details>

**27.** SMBus 相對於 I²C 增加了哪些規定？舉三項。

<details><summary>解答</summary>

固定交易格式（Read Byte／Word／Block…）、逾時機制（SCL 低 25–35 ms）、PEC、SMBALERT#、最低時脈 10 kHz、固定邏輯門檻等。（第 10 章）

</details>

**28.** 7-bit 位址 `0x68` 的寫入與讀取位址 byte？

<details><summary>解答</summary>

`0xD0`（寫）、`0xD1`（讀）。（第 11 章）

</details>

**29.** 規格書寫 PMBus 位址 `0xB2`，`i2cget` 應使用？

<details><summary>解答</summary>

`0x59`（`0xB2 >> 1`）。大於 0x7F 必為 8-bit 表示法。（第 11 章）

</details>

**30.** Block Read 回傳的第一個 byte 是什麼？

<details><summary>解答</summary>

Byte Count：後續資料的長度，不是資料本身。（第 11 章）

</details>

## 進階（31–40）

**31.** 解碼 Linear11：`0xF398`。

<details><summary>解答</summary>

N = `11110b` = −2；Y = `0x398` = 920；值 = 920 × 2⁻² = **230.0**（例如 230 V）。（第 12 章）

</details>

**32.** `VOUT_MODE = 0x17`、`READ_VOUT = 0x1800`，輸出電壓？

<details><summary>解答</summary>

指數 = `10111b` = −9；6144 × 2⁻⁹ = **12.0 V**。（第 12 章）

</details>

**33.** 邏輯分析儀在 `READ_POUT` 交易的資料階段依序看到 `0xEE`、`0x0A`。功率是多少？

<details><summary>解答</summary>

低位元組在前 → word = `0x0AEE`；N = +1，Y = 750；**1500 W**。（第 11、12 章）

</details>

**34.** 解碼 Linear11：`0xE7B0`（注意符號）。

<details><summary>解答</summary>

N = `11100b` = −4；Y = `0x7B0` = 1968 → 1968 − 2048 = −80；值 = −80 ÷ 16 = **−5.0**。（第 12 章）

</details>

**35.** `STATUS_WORD = 0x0848` 表示哪些狀態？

<details><summary>解答</summary>

bit 11 POWER_GOOD#（Power Good 無效）、bit 6 OFF（輸出關閉）、bit 3 VIN_UV_FAULT（輸入欠壓）。（第 12 章）

</details>

**36.** PEC 用什麼演算法？涵蓋哪些 byte？

<details><summary>解答</summary>

CRC-8，多項式 x⁸+x²+x+1（0x07）；涵蓋整筆交易的所有 byte，包含位址＋R/W byte、Command Code 與資料。（第 11 章）

</details>

**37.** Redfish 顯示 PSU 輸出功率 1498 W，同時間你用功率分析儀量到 1512 W。列出三個可能原因。

<details><summary>解答</summary>

BMC 輪詢與快取造成的時間差；PSU 內部量測精度（±數 %）與 Linear11 解析度；量測位置不同（PSU 內部 vs 外部線路）；平均／濾波；四捨五入。（第 12、13 章）

</details>

**38.** 你在 WSL2（預設網路）內架 TFTP，BMC 抓檔逾時。最可能的根本原因與驗證方式？

<details><summary>解答</summary>

WSL2 NAT 模式下 WSL 位於虛擬網段，BMC 無法連入。驗證：WSL 內 `tcpdump udp port 69` 看不到 RRQ。改用原生 Linux／Windows TFTP，或設定 Mirrored Networking 並開防火牆。（第 14、15 章）

</details>

**39.** `curl -v` 顯示 TLS 握手成功、`HTTP/1.1 200 OK`，但 PowerSupplies 集合的 `Members` 是空陣列。請給出排查順序。

<details><summary>解答</summary>

① 是否連到管理 PSU 的控制器（節點 BMC vs SMM）；② 路徑是否為該平台實際使用的模型（Power vs PowerSubsystem）；③ BMC 是否剛開機尚未盤點；④ IPMI `sdr type "Power Supply"` 交叉確認；⑤ PSU 在位與 AC；⑥ BMC Log 的 I²C 錯誤；⑦ 授權下唯讀確認 I²C ACK；⑧ 交換法。（第 13 章）

</details>

**40.** 韌體更新前至少列出六項必須確認的事項，並說明為何「FirmwareInventory 看得到版本」不足以證明可以更新。

<details><summary>解答</summary>

確認：授權與維護時段、硬體型號與韌體對應、檔案雜湊／簽章、目前版本與相依性、備援與 Health、更新順序、Recovery 方案、更新中不中斷電源、紀錄保存、更新後驗證。Inventory 只是清單；能否更新取決於 `Updateable`、UpdateService 提供的 Action 與支援協定、以及廠商是否支援該途徑，且實際流程須依官方文件。（第 8、15 章）

</details>

---

## 計分建議

| 答對題數 | 建議 |
|---|---|
| 36–40 | 很扎實，可以挑戰第 16 章專題 |
| 28–35 | 回頭複習錯題對應章節的「常見誤解」與流程圖 |
| 低於 28 | 依學習路徑從第 1 階段重新走一次，每章做完練習題 |
