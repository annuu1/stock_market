import customtkinter as ctk
import yfinance as yf
import pandas as pd
import tkinter as tk
from tkinter import ttk

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
        
        # Create output area
        self.output_text = ctk.CTkTextbox(self, width=600, height=300)
        self.output_text.pack(pady=10)
        
        self.all_demand_zones = []
        self.all_supply_zones = []
    
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

# Run the application
if __name__ == "__main__":
    app = StockApp()
    app.mainloop()
