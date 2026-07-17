from vnpy.trader.constant import Direction, Offset
from vnpy_ctastrategy import ArrayManager, BarData, BarGenerator, CtaTemplate, OrderData, StopOrder, TickData, TradeData


class TailMomentumReversalStrategy(CtaTemplate):
    """Daily-bar simulation of end-of-day momentum/reversal entries for A shares."""

    author = "trade-workspace"

    trend_window = 26
    momentum_window = 20
    reversal_window = 5
    min_tail_position = 0.65
    min_pullback = 0.03
    stop_loss = 0.06
    take_profit = 0.12
    max_holding_days = 10
    fixed_size = 100

    trend_ma = 0.0
    tail_position = 0.0
    pullback_return = 0.0
    entry_price = 0.0
    holding_days = 0

    parameters = [
        "trend_window",
        "momentum_window",
        "reversal_window",
        "min_tail_position",
        "min_pullback",
        "stop_loss",
        "take_profit",
        "max_holding_days",
        "fixed_size",
    ]
    variables = ["trend_ma", "tail_position", "pullback_return", "entry_price", "holding_days"]

    def on_init(self) -> None:
        self.write_log("策略初始化")
        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager(size=max(self.trend_window, self.momentum_window, self.reversal_window) + 20)

    def on_start(self) -> None:
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self) -> None:
        self.write_log("策略停止")
        self.put_event()

    def on_tick(self, tick: TickData) -> None:
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        close_array = self.am.close_array
        high_array = self.am.high_array
        low_array = self.am.low_array

        self.trend_ma = self.am.sma(self.trend_window)
        day_range = bar.high_price - bar.low_price
        self.tail_position = (bar.close_price - bar.low_price) / day_range if day_range > 0 else 0.5
        self.pullback_return = bar.close_price / close_array[-self.reversal_window] - 1

        previous_high = max(high_array[-self.momentum_window - 1 : -1])
        uptrend = bar.close_price > self.trend_ma
        tail_strong = self.tail_position >= self.min_tail_position
        momentum_signal = uptrend and tail_strong and bar.close_price > previous_high
        reversal_signal = (
            uptrend
            and tail_strong
            and self.pullback_return <= -self.min_pullback
            and bar.close_price > close_array[-2]
        )

        if self.pos == 0:
            self.holding_days = 0
            if momentum_signal or reversal_signal:
                self.buy(bar.close_price, self.fixed_size)
        else:
            self.holding_days += 1
            exit_signal = (
                bar.close_price <= self.entry_price * (1 - self.stop_loss)
                or bar.close_price >= self.entry_price * (1 + self.take_profit)
                or bar.close_price < self.trend_ma
                or self.holding_days >= self.max_holding_days
            )
            if exit_signal:
                self.sell(bar.close_price, abs(self.pos))

        self.put_event()

    def on_order(self, order: OrderData) -> None:
        pass

    def on_trade(self, trade: TradeData) -> None:
        if trade.direction == Direction.LONG and trade.offset == Offset.OPEN:
            self.entry_price = trade.price
            self.holding_days = 0
        elif trade.direction == Direction.SHORT and trade.offset == Offset.CLOSE:
            self.entry_price = 0
            self.holding_days = 0
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder) -> None:
        pass
