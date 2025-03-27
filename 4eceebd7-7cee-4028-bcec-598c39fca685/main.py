# Full Script for Surmount AI: Multi-Asset Day Trading Bot (Robinhood-connected)
# Target: Automate trading across Stocks, Options, Crypto, and Forex
# Uses: Breakout, Mean Reversion, RSI/VWAP/EMA logic, stop-loss, trailing profits

from surmount import Strategy, Option, Stock, Crypto, Forex, technical_indicators as ti

class MultiAssetDayTrader(Strategy):
    def __init__(self):
        self.stocks = ["AAPL", "TSLA", "AMD"]
        self.cryptos = ["BTC-USD", "ETH-USD"]
        self.forex = ["EURUSD", "GBPUSD"]
        self.max_risk_pct = 0.03  # 3% of account per trade
        self.trailing_trigger_pct = 0.02  # Trail stop when up 2%
        self.trailing_stop_pct = 0.01  # Trail by 1%

    def on_data(self, asset):
        price = asset.price
        rsi = ti.rsi(asset, 14)
        vwap = ti.vwap(asset)
        ema9 = ti.ema(asset, 9)
        ema20 = ti.ema(asset, 20)

        is_trending_up = ema9 > ema20 and price > vwap
        is_momentum_buy = rsi < 70 and is_trending_up
        is_mean_reversion_buy = rsi < 25 and price < ema9
        is_mean_reversion_sell = rsi > 75 and price > ema9

        # Entry logic
        if not asset.has_position:
            if is_momentum_buy:
                self.enter_long(asset, "Momentum")
            elif is_mean_reversion_buy:
                self.enter_long(asset, "MeanReversion")
            elif is_mean_reversion_sell:
                self.enter_short(asset, "MeanReversion")

        # Exit logic
        if asset.has_position:
            entry_price = asset.entry_price
            unrealized_pct = (price - entry_price) / entry_price if asset.is_long else (entry_price - price) / entry_price

            # Trailing stop profit logic
            if unrealized_pct > self.trailing_trigger_pct:
                stop_trigger = entry_price * (1 + self.trailing_stop_pct) if asset.is_long else entry_price * (1 - self.trailing_stop_pct)
                if (asset.is_long and price < stop_trigger) or (asset.is_short and price > stop_trigger):
                    self.exit_position(asset, reason="Trailing Stop Hit")

            # Stop loss
            if unrealized_pct < -self.max_risk_pct:
                self.exit_position(asset, reason="Max Loss")

    def assets(self):
        return [Stock(ticker) for ticker in self.stocks] + \
               [Crypto(ticker) for ticker in self.cryptos] + \
               [Forex(pair) for pair in self.forex]
e