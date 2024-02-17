import pandas as pd

# Prompt for the total USD amount invested and the entry buy price per token.
total_usd_investment = float(input("Enter the total USD amount of our buy: "))
entry_buy_price_per_token = float(input("Enter our entry buy price per token: "))

# Read the CSV file and sort by timestamp.
df = pd.read_csv(r'C:\Users\dan\PycharmProjects\OurProfitCalculator\transactions.csv', parse_dates=['timestamp'])
df.sort_values('timestamp', inplace=True)

# Initialize columns for our profit and SPL balance.
df['our_profit'] = 0.0
df['our_spl_balance'] = 0.0

# Initialize our SPL balance and ratio.
our_spl_balance = total_usd_investment / entry_buy_price_per_token
wallet_total_spl_purchased = 0

# Go through each transaction.
for index, row in df.iterrows():
    if row['action'] == 'Buy':
        # Update the total SPL purchased by the wallet.
        wallet_total_spl_purchased += row['spl_amount']
        # Recalculate our ratio based on the total SPL purchased by the wallet.
        our_ratio = our_spl_balance / wallet_total_spl_purchased
        # Update our balance after a buy.
        df.at[index, 'our_spl_balance'] = our_spl_balance
    elif row['action'] == 'Sell' and our_spl_balance > 0:
        # Calculate the selling amount based on our ratio.
        our_sell_amount = row['spl_amount'] * our_ratio
        # Ensure we do not sell more than we have.
        our_sell_amount = min(our_sell_amount, our_spl_balance)
        # Calculate our profit for this sell transaction.
        profit_per_token = row['price_per_token'] - entry_buy_price_per_token
        our_profit = our_sell_amount * profit_per_token
        # Update our balance and record profit in the dataframe.
        our_spl_balance -= our_sell_amount
        df.at[index, 'our_profit'] = our_profit
        df.at[index, 'our_spl_balance'] = our_spl_balance

# Save the updated DataFrame to a new CSV file.
output_file = r'C:\Users\dan\PycharmProjects\OurProfitCalculator\transactions_with_our_profit_and_balance.csv'
df.to_csv(output_file, index=False)

print(f"Transactions with our profit and balance have been saved to {output_file}.")












