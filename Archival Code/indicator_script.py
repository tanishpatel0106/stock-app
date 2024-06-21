import pandas as pd
import talib
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta
import os
import glob

def read_csv(file_path):
    """
    Read a CSV file and return a DataFrame.

    Parameters:
    - file_path (str): The file path of the CSV file to be read.

    Returns:
    - df (pandas.DataFrame): DataFrame containing the data read from the CSV file.
    """
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    return df

def calculate_monthly_indicators(df):
    """
    Calculate monthly indicators such as Simple Moving Average (SMA), Choppiness Index (CI),
    and SuperTrend for a DataFrame.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing the necessary columns ('Close', 'High', 'Low', 'Adj Close').

    Returns:
    - df_indicators (pandas.DataFrame): DataFrame containing calculated indicators ('Close', 'SMA_20', 'Choppiness_Index', 'SuperTrend').
    """
    df['SMA_20'] = talib.SMA(df['Adj Close'], timeperiod=20)
    CI = ta.chop(df["High"], df["Low"], df["Adj Close"])
    df['Choppiness_Index'] = CI
    ST = ta.supertrend(df["High"], df["Low"], df["Adj Close"])
    df["SuperTrend"] = ST.iloc[:,0]
    return df[['Open', 'Close', 'Volume','Adj Close', 'SMA_20', 'Choppiness_Index', 'SuperTrend']]

def calculate_weekly_indicators(df):
    """
    Calculate weekly indicators such as Moving Average Convergence Divergence (MACD), 
    Relative Strength Index (RSI), Simple Moving Averages (SMA), and Exponential Moving Averages (EMA)
    for a DataFrame.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing the necessary columns ('Close', 'Adj Close').

    Returns:
    - df_indicators (pandas.DataFrame): DataFrame containing calculated indicators ('Close', 'MACD', 
      'MACD_Signal', 'RSI', 'SMA_50', 'EMA_20', 'EMA_10').
    """
    macd = ta.macd(df["Adj Close"], fast_period = 12, slow_period = 26, signal_period = 9)
    df["MACD"] = macd.iloc[:,0]
    df["MACD_Signal"] = macd.iloc[:,2]
    df['RSI'] = talib.RSI(df['Adj Close'], timeperiod=14)
    df['SMA_50'] = talib.SMA(df['Adj Close'], timeperiod=50)
    df['EMA_20'] = talib.EMA(df['Adj Close'], timeperiod=20)
    df['EMA_10'] = talib.EMA(df['Adj Close'], timeperiod=10)
    return df[['Open', 'Close', 'Adj Close', 'MACD', 'MACD_Signal', 'RSI', 'SMA_50', 'EMA_20', 'EMA_10']]

def calculate_daily_indicators(df):
    """
    Calculate daily indicators such as Volume Weighted Simple Moving Average (VWSMA), 
    Volume Weighted Exponential Moving Average (VWEMA), Relative Strength Index (RSI), 
    Average Directional Movement Index (ADX), and Moving Average Convergence Divergence (MACD)
    for a DataFrame.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing the necessary columns ('Close', 'High', 'Low', 'Adj Close').

    Returns:
    - df_indicators (pandas.DataFrame): DataFrame containing calculated indicators 
      ('Close', 'VWSMA_200', 'VWEMA_50', 'VWEMA_20', 'RSI_Daily', 'ADX', 'MACD', 'MACD_Signal').
    """
    df['VWSMA_200'] = df['Adj Close'].rolling(window=200).mean()
    df['VWEMA_50'] = df['Adj Close'].ewm(span=50, adjust=False).mean()
    df['VWEMA_20'] = df['Adj Close'].ewm(span=20, adjust=False).mean()
    df['RSI_Daily'] = talib.RSI(df['Adj Close'], timeperiod=14)
    df['ADX'] = talib.ADX(df['High'], df['Low'], df['Adj Close'], timeperiod=14)
    return df[['Open', 'Close', 'Adj Close', 'VWSMA_200', 'VWEMA_50', 'VWEMA_20', 'RSI_Daily', 'ADX']]

def main():
    # Specify the folder containing stock data
    stock_data_folder = "/home/tanishpatel01/Desktop/Stock_Market_Data/Data"  # Replace with the path to your stock data folder
    
    # Define the mapping for time frames
    time_frame_mapping = {
        '1d': 'daily',
        '1wk': 'weekly',
        '1mo': 'monthly'
    }

    # Loop through each stock
    for stock_folder in glob.glob(stock_data_folder + "/*"):
        stock_name = os.path.basename(stock_folder)
        print(f"Processing data for {stock_name}...")

        # Process each time frame
        for interval, time_frame in time_frame_mapping.items():
            file_path = f"{stock_folder}/{stock_name}_{interval}.csv"
            if os.path.exists(file_path):
                df = read_csv(file_path)

                if time_frame == 'daily':
                    indicators_df = calculate_daily_indicators(df)
                elif time_frame == 'weekly':
                    indicators_df = calculate_weekly_indicators(df)
                else:  # Monthly
                    indicators_df = calculate_monthly_indicators(df)

                # Save the indicators to a new folder
                indicators_folder = "indicators"
                if not os.path.exists(indicators_folder):
                    os.makedirs(indicators_folder)

                output_file_path = f"{indicators_folder}/{stock_name}_{time_frame}_indicators.csv"
                indicators_df.to_csv(output_file_path)
                print(f"Saved indicators to {output_file_path}")
            else:
                print(f"No data found for {stock_name} in {time_frame} time frame.")

if __name__ == "__main__":
    main()
