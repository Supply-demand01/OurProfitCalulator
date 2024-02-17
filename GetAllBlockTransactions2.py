import requests
import json
import csv
import sys
import time

# Endpoint URL
endpoint = "https://wispy-burned-darkness.solana-mainnet.quiknode.pro/28a11a4c2dc26c158a5da1469a494fa7bb66d64a/"

def get_block_number_for_transaction(tx_hash, retries=50, delay=5, timeout=10):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getConfirmedTransaction",
        "params": [
            tx_hash,
            "jsonParsed"
        ]
    }

    for attempt in range(retries):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code

            json_data = response.json()
            if 'result' in json_data and json_data['result']:
                return json_data['result']['slot']
            else:
                print(f"Transaction data not found for {tx_hash}. Attempt {attempt + 1}/{retries}")
                time.sleep(delay)
        except requests.exceptions.ReadTimeout:
            print(f"ReadTimeout encountered. Retrying attempt {attempt + 1}/{retries} after {delay} seconds...")
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying attempt {attempt + 1}/{retries}...")
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
    with open(r'C:\Users\dan\PycharmProjects\OurProfitCalculator\GetBlockTransactions.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Block Number', 'Tx Hash'])  # Writing the headers

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
                    else:
                        print(f"No matching transactions in block {current_slot}")
            else:
                print(f"No transactions data found for block {current_slot}")

def process_transaction_hashes(tx_hashes):
    for tx_hash in tx_hashes:
        print(f"Received transaction hash: {tx_hash}")
        found_slot = get_block_number_for_transaction(tx_hash)

        if found_slot is not None:
            print(f"Found slot: {found_slot}")
            number_of_blocks_to_check = 75
            specific_contract_address = "6HDo6eK1hLUt471vJ4XFcNjU6A3oZPs4rXs1haKrk2Ha"
            process_blocks(found_slot, number_of_blocks_to_check, specific_contract_address)
        else:
            print("Could not find the block number for the given transaction hash.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        tx_hashes = sys.argv[1:]
        process_transaction_hashes(tx_hashes)
    else:
        print("No transaction hash provided.")

