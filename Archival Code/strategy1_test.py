import pandas as pd
from datetime import datetime, timedelta

# Load your datasets here
daily_data = pd.read_csv('/home/tanishpatel01/Documents/Backup_Tanish/Stock_Market_Data/Data_Visualisations/indicators_processed/INFY_daily_indicators_processed.csv')
weekly_data = pd.read_csv('/home/tanishpatel01/Documents/Backup_Tanish/Stock_Market_Data/Data_Visualisations/indicators_processed/INFY_weekly_indicators_processed.csv')
monthly_data = pd.read_csv('/home/tanishpatel01/Documents/Backup_Tanish/Stock_Market_Data/Data_Visualisations/indicators_processed/INFY_monthly_indicators_processed.csv')

import pandas as pd
from datetime import datetime, timedelta

def get_previous_week_data(date, weekly_data):
    start_of_week = date - timedelta(days=date.weekday())
    previous_week_start = start_of_week - timedelta(weeks=1)
    return weekly_data[weekly_data['Date'] == previous_week_start.strftime('%Y-%m-%d')]

def get_corresponding_month_data(date, monthly_data):
    start_of_month = date.replace(day=1)
    return monthly_data[monthly_data['Date'] == start_of_month.strftime('%Y-%m-%d')]

def check_rsi_trend(weekly_data, start_date, end_date, condition):
    weekly_data_filtered = weekly_data[(weekly_data['Date'] >= start_date.strftime('%Y-%m-%d')) & 
                                       (weekly_data['Date'] <= end_date.strftime('%Y-%m-%d'))]
    if weekly_data_filtered.empty or len(weekly_data_filtered) < 6:
        return False
    rsi_values = weekly_data_filtered['RSI']
    
    if condition == 'increasing_under_40':
        return all(rsi < 40 for rsi in rsi_values[:-1]) and rsi_values.iloc[-1] > 30 and all(x < y for x, y in zip(rsi_values, rsi_values[1:]))
    elif condition == 'increasing_50_to_80':
        return all(50 <= rsi <= 80 for rsi in rsi_values) and all(x < y for x, y in zip(rsi_values, rsi_values[1:]))
    elif condition == 'decreasing_above_70':
        return all(rsi > 70 for rsi in rsi_values) and all(x > y for x, y in zip(rsi_values, rsi_values[1:]))
    else:
        return False

def calculate_buy_sell_tags(row, daily_data, weekly_data, monthly_data):
    date = pd.to_datetime(row['Date'])
    weekly_row = get_previous_week_data(date, weekly_data)
    monthly_row = get_corresponding_month_data(date, monthly_data)

    if weekly_row.empty or monthly_row.empty:
        return (float('nan'), float('nan'))

    choppiness_index = monthly_row['Choppiness_Index'].iloc[0]
    supertrend = monthly_row['SuperTrend'].iloc[0]
    current_price = (row['Open'] + row['Close']) / 2
    sma_20 = monthly_row['SMA_20'].iloc[0]
    vwsma_200 = row['VWSMA_200']
    vwema_20 = row['VWEMA_20']
    vwema_50 = row['VWEMA_50']
    macd = weekly_row['MACD'].iloc[0]
    macd_signal = weekly_row['MACD_Signal'].iloc[0]
    rsi_weekly = weekly_row['RSI'].iloc[0]

    buy_tag, sell_tag = 0, 0

    # Logic for Buy_Tag
    if choppiness_index < 38.2:
        if supertrend > current_price:
            buy_tag = 0
        elif current_price > sma_20 and current_price > vwsma_200 and vwema_20 > vwema_50 and vwema_50 > vwsma_200:
            if macd > 0 and macd_signal > 0 and macd >= macd_signal:
                if check_rsi_trend(weekly_data, date - timedelta(weeks=6), date, 'increasing_50_to_80'):
                    buy_tag = 1
                else:
                    buy_tag = 0
            else:
                buy_tag = 0
        else:
            buy_tag = 0
    elif choppiness_index > 61.8:
        if supertrend > current_price:
            buy_tag = 0
        elif current_price > sma_20 and current_price > vwsma_200 and vwema_20 > vwema_50 and vwema_50 > vwsma_200:
            if check_rsi_trend(weekly_data, date - timedelta(weeks=6), date, 'increasing_under_40'):
                buy_tag = 1
            else:
                buy_tag = 0
        else:
            buy_tag = 0
    else:
        buy_tag = 0

    # Logic for Sell_Tag
    if buy_tag == 1:
        for future_date in pd.date_range(start=date + timedelta(days=1), periods=30):  # 30-day window for selling
            future_row = daily_data[daily_data['Date'] == future_date.strftime('%Y-%m-%d')].iloc[0]
            if not future_row.empty:
                future_price = (future_row['Open'] + future_row['Close']) / 2
                future_macd = future_row['MACD']
                future_macd_signal = future_row['MACD_Signal']
                if check_rsi_trend(weekly_data, future_date - timedelta(weeks=6), future_date, 'decreasing_above_70'):
                    if future_macd < future_macd_signal or future_price < sma_20 or future_price < vwsma_200 or vwema_20 < 0.95 * vwema_50:
                        sell_tag = 1
                        break
                elif future_price < sma_20 or future_price < vwsma_200:
                    sell_tag = 1
                    break

    return buy_tag, sell_tag

# Apply the function to each row in the dataset
daily_data[['Buy_Tag', 'Sell_Tag']] = daily_data.apply(lambda row: calculate_buy_sell_tags(row, daily_data, weekly_data, monthly_data), axis=1, result_type='expand')

# Save or display your results
daily_data.to_csv('updated_daily_data.csv', index=False)
print(daily_data.head())
