import yfinance as yf
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt

# -----------------------------
# Data Fetching and Preparation
# -----------------------------

# Fetch historical data for Bank Nifty using yfinance
symbol = "^NSEBANK"
start_date = "2023-01-01"
end_date = "2024-12-31"
data = yf.download(symbol, start=start_date, end=end_date, interval="1d")

# Ensure data was fetched successfully
if data.empty:
    raise ValueError(f"No data fetched for symbol {symbol} between {start_date} and {end_date}.")

# -----------------------------
# Candle Class Definition
# -----------------------------

class Candle:
    """
    Represents a single candlestick in the chart with properties to determine its characteristics.
    """
    def __init__(self, open_price, high, low, close):
        self.open_price = open_price
        self.high = high
        self.low = low
        self.close = close

    @property
    def body_size(self):
        """
        Calculates the absolute size of the candle's body.
        """
        return abs(self.close - self.open_price)

    @property
    def candle_range(self):
        """
        Calculates the range of the candle (high - low).
        """
        return self.high - self.low

    @property
    def body_percentage(self):
        """
        Determines the percentage of the candle's body relative to its range.
        """
        if self.candle_range == 0:
            return 0
        return (self.body_size / self.candle_range) * 100

    @property
    def is_bullish(self):
        """
        Checks if the candle is bullish (closing price higher than opening price).
        """
        return self.close > self.open_price

# -----------------------------
# Demand Zone Detection Functions
# -----------------------------

def is_legin_candle(candle):
    """
    Determines if a candle qualifies as a leg-in candle based on body percentage (>50%).
    """
    return candle.body_percentage > 50

def is_base_candle(candle):
    """
    Determines if a candle qualifies as a base candle based on body percentage (<50%).
    """
    return candle.body_percentage < 50

def is_legout_candle(candle):
    """
    Determines if a candle qualifies as a leg-out candle based on body percentage (>50%).
    """
    return candle.body_percentage > 50

def detect_demand_zones(candles):
    """
    Detects demand zones in the list of candles based on the defined criteria.
    
    Returns:
        List of tuples containing:
        - Index of leg-in candle
        - Index of leg-out candle
        - List of base candles
    """
    demand_zones = []
    i = 0
    while i < len(candles) - 2:
        if is_legin_candle(candles[i]):
            base_candles = []
            j = i + 1
            # Collect up to 5 consecutive base candles
            while j < len(candles) and len(base_candles) < 5 and is_base_candle(candles[j]):
                base_candles.append(candles[j])
                j += 1

            if j < len(candles) and is_legout_candle(candles[j]):
                legin_candle = candles[i]
                legout_candle = candles[j]

                # Verify the demand zone criteria
                if base_candles and (legout_candle.is_bullish and
                                     legout_candle.close > legin_candle.high and
                                     legout_candle.close > max(candle.high for candle in base_candles)):
                    demand_zones.append((i, j, base_candles))  # Store indices and base candles
            i = j  # Move to the next potential pattern after the leg-out candle
        else:
            i += 1

    return demand_zones

def check_zone_tested_and_target(demand_zone, candles, start_index):
    """
    Checks whether the price has returned to the detected demand zone and if it achieved a 1:2 risk-reward target.
    
    Returns:
        - 'pink' if the target was achieved
        - 'blue' if the zone was broken without achieving the target
        - 'green' if the zone remains fresh (untested)
    """
    base_candles = demand_zone[2]
    highest_high = max(candle.high for candle in base_candles)
    lowest_low = min(candle.low for candle in base_candles)
    
    # Calculate risk and target price for 1:2 risk-reward ratio
    risk = highest_high - lowest_low
    target_price = highest_high + 2 * risk

    # Flags to track the status
    zone_entered = False
    target_hit = False
    zone_broken = False

    # Iterate through candles starting from after the leg-out candle
    for k in range(start_index, len(candles)):
        candle = candles[k]
        # Check if price enters the zone
        if not zone_entered:
            if candle.low <= highest_high and candle.high >= lowest_low:
                zone_entered = True
        if zone_entered and not target_hit:
            # Check if target is hit
            if candle.high >= target_price:
                target_hit = True
                break  # Target achieved
            # Check if zone is broken before target
            if candle.low < lowest_low:
                zone_broken = True
                break  # Zone broken before target

    if zone_entered:
        if target_hit:
            return 'pink'  # Target achieved
        elif zone_broken:
            return 'blue'  # Zone broken before achieving target
        else:
            return 'green'  # Zone entered but neither target hit nor zone broken
    else:
        return 'green'  # Zone not yet tested

# -----------------------------
# Data Processing and Visualization
# -----------------------------

# Convert fetched data to Candle objects
candles = []
for idx, row in data.iterrows():
    candles.append(Candle(row['Open'], row['High'], row['Low'], row['Close']))

# Detect demand zones based on the updated criteria
demand_zones = detect_demand_zones(candles)

# Counters for different zone statuses
fresh_zones = 0
tested_zones = 0
target_zones = 0

# Set up the plot with desired configurations
fig, ax = mpf.plot(data, type='candle', style='charles',
                   title='Bank Nifty with Detected Demand Zones',
                   ylabel='Price',
                   volume=False,  # Remove the volume subplot
                   tight_layout=True,  # Reduce margins
                   show_nontrading=True,
                   returnfig=True)

# Iterate through detected demand zones to analyze and plot them
for dz in demand_zones:
    base_candles = dz[2]
    
    # Determine the highest high and lowest low among base candles
    highest_high = max(candle.high for candle in base_candles)
    lowest_low = min(candle.low for candle in base_candles)
    
    # Check the status of the zone (fresh, tested, or target achieved)
    start_index = dz[1] + 1  # Begin checking after the leg-out candle
    color = check_zone_tested_and_target(dz, candles, start_index)
    
    # Update counters based on the zone status
    if color == 'green':
        fresh_zones += 1
    elif color == 'blue':
        tested_zones += 1
    elif color == 'pink':
        target_zones += 1
    
    # Plot horizontal lines representing the demand zone boundaries
    start_date = data.index[dz[0]]
    end_date = data.index[-1]
    ax[0].hlines(y=highest_high, xmin=start_date, xmax=end_date, color=color, linestyle='--', linewidth=1.5)
    ax[0].hlines(y=lowest_low, xmin=start_date, xmax=end_date, color=color, linestyle='--', linewidth=1.5)

plt.show()

# Display counts of different zone statuses
print(f"Number of fresh zones (Green): {fresh_zones}")
print(f"Number of tested zones without target achievement (Blue): {tested_zones}")
print(f"Number of zones where 1:2 target was achieved (Pink): {target_zones}")
