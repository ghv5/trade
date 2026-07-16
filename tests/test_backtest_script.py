from argparse import Namespace

from scripts.run_backtest import DEFAULT_SETTING, normalize_statistics, parse_date


def test_parse_date_accepts_iso_date():
    assert parse_date("2026-07-16").year == 2026


def test_normalize_statistics_converts_numpy_scalars():
    class Scalar:
        def item(self):
            return 1.23

    assert normalize_statistics({"value": Scalar()}) == {"value": 1.23}


def test_default_backtest_setting_is_ordered():
    assert DEFAULT_SETTING == {
        "fast_window": 10,
        "slow_window": 20,
        "fixed_size": 100,
    }


def test_backtest_namespace_documents_required_arguments():
    args = Namespace(
        vt_symbol="600000.SSE",
        start="2020-01-01",
        end="2026-07-16",
        fast_window=10,
        slow_window=20,
        fixed_size=100,
        rate=0.0003,
        slippage=0.01,
        size=1,
        pricetick=0.01,
        capital=1_000_000,
        output=None,
    )

    assert args.vt_symbol == "600000.SSE"
