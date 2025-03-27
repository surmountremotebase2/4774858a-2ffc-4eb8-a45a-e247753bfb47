from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Focusing on a highly liquid market
        self.tickers = ["SPY"]  # S&P 500 ETF as it's highly liquid and suitable for day trading

        # Assuming the platform or account allows for high leverage - use cautiously
        self.leverage = 5
        
        # Risk management parameters
        self.stop_loss_percent = 0.02  # 2% stop loss per trade
        self.take_profit_percent = 0.01  # 1% take profit per trade
        self.max_daily_loss_percent = 0.1  # 10% maximum daily loss threshold
        
        # Strategy parameters
        self.fast_ema_period = 5   # Fast EMA period
        self.slow_ema_period = 10  # Slow EMA period
    
    @property
    def interval(self):
        return "1min"  # High-frequency trading strategy
    
    @property
    def assets(self):
        return self.tickers
    
    @property
    def data(self):
        return []  # OHLCV data is provided automatically, no additional data needed

    def run(self, data):
        # Initialize allocation with zero
        allocation = {ticker: 0 for ticker in self.tickers}
        
        for ticker in self.tickers:
            # Extracting close prices for the ticker
            close_prices = [d[ticker]["close"] for d in datacv"]]
            
            if len(close_prices) >= self.slow_ema_period:
                # Calculate Fast and Slow EMAs
                fast_ema = EMA(ticker, data["ohlcv"], self.fast_ema_period)[-1]
                slow_ema = EMA(ticker, data["ohlcv"], self.slow_ema_period)[-1]
                
                # Trading Signals
                if fast_ema > slow_ema:  # Bullish signal
                    allocation[ticker] = 1 * self.leverage
                elif fast_ema < slow_ema:  # Bearish signal
                    allocation[ticker] = -1 * self.leverage
        
        # Consider implementing risk management checks here
        
        return TargetAllocation(allocation)