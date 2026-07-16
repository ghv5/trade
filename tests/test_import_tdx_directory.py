from datetime import datetime

from scripts.import_tdx_day import TdxDailyBar
from scripts.import_tdx_directory import build_directory_report, has_invalid_price, has_ohlc_error, summarize_file


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
