from datetime import datetime

from scripts.import_tdx_day import TdxDailyBar
from scripts.import_tdx_directory import (
    build_directory_report,
    has_invalid_price,
    has_ohlc_error,
    is_a_stock_path,
    is_a_stock_symbol,
    summarize_file,
)


def make_bar(symbol="600000", exchange="SSE", close_price=10, volume=100):
    return TdxDailyBar(
        symbol=symbol,
        exchange=exchange,
        datetime=datetime(2026, 7, 16),
        open_price=10,
        high_price=11,
        low_price=9,
        close_price=close_price,
        volume=volume,
        turnover=1000,
    )


def test_quality_checks_detect_invalid_price_and_ohlc_error():
    assert has_invalid_price(make_bar(close_price=0))

    bad_bar = TdxDailyBar(
        symbol="600000",
        exchange="SSE",
        datetime=datetime(2026, 7, 16),
        open_price=10,
        high_price=9,
        low_price=8,
        close_price=10,
        volume=100,
        turnover=1000,
    )
    assert has_ohlc_error(bad_bar)


def test_build_directory_report_aggregates_file_reports(tmp_path):
    first = summarize_file(tmp_path / "sh600000.day", [make_bar()], tmp_path)
    second = summarize_file(tmp_path / "sz000001.day", [make_bar(symbol="000001", exchange="SZSE", volume=0)], tmp_path)

    report = build_directory_report(tmp_path, [first, second])

    assert report.files == 2
    assert report.parsed_files == 2
    assert report.failed_files == 0
    assert report.records == 2
    assert report.start == "2026-07-16"
    assert report.end == "2026-07-16"
    assert report.zero_volume_records == 1


def test_a_stock_filter_keeps_stock_codes_and_excludes_indexes_funds_b_shares():
    assert is_a_stock_symbol("600000", "SSE")
    assert is_a_stock_symbol("688001", "SSE")
    assert is_a_stock_symbol("000001", "SZSE")
    assert is_a_stock_symbol("300001", "SZSE")
    assert is_a_stock_symbol("920578", "BSE")

    assert not is_a_stock_symbol("000001", "SSE")
    assert not is_a_stock_symbol("399001", "SZSE")
    assert not is_a_stock_symbol("200012", "SZSE")
    assert not is_a_stock_symbol("510300", "SSE")


def test_a_stock_filter_uses_tdx_filename_prefixes():
    assert is_a_stock_path("sh600000.day")
    assert is_a_stock_path("sz300001.day")
    assert is_a_stock_path("bj920578.day")
    assert not is_a_stock_path("sh000001.day")
    assert not is_a_stock_path("sz399001.day")
