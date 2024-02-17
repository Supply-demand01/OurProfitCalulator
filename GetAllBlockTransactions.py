import requests
import json
import csv
import sys
import os
import time


endpoint = "https://wispy-burned-darkness.solana-mainnet.quiknode.pro/28a11a4c2dc26c158a5da1469a494fa7bb66d64a/"

def get_block_number_for_transaction(tx_hash, retries=50, delay=5, timeout=10):
    headers = {
        "Content-Type": "application/json",
    }

    # Adjusting the payload to match the structure provided in the documentation.
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            tx_hash,
            {
                "encoding": "jsonParsed",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }

    for attempt in range(retries):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()

            json_data = response.json()
            if 'result' in json_data and json_data['result']:
                return json_data['result']['slot']
            else:
                print(f"Attempt {attempt + 1}/{retries}: Transaction data not found for {tx_hash}.")
                print(f"Response: {response.text}")  # Enhanced error logging
                time.sleep(delay)
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
            print(f"Response: {response.text}")  # Enhanced error logging
            time.sleep(delay)
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
            time.sleep(delay)
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
            time.sleep(delay)
        except requests.exceptions.RequestException as err:
            print(f"Error: {err}")
            print(f"Response: {response.text}")  # Enhanced error logging
            time.sleep(delay)

    print(f"Max retries reached for transaction {tx_hash}.")
    return None

def get_block_data(slot):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBlock",
        "params": [
            slot,
            {
                "encoding": "jsonParsed",
                "transactionDetails": "full",
                "rewards": False,
                "maxSupportedTransactionVersion": 0
            }
        ]
    }

    response = requests.post(endpoint, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json().get('result')
    else:
        print(f"Failed to fetch block data for slot {slot}. Status code: {response.status_code}, Response: {response.text}")
        return None



def extract_transaction_signature(transaction):
    return transaction['transaction']['signatures'][0]

def process_blocks(starting_slot, number_of_blocks, contract_address):
    file_path = r'C:\Users\dan\PycharmProjects\OurProfitCalculator\GetBlockTransactions.csv'

    # Check if file exists. If not, create it and write headers.
    if not os.path.exists(file_path):
        print("CSV file not found. Creating a new file.")
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Block Number', 'Tx Hash'])  # Writing the headers

    # Append data to the file
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        for i in range(number_of_blocks):
            current_slot = starting_slot + i
            print(f"Processing block {current_slot}")
            block_data = get_block_data(current_slot)

            if block_data and 'transactions' in block_data:
                for transaction in block_data['transactions']:
                    # Check if the transaction contains the contract address
                    if any(contract_address == account["pubkey"] for account in transaction["transaction"]["message"]["accountKeys"]):
                        tx_signature = extract_transaction_signature(transaction)
                        writer.writerow([current_slot, tx_signature])  # Writing data to CSV
                        print(f"Appended data for block {current_slot}")
                    else:
                        print(f"No matching transactions in block {current_slot}")
            else:
                print(f"No transactions data found for block {current_slot}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Loop through all arguments (excluding the script name itself)
        for tx_hash in sys.argv[1:]:
            print(f"Received transaction hash: {tx_hash}")
            found_slot = get_block_number_for_transaction(tx_hash)

            if found_slot is not None:
                print(f"Found slot: {found_slot}")
                number_of_blocks_to_check = 75
                specific_contract_address = "6HDo6eK1hLUt471vJ4XFcNjU6A3oZPs4rXs1haKrk2Ha"
                process_blocks(found_slot, number_of_blocks_to_check, specific_contract_address)
            else:
                print("Could not find the block number for the given transaction hash.")
    else:
        print("No transaction hash provided.")





