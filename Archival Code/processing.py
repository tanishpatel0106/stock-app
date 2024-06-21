import pandas as pd
import os
import glob

def read_and_filter_data(file_path, start_date, end_date):
    """
    Read a CSV file, filter the data based on the specified date range, and return the filtered DataFrame.

    Parameters:
    - file_path (str): Path to the CSV file.
    - start_date (str): Start date for filtering.
    - end_date (str): End date for filtering.

    Returns:
    - filtered_df (pandas.DataFrame): DataFrame containing the filtered data.
    """
    df = pd.read_csv(file_path, index_col='Date', parse_dates=True)
    filtered_df = df[(df.index >= start_date) & (df.index <= end_date)]
    return filtered_df

def process_indicators(indicators_folder):
    """
    Process indicator files by filtering based on specified date ranges for monthly, weekly, and daily data.

    Parameters:
    - indicators_folder (str): Path to the folder containing the indicator files.

    Returns:
    - None
    """
    intervals = {
        'daily': ('2017-10-30', '2024-03-01'),
        'weekly': ('2017-10-30', '2024-02-26'),
        'monthly': ('2017-10-01', '2024-03-01')
    }

    # Create 'indicators_processed' folder if it doesn't exist
    processed_folder = os.path.join(indicators_folder, "indicators_processed")
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder)

    for file_path in glob.glob(indicators_folder + "/*_indicators.csv"):
        file_name = os.path.basename(file_path)
        stock_name, interval = file_name.split('_')[:2]

        if interval in intervals:
            filtered_df = read_and_filter_data(file_path, *intervals[interval])
            
            # Save the processed data
            output_file_path = os.path.join(processed_folder, f"{stock_name}_{interval}_indicators_processed.csv")
            filtered_df.to_csv(output_file_path)
            print(f"Processed data saved to {output_file_path}")
        else:
            print(f"Unknown interval format in file: {file_name}")

def main():
    indicators_folder = "/home/tanishpatel01/Desktop/Stock_Market_Data/Data_Visualisations/indicators"
    process_indicators(indicators_folder)

if __name__ == "__main__":
    main()
