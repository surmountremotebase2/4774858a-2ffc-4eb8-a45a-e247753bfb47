from surmount.base_class import Strategy

class TradingStrategy(Strategy):
    def initialize(self, context):
        context.assets = ["AAPL", "TSLA", "AMD", "BTC-USD", "ETH-USD", "EURUSD", "GBPUSD"]
        context.max_risk_pct = 0.03
        context.trailing_trigger_pct = 0.02
        context.trailing_stop_pct = 0.01

    def handle_data(self, context, data):
        for symbol in context.assets:
            if symbol not in data:
                continue

            price = data[symbol]["price"]
            rsi = data[symbol].get("rsi_14")
            ema9 = data[symbol].get("ema_9")
            ema20 = data[symbol].get("ema_20")
            vwap = data[symbol].get("vwap")

            if None in [price, rsi, ema9, ema20, vwap]:
                continue  # skip if any data is missing

            has_position = context.portfolio.positions.get(symbol, 0) != 0
            is_trending_up = ema9 > ema20 and price > vwap
            is_momentum_buy = rsi < 70 and is_trending_up
            is_mean_reversion_buy = rsi < 25 and price < ema9
            is_mean_reversion_sell = rsi > 75 and price > ema9

            # Entry logic
            if not has_position:
                if is_momentum_buy or is_mean_reversion_buy:
                    context.order(symbol, 1)  # go long
                elif is_mean_reversion_sell:
                    context.order(symbol, -1)  # go short

            # Exit logic
            position = context.portfolio.positions.get(symbol, 0)
            if position != 0:
                entry_price = context.portfolio.entry_price.get(symbol, price)
                pnl_pct = (price - entry_price) / entry_price if position > 0 else (entry_price - price) / entry_price

                if pnl_pct > context.trailing_trigger_pct:
                    stop_price = entry_price * (1 + context.trailing_stop_pct) if position > 0 else entry_price * (1 - context.trailing_stop_pct)
                    if (position > 0 and price < stop_price) or (position < 0 and price > stop_price):
                        context.order(symbol, 0)

                if pnl_pct < -context.max_risk_pct:
                    context.order(symbol, 0)