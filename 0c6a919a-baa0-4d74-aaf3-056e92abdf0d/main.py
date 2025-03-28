# Import necessary components from the Surmount package
from surmount.base_class import Strategy, TargetAllocation
from surmount.data import InsiderTrading, SocialSentiment
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the blue-chip stocks of interest (example tickers)
        self.tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
        
        # Initialize the data sources required for the strategy
        self.data_list = [SocialSentiment(ticker) for ticker in self.tickers]
        self.data_list += [InsiderTrading(ticker) for ticker in self.tickers]

    @property
    def interval(self):
        # Use daily data for this strategy
        return "1day"

    @property
    def assets(self):
        # Define the assets of interest
        return self.tickers

    @property
    def data(self):
        # Return the initialized data sources
        return self.data_list

    def run(self, data):
        # Initialize an empty allocation dictionary
        allocation_dict = {}
        
        # Iterate through the tickers to determine allocation
        for ticker in self.tickers:
            sentiment_key = ("social_sentiment", ticker)
            insider_trading_key = ("insider_trading", ticker)
            
            allocation = 0.25 # Default to an even distribution initially
            
            # Adjust based on social sentiment (positive sentiment increases allocation)
            if sentiment_key in data and data[sentiment_key]:
                sentiment = data[sentiment_key][-1]["twitterSentiment"]
                if sentiment > 0.5: # Assume a sentiment value > 0.5 is positive
                    allocation += 0.05
                else:
                    allocation -= 0.05
            
            # Adjust based on recent insider trading (sales reduce the allocation)
            if insider_trading_key in data and data[insider_trading_key]:
                recent_insider_activity = data[insider_trading_key][-1]["transactionType"]
                if "Sale" in recent_insider_activity:
                    allocation -= 0.1
            
            # Ensure allocation is within 0 to 1 bounds
            allocation_dict[ticker] = max(0, min(1, allocation))
        
        # Log the final allocations for transparency
        log(f"Final Allocations: {allocation_dict}")
        
        return TargetAllocation(allocation_dict)