# I²C Address 與 Linux 指令

> 📌 **一句話重點**：**7-bit 位址 `0x68`** 在線上會變成 **`0xD0`（寫）／`0xD1`（讀）**，因為位址左移 1 位後最低位元放 R/W。Linux 的 i2c-tools **一律吃 7-bit 位址**。

## 1. 0x68 為什麼會跟 0xD0／0xD1 扯上關係

I²C 線上的第一個 byte 是「7 bit 位址＋1 bit 方向」：

<div class="bits b8">
<span class="m">1</span><span class="m">1</span><span class="m">0</span><span class="m">1</span><span class="m">0</span><span class="m">0</span><span class="m">0</span><span class="r">R/W</span>
<span class="lbl" style="--n:7">7-bit 位址 0x68 = 110&nbsp;1000</span><span class="lbl" style="--n:1">方向</span>
</div>

| 方向 | 計算 | 線上的 byte |
|---|---|---|
| 寫（W=0） | `0x68 << 1 \| 0` = `1101 0000` | **`0xD0`** |
| 讀（R=1） | `0x68 << 1 \| 1` = `1101 0001` | **`0xD1`** |

反過來：`0xD0 >> 1 = 0x68`。

```python
addr7 = 0x68
print(hex(addr7 << 1), hex(addr7 << 1 | 1))   # 0xd0 0xd1
print(hex(0xD0 >> 1))                         # 0x68
```

### 誰用哪一種表示法？

| 來源 | 常見寫法 |
|---|---|
| Linux i2c-tools、`/dev/i2c-*`、Device Tree | **7-bit**（`0x68`） |
| 邏輯分析儀／示波器解碼 | 兩種都有，通常可切換；原始 byte 看到的是 `0xD0`／`0xD1` |
| 部分 PSU／晶片規格書、舊文件 | **8-bit**（寫 `0xD0`，或寫成「`0xD0/0xD1`」） |
| PMBus PSU 規格 | 兩種都有，**一定要確認** |

> ⚠️ **判斷技巧**：7-bit 位址最大是 `0x7F`。如果文件寫的位址 **> 0x7F**（例如 `0xB0`、`0xD0`），它一定是 8-bit 表示法，要右移 1 位才能給 Linux 用（`0xB0` → `0x58`）。如果 ≤ 0x7F 就無法單憑數字判斷，要看文件說明或用波形確認。

## 2. 四個容易混淆的「數字」

以 `i2cget -y 8 0x68 0x8B w` 為例：

<div class="frame"><span class="p">i2cget -y</span><span class="k">8<small>Bus Number</small></span><span class="a">0x68<small>7-bit 位址</small></span><span class="c">0x8B<small>Command Code</small></span><span class="d">w<small>讀取模式：Word</small></span></div>

| 名稱 | 意義 | 決定者 |
|---|---|---|
| **Bus Number** `8` | Linux 給這條 I²C adapter 的編號，對應 `/dev/i2c-8` | 驅動載入順序、Device Tree；**MUX 的每個通道也會變成一個獨立的 bus 編號** |
| **Address** `0x68` | Target 在這條匯流排上的 7-bit 位址 | 裝置硬體／位址腳／槽位 |
| **R/W bit** | 方向，由工具自動加 | 交易類型 |
| **Command Code／Register** `0x8B` | 要存取裝置內的哪個命令或暫存器 | 裝置規格（PMBus：`0x8B` = READ_VOUT） |
| **裝置節點** `/dev/i2c-8` | 使用者空間存取該 bus 的檔案 | `i2c-dev` 核心模組 |

> ⚠️ **Bus 編號不是固定的**：換一版 BMC 韌體、換一個機型，同一條實體匯流排的編號可能不同。「Bus 8、位址 0x68」只是過去某平台的案例，**在其他平台需重新驗證**，不可宣稱所有 Lenovo 平台相同。

## 3. i2c-tools 四個指令

**🟢 可執行（唯讀、不碰匯流排）**

