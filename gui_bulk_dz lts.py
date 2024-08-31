import customtkinter as ctk
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from tkinter import messagebox

# -----------------------------
# Candle Class Definition
# -----------------------------

class Candle:
    def __init__(self, open_price, high, low, close, date):
        self.open_price = open_price
        self.high = high
        self.low = low
        self.close = close
        self.date = date

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

    @property
    def upper_body(self):
        return max(self.open_price, self.close)

# -----------------------------
# Demand Zone Detection Functions
# -----------------------------

def is_legin_candle(candle, min_body_percent, min_candles):
    return candle.body_percentage > min_body_percent and min_candles > 0

def is_base_candle(candle, max_body_percent):
    return candle.body_percentage < max_body_percent

def is_legout_candle(candle, min_body_percent):
    return candle.body_percentage > min_body_percent

def detect_demand_zones(candles, min_body_percent_legin, max_body_percent_base, min_body_percent_legout, max_base_candles, min_legin_candles, min_legout_candles):
    demand_zones = []
    i = 0
    while i < len(candles) - 2:
        if is_legin_candle(candles[i], min_body_percent_legin, min_legin_candles):
            base_candles = []
            j = i + 1
            while j < len(candles) and len(base_candles) < max_base_candles and is_base_candle(candles[j], max_body_percent_base):
                base_candles.append(candles[j])
                j += 1

            if base_candles:  # Ensure there are base candles before proceeding
                # Check if the required number of leg-out candles is found
                legout_candles = []
                while j < len(candles) and len(legout_candles) < min_legout_candles and is_legout_candle(candles[j], min_body_percent_legout):
                    legout_candles.append(candles[j])
                    j += 1

                if len(legout_candles) == min_legout_candles:
                    legin_candle = candles[i]
                    legout_candle = legout_candles[-1]  # Last leg-out candle

                    # Determine the upper boundary of the demand zone
                    upper_body_lowest = min(c.upper_body for c in base_candles)
                    zone_low = min(candle.low for candle in base_candles)

                    if legout_candle.is_bullish and legout_candle.close > legin_candle.high and legout_candle.close > upper_body_lowest:
                        demand_zones.append((i, j-1, base_candles, legout_candles, upper_body_lowest, zone_low))
                else:
                    j += 1  # Move to the next potential pattern after insufficient leg-out candles

            i = j  # Skip to the end of the current pattern
        else:
            i += 1

    return demand_zones

def check_zone_tested_and_target(demand_zone, candles, start_index):
    upper_body_lowest = demand_zone[4]
    zone_low = demand_zone[5]
    
    risk = upper_body_lowest - zone_low
    target_price = upper_body_lowest + 2 * risk

    zone_entered = False
    target_hit = False
    zone_broken = False

    for k in range(start_index, len(candles)):
        candle = candles[k]
        if not zone_entered:
            if candle.low <= upper_body_lowest and candle.high >= zone_low:
                zone_entered = True
        if zone_entered and not target_hit:
            if candle.high >= target_price:
                target_hit = True
                break
            if candle.low < zone_low:
                zone_broken = True
                break

    if zone_entered:
        if target_hit:
            return 'pink'
        elif zone_broken:
            return 'blue'
        else:
            return 'green'
    else:
        return 'green'

# -----------------------------
# Chart Display Functionality
# -----------------------------

def display_chart_with_zones(stock, candles, demand_zones):
    # Convert the list of Candle objects into a DataFrame
    data = {
        'Date': [c.date for c in candles],
        'Open': [c.open_price for c in candles],
        'High': [c.high for c in candles],
        'Low': [c.low for c in candles],
        'Close': [c.close for c in candles],
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)

    # Prepare the zones to be plotted
    colors = {
        'pink': 'red',  # Target achieved
        'blue': 'blue',  # Zone tested but not target achieved
        'green': 'green',  # Fresh zone
    }

    addplots = []
    for dz in demand_zones:
        start_index = dz[1] + 1
        color = check_zone_tested_and_target(dz, candles, start_index)
        addplots.append(mpf.make_addplot([dz[4]] * len(df), panel=0, color=colors[color], alpha=0.3))
        addplots.append(mpf.make_addplot([dz[5]] * len(df), panel=0, color=colors[color], alpha=0.3))

    # Plot the candlestick chart with demand zones
    mpf.plot(df, type='candle', style='charles', addplot=addplots, title=stock, ylabel='Price')

