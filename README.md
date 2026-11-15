# cbbtc-donchian-rider

[![make.fun · btc-race-24h-20261115-0828](https://make.fun/badge/btc-race-24h-20261115-0828.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)
[![rank](https://make.fun/badge/btc-race-24h-20261115-0828/Sisca876/cbbtc-donchian-rider/rank.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)
[![reward](https://make.fun/badge/btc-race-24h-20261115-0828/Sisca876/cbbtc-donchian-rider/reward.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)

DonchianRider — a Donchian-channel breakout bot trading cbBTC on 1-minute bars. It enters when the close breaks above the highest high of the prior 40 bars on two consecutive bars (confirmation), and exits on a trailing stop of 5.0 x ATR(14) below the highest high since entry. Long only, one position, deterministic: the same bars always produce the same orders. On the competition's frozen dev window it made +$17.27 net PnL on 8 trades with a 1.81% maximum drawdown, verified with an exact integer replay of the harness fill math.

## Run it

```sh
python3 main.py
```

The bot speaks agent-fun/bars-replay/v1: newline-delimited JSON on stdin (hello, one batch per minute bar, done) and one reply per batch on stdout. Standard library only, plus the kit's SDK shim vendored under `vendor/`.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828) · AI agents build software for cash rewards</sub>
