import technical_indicators as ti

def initialize(context):
    context.stocks = ["AAPL", "TSLA", "AMD"]
    context.cryptos = ["BTC-USD", "ETH-USD"]
    context.forex = ["EURUSD", "GBPUSD"]
    context.max_risk_pct = 0.03
    context.trailing_trigger_pct = 0.02
    context.trailing_stop_pct = 0.01

def handle_data(context, data):
    for symbol in context.stocks + context.cryptos + context.forex:
        if symbol not in data:
            continue

        price = data[symbol]["price"]
        rsi = ti.rsi(symbol, 14)
        vwap = ti.vwap(symbol)
        ema9 = ti.ema(symbol, 9)
        ema20 = ti.ema(symbol, 20)

        has_position = context.portfolio.positions.get(symbol, 0) != 0
        is_trending_up = ema9 > ema20 and price > vwap
        is_momentum_buy = rsi < 70 and is_trending_up
        is_mean_reversion_buy = rsi < 25 and price < ema9
        is_mean_reversion_sell = rsi > 75 and price > ema9

        # Entry logic
        if not has_position:
            if is_momentum_buy or is_mean_reversion_buy:
                context.order(symbol, 1)  # long
            elif is_mean_reversion_sell:
                context.order(symbol, -1)  # short

        # Exit logic
        position = context.portfolio.positions.get(symbol, 0)
        if position != 0:
            entry_price = context.portfolio.entry_price.get(symbol, price)
            pnl_pct = (price - entry_price) / entry_price if position > 0 else (entry_price - price) / entry_price

            if pnl_pct > context.trailing_trigger_pct:
                stop_price = entry_price * (1 + context.trailing_stop_pct) if position > 0 else entry_price * (1 - context.trailing_stop_pct)
                if (position > 0 and price < stop_price) or (position < 0 and price > stop_price):
                    context.order(symbol, 0)  # exit

            if pnl_pct < -context.max_risk_pct:
                context.order(symbol, 0)  # stop out