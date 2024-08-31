import yfinance as yf
import pandas as pd
import mplfinance as mpf

def fetch_stock_data(symbol, interval='1d', period='1y'):
    """
    Fetch stock data using yfinance.
    
    :param symbol: Stock symbol to fetch data for.
    :param interval: Interval for the data ('1d', '1mo', etc.).
    :param period: The period for which to fetch data (e.g., '1y', '5y').
    :return: DataFrame with stock data.
    """
    stock = yf.Ticker(symbol)
    data = stock.history(interval=interval, period=period)
    data = data[['Open', 'High', 'Low', 'Close']]
    data.columns = ['open', 'high', 'low', 'close']
    return data

def detect_demand_zones(data):
    """
    Detects demand zones in stock data based on the provided criteria.
    
    :param data: DataFrame with columns ['open', 'high', 'low', 'close']
    :return: List of demand zones as tuples of (start_index, end_index, lower_line, upper_line)
    """
    
    demand_zones = []
    i = 0
    n = len(data)
    
    while i < n:
        # Leg-in candle
        body_size = abs(data['close'][i] - data['open'][i])
        range_size = data['high'][i] - data['low'][i]
        body_percent = (body_size / range_size) * 100
        
        if body_percent > 50:  # Potential leg-in candle
            start_index = i
            i += 1
            
            # Base candles
            base_candles = []
            lower_line = float('inf')
            upper_line = float('-inf')
            while i < n:
                body_size = abs(data['close'][i] - data['open'][i])
                range_size = data['high'][i] - data['low'][i]
                body_percent = (body_size / range_size) * 100
                
                if body_percent < 50:
                    base_candles.append(i)
                    lower_line = min(lower_line, data['low'][i])
                    upper_line = max(upper_line, data['high'][i])
                    i += 1
                else:
                    break  # End of base candles
            
            # Leg-out candle
            if i < n:
                body_size = abs(data['close'][i] - data['open'][i])
                range_size = data['high'][i] - data['low'][i]
                body_percent = (body_size / range_size) * 100
                
                if body_percent > 50 and data['close'][i] > data['open'][i]:  # Green candle
                    end_index = i
                    demand_zones.append((start_index, end_index, lower_line, upper_line))
        
        i += 1
    
    return demand_zones

def filter_daily_zones_with_monthly(daily_zones, monthly_zones):
    """
    Filters daily demand zones based on the lower line being below the upper line of monthly demand zones.
    
    :param daily_zones: List of demand zones on daily timeframe.
    :param monthly_zones: List of demand zones on monthly timeframe.
    :return: List of filtered daily demand zones.
    """
    filtered_zones = []
    
    for daily_zone in daily_zones:
        daily_lower_line = daily_zone[2]
        for monthly_zone in monthly_zones:
            monthly_upper_line = monthly_zone[3]
            if daily_lower_line < monthly_upper_line:
                filtered_zones.append(daily_zone)
                break
    
    return filtered_zones

def plot_zones_with_support(daily_data, daily_zones, monthly_zones):
    """
    Plots the daily stock data with candlesticks and overlays daily and monthly demand zones as horizontal rays.
    
    :param daily_data: DataFrame with daily stock data.
    :param daily_zones: List of daily demand zones.
    :param monthly_zones: List of monthly demand zones.
    """
    daily_plot_data = daily_data.copy()
    daily_plot_data.index.name = 'Date'  # Ensure the index is labeled for mplfinance

    # Prepare to draw rays for monthly zones (in blue)
    add_plots = []
    for zone in monthly_zones:
        start_date = zone[0]
        end_date = len(daily_plot_data)
        y_values = [None] * start_date + [zone[2]] * (end_date - start_date)  # Lower line
        add_plots.append(mpf.make_addplot(y_values, color='blue', linestyle='--'))
        y_values = [None] * start_date + [zone[3]] * (end_date - start_date)  # Upper line
        add_plots.append(mpf.make_addplot(y_values, color='blue', linestyle='-'))

    # Prepare to draw rays for daily zones (in green)
    for zone in daily_zones:
        start_date = zone[0]
        end_date = len(daily_plot_data)
        y_values = [None] * start_date + [zone[2]] * (end_date - start_date)  # Lower line
        add_plots.append(mpf.make_addplot(y_values, color='green', linestyle='--'))
        y_values = [None] * start_date + [zone[3]] * (end_date - start_date)  # Upper line
        add_plots.append(mpf.make_addplot(y_values, color='green', linestyle='-'))

    # Plot the candlestick chart with rays
    mpf.plot(daily_plot_data, type='candle', style='charles', addplot=add_plots, title='Tata Motors - Daily Candlestick Chart with Demand Zones', ylabel='Price')

# Fetch data
monthly_data = fetch_stock_data('TATAMOTORS.NS', interval='1mo', period='5y')
daily_data = fetch_stock_data('TATAMOTORS.NS', interval='1d', period='1y')

# Detect demand zones
monthly_zones = detect_demand_zones(monthly_data)
daily_zones = detect_demand_zones(daily_data)

# Filter daily zones with monthly zones
filtered_daily_zones = filter_daily_zones_with_monthly(daily_zones, monthly_zones)

# Plot the results with rays extending to the right
plot_zones_with_support(daily_data, filtered_daily_zones, monthly_zones)
