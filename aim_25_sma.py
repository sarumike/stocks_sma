import requests
import pandas as pd
import os
from datetime import datetime
import argparse
import re
import matplotlib.pyplot as plt

# -----------------------------
# ANSI color codes for console
# -----------------------------
class bcolors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'

# -----------------------------
# Command-line arguments
# -----------------------------
parser = argparse.ArgumentParser(description="Download AIM historical data and calculate SMA25.")
parser.add_argument('-csv', '--csv', action='store_true', help='Export results to Excel')
parser.add_argument('--folder', nargs='?', const='data/', default='data/', help='Folder to store CSVs')
parser.add_argument('--plot', action='store_true', help='Generate SMA25 plots for each ticker')
args = parser.parse_args()

folder = os.path.abspath(args.folder)
os.makedirs(folder, exist_ok=True)

# -----------------------------
# Config
# -----------------------------
API_KEY = "cb41007838e5cef760c18c132a5bb773"  # <-- Replace with your MarketStack API key
DATE_FROM = "2025-01-01"
DATE_TO = datetime.today().strftime("%Y-%m-%d")
LIMIT = 1000

# Example AIM tickers (top 30)
aim_tickers = [
    "FEVR.L"

]

# -----------------------------
# Functions
# -----------------------------
def download_marketstack(ticker):
    url = "http://api.marketstack.com/v1/eod"
    params = {
        "access_key": API_KEY,
        "symbols": ticker,
        "date_from": DATE_FROM,
        "date_to": DATE_TO,
        "limit": LIMIT
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "data" in data and data["data"]:
        df = pd.DataFrame(data["data"])
        df.to_csv(os.path.join(folder, f"{ticker}.csv"), index=False)
        return df
    else:
        return None

def calculate_sma25(df):
    # Use 'close' column if available
    col_candidates = [c for c in df.columns if 'close' in c.lower()]
    if not col_candidates:
        return None, None
    price_col = col_candidates[0]
    df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
    df = df.dropna(subset=[price_col])
    df = df.sort_values('date')
    df['SMA25'] = df[price_col].rolling(window=25).mean()
    latest_close = df[price_col].iloc[-1]
    latest_sma = df['SMA25'].iloc[-1]
    return latest_close, latest_sma




def plot_sma(df, ticker, folder):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("⚠️ matplotlib not installed. Run 'pip install matplotlib' to enable plotting.")
        return

    col_candidates = [c for c in df.columns if 'close' in c.lower()]
    if not col_candidates:
        return
    price_col = col_candidates[0]

    df = df.sort_values('date')
    df['SMA25'] = df[price_col].rolling(window=25).mean()

    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df[price_col], label="Close Price", color='blue')
    plt.plot(df['date'], df['SMA25'], label="SMA25", color='orange', linewidth=2)
    plt.title(f"{ticker} Closing Price vs SMA25")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    plot_path = os.path.join(folder, f"{ticker}_sma25.png")
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"📈 Plot saved: {plot_path}")



# -----------------------------
# Main processing
# -----------------------------
summary_data = []
below_sma_data = []
missing_data = []

run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
filename = f"aim_top30_results_{datetime.now().strftime('%Y-%m-%d')}.xlsx"

print("⏱️ Starting AIM top-30 processing...\n")

for ticker in aim_tickers:
    print(f"[⏱] Processing {ticker}...")
    try:
        df = download_marketstack(ticker)
        if df is None:
            print(f"{bcolors.MAGENTA}[ERROR]{bcolors.RESET} No data for {ticker}")
            missing_data.append({"Ticker": ticker, "Error": "No data returned"})
            continue

        latest_close, latest_sma = calculate_sma25(df)
        if latest_sma is None:
            status = "INSUFFICIENT-HISTORY"
            color = bcolors.YELLOW
        else:
            if latest_close < latest_sma:
                status = "BELOW"
                color = bcolors.RED
            else:
                status = "ABOVE_OR_EQUAL"
                color = bcolors.GREEN

        record = {
            "Ticker": ticker,
            "Latest Close": latest_close,
            "SMA25": latest_sma,
            "Status": status
        }
        summary_data.append(record)
        if status == "BELOW":
            below_sma_data.append(record)

        print(f"{color}[{status}]{bcolors.RESET} {ticker}: Close={latest_close:.2f}, SMA25={latest_sma if latest_sma else 'NaN'}")

# if flag set, plot  sma for each ticker. Creates a png file in data folder
        if args.plot:
            plot_sma(df, ticker, folder)

    except Exception as e:
        print(f"{bcolors.MAGENTA}[ERROR]{bcolors.RESET} {ticker}: {e}")
        missing_data.append({"Ticker": ticker, "Error": str(e)})

# -----------------------------
# Export to Excel
# -----------------------------
df_summary = pd.DataFrame(summary_data)
df_below = pd.DataFrame(below_sma_data)
df_missing = pd.DataFrame(missing_data)

if args.csv:
    import openpyxl
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Summary", index=False)
        df_below.to_excel(writer, sheet_name="Below_SMA25", index=False)
        df_missing.to_excel(writer, sheet_name="Missing_Data", index=False)
    print(f"\n✅ Results exported to {filename}")

print(f"\n⏱ Scan completed at {run_time}")
