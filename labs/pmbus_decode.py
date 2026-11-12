"""PMBus 資料解碼工具（對應筆記第 11、12 章）。純運算，不存取任何硬體。"""


def _signed(value: int, bits: int) -> int:
    """把 bits 位元的無號整數解讀為二補數有號數。"""
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def _check_word(word: int) -> None:
    if not 0 <= word <= 0xFFFF:
        raise ValueError("word 必須是 0..0xFFFF")


def linear11(word: int) -> float:
    """Linear11：高 5 bit 為有號指數 N，低 11 bit 為有號尾數 Y，值 = Y * 2^N。"""
    _check_word(word)
    n = _signed(word >> 11, 5)
    y = _signed(word & 0x7FF, 11)
    return y * 2.0 ** n


def linear16(word: int, vout_mode: int) -> float:
    """Linear16：尾數為 16-bit 無號 word，指數來自 VOUT_MODE 低 5 bit（有號）。"""
    _check_word(word)
    mode = (vout_mode >> 5) & 0x7
    if mode != 0:
        raise ValueError(f"VOUT_MODE 模式為 {mode:03b}，不是 Linear，不能用 Linear16 解碼")
    n = _signed(vout_mode & 0x1F, 5)
    return word * 2.0 ** n


def direct(word: int, m: int, b: int, r: int) -> float:
    """DIRECT：X = (1/m) * (Y * 10^-R - b)，Y 為 16-bit 有號。"""
    _check_word(word)
    y = _signed(word, 16)
    return (y * 10.0 ** (-r) - b) / m


def word_from_bytes(low: int, high: int) -> int:
    """SMBus 低位元組先送。"""
    return (high << 8) | low


def to_wire(addr7: int) -> tuple[int, int]:
    """7-bit 位址 → (寫入 byte, 讀取 byte)。"""
    if not 0 <= addr7 <= 0x7F:
        raise ValueError("7-bit 位址必須是 0..0x7F")
    return addr7 << 1, addr7 << 1 | 1


def to_addr7(byte8: int) -> int:
    """8-bit 表示法（含 R/W）→ 7-bit 位址。"""
    return byte8 >> 1


def pec(data: bytes) -> int:
    """SMBus PEC：CRC-8，多項式 0x07，初值 0；涵蓋含位址 byte 在內的整筆交易。"""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


STATUS_WORD_BITS = {
    15: "VOUT", 14: "IOUT/POUT", 13: "INPUT", 12: "MFR_SPECIFIC",
    11: "POWER_GOOD#", 10: "FANS", 9: "OTHER", 8: "UNKNOWN",
    7: "BUSY", 6: "OFF", 5: "VOUT_OV_FAULT", 4: "IOUT_OC_FAULT",
    3: "VIN_UV_FAULT", 2: "TEMPERATURE", 1: "CML", 0: "NONE_OF_THE_ABOVE",
}


def decode_status_word(word: int) -> list[str]:
    """回傳 STATUS_WORD 中被設定的位元名稱（由高位到低位）。"""
    _check_word(word)
    return [name for bit, name in sorted(STATUS_WORD_BITS.items(), reverse=True) if word >> bit & 1]


if __name__ == "__main__":
    print("READ_VIN  0xF398 ->", linear11(0xF398), "V")
    print("READ_POUT 0x0AEE ->", linear11(0x0AEE), "W")
    print("READ_VOUT 0x1800 (VOUT_MODE 0x17) ->", linear16(0x1800, 0x17), "V")
    print("STATUS_WORD 0x0848 ->", decode_status_word(0x0848))
    print("0x68 on wire ->", [hex(b) for b in to_wire(0x68)])
