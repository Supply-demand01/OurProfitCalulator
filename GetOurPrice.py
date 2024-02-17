import pandas as pd

# Load the data from CSV
input_csv_path = "C:\\Users\\dan\\PycharmProjects\\OurProfitCalculator\\GetTokenPrice.csv"
df = pd.read_csv(input_csv_path)

# Make sure that 'Token Price' is numeric
df['Token Price'] = pd.to_numeric(df['Token Price'], errors='coerce')

# Drop rows where 'Token Price' is not a number (NaN)
df = df.dropna(subset=['Token Price'])

# Calculate the 75th percentile of the 'Token Price' column
percentile_75 = df['Token Price'].quantile(0.75)

# Calculate the average price of the top 25% of the most expensive tokens
top_prices = df[df['Token Price'] >= percentile_75]['Token Price']
average_top_prices = top_prices.mean()

# Save the result to a new CSV file
output_csv_path = "C:\\Users\\dan\\PycharmProjects\\OurProfitCalculator\\OurPrice.csv"
result_df = pd.DataFrame({'75th Percentile Average Price': [average_top_prices]})
result_df.to_csv(output_csv_path, index=False)

print(f"The 75th percentile average price is: {average_top_prices}")