```bash
sudo apt install i2c-tools     # 或 yum install i2c-tools
i2cdetect -l                   # 列出所有 I²C adapter（bus 編號與名稱）
ls -l /dev/i2c-*
```

| 指令 | 用途 | 風險 |
|---|---|---|
| `i2cdetect -l` | 列出 bus | 🟢 無 |
| `i2cdetect -y <bus>` | 掃描該 bus 上有哪些位址回應 | 🟡 **會對每個位址發探測交易**；少數裝置可能誤動作或被探測改變狀態 |
| `i2cget -y <bus> <addr> [cmd] [mode]` | 讀 | 🟡 一般安全，但某些暫存器「讀了會清除」 |
| `i2cset -y <bus> <addr> <cmd> [val] [mode]` | **寫** | 🔴 可改變輸出電壓、關閉輸出、破壞設定 |
| `i2ctransfer -y <bus> ...` | 自訂任意交易序列 | 🔴 最靈活也最危險；可寫入 |
| `i2cdump` | 連續讀整個範圍 | 🟡 等於對每個命令碼都讀一次，對 PMBus 裝置不建議 |

> 🔴 **在伺服器上操作 I²C 的注意事項**
> - BMC 自己也在輪詢同一條匯流排，你的交易會與它**競爭**；可能造成 BMC 偶發讀值錯誤或你讀到被打斷的資料。
> - 掃描與寫入可能讓 PSU 誤動作。**只在授權的測試設備上、確認拓樸與命令後才執行**，並以唯讀為預設。
> - `-y` 會跳過互動確認，下指令前再看一次 bus 與位址。

`i2cdetect -y 8` 輸出範例（模擬）：

```text
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
50: 50 -- -- -- -- -- -- -- 58 -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- --
70: UU -- -- -- -- -- -- --
```

- 數字＝該位址有 ACK；`--`＝無回應（NACK）；`UU`＝已被核心驅動佔用（例如 MUX 驅動）。

## 4. Byte／Word／Block：三種讀取交易

### 4.1 Read Byte（讀 1 byte）— `i2cget ... b`

<div class="frame"><span class="s">S</span><span class="a">Addr</span><span class="rw">W</span><span class="k">A</span><span class="c">Cmd</span><span class="k">A</span><span class="s">Sr</span><span class="a">Addr</span><span class="rw">R</span><span class="k">A</span><span class="d">Data</span><span class="k">N</span><span class="p">P</span></div>

例：`VOUT_MODE`（0x20）、`STATUS_BYTE`（0x78）。

### 4.2 Read Word（讀 2 bytes）— `i2cget ... w`

<div class="frame"><span class="s">S</span><span class="a">Addr</span><span class="rw">W</span><span class="k">A</span><span class="c">Cmd</span><span class="k">A</span><span class="s">Sr</span><span class="a">Addr</span><span class="rw">R</span><span class="k">A</span><span class="d">Data Low</span><span class="k">A</span><span class="d">Data High</span><span class="k">N</span><span class="p">P</span></div>

例：`READ_VOUT`（0x8B）、`READ_POUT`（0x96）、`STATUS_WORD`（0x79）。

> 📌 **Byte Order**：SMBus 規定 **低位元組先送（little-endian）**。線上先看到 `0x98` 再看到 `0xF3`，組合成 word 是 **`0xF398`**。`i2cget ... w` 已經幫你組好，印出 `0xf398`。用 `i2ctransfer` 或邏輯分析儀看原始 bytes 時要自己組：`word = low | (high << 8)`。

### 4.3 Block Read（讀可變長度）— `i2cget ... s`（較新版 i2c-tools）

<div class="frame"><span class="s">S</span><span class="a">Addr</span><span class="rw">W</span><span class="k">A</span><span class="c">Cmd</span><span class="k">A</span><span class="s">Sr</span><span class="a">Addr</span><span class="rw">R</span><span class="k">A</span><span class="rw">Byte Count = N</span><span class="k">A</span><span class="d">Data 1</span><span class="k">A</span><span class="d">…</span><span class="k">A</span><span class="d">Data N</span><span class="k">N</span><span class="p">P</span></div>

