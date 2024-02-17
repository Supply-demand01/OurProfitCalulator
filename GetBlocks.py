import requests
import json

# Endpoint URL
endpoint = "https://docs-demo.solana-mainnet.quiknode.pro/"

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
                "maxSupportedTransactionVersion": 0,
                "transactionDetails": "full",
                "rewards": False
            }
        ]
    }

    response = requests.post(endpoint, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json().get('result')
    else:
        print(
            f"Failed to fetch block data for slot {slot}. Status code: {response.status_code}, Response: {response.text}")
        return None

def process_blocks(starting_slot, number_of_blocks):
    for i in range(number_of_blocks):
        current_slot = starting_slot + i
        block_data = get_block_data(current_slot)
        if block_data:
            print(f"Processing data for block {current_slot}")
            # Implement your logic to process the block data here
        else:
            print(f"No data found for block {current_slot}")

# Example starting slot
found_slot = 245736485
number_of_blocks_to_check = 75

process_blocks(found_slot, number_of_blocks_to_check)


