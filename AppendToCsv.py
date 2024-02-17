import csv
from datetime import datetime


def parse_transaction_blocks(input_lines):
    transactions = []
    # Process blocks of lines, assuming each transaction occupies a set number of lines
    for i in range(0, len(input_lines), 7):
        block = input_lines[i:i + 7]
        # Skip if 'done' is found
        if 'done' in block:
            continue
        try:
            # Extract the transaction details
            timestamp_str = block[0]
            action = block[1]
            usd_value = block[2].replace(',', '')
            spl_amount = block[3].replace(',', '')
            price_per_token = block[5].strip('$')

            # Parse the timestamp
            # Adjust the following line to match the format of your timestamp
            timestamp = datetime.strptime(timestamp_str, '%b %d %I:%M:%S %p')

            transactions.append({
                'timestamp': timestamp,
                'action': action,
                'usd_value': float(usd_value),
                'spl_amount': int(spl_amount),
                'price_per_token': float(price_per_token)
            })
        except Exception as e:
            print(f"Error processing transaction block: {block}")
            print(f"Error: {e}")
    return transactions


def save_to_csv(transactions, filename):
    # Sort transactions by timestamp
    transactions.sort(key=lambda x: x['timestamp'])

    with open(filename, 'w', newline='') as file:  # 'w' to write/overwrite the CSV file
        writer = csv.writer(file)

        # Always write headers when opening in write mode
        writer.writerow(['timestamp', 'action', 'usd_value', 'spl_amount', 'price_per_token'])

        for trans in transactions:
            writer.writerow([trans['timestamp'].strftime('%Y-%m-%d %H:%M:%S'), trans['action'], trans['usd_value'],
                             trans['spl_amount'], trans['price_per_token']])
            print(f"Saved transaction: {trans}")


# Main script
print("Enter your transactions, followed by 'end' on a new line:")
input_lines = []
while True:
    line = input()
    if line == 'end':
        break
    input_lines.append(line)

transactions = parse_transaction_blocks(input_lines)
csv_filename = 'transactions.csv'
save_to_csv(transactions, csv_filename)

print(f"Transactions have been saved to {csv_filename}.")