例：`MFR_ID`（0x99）、`MFR_MODEL`（0x9A）、`MFR_SERIAL`（0x9E）——回傳 ASCII 字串。

> ⚠️ **Block Read 的第一個回傳 byte 是長度（Byte Count），不是資料**。用 `i2ctransfer` 自己讀時要先知道（或多讀）長度，並把第一個 byte 當 count 處理。這是「字串前面多一個怪字元」的原因。

### 4.4 為什麼需要 Repeated START？

若在送完 Command Code 後發 STOP 再重新 START 讀，等於兩次獨立交易：中間匯流排被釋放，BMC（或其他 Controller）可能插進來，Target 也可能忘記剛才的 Command Code。Repeated START 讓「指定命令 → 讀回資料」成為**不可分割**的一次交易。

### 4.5 對照表

| 交易 | 回傳長度 | i2cget 模式 | PMBus 例子 |
|---|---|---|---|
| Read Byte | 1 | `b` | VOUT_MODE、STATUS_BYTE、STATUS_VOUT |
| Read Word | 2 | `w` | READ_VIN／IIN／VOUT／IOUT／POUT／PIN、STATUS_WORD |
| Block Read | 1（count）＋ N | `s`（SMBus block）／`i`（I²C block，需給長度） | MFR_ID、MFR_MODEL、READ_EIN |
| Send Byte | 0（只送命令） | —（屬於寫入） | CLEAR_FAULTS 🔴 |

**各命令用哪一種不能一概而論**，以 PMBus 規範與 PSU 規格為準。用錯長度不會報錯，只會得到錯誤或被截斷的資料。

## 5. PEC（Packet Error Checking）

- PEC 是附在交易最後的 **1 byte CRC-8**（多項式 `x⁸+x²+x+1`，即 `0x07`，初值 0）。
- 計算範圍：**交易中所有 byte**，包含位址＋R/W 那兩個 byte（`0xD0`、`0xD1`）、Command Code、資料。
- 讀取時由 Target 送出 PEC，Controller 驗證；寫入時由 Controller 送出。
- 是否支援：查 PSU 規格，或讀 `CAPABILITY`（0x19）的 bit 7。

Read Word with PEC：

<div class="frame"><span class="s">S</span><span class="a">Addr</span><span class="rw">W</span><span class="k">A</span><span class="c">Cmd</span><span class="k">A</span><span class="s">Sr</span><span class="a">Addr</span><span class="rw">R</span><span class="k">A</span><span class="d">Low</span><span class="k">A</span><span class="d">High</span><span class="k">A</span><span class="rw">PEC</span><span class="k">N</span><span class="p">P</span></div>

```python
def pec(data: bytes) -> int:
    """SMBus PEC：CRC-8，多項式 0x07，初值 0。"""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc

# READ_VOUT：位址 0x68，回傳 low=0x00, high=0x18
frame = bytes([0xD0, 0x8B, 0xD1, 0x00, 0x18])
print(hex(pec(frame)))
```

`i2cget` 預設不使用 PEC；i2c-tools 4.x 的 `i2cget`／`i2cset` 可用 `-p`（需 adapter 支援）。

## 6. 範例與正確解讀

**🟡 需要設備與權限**（僅在確認 bus、位址、命令與回傳格式後，於授權測試設備執行）

```bash
# 示意：Linux I²C bus 8、7-bit 位址 0x68
i2cget -y 8 0x68 0x20 b      # VOUT_MODE（Read Byte）
i2cget -y 8 0x68 0x8B w      # READ_VOUT（Read Word）
```

成功輸出：

```text
0x17
0x1800
```

失敗輸出與意義：

```text
Error: Read failed
```

