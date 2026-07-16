import struct
from datetime import datetime
from pathlib import Path

import pytest

from scripts.import_tdx_day import infer_symbol_exchange, parse_day_file, parse_record


def make_record(date, open_price, high_price, low_price, close_price, turnover, volume):
    return struct.pack(
        "<IIIIIfII",
        date,
        round(open_price * 100),
        round(high_price * 100),
        round(low_price * 100),
        round(close_price * 100),
        float(turnover),
        volume,
        0,
    )


def test_infer_symbol_exchange_from_standard_tdx_name():
    assert infer_symbol_exchange(Path("sh600000.day")) == ("600000", "SSE")
    assert infer_symbol_exchange(Path("sz000001.day")) == ("000001", "SZSE")
    assert infer_symbol_exchange(Path("bj920578.day")) == ("920578", "BSE")


def test_parse_record_converts_tdx_prices_and_date():
    bar = parse_record(make_record(20260716, 10.12, 10.88, 9.99, 10.5, 123456.0, 10000), "600000", "SSE")

    assert bar.symbol == "600000"
    assert bar.exchange == "SSE"
    assert bar.datetime == datetime(2026, 7, 16)
    assert bar.open_price == 10.12
    assert bar.high_price == 10.88
    assert bar.low_price == 9.99
    assert bar.close_price == 10.5
    assert bar.volume == 10000
    assert bar.turnover == 123456.0


def test_parse_day_file_sorts_records(tmp_path):
    file_path = tmp_path / "sh600000.day"
    file_path.write_bytes(
        make_record(20260717, 11, 12, 10, 11.5, 2_000, 200)
        + make_record(20260716, 10, 11, 9, 10.5, 1_000, 100)
    )

    bars = parse_day_file(file_path)

    assert [bar.datetime for bar in bars] == [datetime(2026, 7, 16), datetime(2026, 7, 17)]
    assert [bar.close_price for bar in bars] == [10.5, 11.5]


def test_parse_day_file_rejects_bad_record_size(tmp_path):
    file_path = tmp_path / "sh600000.day"
    file_path.write_bytes(b"bad")

    with pytest.raises(ValueError, match="not aligned"):
        parse_day_file(file_path)
