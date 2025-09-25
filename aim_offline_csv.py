import pandas as pd
import glob
from datetime import datetime
import re
import argparse
import os

# ANSI color codes
class bcolors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'

# Command-line arguments
parser = argparse.ArgumentParser(description="Process AIM CSVs and calculate SMA25.")
parser.add_argument('-csv', '--csv', action='store_true', help='Export results to Excel')
parser.add_argument('--folder', default='csv/', help='Folder containing CSVs')
parser.add_argument('--plot', action='store_true', help='Generate plots for each ticker')  # NEW

args = parser.parse_args()

csv_folder = args.folder
csv_files = glob.glob(csv_folder + "*.csv")

# Optional plots folder
plot_folder = csv_folder
if args.plot:
    os.makedirs(plot_folder, exist_ok=True)

summary_data = []
below_sma_data = []
missing_data = []

run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
date_str = datetime.now().strftime("%Y-%m-%d")
filename = f"aim_top30_results_{date_str}.xlsx"

print("⏱️ Starting processing of AIM CSVs...\n")

# -----------------------------
# Plotting function
# -----------------------------
def plot_sma(df, ticker, price_col):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print(f"{bcolors.MAGENTA}[WARN]{bcolors.RESET} matplotlib not installed, skipping plots.")
        return

    plt.figure(figsize=(10,6))
    plt.plot(df['Date'], df[price_col], label="Close Price", color="blue")
    plt.plot(df['Date'], df['SMA25'], label="SMA25", color="orange", linestyle="--")
    plt.title(f"{ticker} - Closing Price vs SMA25")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    out_path = os.path.join(plot_folder, f"{ticker}.png")
    plt.savefig(out_path)
    plt.close()
    print(f"📊 Plot saved: {out_path}")

# -----------------------------
# Main loop
# -----------------------------
for file in csv_files:
    try:
        ticker = os.path.splitext(os.path.basename(file))[0] #file.split('/')[-1].replace('.csv','')
        df = pd.read_csv(file)

        # Detect price column
        price_col = None
        for col in ['Close','Price','Last']:
            if col in df.columns:
                price_col = col
                break
        if price_col is None:
            raise ValueError("No valid price column found")

        # Clean numeric values
        df[price_col] = df[price_col].astype(str).apply(lambda x: re.sub(r'[^\d\.-]', '', x))
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
        df = df.dropna(subset=[price_col])

        # Sort by date
        if 'Date' in df.columns:
            df = df.sort_values('Date')

        # Calculate SMA25
        df['SMA25'] = df[price_col].rolling(window=25).mean()
        latest_close = df[price_col].iloc[-1]
        latest_sma = df['SMA25'].iloc[-1]

        if pd.isna(latest_sma):
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

        # Print colored output
        print(f"{color}[{status}]{bcolors.RESET} {ticker}: Close={latest_close:.2f}, SMA25={latest_sma if not pd.isna(latest_sma) else 'NaN'}")

        # Optional plot
        if args.plot:
            plot_sma(df, ticker, price_col)

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
    stamp_df = pd.DataFrame([{"Ticker": f"Scan run at {run_time}"}])
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        pd.concat([stamp_df, df_summary], ignore_index=True).to_excel(writer, sheet_name="Summary", index=False)
        pd.concat([stamp_df, df_below], ignore_index=True).to_excel(writer, sheet_name="Below_SMA25", index=False)
        pd.concat([stamp_df, df_missing], ignore_index=True).to_excel(writer, sheet_name="Missing_Data", index=False)
    print(f"\n✅ Results exported to {filename}")

print(f"\n⏱ Scan completed at {run_time}")