| 失敗原因 | 檢查 |
|---|---|
| 位址沒有 ACK（NACK） | 位址是否用了 8-bit 表示法？bus 編號對嗎？MUX 通道有切嗎？PSU 有待機電嗎？ |
| 不支援該命令 | PSU 可能對不支援的命令 NACK，或回傳 0xFF／0xFFFF |
| 匯流排忙碌／被 BMC 佔用 | 重試；確認 SCL／SDA 沒被卡低 |
| 權限 | 需 root 或 `i2c` 群組；`Could not open file /dev/i2c-8` |

> 🔴 **`0x1800` 不是 0x1800 伏特，也不是 6144 伏特！** 這是 Linear16 的原始值，必須搭配 `VOUT_MODE` 解碼：`0x17` → 指數 −9 → `6144 × 2⁻⁹ = 12.0 V`。解碼方法見 [第 12 章](#/doc/ch12)。**任何時候都不得直接把 raw word 當成物理量。**

用 `i2ctransfer` 看原始 bytes（同一筆交易）：

```bash
# w1@0x68 0x8B：寫 1 byte（命令碼）；r2：Repeated START 後讀 2 bytes
i2ctransfer -y 8 w1@0x68 0x8B r2
# 輸出：0x00 0x18   ← low byte 在前，組合後為 0x1800
```

## 7. 常見疑問 FAQ

| 疑問 | 解答 |
|---|---|
| 規格書寫 `0xB0`，`i2cdetect` 卻在 `0x58` 看到 | 規格書用 8-bit 表示，`0xB0 >> 1 = 0x58` |
| `i2cget w` 的值和邏輯分析儀看到的 byte 順序相反 | SMBus 低位元組先送，工具已幫你組成 word |
| Block Read 回來的字串開頭多一個字元 | 那是 Byte Count |
| 讀到 `0xFFFF` | 匯流排沒被驅動（全靠上拉）或裝置不支援；不要當成有效資料 |
| 同一個位址在兩個 bus 都看到 | MUX 的父 bus 與子通道；或真的有兩顆相同位址的裝置在不同分支 |
| `i2cdetect` 顯示 `UU` | 位址被核心驅動綁定，使用者空間工具預設不能存取（`-f` 可強制，但有風險） |

## 8. 練習題

**Q1.** 7-bit 位址 `0x58` 的寫入與讀取 byte 各是多少？

<details><summary>看解答</summary>

`0x58 << 1 = 0xB0`（寫），`0xB1`（讀）。

</details>

**Q2.** 規格書寫 PSU 位址 `0xB4`，Linux 指令要用多少？為什麼可以確定它是 8-bit 表示法？

<details><summary>看解答</summary>

`0xB4 >> 1 = 0x5A`。因為 7-bit 位址上限為 `0x7F`，大於此值必然是含 R/W 位元的 8-bit 表示。

</details>

**Q3.** 說明 Bus Number、Address、Command Code 的差別。

<details><summary>看解答</summary>

Bus Number 是 Linux 對某條 I²C adapter（或 MUX 通道）的編號；Address 是該匯流排上目標裝置的 7-bit 位址；Command Code 是裝置內要存取的命令／暫存器。三者分別回答「哪條線、哪顆裝置、裝置裡的哪個項目」。

</details>

**Q4.** 邏輯分析儀在 Read Word 中依序看到資料 `0xEE`、`0x0A`，word 值是多少？

<details><summary>看解答</summary>

低位元組先送，所以 word = `0x0AEE`。

</details>

**Q5.** Block Read 與 Read Word 在線上最大的不同？

<details><summary>看解答</summary>

Block Read 的第一個回傳 byte 是 Byte Count（後續資料長度），資料長度可變；Read Word 固定回傳 2 bytes，無長度欄位。

</details>

**🔧 動手練習**（🟢 純 Python）：實作 `to_wire(addr7)` 回傳 `(write_byte, read_byte)`、`to_addr7(byte8)`，並用本章的 `pec()` 計算 `[0xB0, 0x79, 0xB1, 0x00, 0x00]` 的 PEC。
