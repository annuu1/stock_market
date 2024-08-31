import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Fetch historical data for Bank Nifty on a 1-hour interval
symbol = "^NSEBANK"
data = yf.download(symbol, start="2023-01-01", end="2023-12-31", interval="1h")

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
    def is_bullish(self):
        return self.close > self.open_price

    @property
    def is_bearish(self):
        return self.close < self.open_price

def is_legin_candle(candle):
    # Consider any candle with significant movement as a leg-in candle
    return candle.body_size > candle.candle_range * 0.5

def is_base_candle(candle):
    # Base candle is a candle with smaller body size, showing consolidation
    return candle.body_size < candle.candle_range * 0.5

def is_legout_candle(candle):
    # Consider a leg-out candle as one that shows a strong directional move (bullish)
    return candle.body_size > candle.candle_range * 0.7

def detect_demand_zones(candles):
    demand_zones = []
    i = 0
    while i < len(candles) - 4:  # Ensure there are enough candles after legin for validation
        if is_legin_candle(candles[i]):
            base_candles = []
            j = i + 1
            while j < len(candles) and len(base_candles) < 4 and is_base_candle(candles[j]):
                base_candles.append(candles[j])
                j += 1

            legout_candles = []
            while j < len(candles) and is_legout_candle(candles[j]):
                legout_candles.append(candles[j])
                j += 1

            if len(legout_candles) > 1 and base_candles:
                # We found significant leg-out move with more than 1 bullish candle
                demand_zones.append((i, j, base_candles))
            i = j  # Skip to the next possible pattern after the legout candle
        else:
            i += 1

    return demand_zones

def check_zone_tested_and_target(demand_zone, candles, start_index):
    base_candles = demand_zone[2]

    # Ensure base_candles is not empty before calculating highest_high and lowest_low
    if base_candles:
        highest_high = max(candle.high for candle in base_candles)
        lowest_low = min(candle.low for candle in base_candles)
        
        # Determine the target for a 1:2 risk-reward ratio
        risk = highest_high - lowest_low
        target_price = highest_high + 2 * risk

        for k in range(start_index, len(candles)):
            if candles[k].low <= highest_high and candles[k].high >= lowest_low:
                # Check if the price hits the 1:2 target after entering the zone
                for m in range(k, len(candles)):
                    if candles[m].high >= target_price:
                        return 'pink'  # Zone achieved 1:2 target
                    if candles[m].low < lowest_low:
                        return 'blue'  # Zone was broken before achieving target
                break
        
        return 'green'  # Zone has not been tested
    return None  # No valid zone found

# Convert fetched data to Candle objects
candles = []
for idx, row in data.iterrows():
    candles.append(Candle(row['Open'], row['High'], row['Low'], row['Close']))

# Detect demand zones
demand_zones = detect_demand_zones(candles)

# Track the number of fresh and tested zones
fresh_zones = 0
tested_zones = 0
target_zones = 0

# Prepare the plot using Plotly
fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.03)
candlestick = go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name='Candles'
)
fig.add_trace(candlestick)

# Add horizontal lines for demand zones
for dz in demand_zones:
    base_candles = dz[2]
    
    # Find the highest high and lowest low of the base candles
    color = check_zone_tested_and_target(dz, candles, dz[1] + 1)
    
    if color:
        highest_high = max(candle.high for candle in base_candles)
        lowest_low = min(candle.low for candle in base_candles)
    
        if color == 'green':
            fresh_zones += 1
        elif color == 'blue':
            tested_zones += 1
        elif color == 'pink':
            target_zones += 1
        
        # Add horizontal lines representing demand zones
        fig.add_shape(
            type="rect",
            x0=data.index[dz[0]],
            x1=data.index[-1],
            y0=lowest_low,
            y1=highest_high,
            line=dict(color=color),
            fillcolor=color,
            opacity=0.2,
        )

# Update the layout
fig.update_layout(
    title="Bank Nifty with Detected Demand Zones",
    yaxis_title="Price",
    xaxis_title="Date",
    showlegend=False,
    xaxis_rangeslider_visible=False
)

# Show the plot
fig.show()

# Print the number of fresh, tested, and target zones
print(f"Number of fresh zones: {fresh_zones}")
print(f"Number of tested zones: {tested_zones}")
print(f"Number of zones that met 1:2 target: {target_zones}")
