# Import the functions from the other scripts
from GetAllBlockTransactions2 import process_transaction_hashes
from GetPrice2 import main_process
from GetBothPrices2 import process_our_price

# Define the paths of the input and output CSV files for Script 3 and Script 4
input_csv_path_script3 = r"C:\Users\dan\PycharmProjects\OurProfitCalculator\GetBlockTransactions.csv"
output_csv_path_script3 = r"C:\Users\dan\PycharmProjects\OurProfitCalculator\GetTokenPrice.csv"

input_csv_path_script4 = r"C:\Users\dan\PycharmProjects\OurProfitCalculator\GetTokenPrice.csv"
output_csv_path_script4 = r"C:\Users\dan\PycharmProjects\OurProfitCalculator\OurPrice.csv"

# Prompt user for transaction hashes
input_hashes = input("Enter transaction hashes separated by line breaks:\n")
transaction_hashes = input_hashes.strip().split('\n')

# Process each transaction hash with GetAllBlockTransactions2.py
for transaction_hash in transaction_hashes:
    print(f"Processing transaction hash: {transaction_hash}")
    process_transaction_hashes([transaction_hash])

# Call the main functions from GetPrice2.py and GetBothPrices2.py
# These are called after all transaction hashes have been processed by GetAllBlockTransactions2.py
main_process(input_csv_path_script3, output_csv_path_script3)
process_our_price(input_csv_path_script4, output_csv_path_script4, transaction_hashes)

