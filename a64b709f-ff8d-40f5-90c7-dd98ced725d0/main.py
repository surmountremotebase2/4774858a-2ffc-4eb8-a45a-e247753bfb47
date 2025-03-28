class TradingStrategy:
    def initialize(self):
        # Your custom universe of tickers
        self.set_universe(["MARA", "RIOT", "SOXL", "PLTR", "IONQ", "TQQQ", "TSLA", "NVDA", "LABU"])
        
        # Set trading timeframe and position size
        self.set_timeframe("5m")
        self.set_position_size(percent=0.25)

    def on_data(self, data):
        for symbol in data:
            price = data[symbol].current_price
            ema_9 = data[symbol].ema(9)
            rsi_14 = data[symbol].rsi(14)

            # Entry logic
            if not self.has_position(symbol) and price > ema_9 and 50 < rsi_14 < 70:
                self.enter_position(symbol, direction="long")

            # Exit logic
            if self.has_position(symbol):
                entry_price = self.get_entry_price(symbol)
                gain_percent = (price - entry_price) / entry_price * 100

                if gain_percent >= 7 or rsi_14 > 75 or gain_percent <= -3:
                    self.exit_position(symbol)