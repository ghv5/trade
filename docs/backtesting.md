# 回测流程

本仓库已经将通达信 A 股日线导入 vn.py SQLite：

- 数据库：`/Users/mac/.vntrader/database.db`
- 日线记录：`18101272`
- 标的概览：`6112`

## 命令行回测

先激活环境：

```bash
conda activate trade-vnpy
```

运行最小双均线策略：

```bash
python scripts/run_backtest.py --vt-symbol 600000.SSE --start 2020-01-01 --end 2026-07-16
```

运行尾盘动量/反转策略：

```bash
python scripts/run_backtest.py \
  --strategy tail-momentum-reversal \
  --vt-symbol 600000.SSE \
  --start 2020-01-01 \
  --end 2026-07-16
```

输出 JSON 报告：

```bash
python scripts/run_backtest.py \
  --vt-symbol 000001.SZSE \
  --start 2020-01-01 \
  --end 2026-07-16 \
  --output reports/backtest_000001_double_ma.json
```

`reports/` 默认不提交 Git。

## 策略

当前仓库策略：

- `strategies/double_ma_a_share.py`：A 股日线双均线策略，只做多，不做空。
- `strategies/tail_momentum_reversal.py`：尾盘动量/反转策略的日线模拟版本，只做多，不做空。

双均线默认参数：

- `fast_window=10`
- `slow_window=20`
- `fixed_size=100`

尾盘动量/反转默认参数：

- `trend_window=26`：趋势过滤，收盘价在 26 日均线上方才考虑买入。
- `momentum_window=20`：向上突破过去 20 日高点视为动量触发。
- `reversal_window=5`：5 日回调后，如果尾盘收在日内上半区并重新转强，视为反转触发。
- `min_tail_position=0.65`：收盘价至少处在当日振幅上方 65%。
- `min_pullback=0.03`：反转触发要求最近 5 日至少回调 3%。
- `stop_loss=0.06`：6% 止损。
- `take_profit=0.12`：12% 止盈。
- `max_holding_days=10`：最多持有 10 根日线。

这个策略目前只使用日线数据近似尾盘状态，适合验证研究框架；如果后续导入 1 分钟或 5 分钟数据，再把 14:30 之后的真实分时确认接入。

## vn.py 图形界面

```bash
conda activate trade-vnpy
python scripts/launch_vntrader.py
```

打开后检查：

- DataManager 是否能看到本地日线数据。
- CTA Backtester 是否能选择 `600000.SSE`、`000001.SZSE` 等标的。
- 回测参数的手续费、滑点、合约乘数、最小价格变动是否符合你的假设。

如果只想验证 GUI 依赖是否完整，不打开窗口：

```bash
python scripts/launch_vntrader.py --check
```

## 注意

当前策略只用于验证数据和回测链路，不代表可交易策略。下一步应增加股票池筛选、复权处理、停牌处理、涨跌停约束和交易成本建模。
