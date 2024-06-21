import streamlit as st
import pandas as pd
import talib
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta

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
    return df[['Adj Close', 'SMA_20', 'Choppiness_Index', 'SuperTrend']]

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
    df["MACD_Signal"] = macd.iloc[:,1]
    df['RSI'] = talib.RSI(df['Adj Close'], timeperiod=14)
    df['SMA_50'] = talib.SMA(df['Adj Close'], timeperiod=50)
    df['EMA_20'] = talib.EMA(df['Adj Close'], timeperiod=20)
    df['EMA_10'] = talib.EMA(df['Adj Close'], timeperiod=10)
    return df[['Adj Close', 'MACD', 'MACD_Signal', 'RSI', 'SMA_50', 'EMA_20', 'EMA_10']]

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
    macd = ta.macd(df["Adj Close"], fast_period = 12, slow_period = 26, signal_period = 9)
    df["MACD"] = macd.iloc[:,0]
    df["MACD_Signal"] = macd.iloc[:,1]
    return df[['Adj Close', 'VWSMA_200', 'VWEMA_50', 'VWEMA_20', 'RSI_Daily', 'ADX', 'MACD', 'MACD_Signal']]

def plot_daily_trends(df, title):
    """
    Plot daily trends including price and various indicators on subplots.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing the necessary columns (index should be datetime, 'Close', 'VWSMA_200', 'VWEMA_50', 'VWEMA_20', 'RSI_Daily', 'ADX', 'MACD', 'MACD_Signal').
    - title (str): Title of the plot.

    Returns:
    - fig (plotly.graph_objects.Figure): Plotly figure object containing the subplots.
    """
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, subplot_titles=('Price and Moving Averages', 'RSI', 'ADX', 'MACD and MACD Signal'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Adj Close'], mode='lines', name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWSMA_200'], mode='lines', name='VWSMA 200'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWEMA_50'], mode='lines', name='VWEMA 50'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWEMA_20'], mode='lines', name='VWEMA 20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI_Daily'], mode='lines', name='RSI'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['ADX'], mode='lines', name='ADX'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD'), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], mode='lines', name='MACD Signal'), row=4, col=1)
    fig.update_layout(title=title, xaxis_title='Date', height=800, width=1000)
    return fig

def plot_weekly_trends(df, title):
    """
    Plot weekly trends including price and various indicators on subplots.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing the necessary columns (index should be datetime, 'Close', 'SMA_50', 'EMA_20', 'EMA_10', 'RSI', 'MACD', 'MACD_Signal').
    - title (str): Title of the plot.

    Returns:
    - fig (plotly.graph_objects.Figure): Plotly figure object containing the subplots.
    """
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, subplot_titles=('Price and Moving Averages', 'RSI', 'MACD and MACD Signal'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Adj Close'], mode='lines', name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='SMA 50'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], mode='lines', name='EMA 20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_10'], mode='lines', name='EMA 10'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], mode='lines', name='MACD Signal'), row=3, col=1)
    fig.update_layout(title=title, xaxis_title='Date', height=800, width=1000)
    return fig

def plot_monthly_trends(df, title):
    """
    Plot monthly trends including price and various indicators on subplots.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing the necessary columns (index should be datetime, 'Close', 'SMA_20', 'SuperTrend', 'Choppiness_Index').
    - title (str): Title of the plot.

    Returns:
    - fig (plotly.graph_objects.Figure): Plotly figure object containing the subplots.
    """
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, subplot_titles=('Price and SMA 20', 'Supertrend', 'Choppiness Index'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Adj Close'], mode='lines', name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], mode='lines', name='SMA 20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SuperTrend'], mode='lines', name='Supertrend'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Choppiness_Index'], mode='lines', name='Choppiness Index'), row=3, col=1)
    fig.update_layout(title=title, xaxis_title='Date', height=800, width=1000)
    return fig


def main():
    """
    Main function for the stock market data analysis app.

    The function interacts with the user through Streamlit's interface to input CSV file paths or URLs,
    calculates monthly, weekly, and daily indicators, and visualizes trends using plotly charts.

    Returns:
    - None
    """
    
    st.title('Stock Market Data Analysis')
    st.write('This app allows you to analyze stock market data by calculating indicators and visualizing trends.')

    monthly_file = st.file_uploader('Upload monthly data CSV file:', type=['csv'])
    weekly_file = st.file_uploader('Upload weekly data CSV file:', type=['csv'])
    daily_file = st.file_uploader('Upload daily data CSV file:', type=['csv'])

    if monthly_file and weekly_file and daily_file:
        df_monthly = read_csv(monthly_file)
        df_weekly = read_csv(weekly_file)
        df_daily = read_csv(daily_file)

        monthly_indicators = calculate_monthly_indicators(df_monthly)
        weekly_indicators = calculate_weekly_indicators(df_weekly)
        daily_indicators = calculate_daily_indicators(df_daily)

        st.subheader('Monthly Trends')
        st.write(monthly_indicators)
        monthly_plots = plot_monthly_trends(monthly_indicators, 'Monthly Trends')
        st.plotly_chart(monthly_plots, use_container_width=True)

        st.subheader('Weekly Trends')
        st.write(weekly_indicators)
        weekly_plots = plot_weekly_trends(weekly_indicators, 'Weekly Trends')
        st.plotly_chart(weekly_plots, use_container_width=True)

        st.subheader('Daily Trends')
        st.write(daily_indicators)
        daily_plots = plot_daily_trends(daily_indicators, 'Daily Trends')
        st.plotly_chart(daily_plots, use_container_width=True)

if __name__ == "__main__":
    main()
