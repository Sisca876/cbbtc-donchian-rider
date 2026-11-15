"""DonchianRider: a Donchian-channel breakout bot for the make.fun BTC race.

Strategy (long only, one position, all-in):
  Entry: the close breaks above the highest HIGH of the prior 40 bars, on TWO
      consecutive bars (confirmation). A single-bar poke above the channel is
      ignored: on the dev window it whipsawed and lost, while the confirmed
      breakout caught the real trend moves.
  Exit: a trailing stop of 5.0 x ATR(14) (Wilder) below the highest HIGH seen
      since entry. No take-profit: the stop lets a trend run and cuts it when
      momentum fades. The stop also serves as the hard risk control.

Everything is computed from the bars the harness sends, in wire units (price
scale 5); no clock, no network, no randomness, so two runs on the same data
produce identical orders.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
N_ENTRY = 40          # Donchian lookback: prior bars whose high must be broken
ATR_N = 14            # ATR period (Wilder smoothing)
ATR_MULT = 5.0        # trailing stop distance, in ATRs below the highest high
CONFIRM = 2           # consecutive breakout closes required to enter
MAX_SLIPPAGE_BPS = 100


class DonchianRider:
    def __init__(self):
        self.highs = []       # bar highs, wire units, in order
        self.closes = []      # bar closes, wire units, in order
        self.prev_close = None
        self.tr_sum = 0       # sum of true ranges while seeding ATR
        self.atr = None       # Wilder ATR, wire units (float)
        self.confirm = 0      # consecutive breakout closes
        self.in_position = False
        self.hmark = 0        # highest high since entry, wire units

    def _update_indicators(self, high, low, close):
        if self.prev_close is None:
            tr = high - low
        else:
            tr = max(high - low, abs(high - self.prev_close), abs(low - self.prev_close))
        self.prev_close = close
        self.highs.append(high)
        self.closes.append(close)
        n_bars = len(self.closes)
        if n_bars < ATR_N:
            self.tr_sum += tr
        elif n_bars == ATR_N:
            self.tr_sum += tr
            self.atr = self.tr_sum / ATR_N
        else:
            self.atr = (self.atr * (ATR_N - 1) + tr) / ATR_N

    def _breakout(self):
        """True when the latest close exceeds the highest high of the N prior bars."""
        if len(self.highs) <= N_ENTRY:
            return False
        prior_high = max(self.highs[-N_ENTRY - 1:-1])
        return self.closes[-1] > prior_high

    def on_batch(self, state, batch):
        if state.warming_up:
            return []
        bar = state.latest.get(SYMBOL)
        if bar is None:
            return []
        high = int(bar["h"])
        low = int(bar["l"])
        close = int(bar["c"])
        self._update_indicators(high, low, close)
        if self.atr is None or len(self.closes) <= N_ENTRY:
            return []

        # Reconcile with the account the harness reports: if the entry buy was
        # rejected (e.g. a gap through max_slippage), drop back to flat instead
        # of tracking a position that never filled; if a sell was rejected,
        # re-adopt the holding so the stop is retried next bar.
        holding = state.positions.get(SYMBOL)
        has_holding = holding is not None and holding.qty > 0
        if self.in_position and not has_holding:
            self.in_position = False
            self.confirm = 0
        elif not self.in_position and has_holding:
            self.in_position = True
            self.confirm = 0
            self.hmark = high

        if not self.in_position:
            if self._breakout():
                self.confirm += 1
                if self.confirm >= CONFIRM:
                    self.confirm = 0
                    self.in_position = True
                    self.hmark = high
                    return [{
                        "side": "buy",
                        "symbol": SYMBOL,
                        "notional_quote_units": state.cash,
                        "max_slippage_bps": MAX_SLIPPAGE_BPS,
                    }]
            else:
                self.confirm = 0
            return []

        # In position: trail the stop from the highest high since entry.
        if high > self.hmark:
            self.hmark = high
        stop = self.hmark - ATR_MULT * self.atr
        if close < stop:
            self.in_position = False
            self.confirm = 0
            holding = state.positions.get(SYMBOL)
            if holding is None or holding.qty <= 0:
                return []
            return [{
                "side": "sell",
                "symbol": SYMBOL,
                "qty": holding.qty,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }]
        return []


def main():
    bot = DonchianRider()
    makefun_bars.run(bot.on_batch)


if __name__ == "__main__":
    main()
