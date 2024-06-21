import pandas as pd
import talib
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def read_csv(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    return df

def calculate_monthly_indicators(df):
    df['SMA_20'] = talib.SMA(df['Close'], timeperiod=20)
    df['Choppiness_Index'] = calculate_choppiness_index(df)
    df['SuperTrend'] = calculate_super_trend(df)
    return df[['SMA_20', 'Choppiness_Index', 'SuperTrend']]

def calculate_weekly_indicators(df):
    df['MACD'], df['MACD_Signal'], _ = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['RSI'] = talib.RSI(df['Close'], timeperiod=14)
    df['SMA_50'] = talib.SMA(df['Close'], timeperiod=50)
    df['EMA_20'] = talib.EMA(df['Close'], timeperiod=20)
    df['EMA_10'] = talib.EMA(df['Close'], timeperiod=10)
    return df[['MACD', 'MACD_Signal', 'RSI', 'SMA_50', 'EMA_20', 'EMA_10']]

def calculate_daily_indicators(df):
    df['VWSMA_200'] = df['Close'].rolling(window=200).mean()
    df['VWEMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['VWEMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['RSI_Daily'] = talib.RSI(df['Close'], timeperiod=14)
    df['ADX'] = talib.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    df['MACD'], df['MACD_Signal'], _ = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    return df[['VWSMA_200', 'VWEMA_50', 'VWEMA_20', 'RSI_Daily', 'ADX', 'MACD', 'MACD_Signal']]

def calculate_choppiness_index(df, period=14):
    hl_range = df['High'] - df['Low']
    atr = talib.SMA(talib.TRANGE(df['High'], df['Low'], df['Close']), period)
    normalized_range = hl_range / atr
    choppiness_index = talib.SMA(normalized_range, period)
    return choppiness_index

def calculate_super_trend(df, atr_period=14, multiplier=2):
    high = df['High']
    low = df['Low']
    close = df['Close']
    atr = talib.ATR(high, low, close, timeperiod=atr_period)
    basic_upper_band = (high + low) / 2 + multiplier * atr
    basic_lower_band = (high + low) / 2 - multiplier * atr
    super_trend = pd.Series(index=df.index)
    super_trend.iloc[0] = close.iloc[0]
    for i in range(1, len(super_trend)):
        if close.iloc[i - 1] <= basic_upper_band.iloc[i - 1]:
            super_trend.iloc[i] = max(basic_upper_band.iloc[i], super_trend.iloc[i - 1])
        else:
            super_trend.iloc[i] = min(basic_lower_band.iloc[i], super_trend.iloc[i - 1])
    return super_trend

def process_stock(monthly_file, weekly_file, daily_file, stock_name):
    df_monthly = read_csv(monthly_file)
    df_weekly = read_csv(weekly_file)
    df_daily = read_csv(daily_file)

    monthly_indicators = calculate_monthly_indicators(df_monthly)
    weekly_indicators = calculate_weekly_indicators(df_weekly)
    daily_indicators = calculate_daily_indicators(df_daily)

    plot_trend(monthly_indicators, ['SMA_20', 'Choppiness_Index', 'SuperTrend'], stock_name, 'Monthly')
    plot_trend(weekly_indicators, ['MACD', 'MACD_Signal', 'RSI', 'SMA_50', 'EMA_20', 'EMA_10'], stock_name, 'Weekly')
    plot_trend(daily_indicators, ['VWSMA_200', 'VWEMA_50', 'VWEMA_20', 'RSI_Daily', 'ADX', 'MACD', 'MACD_Signal'], stock_name, 'Daily')

def plot_trend(df, indicators, stock_name, timeframe):
    fig = make_subplots(rows=len(indicators), cols=1, shared_xaxes=True, 
                        subplot_titles=indicators)

    for i, indicator in enumerate(indicators):
        fig.add_trace(go.Scatter(x=df.index, y=df[indicator], mode='lines', name=indicator), row=i+1, col=1)

    fig.update_layout(title=f'Stock: {stock_name} - {timeframe} Trends', 
                      xaxis_title='Date', 
                      yaxis_title='Indicator Value',
                      height=800, 
                      width=1000)
    fig.show()

# Example usage
process_stock('/home/tanishpatel01/Desktop/Stock_Market_Data/ADANIENT_Monthly.csv', '/home/tanishpatel01/Desktop/Stock_Market_Data/ADANIENT_Weekly.csv', '/home/tanishpatel01/Desktop/Stock_Market_Data/ADANIENT_Daily.csv', 'ADANIENT')