# -----------------------------
# Analysis for All Stocks
# -----------------------------

def run_analysis_for_all():
    try:
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        interval = interval_entry.get()
        min_body_percent_legin = float(min_body_percent_legin_entry.get())
        max_body_percent_base = float(max_body_percent_base_entry.get())
        min_body_percent_legout = float(min_body_percent_legout_entry.get())
        max_base_candles = int(max_base_candles_entry.get())
        min_legin_candles = int(min_legin_candles_entry.get())
        min_legout_candles = int(min_legout_candles_entry.get())

        symbols_df = pd.read_csv('yf_symbols.csv')
        nifty50_stocks = symbols_df['Symbol'].tolist()

        analysis_results = []
        zone_details = []

        for stock in nifty50_stocks:
            data = yf.download(stock, start=start_date, end=end_date, interval=interval)
            if data.empty:
                print(f"No data fetched for symbol {stock} between {start_date} and {end_date}.")
                continue

            candles = []
            for idx, row in data.iterrows():
                candles.append(Candle(row['Open'], row['High'], row['Low'], row['Close'], idx))

            demand_zones = detect_demand_zones(candles, min_body_percent_legin, max_body_percent_base, min_body_percent_legout, max_base_candles, min_legin_candles, min_legout_candles)

            fresh_zones = 0
            tested_zones = 0
            target_zones = 0

            for dz in demand_zones:
                start_index = dz[1] + 1
                color = check_zone_tested_and_target(dz, candles, start_index)
                zone_details.append({
                    "Stock": stock,
                    "Leg-In Date": candles[dz[0]].date,
                    "Leg-Out Date": candles[dz[1]].date,
                    "Zone High (Upper Body Lowest)": dz[4],
                    "Zone Low": dz[5],
                    "Zone Status": "Achieved Target" if color == 'pink' else "Tested" if color == 'blue' else "Fresh",
                })

                if color == 'green':
                    fresh_zones += 1
                elif color == 'blue':
                    tested_zones += 1
                elif color == 'pink':
                    target_zones += 1

            analysis_results.append({
                "Stock": stock,
                "Fresh Zones (Green)": fresh_zones,
                "Tested Zones (Blue)": tested_zones,
                "Target Zones (Pink)": target_zones
            })

        # Save the summary analysis results
        analysis_df = pd.DataFrame(analysis_results)
        analysis_csv_filename = "nifty50_demand_zones_analysis.csv"
        analysis_df.to_csv(analysis_csv_filename, index=False)

        # Save the detailed zones data
        zones_df = pd.DataFrame(zone_details)
        zones_csv_filename = "zones.csv"
        zones_df.to_csv(zones_csv_filename, index=False)

        messagebox.showinfo("Success", f"Analysis saved to {analysis_csv_filename} and zone details saved to {zones_csv_filename}.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# -----------------------------
# Analysis for Individual Stock
# -----------------------------

def view_chart():
    try:
        stock = stock_selector.get()
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        interval = interval_entry.get()
        min_body_percent_legin = float(min_body_percent_legin_entry.get())
        max_body_percent_base = float(max_body_percent_base_entry.get())
        min_body_percent_legout = float(min_body_percent_legout_entry.get())
        max_base_candles = int(max_base_candles_entry.get())
        min_legin_candles = int(min_legin_candles_entry.get())
        min_legout_candles = int(min_legout_candles_entry.get())

        data = yf.download(stock, start=start_date, end=end_date, interval=interval)
        if data.empty:
            messagebox.showerror("Error", f"No data fetched for symbol {stock} between {start_date} and {end_date}.")
            return

        candles = []
        for idx, row in data.iterrows():
            candles.append(Candle(row['Open'], row['High'], row['Low'], row['Close'], idx))

        demand_zones = detect_demand_zones(candles, min_body_percent_legin, max_body_percent_base, min_body_percent_legout, max_base_candles, min_legin_candles, min_legout_candles)

        if demand_zones:
            display_chart_with_zones(stock, candles, demand_zones)
        else:
            messagebox.showinfo("Info", "No demand zones detected for the selected stock.")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# -----------------------------
# GUI Application
# -----------------------------

def create_gui():
    ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

    root = ctk.CTk()
    root.title("Demand Zone Detection")

    frame = ctk.CTkScrollableFrame(root, width=400, height=550)
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    global start_date_entry, end_date_entry, interval_entry, min_body_percent_legin_entry
    global max_body_percent_base_entry, min_body_percent_legout_entry, max_base_candles_entry
    global min_legin_candles_entry, min_legout_candles_entry, stock_selector

    ctk.CTkLabel(frame, text="Select Stock:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    stock_selector = ctk.CTkComboBox(frame, values=pd.read_csv('yf_symbols.csv')['Symbol'].tolist())
    stock_selector.grid(row=0, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    start_date_entry = ctk.CTkEntry(frame)
    start_date_entry.insert(0, "2023-01-01")
    start_date_entry.grid(row=1, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    end_date_entry = ctk.CTkEntry(frame)
    end_date_entry.insert(0, "2024-12-31")
    end_date_entry.grid(row=2, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame, text="Time Frame (e.g., 1d, 1h):").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    interval_entry = ctk.CTkEntry(frame)
    interval_entry.insert(0, "1d")
    interval_entry.grid(row=3, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame, text="Min Body % for Leg-In Candle:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
    min_body_percent_legin_entry = ctk.CTkEntry(frame)
    min_body_percent_legin_entry.insert(0, "50")
    min_body_percent_legin_entry.grid(row=4, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame, text="Max Body % for Base Candle:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
    max_body_percent_base_entry = ctk.CTkEntry(frame)
    max_body_percent_base_entry.insert(0, "50")
    max_body_percent_base_entry.grid(row=5, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame, text="Min Body % for Leg-Out Candle:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
    min_body_percent_legout_entry = ctk.CTkEntry(frame)
    min_body_percent_legout_entry.insert(0, "50")
    min_body_percent_legout_entry.grid(row=6, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame, text="Max Base Candles:").grid(row=7, column=0, sticky="w", padx=10, pady=5)
    max_base_candles_entry = ctk.CTkEntry(frame)
    max_base_candles_entry.insert(0, "5")
    max_base_candles_entry.grid(row=7, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame, text="Min Leg-In Candles:").grid(row=8, column=0, sticky="w", padx=10, pady=5)
    min_legin_candles_entry = ctk.CTkEntry(frame)
    min_legin_candles_entry.insert(0, "1")
    min_legin_candles_entry.grid(row=8, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame, text="Min Leg-Out Candles:").grid(row=9, column=0, sticky="w", padx=10, pady=5)
    min_legout_candles_entry = ctk.CTkEntry(frame)
    min_legout_candles_entry.insert(0, "1")
    min_legout_candles_entry.grid(row=9, column=1, padx=10, pady=5)

    ctk.CTkButton(frame, text="View Chart for Selected Stock", command=view_chart).grid(row=10, column=0, columnspan=2, pady=10)
    ctk.CTkButton(frame, text="Run Analysis for All Stocks", command=run_analysis_for_all).grid(row=11, column=0, columnspan=2, pady=10)

    root.mainloop()

# Run the GUI
create_gui()
