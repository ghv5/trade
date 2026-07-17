from argparse import Namespace

from scripts.run_backtest import DEFAULT_SETTING, TAIL_MOMENTUM_REVERSAL_SETTING, build_parser, normalize_statistics, parse_date


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


def test_tail_momentum_reversal_default_setting_documents_risk_controls():
    assert TAIL_MOMENTUM_REVERSAL_SETTING["trend_window"] == 26
    assert TAIL_MOMENTUM_REVERSAL_SETTING["stop_loss"] == 0.06
    assert TAIL_MOMENTUM_REVERSAL_SETTING["take_profit"] == 0.12


def test_backtest_namespace_documents_required_arguments():
    args = Namespace(
        strategy="double-ma",
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


def test_backtest_parser_accepts_tail_momentum_reversal_strategy():
    args = build_parser().parse_args(
        [
            "--strategy",
            "tail-momentum-reversal",
            "--vt-symbol",
            "600000.SSE",
            "--min-tail-position",
            "0.7",
        ]
    )

    assert args.strategy == "tail-momentum-reversal"
    assert args.min_tail_position == 0.7
