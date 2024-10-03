import pandas as pd
from datetime import timedelta

# Define the list of scripts
scripts = ['WIPRO', 'TCS', 'INFY']  # Add more script names as needed

# Helper function to get the previous week's data based on a given date
def get_previous_week_data(date, weekly_data):
    start_of_week = date - timedelta(days=date.weekday())
    previous_week_start = start_of_week - timedelta(weeks=1)
    return weekly_data[weekly_data['Date'] == previous_week_start.strftime('%Y-%m-%d')]

# Helper function to get the corresponding month's data based on a given date
def get_corresponding_month_data(date, monthly_data):
    start_of_month = date.replace(day=1)
    return monthly_data[monthly_data['Date'] == start_of_month.strftime('%Y-%m-%d')]

# Helper function to check RSI trends based on given conditions
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

# Main function to calculate buy and sell tags
def calculate_buy_sell_tags(daily_data, weekly_data, monthly_data):
    buy_results = []
    sell_results = []

    for index, row in daily_data.iterrows():
        date = pd.to_datetime(row['Date'])
        weekly_row = get_previous_week_data(date, weekly_data)
        monthly_row = get_corresponding_month_data(date, monthly_data)

        if weekly_row.empty or monthly_row.empty:
            buy_results.append((row['Date'], 0))
            sell_results.append((row['Date'], 0))
            continue

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

        # Buy Logic
        if choppiness_index < 38.2:
            if supertrend > current_price:
                buy_results.append((row['Date'], 0))
            elif current_price > sma_20 and current_price > vwsma_200 and vwema_20 > vwema_50 and vwema_50 > vwsma_200:
                if macd > 0 and macd_signal > 0 and macd >= macd_signal:
                    if check_rsi_trend(weekly_data, date - timedelta(weeks=6), date, 'increasing_50_to_80'):
                        buy_results.append((row['Date'], 1))
                    else:
                        buy_results.append((row['Date'], 0))
                else:
                    buy_results.append((row['Date'], 0))
            else:
                buy_results.append((row['Date'], 0))
        elif choppiness_index > 61.8:
            if supertrend > current_price:
                buy_results.append((row['Date'], 0))
            elif current_price > sma_20 and current_price > vwsma_200 and vwema_20 > vwema_50 and vwema_50 > vwsma_200:
                if check_rsi_trend(weekly_data, date - timedelta(weeks=6), date, 'increasing_under_40'):
                    buy_results.append((row['Date'], 1))
                else:
                    buy_results.append((row['Date'], 0))
            else:
                buy_results.append((row['Date'], 0))
        else:
            buy_results.append((row['Date'], 0))

        # Sell Logic
        if check_rsi_trend(weekly_data, date - timedelta(weeks=6), date, 'decreasing_above_70'):
            if macd < macd_signal or current_price < sma_20 or current_price < vwsma_200 or vwema_20 < 0.95 * vwema_50:
                sell_results.append((row['Date'], 1))
            else:
                sell_results.append((row['Date'], 0))
        elif current_price < sma_20 or current_price < vwsma_200:
            sell_results.append((row['Date'], 1))
        else:
            sell_results.append((row['Date'], 0))

    return buy_results, sell_results

# Function to generate transactions and calculate returns
def generate_transactions(daily_data, result_df, script):
    transactions = []
    buy_dates = []
    buy_prices = []

    for index, row in result_df.iterrows():
        if row['Buy_Tag'] == 1:
            buy_date = row['Date']
            buy_row = daily_data[daily_data['Date'] == buy_date].iloc[0]
            buy_price = (buy_row['Open'] + buy_row['Close']) / 2
            buy_dates.append(buy_date)
            buy_prices.append(buy_price)
        elif row['Sell_Tag'] == 1:
            sell_date = row['Date']
            sell_row = daily_data[daily_data['Date'] == sell_date].iloc[0]
            sell_price = (sell_row['Open'] + sell_row['Close']) / 2
            for buy_date, buy_price in zip(buy_dates, buy_prices):
                transaction_return = sell_price - buy_price
                transactions.append((script, buy_date, sell_date, transaction_return))

    return pd.DataFrame(transactions, columns=['Script', 'Buy_Date', 'Sell_Date', 'Return'])

# Loop through each script and perform the operations
for script in scripts:
    # Load the daily, weekly, and monthly datasets for the script
    daily_data = pd.read_csv(f'indicators_processed/{script}_daily_indicators_processed.csv')
    weekly_data = pd.read_csv(f'indicators_processed/{script}_weekly_indicators_processed.csv')
    monthly_data = pd.read_csv(f'indicators_processed/{script}_monthly_indicators_processed.csv')

    # Calculate buy and sell tags
    buy_results, sell_results = calculate_buy_sell_tags(daily_data, weekly_data, monthly_data)

    # Convert the results to DataFrames and save to CSV
    buy_df = pd.DataFrame(buy_results, columns=['Date', 'Buy_Tag'])
    sell_df = pd.DataFrame(sell_results, columns=['Date', 'Sell_Tag'])
    result_df = pd.merge(buy_df, sell_df, on='Date')
    result_df.to_csv(f'{script}_updated_daily_data.csv', index=False)

    # Generate transactions and calculate returns
    transactions_df = generate_transactions(daily_data, result_df, script)

    # Save the transactions to CSV
    transactions_df.to_csv(f'{script}_transactions.csv', index=False)

    print(f'Processed {script}')
