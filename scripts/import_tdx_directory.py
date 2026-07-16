#!/usr/bin/env python3
"""Scan or import a directory of Tongdaxin .day files."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

try:
    from scripts.import_tdx_day import TdxDailyBar, parse_day_file, save_to_vnpy
except ModuleNotFoundError:
    from import_tdx_day import TdxDailyBar, parse_day_file, save_to_vnpy


@dataclass(frozen=True)
class FileReport:
    path: str
    symbol: str | None
    exchange: str | None
    records: int
    start: str | None
    end: str | None
    zero_volume_records: int
    invalid_price_records: int
    ohlc_error_records: int
    error: str | None = None


@dataclass(frozen=True)
class DirectoryReport:
    root: str
    files: int
    parsed_files: int
    failed_files: int
    records: int
    start: str | None
    end: str | None
    zero_volume_records: int
    files_with_invalid_prices: int
    files_with_ohlc_errors: int
    failures: list[FileReport]


def iter_day_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.day") if path.is_file())


def has_invalid_price(bar: TdxDailyBar) -> bool:
    return min(bar.open_price, bar.high_price, bar.low_price, bar.close_price) <= 0


def has_ohlc_error(bar: TdxDailyBar) -> bool:
    prices = [bar.open_price, bar.high_price, bar.low_price, bar.close_price]
    return bar.high_price < max(prices) or bar.low_price > min(prices)


def summarize_file(path: Path, bars: list[TdxDailyBar], root: Path) -> FileReport:
    if not bars:
        return FileReport(
            path=str(path.relative_to(root)),
            symbol=None,
            exchange=None,
            records=0,
            start=None,
            end=None,
            zero_volume_records=0,
            invalid_price_records=0,
            ohlc_error_records=0,
            error=None,
        )

    return FileReport(
        path=str(path.relative_to(root)),
        symbol=bars[0].symbol,
        exchange=bars[0].exchange,
        records=len(bars),
        start=bars[0].datetime.strftime("%Y-%m-%d"),
        end=bars[-1].datetime.strftime("%Y-%m-%d"),
        zero_volume_records=sum(1 for bar in bars if bar.volume == 0),
        invalid_price_records=sum(1 for bar in bars if has_invalid_price(bar)),
        ohlc_error_records=sum(1 for bar in bars if has_ohlc_error(bar)),
        error=None,
    )


def build_directory_report(root: Path, file_reports: list[FileReport]) -> DirectoryReport:
    parsed_reports = [report for report in file_reports if report.error is None]
    failures = [report for report in file_reports if report.error is not None]
    starts = [datetime.strptime(report.start, "%Y-%m-%d") for report in parsed_reports if report.start]
    ends = [datetime.strptime(report.end, "%Y-%m-%d") for report in parsed_reports if report.end]

    return DirectoryReport(
        root=str(root),
        files=len(file_reports),
        parsed_files=len(parsed_reports),
        failed_files=len(failures),
        records=sum(report.records for report in parsed_reports),
        start=min(starts).strftime("%Y-%m-%d") if starts else None,
        end=max(ends).strftime("%Y-%m-%d") if ends else None,
        zero_volume_records=sum(report.zero_volume_records for report in parsed_reports),
        files_with_invalid_prices=sum(1 for report in parsed_reports if report.invalid_price_records > 0),
        files_with_ohlc_errors=sum(1 for report in parsed_reports if report.ohlc_error_records > 0),
        failures=failures[:50],
    )


def write_report(path: Path, directory_report: DirectoryReport, file_reports: list[FileReport]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": asdict(directory_report),
        "files": [asdict(report) for report in file_reports],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def print_summary(report: DirectoryReport) -> None:
    print(f"root: {report.root}")
    print(f"files: {report.files}")
    print(f"parsed_files: {report.parsed_files}")
    print(f"failed_files: {report.failed_files}")
    print(f"records: {report.records}")
    print(f"range: {report.start} -> {report.end}")
    print(f"zero_volume_records: {report.zero_volume_records}")
    print(f"files_with_invalid_prices: {report.files_with_invalid_prices}")
    print(f"files_with_ohlc_errors: {report.files_with_ohlc_errors}")

    if report.failures:
        print("failures:")
        for failure in report.failures[:10]:
            print(f"  {failure.path}: {failure.error}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan or import Tongdaxin .day files in a directory.")
    parser.add_argument("root", type=Path, help="Root directory containing .day files.")
    parser.add_argument("--dry-run", action="store_true", help="Scan and print summary without writing database.")
    parser.add_argument("--save-vnpy", action="store_true", help="Write parsed bars into vn.py database.")
    parser.add_argument("--limit", type=int, help="Limit number of files for a sample run.")
    parser.add_argument("--report", type=Path, help="Write a JSON quality report.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.dry_run and not args.save_vnpy:
        parser.error("Choose --dry-run or --save-vnpy.")

    files = iter_day_files(args.root)
    if args.limit is not None:
        files = files[: args.limit]

    file_reports: list[FileReport] = []
    for path in files:
        try:
            bars = parse_day_file(path)
            file_reports.append(summarize_file(path, bars, args.root))
            if args.save_vnpy and bars:
                save_to_vnpy(bars)
        except Exception as exc:
            file_reports.append(
                FileReport(
                    path=str(path.relative_to(args.root)),
                    symbol=None,
                    exchange=None,
                    records=0,
                    start=None,
                    end=None,
                    zero_volume_records=0,
                    invalid_price_records=0,
                    ohlc_error_records=0,
                    error=str(exc),
                )
            )

    directory_report = build_directory_report(args.root, file_reports)
    print_summary(directory_report)

    if args.report:
        write_report(args.report, directory_report, file_reports)
        print(f"report: {args.report}")

    return 1 if directory_report.failed_files else 0


if __name__ == "__main__":
    raise SystemExit(main())
