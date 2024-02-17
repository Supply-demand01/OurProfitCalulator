import pandas as pd
import sys


# Function to calculate the 75th percentile average price, ignoring first 10 seconds
def calculate_75th_percentile_avg_price(df, ignore_seconds=10):
    df['BlockTime'] = pd.to_datetime(df['BlockTime'])
    df = df.sort_values('BlockTime')

    # Start ignore_seconds after the first transaction
    start_time = df['BlockTime'].iloc[0] + pd.Timedelta(seconds=ignore_seconds)

    # Filter data to be after the ignore_seconds mark
    filtered_df = df[df['BlockTime'] > start_time].copy()
    filtered_df['Token Price'] = pd.to_numeric(filtered_df['Token Price'], errors='coerce')

    # Exclude rows with NaN or zero values in 'Token Price'
    filtered_df = filtered_df[(filtered_df['Token Price'].notna()) & (filtered_df['Token Price'] > 0)]

    percentile_75 = filtered_df['Token Price'].quantile(0.75)
    top_prices = filtered_df[filtered_df['Token Price'] >= percentile_75]['Token Price']
    return top_prices.mean()


# Function to append data to CSV based on transaction hash
def append_transaction_with_our_price(input_csv_path, output_csv_path, transaction_hash, our_price):
    df = pd.read_csv(input_csv_path)
    transaction_row = df[df['Txhash'] == transaction_hash].copy()

    if not transaction_row.empty:
        transaction_row.loc[:, 'Our Price'] = our_price
        # Check if the output CSV exists, if not, write header
        with open(output_csv_path, 'a', newline='') as f:
            transaction_row.to_csv(f, header=f.tell() == 0, index=False)
        print(f"Transaction {transaction_hash} appended to {output_csv_path}.")
    else:
        print("Transaction hash not found in the file.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        transaction_hash = sys.argv[1]
        input_csv_path = r"C:\Users\dan\PycharmProjects\OurProfitCalculator\GetTokenPrice.csv"
        output_csv_path = r"C:\Users\dan\PycharmProjects\OurProfitCalculator\OurPrice.csv"

        df = pd.read_csv(input_csv_path)
        our_price = calculate_75th_percentile_avg_price(df)
        print(f"The 75th percentile average price is: {our_price}")

        append_transaction_with_our_price(input_csv_path, output_csv_path, transaction_hash, our_price)

