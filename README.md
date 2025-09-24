# stocks_sma
a  python script to track SMAs of AIM stocks

A couple of python scripts to calculate 25 SMA for  AIM sticks in Uk.

This can be applied to any market.

Prerequisites:
This  runs under linux or Git Bash for Windows.

Python needs to be installed, I used v3.9.12.

Libraries used by the scripts:
  pandas
  openpyxl
  matplotlib


Two python scripts:

# aim_25_sma.py
This downlaods historical data and calculates  SMA from a given date. The source used is Marketstack. Tehuser will need to apply for a API Key to use thsi script.
NB Marketstack API key allows 100 requests per month, ie ticker requests.

Usage:
functionality  is controlled through the use of flags.

ie 
--folder <name> : specifies a folder where the results are to be stored, default from current location is data
-csv : creates a csv file  with the results. Default is to output results  to terminal screen
--plot : creates a png plot/graph of SMA for each ticker. This is saved in the folder location

#  aim_offline_csv.py
This script  can be used if the user has manually downloaded histrical data csv files.

Same functionality and flags as in the previous script  except plotting the graphs.

