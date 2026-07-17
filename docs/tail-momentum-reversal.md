# 尾盘动量/反转策略

当前实现是日线回测版本，用收盘附近状态近似尾盘确认。它不是高频策略，也不使用 Level-2、tick 或盘口队列信息。

## 交易假设

- 只做 A 股股票，只做多，不做空。
- 使用日线数据验证思路。
- 收盘价处于当日振幅上半区，代表尾盘没有走坏。
- 回测中的成交价使用日线收盘价近似尾盘成交价。

## 入场逻辑

先满足趋势过滤：

- 收盘价高于 26 日均线。

动量触发：

- 收盘价突破过去 20 日高点。
- 收盘位置在当日振幅上方 65% 以上。

反转触发：

- 最近 5 日回调至少 3%。
- 当日收盘高于前一日收盘。
- 收盘位置在当日振幅上方 65% 以上。

## 出场逻辑

满足任一条件即卖出：

- 跌破入场价 6%。
- 上涨达到入场价 12%。
- 收盘价跌破 26 日均线。
- 持有达到 10 根日线。

## 回测命令

```bash
conda activate trade-vnpy
python scripts/run_backtest.py \
  --strategy tail-momentum-reversal \
  --vt-symbol 600000.SSE \
  --start 2020-01-01 \
  --end 2026-07-16
```

输出报告：

```bash
python scripts/run_backtest.py \
  --strategy tail-momentum-reversal \
  --vt-symbol 000001.SZSE \
  --start 2020-01-01 \
  --end 2026-07-16 \
  --output reports/backtest_000001_tail_mr.json
```

## 后续增强

- 导入 1 分钟或 5 分钟数据后，用 14:30 之后价格结构替代日线收盘近似。
- 增加涨跌停不可成交约束。
- 增加停牌、退市和 ST 过滤。
- 加入市场指数和行业强度过滤。
- 对参数做 walk-forward，而不是只看单段历史收益。
