"""pmbus_decode 的測試。可用 `python labs/test_pmbus_decode.py` 或 `pytest labs/` 執行。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pmbus_decode import (  # noqa: E402
    decode_status_word, direct, linear11, linear16, pec, to_addr7, to_wire, word_from_bytes,
)


def test_linear11():
    assert linear11(0xF398) == 230.0       # VIN
    assert linear11(0x0AEE) == 1500.0      # POUT
    assert linear11(0xD1F4) == 7.8125      # IOUT
    assert linear11(0xE7B0) == -5.0        # 負尾數
    assert linear11(0xF3C8) == 242.0
    assert linear11(0x0A58) == 1200.0
    assert linear11(0x0000) == 0.0


def test_linear11_project_b_samples():
    assert linear11(0xF178) == 94.0
    assert linear11(0xD280) == 10.0
    assert linear11(0xF1E1) == 120.25
    assert linear11(0xDA58) == 18.75
    assert linear11(0xF381) == 224.25
    assert linear11(0xE3E8) == 62.5
    assert linear11(0x02EC) == 748.0


def test_linear16():
    assert linear16(0x1800, 0x17) == 12.0
    assert linear16(0x3600, 0x18) == 54.0
    assert abs(linear16(0x1866, 0x17) - 12.199) < 0.001


def test_linear16_rejects_non_linear_mode():
    try:
        linear16(0x1800, 0x40)             # 模式 010 = DIRECT
    except ValueError:
        return
    raise AssertionError("應該丟出 ValueError")


def test_direct():
    assert direct(1205, m=100, b=0, r=0) == 12.05


def test_bytes_and_address():
    assert word_from_bytes(0x98, 0xF3) == 0xF398
    assert word_from_bytes(0xEE, 0x0A) == 0x0AEE
    assert to_wire(0x68) == (0xD0, 0xD1)
    assert to_wire(0x58) == (0xB0, 0xB1)
    assert to_addr7(0xB0) == 0x58
    assert to_addr7(0xB4) == 0x5A
    assert to_addr7(0xB2) == 0x59


def test_status_word():
    assert decode_status_word(0x0848) == ["POWER_GOOD#", "OFF", "VIN_UV_FAULT"]
    assert decode_status_word(0x2008) == ["INPUT", "VIN_UV_FAULT"]
    assert decode_status_word(0x0000) == []


def test_pec_known_vector():
    # CRC-8 (poly 0x07, init 0) 的標準檢查值："123456789" -> 0xF4
    assert pec(b"123456789") == 0xF4
    assert pec(b"") == 0


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for name, fn in tests:
        fn()
        print("PASS", name)
    print(f"全部 {len(tests)} 項測試通過")
