import yfinance as yf
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import customtkinter as ctk
import csv
import os

# Define the main application class
class DemandZoneApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Demand Zone Detector")
        self.geometry("600x900")

        # Create a scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=580, height=800)
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

        # Button to trigger demand zone detection for a single stock
        self.calculate_button = ctk.CTkButton(self.scrollable_frame, text="Detect Demand Zones", command=self.detect_zones)
        self.calculate_button.pack(pady=20)

        # Button to trigger scanning of all Nifty 50 stocks
        self.scan_all_button = ctk.CTkButton(self.scrollable_frame, text="Scan All Nifty 50 Stocks", command=self.scan_all_nifty50)
        self.scan_all_button.pack(pady=20)

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

        # Fetch monthly data for the given symbol
        monthly_data = yf.download(symbol, start=start_date, end=end_date, interval="1mo")

        # Convert monthly data to a list of Candle objects
        monthly_candles = []
        for idx, row in monthly_data.iterrows():
            monthly_candles.append(Candle(row['Open'], row['High'], row['Low'], row['Close'], idx))

        # Detect monthly demand zones using user-defined or default parameters
        monthly_demand_zones = self.detect_demand_zones(monthly_candles, min_legin_pct, max_legin_pct, min_base, max_base, min_base_pct, max_base_pct, min_legout_pct, max_legout_pct)

        if not monthly_demand_zones:
            self.output_label.configure(text="No monthly demand zones detected.")
            return

        # Fetch daily data for the given symbol
        daily_data = yf.download(symbol, start=start_date, end=end_date, interval="1d")

        # Filter daily data based on the detected monthly demand zones
        filtered_daily_data = pd.DataFrame()
        for dz in monthly_demand_zones:
            first_base_date = monthly_data.index[dz[0]]
            last_base_date = monthly_data.index[dz[1]]

            filtered_data = daily_data.loc[first_base_date:last_base_date]
            
            # Ensure the filtered data has a DatetimeIndex
            filtered_data.index = pd.to_datetime(filtered_data.index)
            
            filtered_daily_data = pd.concat([filtered_daily_data, filtered_data])

        # Reset the index to ensure it's a proper DatetimeIndex after filtering
        filtered_daily_data.index = pd.to_datetime(filtered_daily_data.index)

        if filtered_daily_data.empty:
            self.output_label.configure(text="No data available for the selected date range or criteria.")
            return

        # Convert filtered daily data to Candle objects
        filtered_candles = []
        for idx, row in filtered_daily_data.iterrows():
            filtered_candles.append(Candle(row['Open'], row['High'], row['Low'], row['Close'], idx))

        # Detect demand zones in the filtered daily data
        demand_zones = self.detect_demand_zones(filtered_candles, min_legin_pct, max_legin_pct, min_base, max_base, min_base_pct, max_base_pct, min_legout_pct, max_legout_pct)

        if not demand_zones:
            self.output_label.configure(text="No demand zones detected in the selected time range.")
            return

        # Prepare data for CSV export
        csv_data = []
        fresh_zones = 0
        tested_zones = 0
        target_zones = 0

        # Prepare the plot and mark demand zones with horizontal rays
        fig, ax = mpf.plot(filtered_daily_data, type='candle', style='charles',
                           title='Bank Nifty with Detected Demand Zones',
                           ylabel='Price',
                           volume=False,  # Remove the volume
                           tight_layout=True,  # Remove the margin
                           show_nontrading=True,
                           returnfig=True,
                           figsize=(15, 10))  # Increased figure size to reduce overlap

        # Add horizontal rays for demand zones and prepare CSV data
        zone_info = []
        for dz in demand_zones:
            base_candles = dz[2]

            # Find the highest high and lowest low of the base candles
            highest_high = max(candle.high for candle in base_candles)
            lowest_low = min(candle.low for candle in base_candles)

            # Check if the zone has been tested and if it met the 1:2 target
            # Change: We now check until the last candle in the entire dataset.
            color = self.check_zone_tested_and_target(dz, filtered_candles, dz[1] + 1)

            if color == 'green':
                status = 'Fresh'
                fresh_zones += 1
            elif color == 'blue':
                status = 'Tested'
                tested_zones += 1
            elif color == 'pink':
                status = 'Target Achieved'
                target_zones += 1

            # Add horizontal rays (lines) from these points extending to the right
            ax[0].hlines(y=highest_high, xmin=filtered_daily_data.index[dz[0]], xmax=filtered_daily_data.index[-1], color=color, linestyle='--', linewidth=1.5)
            ax[0].hlines(y=lowest_low, xmin=filtered_daily_data.index[dz[0]], xmax=filtered_daily_data.index[-1], color=color, linestyle='--', linewidth=1.5)

            # Define leg-in and leg-out candles
            legin_candle = filtered_candles[dz[0]]
            legout_candle = filtered_candles[dz[1]]

            # Map the corresponding monthly demand zone
            higher_timeframe_zone = None
            for monthly_zone in monthly_demand_zones:
                if filtered_daily_data.index[dz[0]] >= monthly_data.index[monthly_zone[0]] and filtered_daily_data.index[dz[1]] <= monthly_data.index[monthly_zone[1]]:
                    higher_timeframe_zone = monthly_zone
                    break

            if higher_timeframe_zone:
                higher_legin_candle = monthly_candles[higher_timeframe_zone[0]]
                higher_legout_candle = monthly_candles[higher_timeframe_zone[1]]
            else:
                higher_legin_candle = None
                higher_legout_candle = None

            zone_info.append(
                f"Leg-In: {legin_candle.date} Price: {legin_candle.close}\n"
                f"Leg-Out: {legout_candle.date} Price: {legout_candle.close}\n"
                f"Belongs to Higher Timeframe Zone (Monthly)\n"
                f"Zone High: {highest_high}, Zone Low: {lowest_low}\n"
            )

            csv_data.append({
                "Symbol": symbol,
                "Leg-In Time": legin_candle.date,
                "Leg-Out Time": legout_candle.date,
                "Zone High": highest_high,
                "Zone Low": lowest_low,
                "Status": status,
                "Higher Timeframe Leg-In Time": higher_legin_candle.date if higher_legin_candle else "N/A",
                "Higher Timeframe Leg-Out Time": higher_legout_candle.date if higher_legout_candle else "N/A",
                "Higher Timeframe Zone High": higher_legin_candle.high if higher_legin_candle else "N/A",
                "Higher Timeframe Zone Low": higher_legout_candle.low if higher_legout_candle else "N/A"
            })

        plt.show()

        # Write data to CSV
        self.write_to_csv(csv_data)

        # Display zone information
        output_text = (f"Number of fresh zones: {fresh_zones}\n"
                       f"Number of tested zones: {tested_zones}\n"
                       f"Number of zones that met 1:2 target: {target_zones}\n\n"
                       f"Detected Zones Information:\n" + "\n".join(zone_info))
        self.output_label.configure(text=output_text)

    def scan_all_nifty50(self):
        nifty50_symbols = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS", 
            "KOTAKBANK.NS", "HDFC.NS", "BHARTIARTL.NS", "ITC.NS", "LT.NS", "SBIN.NS", 
            "ASIANPAINT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "HCLTECH.NS", "MARUTI.NS", 
            "HDFCLIFE.NS", "SUNPHARMA.NS", "WIPRO.NS", "ULTRACEMCO.NS", "ONGC.NS", "POWERGRID.NS", 
            "TITAN.NS", "NTPC.NS", "GRASIM.NS", "INDUSINDBK.NS", "NESTLEIND.NS", "JSWSTEEL.NS", 
            "BAJAJFINSV.NS", "TATASTEEL.NS", "BPCL.NS", "M&M.NS", "DRREDDY.NS", "DIVISLAB.NS", 
            "HEROMOTOCO.NS", "ADANIPORTS.NS", "CIPLA.NS", "COALINDIA.NS", "SHREECEM.NS", 
            "TECHM.NS", "BRITANNIA.NS", "EICHERMOT.NS", "HINDALCO.NS", "TATACONSUM.NS", 
            "APOLLOHOSP.NS", "ADANIENT.NS", "UPL.NS", "SBILIFE.NS"
        ]

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

        csv_data = []

        for symbol in nifty50_symbols:
            # Fetch monthly data for the given symbol
            monthly_data = yf.download(symbol, start=start_date, end=end_date, interval="1mo")

            # Convert monthly data to a list of Candle objects
            monthly_candles = []
            for idx, row in monthly_data.iterrows():
                monthly_candles.append(Candle(row['Open'], row['High'], row['Low'], row['Close'], idx))

            # Detect monthly demand zones
            monthly_demand_zones = self.detect_demand_zones(
                monthly_candles, min_legin_pct, max_legin_pct, min_base, max_base, min_base_pct, max_base_pct, min_legout_pct, max_legout_pct
            )

            if not monthly_demand_zones:
                continue

            # Fetch daily data for the given symbol
            daily_data = yf.download(symbol, start=start_date, end=end_date, interval="1d")

            # Filter daily data based on the detected monthly demand zones
            filtered_daily_data = pd.DataFrame()
            for dz in monthly_demand_zones:
                first_base_date = monthly_data.index[dz[0]]
                last_base_date = monthly_data.index[dz[1]]

                filtered_data = daily_data.loc[first_base_date:last_base_date]
                
                # Ensure the filtered data has a DatetimeIndex
                filtered_data.index = pd.to_datetime(filtered_data.index)
                
                filtered_daily_data = pd.concat([filtered_daily_data, filtered_data])

            # Reset the index to ensure it's a proper DatetimeIndex after filtering
            filtered_daily_data.index = pd.to_datetime(filtered_daily_data.index)

            if filtered_daily_data.empty:
                continue

            # Convert filtered daily data to Candle objects
            filtered_candles = []
            for idx, row in filtered_daily_data.iterrows():
                filtered_candles.append(Candle(row['Open'], row['High'], row['Low'], row['Close'], idx))

            # Detect demand zones in the filtered daily data
            demand_zones = self.detect_demand_zones(
                filtered_candles, min_legin_pct, max_legin_pct, min_base, max_base, min_base_pct, max_base_pct, min_legout_pct, max_legout_pct
            )

            if not demand_zones:
                continue

            # Prepare CSV data
            for dz in demand_zones:
                base_candles = dz[2]

                # Find the highest high and lowest low of the base candles
                highest_high = max(candle.high for candle in base_candles)
                lowest_low = min(candle.low for candle in base_candles)

                # Define leg-in and leg-out candles
                legin_candle = filtered_candles[dz[0]]
                legout_candle = filtered_candles[dz[1]]

                # Map the corresponding monthly demand zone
                higher_timeframe_zone = None
                for monthly_zone in monthly_demand_zones:
                    if filtered_daily_data.index[dz[0]] >= monthly_data.index[monthly_zone[0]] and filtered_daily_data.index[dz[1]] <= monthly_data.index[monthly_zone[1]]:
                        higher_timeframe_zone = monthly_zone
                        break

                if higher_timeframe_zone:
                    higher_legin_candle = monthly_candles[higher_timeframe_zone[0]]
                    higher_legout_candle = monthly_candles[higher_timeframe_zone[1]]
                else:
                    higher_legin_candle = None
                    higher_legout_candle = None

                # Change: Always check until the last candle in the entire dataset
                status = self.check_zone_tested_and_target(dz, filtered_candles, dz[1] + 1)

                csv_data.append({
                    "Symbol": symbol,
                    "Leg-In Time": legin_candle.date,
                    "Leg-Out Time": legout_candle.date,
                    "Zone High": highest_high,
                    "Zone Low": lowest_low,
                    "Status": status,
                    "Higher Timeframe Leg-In Time": higher_legin_candle.date if higher_legin_candle else "N/A",
                    "Higher Timeframe Leg-Out Time": higher_legout_candle.date if higher_legout_candle else "N/A",
                    "Higher Timeframe Zone High": higher_legin_candle.high if higher_legin_candle else "N/A",
                    "Higher Timeframe Zone Low": higher_legout_candle.low if higher_legout_candle else "N/A"
                })

        # Write the accumulated data to CSV
        self.write_to_csv(csv_data)

        # Update the output label
        self.output_label.configure(text=f"Nifty 50 stocks scan completed. Data saved to CSV.")

    def write_to_csv(self, csv_data):
        if csv_data:
            csv_file = 'demand_zone_data.csv'
            csv_file_exists = os.path.exists(csv_file)
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=csv_data[0].keys())
                if not csv_file_exists:
                    writer.writeheader()  # Write the header only if the file does not exist
                writer.writerows(csv_data)

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

        # Change: Continue checking until the last candle in the dataset
        for k in range(start_index, len(candles)):
            if candles[k].low <= highest_high and candles[k].high >= lowest_low:
                # Check if the price hits the 1:2 target after entering the zone
                for m in range(k, len(candles)):
                    if candles[m].high >= target_price:
                        return 'Target Achieved'  # Zone achieved 1:2 target
                    if candles[m].low < lowest_low:
                        return 'Tested'  # Zone was broken before achieving target
                break

        return 'Fresh'  # Zone has not been tested

    def is_legin_candle(self, candle, min_legin_pct, max_legin_pct):
        return min_legin_pct <= candle.body_percentage <= max_legin_pct

    def is_base_candle(self, candle, min_base_pct, max_base_pct):
        return min_base_pct <= candle.body_percentage <= max_base_pct

    def is_legout_candle(self, candle, min_legout_pct, max_legout_pct):
        return min_legout_pct <= candle.body_percentage <= max_legout_pct

# Convert fetched data to Candle objects
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

# Run the application
if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Set the appearance mode of the GUI
    ctk.set_default_color_theme("blue")  # Set the default color theme
    app = DemandZoneApp()
    app.mainloop()
