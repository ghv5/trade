from scripts.launch_vntrader import build_parser


def test_launch_vntrader_check_flag():
    args = build_parser().parse_args(["--check"])

    assert args.check is True
