
# Stock Market Indicator Analysis

This project involves calculating buy and sell tags for a given stock based on daily, weekly, and monthly technical indicators. The logic includes several financial metrics such as the Choppiness Index, SuperTrend, SMA, VWSMA, VWEMA, MACD, and RSI.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.x
- pandas
- numpy (if not already installed)

## Directory Structure

The following directory structure is expected:

```
Stock_Market_Data/
└── Data_Visualisations/
    └── indicators_processed/
        ├── {script}_daily_indicators_processed.csv
        ├── {script}_weekly_indicators_processed.csv
        └── {script}_monthly_indicators_processed.csv
```

Replace `{script}` with the name of the stock script you are analyzing (e.g., `ADANIENT`).

## Script Explanation

The script calculates buy and sell tags for the specified stock using the given data files. It includes the following steps:

1. **Load Data**: Loads daily, weekly, and monthly data from CSV files.
2. **Helper Functions**:
   - `get_previous_week_data`: Retrieves the previous week's data for a given date.
   - `get_corresponding_month_data`: Retrieves the corresponding month's data for a given date.
   - `check_rsi_trend`: Checks the RSI trend over a specified period based on a given condition.
3. **Main Function**:
   - `calculate_buy_sell_tags`: Calculates buy and sell tags based on various conditions and indicators from the data.
4. **Buy and Sell Logic**:
   - Implements the buy and sell logic based on technical indicators.
5. **Save Results**:
   - Converts the results to DataFrames and saves them to a CSV file.

## How to Run the Script

1. Ensure that the directory structure is set up correctly and that the CSV files are in place.
2. Update the `script` variable with the appropriate stock script name.
3. Run the script using Python:
   ```sh
   python calculate_tags.py
   ```
4. The output will be saved as `{script}_updated_daily_data.csv` in the current directory.

## Notes

- Ensure that the date formats in the CSV files are consistent and in the format `YYYY-MM-DD`.
- The logic for buy and sell tags is based on specific conditions and may need to be adjusted according to different trading strategies or indicators.

## License

This project is licensed under the MIT License.