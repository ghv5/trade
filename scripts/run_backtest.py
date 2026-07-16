#!/usr/bin/env python3
"""Run a minimal vn.py CTA backtest against the local SQLite database."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_SETTING = {
    "fast_window": 10,
    "slow_window": 20,
    "fixed_size": 100,
}


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def normalize_statistics(statistics: dict[str, Any]) -> dict[str, Any]:
    normalized = {}
    for key, value in statistics.items():
        if hasattr(value, "item"):
            value = value.item()
        normalized[key] = value
    return normalized


def run_backtest(args: argparse.Namespace) -> dict[str, Any]:
    from vnpy.trader.constant import Interval
    from vnpy_ctastrategy.backtesting import BacktestingEngine

    from strategies.double_ma_a_share import DoubleMaAShareStrategy

    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol=args.vt_symbol,
        interval=Interval.DAILY,
        start=parse_date(args.start),
        end=parse_date(args.end),
        rate=args.rate,
        slippage=args.slippage,
        size=args.size,
        pricetick=args.pricetick,
        capital=args.capital,
    )

    setting = {
        "fast_window": args.fast_window,
        "slow_window": args.slow_window,
        "fixed_size": args.fixed_size,
    }
    engine.add_strategy(DoubleMaAShareStrategy, setting)
    engine.load_data()
    engine.run_backtesting()
    engine.calculate_result()
    statistics = normalize_statistics(engine.calculate_statistics(output=False))

    return {
        "vt_symbol": args.vt_symbol,
        "start": args.start,
        "end": args.end,
        "setting": setting,
        "statistics": statistics,
    }


def print_summary(result: dict[str, Any]) -> None:
    statistics = result["statistics"]
    keys = [
        "start_date",
        "end_date",
        "total_days",
        "total_trade_count",
        "total_return",
        "annual_return",
        "max_ddpercent",
        "sharpe_ratio",
        "return_drawdown_ratio",
    ]

    print(f"symbol: {result['vt_symbol']}")
    print(f"range: {result['start']} -> {result['end']}")
    print(f"setting: {result['setting']}")
    for key in keys:
        print(f"{key}: {statistics.get(key)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a minimal CTA backtest for local A-share bars.")
    parser.add_argument("--vt-symbol", default="600000.SSE", help="vn.py symbol, for example 600000.SSE.")
    parser.add_argument("--start", default="2020-01-01", help="Start date in YYYY-MM-DD.")
    parser.add_argument("--end", default="2026-07-16", help="End date in YYYY-MM-DD.")
    parser.add_argument("--fast-window", type=int, default=DEFAULT_SETTING["fast_window"])
    parser.add_argument("--slow-window", type=int, default=DEFAULT_SETTING["slow_window"])
    parser.add_argument("--fixed-size", type=int, default=DEFAULT_SETTING["fixed_size"])
    parser.add_argument("--rate", type=float, default=0.0003, help="Commission rate.")
    parser.add_argument("--slippage", type=float, default=0.01, help="Price slippage.")
    parser.add_argument("--size", type=float, default=1, help="Contract size.")
    parser.add_argument("--pricetick", type=float, default=0.01, help="Minimum price tick.")
    parser.add_argument("--capital", type=int, default=1_000_000, help="Initial capital.")
    parser.add_argument("--output", type=Path, help="Optional JSON report path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run_backtest(args)
    print_summary(result)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(f"report: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
