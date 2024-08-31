import yfinance as yf
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt

# Fetch historical data for Bank Nifty
symbol = "^NSEBANK"
data = yf.download(symbol, start="2023-01-01", end="2023-12-31", interval="1d")

# Convert data to a list of Candle objects
class Candle:
    def __init__(self, open_price, high, low, close):
        self.open_price = open_price
        self.high = high
        self.low = low
        self.close = close

    @property
    def body_size(self):
        return abs(self.close - self.open_price)

    @property
    def candle_range(self):
        return self.high - self.low

    @property
    def body_percentage(self):
        if self.candle_range == 0:
            return 0
        return (self.body_size / self.candle_range) * 100

    @property
    def is_bullish(self):
        return self.close > self.open_price

def is_legin_candle(candle):
    return candle.body_percentage > 60

def is_base_candle(candle):
    return candle.body_percentage < 45

def is_legout_candle(candle):
    return candle.body_percentage > 60

def detect_demand_zones(candles):
    demand_zones = []
    i = 0
    while i < len(candles) - 2:
        if is_legin_candle(candles[i]):
            base_candles = []
            j = i + 1
            while j < len(candles) and len(base_candles) < 5 and is_base_candle(candles[j]):
                base_candles.append(candles[j])
                j += 1

            if j < len(candles) and is_legout_candle(candles[j]):
                legin_candle = candles[i]
                legout_candle = candles[j]

                # Check if it's a demand zone
                if base_candles and (legout_candle.is_bullish and
                                     legout_candle.close > legin_candle.high and
                                     legout_candle.close > max(candle.high for candle in base_candles)):
                    demand_zones.append((i, j))  # Store the indices of the legin and legout candles
            i = j  # Skip to the next possible pattern after the legout candle
        else:
            i += 1

    return demand_zones

# Convert fetched data to Candle objects
candles = []
for idx, row in data.iterrows():
    candles.append(Candle(row['Open'], row['High'], row['Low'], row['Close']))

# Detect demand zones
demand_zones = detect_demand_zones(candles)

# Display detected demand zones
for dz in demand_zones:
    legin_index = dz[0]
    legout_index = dz[1]
    print(f"Demand zone detected from {data.index[legin_index]} to {data.index[legout_index]}")

# Plotting the data using mplfinance and marking the demand zones
demand_zone_lines = []
for dz in demand_zones:
    legin_index = dz[0]
    legout_index = dz[1]
    legin_high = data.iloc[legin_index].High
    legout_high = data.iloc[legout_index].High
    legout_low = data.iloc[legout_index].Low
    # Add horizontal lines to mark the demand zones
    demand_zone_lines.append(mpf.make_addplot([legin_high] * len(data), color='green', linestyle='--'))
    demand_zone_lines.append(mpf.make_addplot([legout_low] * len(data), color='green', linestyle='--'))

# Configure the plot
mpf.plot(data, type='candle', style='charles',
         addplot=demand_zone_lines,
         title='Bank Nifty with Detected Demand Zones',
         ylabel='Price',
         volume=True,
         show_nontrading=True)

plt.show()
