#!/usr/bin/env python3
"""Launch the vn.py GUI with local workflow apps enabled."""

from __future__ import annotations

import argparse


def build_main_window():
    from vnpy.event import EventEngine
    from vnpy.trader.engine import MainEngine
    from vnpy.trader.ui import MainWindow, create_qapp
    from vnpy_ctabacktester import CtaBacktesterApp
    from vnpy_ctastrategy import CtaStrategyApp
    from vnpy_datamanager import DataManagerApp

    qapp = create_qapp("Trade vn.py")
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_app(DataManagerApp)
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(CtaBacktesterApp)

    main_window = MainWindow(main_engine, event_engine)
    return qapp, main_window


def check_environment() -> None:
    import talib
    import vnpy
    import vnpy_ctabacktester
    import vnpy_ctastrategy
    import vnpy_datamanager
    import vnpy_sqlite

    print(f"vnpy: {vnpy.__version__}")
    print(f"TA-Lib: {talib.__version__}")
    print(f"vnpy_ctastrategy: {vnpy_ctastrategy.__version__}")
    print(f"vnpy_ctabacktester: {vnpy_ctabacktester.__version__}")
    print(f"vnpy_datamanager: {vnpy_datamanager.__version__}")
    print(f"vnpy_sqlite: {vnpy_sqlite.__version__}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch vn.py GUI with DataManager and CTA apps.")
    parser.add_argument("--check", action="store_true", help="Only verify imports and versions; do not open GUI.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.check:
        check_environment()
        return 0

    qapp, main_window = build_main_window()
    main_window.showMaximized()
    return qapp.exec()


if __name__ == "__main__":
    raise SystemExit(main())
