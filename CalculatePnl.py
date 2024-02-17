import pandas as pd

# Prompt for the total USD amount invested and the entry buy price per token.
total_usd_investment = float(input("Enter the total USD amount of our buy: "))
entry_buy_price_per_token = float(input("Enter our entry buy price per token: "))

# Calculate the number of tokens bought with the total investment at the entry price.
our_buy_spl_amount = total_usd_investment / entry_buy_price_per_token

# Read the CSV file.
df = pd.read_csv(r'C:\Users\dan\PycharmProjects\OurProfitCalculator\transactions.csv', parse_dates=['timestamp'])

# Determine the ratio of our tokens to the wallet's tokens for the first 'Buy' transaction.
wallet_first_buy_amount = df.loc[df['action'] == 'Buy', 'spl_amount'].iloc[0]
our_ratio = our_buy_spl_amount / wallet_first_buy_amount

# Initialize a column for our profit as float to prevent future warnings.
df['our_profit'] = 0.0

# Go through each sell transaction and calculate the profit.
for index, row in df.iterrows():
    if row['action'] == 'Sell':
        # Calculate the number of tokens we would sell in this transaction.
        our_sell_spl_amount = row['spl_amount'] * our_ratio

        # Calculate the profit from this transaction.
        profit_per_token = row['price_per_token'] - entry_buy_price_per_token
        our_profit = our_sell_spl_amount * profit_per_token

        # Update the profit in the DataFrame.
        df.at[index, 'our_profit'] = our_profit

# Save the updated DataFrame to a new CSV file.
output_csv = r'C:\Users\dan\PycharmProjects\OurProfitCalculator\transactions_with_our_profit.csv'
df.to_csv(output_csv, index=False)

print(f"Transactions with our profit have been saved to {output_csv}.")
