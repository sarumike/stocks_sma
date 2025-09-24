# stocks_sma
scripts to track SMAs of AIM stocks

A couple of python scripts to calculate 25 SMA for  AIM stocks in Uk.

This can be applied to any market.

Prerequisites:
This  runs under linux or Git Bash for Windows.

Python needs to be installed, I used v3.9.12.

Libraries used by the scripts:
 
  pandas

  openpyxl
  
  matplotlib





<br/>Two python scripts:

# aim_25_sma.py
This downlaods historical data and calculates  SMA from a given date. The source used is Marketstack. The user will need to apply for a API Key to use this script.
NB Marketstack API key allows 100 requests per month, ie ticker requests.

Usage:
functionality  is controlled through the use of flags.

ie 
--folder <name> : specifies a folder where the results are to be stored, default from current location is data

-csv : creates a csv file  with the results. Default is to output results  to terminal screen

--plot : creates a png plot/graph of SMA for each ticker. This is saved in the folder location

NB data folder contains downloaded data for 20 AIM stocks and plots of a couple of stocks for example.


#  aim_offline_csv.py
This script  can be used if the user has manually downloaded historical data csv files.

Same functionality and flags as in the previous script  except plotting the graphs.

NB csv folder gives examples of historical data downloaded


Example usage:



python aim_25_sma.py #default values, results sent to terminal output, no plots created

python aim_25_sma.py --folder results/ -csv --plot # results saved to csv file in folder 'results', png plots of each stock ticker created
