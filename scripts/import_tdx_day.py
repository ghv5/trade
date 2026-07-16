#!/usr/bin/env python3
"""Import Tongdaxin .day daily bars into vn.py."""

from __future__ import annotations

import argparse
import struct
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


RECORD_SIZE = 32
TDX_DAY_STRUCT = struct.Struct("<IIIIIfII")
EXCHANGE_BY_PREFIX = {
    "sh": "SSE",
    "sz": "SZSE",
}


@dataclass(frozen=True)
class TdxDailyBar:
    symbol: str
    exchange: str
    datetime: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    turnover: float
    open_interest: float = 0


def infer_symbol_exchange(path: Path) -> tuple[str, str]:
    stem = path.stem.lower()
    prefix = stem[:2]
    exchange = EXCHANGE_BY_PREFIX.get(prefix)
    if not exchange or len(stem) < 8:
        raise ValueError(
            "Cannot infer symbol/exchange from filename. "
            "Use --symbol and --exchange explicitly."
        )
    return stem[2:], exchange


def parse_price(raw_value: int) -> float:
    return raw_value / 100


def parse_record(payload: bytes, symbol: str, exchange: str) -> TdxDailyBar:
    if len(payload) != RECORD_SIZE:
        raise ValueError(f"TDX .day record must be {RECORD_SIZE} bytes")

    date_raw, open_raw, high_raw, low_raw, close_raw, turnover, volume, _ = TDX_DAY_STRUCT.unpack(payload)
    trade_date = datetime.strptime(str(date_raw), "%Y%m%d")

    return TdxDailyBar(
        symbol=symbol,
        exchange=exchange,
        datetime=trade_date,
        open_price=parse_price(open_raw),
        high_price=parse_price(high_raw),
        low_price=parse_price(low_raw),
        close_price=parse_price(close_raw),
        volume=volume,
        turnover=float(turnover),
    )


def parse_day_file(path: Path, symbol: str | None = None, exchange: str | None = None) -> list[TdxDailyBar]:
    if not path.exists():
        raise FileNotFoundError(path)

    inferred_symbol, inferred_exchange = infer_symbol_exchange(path) if not symbol or not exchange else (symbol, exchange)
    symbol = symbol or inferred_symbol
    exchange = exchange or inferred_exchange

    content = path.read_bytes()
    if len(content) % RECORD_SIZE != 0:
        raise ValueError(f"{path} size is not aligned to {RECORD_SIZE}-byte TDX records")

    bars = [
        parse_record(content[index : index + RECORD_SIZE], symbol, exchange)
        for index in range(0, len(content), RECORD_SIZE)
    ]
    return sorted(bars, key=lambda bar: bar.datetime)


def to_vnpy_bars(bars: Iterable[TdxDailyBar]):
    from vnpy.trader.constant import Exchange, Interval
    from vnpy.trader.object import BarData

    return [
        BarData(
            symbol=bar.symbol,
            exchange=Exchange(bar.exchange),
            datetime=bar.datetime,
            interval=Interval.DAILY,
            volume=bar.volume,
            turnover=bar.turnover,
            open_interest=bar.open_interest,
            open_price=bar.open_price,
            high_price=bar.high_price,
            low_price=bar.low_price,
            close_price=bar.close_price,
            gateway_name="TDX",
        )
        for bar in bars
    ]


def save_to_vnpy(bars: list[TdxDailyBar]) -> None:
    from vnpy.trader.database import get_database

    database = get_database()
    database.save_bar_data(to_vnpy_bars(bars))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import Tongdaxin .day bars into vn.py database.")
    parser.add_argument("path", type=Path, help="Path to a Tongdaxin .day file.")
    parser.add_argument("--symbol", help="Security symbol, for example 600000.")
    parser.add_argument("--exchange", choices=["SSE", "SZSE"], help="vn.py exchange code.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and print summary without writing database.")
    parser.add_argument("--save-vnpy", action="store_true", help="Write parsed bars into vn.py database.")
    return parser


def print_summary(path: Path, bars: list[TdxDailyBar]) -> None:
    if not bars:
        print(f"{path}: no records")
        return

    first = bars[0]
    last = bars[-1]
    print(f"file: {path}")
    print(f"symbol: {first.symbol}.{first.exchange}")
    print(f"records: {len(bars)}")
    print(f"range: {first.datetime:%Y-%m-%d} -> {last.datetime:%Y-%m-%d}")
    print(
        "last: "
        f"open={last.open_price} high={last.high_price} "
        f"low={last.low_price} close={last.close_price} volume={last.volume}"
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.dry_run and not args.save_vnpy:
        parser.error("Choose --dry-run or --save-vnpy.")

    bars = parse_day_file(args.path, args.symbol, args.exchange)
    print_summary(args.path, bars)

    if args.save_vnpy:
        save_to_vnpy(bars)
        print(f"saved: {len(bars)} bars")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
