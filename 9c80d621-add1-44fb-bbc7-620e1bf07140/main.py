from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MACD, SMA
from surmount.data import SocialSentiment, InsiderTrading
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Focus on high volatility stocks and major indices for broader market movement.
        self.tickers = ["SPY", "QQQ", "TSLA", "AMD", "AAPL"]
        # Including social sentiment and insider trading data to gauge momentum and insider activities.
        self.data_list = [SocialSentiment(ticker) for ticker in self.tickers] + [InsiderTrading(ticker) for ticker in self.tickers]

    @property
    def interval(self):
        # High-frequency day trading strategy.
        return "1min"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            rsi = RSI(ticker, data["ohlcv"], 14)[-1]  # Latest RSI value
            social_sentiment = data[("social_sentiment", ticker)][-1]['twitterSentiment'] if data[("social_sentiment", ticker)] else None
            insider_actions = data[("insider_trading", ticker)]
            recent_sales = any(x['transactionType'] == 'Sale' for x in insider_actions[-3:]) if insider_actions else False

            # High-risk, high-return conditions
            if rsi < 30 and social_sentiment and social_sentiment > 0.5 and not recent_sales:
                # Indicative of a potential bullish turnaround; absence of recent insider sales might indicate insider confidence.
                allocation_dict[ticker] = 0.2  # Aggressive allocation
            elif rsi > 70:
                # Overbought conditions, potential short/sell signal.
                allocation_dict[ticker] = 0  # Avoid or consider shorting if strategy allows
            else:
                allocation_dict[ticker] = 0.1  # Default/base allocation for diversification

        return TargetAllocation(allocation_dict)