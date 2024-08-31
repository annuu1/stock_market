import yfinance as yf
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import customtkinter as ctk

# Define the main application class
class DemandZoneApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Demand Zone Detector")
        self.geometry("600x800")

        # Create a scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=580, height=750)
        self.scrollable_frame.pack(pady=10)

        # Input fields with default values
        self.symbol_label = ctk.CTkLabel(self.scrollable_frame, text="Symbol (e.g., ^NSEBANK):")
        self.symbol_label.pack(pady=5)
        self.symbol_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="^NSEBANK")
        self.symbol_entry.pack(pady=5)

        self.start_date_label = ctk.CTkLabel(self.scrollable_frame, text="Start Date (YYYY-MM-DD):")
        self.start_date_label.pack(pady=5)
        self.start_date_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="2023-01-01")
        self.start_date_entry.pack(pady=5)

        self.end_date_label = ctk.CTkLabel(self.scrollable_frame, text="End Date (YYYY-MM-DD):")
        self.end_date_label.pack(pady=5)
        self.end_date_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="2023-12-31")
        self.end_date_entry.pack(pady=5)

        # Leg-in Candle Inputs
        self.min_legin_label = ctk.CTkLabel(self.scrollable_frame, text="Min Leg-In Candle Body %:")
        self.min_legin_label.pack(pady=5)
        self.min_legin_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="50")
        self.min_legin_entry.pack(pady=5)

        self.max_legin_label = ctk.CTkLabel(self.scrollable_frame, text="Max Leg-In Candle Body %:")
        self.max_legin_label.pack(pady=5)
        self.max_legin_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="100")
        self.max_legin_entry.pack(pady=5)

        # Base Candle Inputs
        self.min_base_label = ctk.CTkLabel(self.scrollable_frame, text="Min Base Candles:")
        self.min_base_label.pack(pady=5)
        self.min_base_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="1")
        self.min_base_entry.pack(pady=5)

        self.max_base_label = ctk.CTkLabel(self.scrollable_frame, text="Max Base Candles:")
        self.max_base_label.pack(pady=5)
        self.max_base_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="5")
        self.max_base_entry.pack(pady=5)

        self.min_base_pct_label = ctk.CTkLabel(self.scrollable_frame, text="Min Base Candle Body %:")
        self.min_base_pct_label.pack(pady=5)
        self.min_base_pct_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="0")
        self.min_base_pct_entry.pack(pady=5)

        self.max_base_pct_label = ctk.CTkLabel(self.scrollable_frame, text="Max Base Candle Body %:")
        self.max_base_pct_label.pack(pady=5)
        self.max_base_pct_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="50")
        self.max_base_pct_entry.pack(pady=5)

        # Leg-out Candle Inputs
        self.min_legout_label = ctk.CTkLabel(self.scrollable_frame, text="Min Leg-Out Candle Body %:")
        self.min_legout_label.pack(pady=5)
        self.min_legout_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="50")
        self.min_legout_entry.pack(pady=5)

        self.max_legout_label = ctk.CTkLabel(self.scrollable_frame, text="Max Leg-Out Candle Body %:")
        self.max_legout_label.pack(pady=5)
        self.max_legout_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="100")
        self.max_legout_entry.pack(pady=5)

        # Button to trigger demand zone detection
        self.calculate_button = ctk.CTkButton(self.scrollable_frame, text="Detect Demand Zones", command=self.detect_zones)
        self.calculate_button.pack(pady=20)

        # Label to display results
        self.output_label = ctk.CTkLabel(self.scrollable_frame, text="")
        self.output_label.pack(pady=20)

    def detect_zones(self):
        # Retrieve user inputs or use default values
        symbol = self.symbol_entry.get() or "^NSEBANK"
        start_date = self.start_date_entry.get() or "2023-01-01"
        end_date = self.end_date_entry.get() or "2023-12-31"
        
        min_legin_pct = float(self.min_legin_entry.get() or "50")
        max_legin_pct = float(self.max_legin_entry.get() or "100")
        
        min_base = int(self.min_base_entry.get() or "1")
        max_base = int(self.max_base_entry.get() or "5")
        min_base_pct = float(self.min_base_pct_entry.get() or "0")
        max_base_pct = float(self.max_base_pct_entry.get() or "50")
        
        min_legout_pct = float(self.min_legout_entry.get() or "50")
        max_legout_pct = float(self.max_legout_entry.get() or "100")

        # Fetch historical data for the given symbol
        data = yf.download(symbol, start=start_date, end=end_date, interval="1d")

        # Convert data to a list of Candle objects
        candles = []
        for idx, row in data.iterrows():
            candles.append(Candle(row['Open'], row['High'], row['Low'], row['Close']))

        # Detect demand zones using user-defined or default parameters
        demand_zones = self.detect_demand_zones(candles, min_legin_pct, max_legin_pct, min_base, max_base, min_base_pct, max_base_pct, min_legout_pct, max_legout_pct)

        # Track the number of fresh, tested, and target zones
        fresh_zones = 0
        tested_zones = 0
        target_zones = 0

        # Prepare the plot and mark demand zones with horizontal rays
        fig, ax = mpf.plot(data, type='candle', style='charles',
                           title='Bank Nifty with Detected Demand Zones',
                           ylabel='Price',
                           volume=False,  # Remove the volume
                           tight_layout=True,  # Remove the margin
                           show_nontrading=True,
                           returnfig=True)

        # Add horizontal rays for demand zones
        for dz in demand_zones:
            base_candles = dz[2]

            # Find the highest high and lowest low of the base candles
            highest_high = max(candle.high for candle in base_candles)
            lowest_low = min(candle.low for candle in base_candles)

            # Check if the zone has been tested and if it met the 1:2 target
            start_index = dz[1] + 1  # Start checking after the leg-out candle
            color = self.check_zone_tested_and_target(dz, candles, start_index)

            if color == 'green':
                fresh_zones += 1
            elif color == 'blue':
                tested_zones += 1
            elif color == 'pink':
                target_zones += 1

            # Add horizontal rays (lines) from these points extending to the right
            ax[0].hlines(y=highest_high, xmin=data.index[dz[0]], xmax=data.index[-1], color=color, linestyle='--', linewidth=1.5)
            ax[0].hlines(y=lowest_low, xmin=data.index[dz[0]], xmax=data.index[-1], color=color, linestyle='--', linewidth=1.5)

        plt.show()

        # Update the output label with the results
        output_text = (f"Number of fresh zones: {fresh_zones}\n"
                       f"Number of tested zones: {tested_zones}\n"
                       f"Number of zones that met 1:2 target: {target_zones}")
        self.output_label.configure(text=output_text)

    def detect_demand_zones(self, candles, min_legin_pct, max_legin_pct, min_base, max_base, min_base_pct, max_base_pct, min_legout_pct, max_legout_pct):
        demand_zones = []
        i = 0
        while i < len(candles) - 2:
            if self.is_legin_candle(candles[i], min_legin_pct, max_legin_pct):
                base_candles = []
                j = i + 1
                while j < len(candles) and len(base_candles) < max_base and self.is_base_candle(candles[j], min_base_pct, max_base_pct):
                    base_candles.append(candles[j])
                    j += 1

                if j < len(candles) and self.is_legout_candle(candles[j], min_legout_pct, max_legout_pct):
                    legin_candle = candles[i]
                    legout_candle = candles[j]

                    # Check if it's a demand zone
                    if len(base_candles) >= min_base and (legout_candle.is_bullish and
                                                         legout_candle.close > legin_candle.high and
                                                         legout_candle.close > max(candle.high for candle in base_candles)):
                        demand_zones.append((i, j, base_candles))  # Store the indices and base candles
                i = j  # Skip to the next possible pattern after the legout candle
            else:
                i += 1

        return demand_zones

    def check_zone_tested_and_target(self, demand_zone, candles, start_index):
        base_candles = demand_zone[2]
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

    def is_legin_candle(self, candle, min_legin_pct, max_legin_pct):
        return min_legin_pct <= candle.body_percentage <= max_legin_pct

    def is_base_candle(self, candle, min_base_pct, max_base_pct):
        return min_base_pct <= candle.body_percentage <= max_base_pct

    def is_legout_candle(self, candle, min_legout_pct, max_legout_pct):
        return min_legout_pct <= candle.body_percentage <= max_legout_pct

# Convert fetched data to Candle objects
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

# Run the application
if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Set the appearance mode of the GUI
    ctk.set_default_color_theme("blue")  # Set the default color theme
    app = DemandZoneApp()
    app.mainloop()
