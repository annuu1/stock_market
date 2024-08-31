import customtkinter as ctk
import yfinance as yf
import pandas as pd
import tkinter as tk
from tkinter import ttk
import sqlite3
import asyncio
import threading

class StockApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Stock Analysis App")
        self.geometry("800x600")

        # Default values
        self.default_period = "1y"
        self.default_interval = "1d"
        self.nifty_50_symbols = [
            "ADANIPORTS.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS",
            "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS", "INFRATEL.NS", "CIPLA.NS", "COALINDIA.NS",
            "DRREDDY.NS", "EICHERMOT.NS", "GAIL.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS",
            "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "HDFC.NS", "ITC.NS", "ICICIBANK.NS",
            "IBULHSGFIN.NS", "IOC.NS", "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS",
            "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS",
            "SBIN.NS", "SUNPHARMA.NS", "TCS.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS",
            "TITAN.NS", "UPL.NS", "ULTRACEMCO.NS", "VEDL.NS", "WIPRO.NS", "YESBANK.NS", "ZEEL.NS"
        ]

        # SQLite database connection
        self.conn = sqlite3.connect('orders.db')
        self.create_orders_table()

        # Create input fields for period and interval
        self.period_label = ctk.CTkLabel(self, text="Enter Period (e.g., 1y, 6mo, 3mo):")
        self.period_label.pack(pady=10)

        self.period_entry = ctk.CTkEntry(self)
        self.period_entry.insert(0, self.default_period)
        self.period_entry.pack(pady=10)

        self.interval_label = ctk.CTkLabel(self, text="Enter Interval (e.g., 1d, 1h, 15m):")
        self.interval_label.pack(pady=10)

        self.interval_entry = ctk.CTkEntry(self)
        self.interval_entry.insert(0, self.default_interval)
        self.interval_entry.pack(pady=10)

        # Create buttons to fetch data and display zones
        self.fetch_button = ctk.CTkButton(self, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.pack(pady=10)

        self.all_zones_button = ctk.CTkButton(self, text="Display All Zones", command=self.show_all_zones)
        self.all_zones_button.pack(pady=10)

        self.latest_zones_button = ctk.CTkButton(self, text="Display Latest Zones", command=self.show_latest_zones)
        self.latest_zones_button.pack(pady=10)

        self.monitor_button = ctk.CTkButton(self, text="Monitor Live Prices", command=self.start_monitoring)
        self.monitor_button.pack(pady=10)

        # Create output area
        self.output_text = ctk.CTkTextbox(self, width=600, height=300)
        self.output_text.pack(pady=10)

        self.all_demand_zones = []
        self.all_supply_zones = []

    def create_orders_table(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS orders (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    symbol TEXT,
                                    zone_type TEXT,
                                    price REAL,
                                    date TEXT
                                )''')

    def fetch_data(self):
        period = self.period_entry.get()
        interval = self.interval_entry.get()

        if period and interval:
            self.all_demand_zones.clear()
            self.all_supply_zones.clear()

            for symbol in self.nifty_50_symbols:
                self.output_text.insert("1.0", f"Fetching data for {symbol} with period {period} and interval {interval}...\n")
                data = yf.download(symbol, period=period, interval=interval)
                self.output_text.insert("2.0", f"Data fetched for {symbol}\n")

                demand_zones, supply_zones = self.detect_zones(data)
                for zone in demand_zones:
                    self.all_demand_zones.append((symbol, zone[0], zone[1], zone[2], zone[3]))
                for zone in supply_zones:
                    self.all_supply_zones.append((symbol, zone[0], zone[1], zone[2], zone[3]))
        else:
            self.output_text.insert("1.0", "Please enter valid period and interval.\n")

    def detect_zones(self, data):
        demand_zones = []
        supply_zones = []

        data['Candle_Range'] = data['High'] - data['Low']
        data['Body_Size'] = abs(data['Close'] - data['Open'])
        data['Exciting'] = (data['Body_Size'] / data['Candle_Range']) > 0.55
        data['Base'] = (data['Body_Size'] / data['Candle_Range']) < 0.45

        i = 0
        while i < len(data) - 2:
            if data['Exciting'].iloc[i]:
                base_count = 0
                j = i + 1
                while j < len(data) and base_count < 3 and data['Base'].iloc[j]:
                    base_count += 1
                    j += 1
                if base_count > 0 and j < len(data) and data['Exciting'].iloc[j]:
                    zone_tested = self.is_zone_tested(data, i + 1, j - 1)
                    if data['Close'].iloc[j] > data['Open'].iloc[j]:
                        demand_zones.append((data.index[i + 1], data['Close'].iloc[i + 1], base_count, zone_tested))
                    elif data['Close'].iloc[j] < data['Open'].iloc[j]:
                        supply_zones.append((data.index[i + 1], data['Close'].iloc[i + 1], base_count, zone_tested))
                i = j + 1
            else:
                i += 1

        return demand_zones, supply_zones

    def is_zone_tested(self, data, start_index, end_index):
        for j in range(end_index + 1, len(data)):
            if data['Low'].iloc[j] <= data['Close'].iloc[start_index] <= data['High'].iloc[j]:
                return True
        return False

    def show_all_zones(self):
        self.show_zones_in_table(self.all_demand_zones, self.all_supply_zones)

    def show_latest_zones(self):
        latest_demand_zones = {}
        latest_supply_zones = {}

        for zone in self.all_demand_zones:
            stock = zone[0]
            date = zone[1]
            if stock not in latest_demand_zones or date > latest_demand_zones[stock][1]:
                latest_demand_zones[stock] = zone

        for zone in self.all_supply_zones:
            stock = zone[0]
            date = zone[1]
            if stock not in latest_supply_zones or date > latest_supply_zones[stock][1]:
                latest_supply_zones[stock] = zone

        latest_zones = list(latest_demand_zones.values()) + list(latest_supply_zones.values())
        self.show_zones_in_table(latest_zones, latest_zones)

    def show_zones_in_table(self, demand_zones, supply_zones):
        table_window = ctk.CTkToplevel(self)
        table_window.title("Detected Zones")
        table_window.geometry("800x600")

        columns = ("Stock", "Type", "Date", "Price", "Base Candles", "Tested")
        table = ttk.Treeview(table_window, columns=columns, show="headings")

        for col in columns:
            table.heading(col, text=col)
            table.column(col, minwidth=0, width=150)

        for zone in demand_zones:
            table.insert("", "end", values=(zone[0], "Demand", zone[1], zone[2], zone[3], "Yes" if zone[4] else "No"))

        for zone in supply_zones:
            table.insert("", "end", values=(zone[0], "Supply", zone[1], zone[2], zone[3], "Yes" if zone[4] else "No"))

        table.pack(fill="both", expand=True)

    def start_monitoring(self):
        self.output_text.insert("1.0", "Starting live price monitoring...\n")
        threading.Thread(target=self.monitor_live_prices, daemon=True).start()

    def monitor_live_prices(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.monitor())

    async def monitor(self):
        while True:
            for symbol in self.nifty_50_symbols:
                data = yf.download(symbol, period='1d', interval='1m')
                if not data.empty:
                    latest_price = data['Close'].iloc[-1]
                    self.check_zones(symbol, latest_price)
                await asyncio.sleep(60)  # Wait for 1 minute before fetching new data

    def check_zones(self, symbol, latest_price):
        latest_price = float(latest_price)  # Ensure latest_price is a float

        for zone in self.all_demand_zones:
            zone_price = float(zone[1])
            if zone[0] == symbol and abs(latest_price - zone_price) / zone_price < 0.01:
                self.place_order(symbol, "Buy", latest_price, zone_price)

        for zone in self.all_supply_zones:
            zone_price = float(zone[1])
            if zone[0] == symbol and abs(latest_price - zone_price) / zone_price < 0.01:
                self.place_order(symbol, "Sell", latest_price, zone_price)

    def place_order(self, symbol, order_type, latest_price, zone_price):
        with self.conn:
            self.conn.execute('''INSERT INTO orders (symbol, zone_type, price, date) 
                                 VALUES (?, ?, ?, ?)''', 
                                 (symbol, order_type, latest_price, pd.Timestamp.now()))
        self.output_text.insert("1.0", f"Order placed: {order_type} {symbol} at {latest_price} (zone price: {zone_price})\n")

# Run the application
if __name__ == "__main__":
    app = StockApp()
    app.mainloop()
