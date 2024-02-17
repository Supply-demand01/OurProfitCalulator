import requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import csv
import json


api_key = "QN_ae66eadea4cc4d6d919abde015b3cb5d"

def get_parsed_transaction_data(transaction_sig, retries=50, delay=5, timeout=10):
    # Your endpoint URL
    url = "https://wispy-burned-darkness.solana-mainnet.quiknode.pro/28a11a4c2dc26c158a5da1469a494fa7bb66d64a/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"  # Authorization header
    }
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            transaction_sig,
            {
                "encoding": "jsonParsed",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }

    for attempt in range(retries):
        try:
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
            response.raise_for_status()
            json_data = response.json()
            if 'result' in json_data and json_data['result']:
                return json_data['result']
            else:
                print(f"Transaction data not found for {transaction_sig}.")
                return None
        except requests.exceptions.ReadTimeout:
            print(f"ReadTimeout encountered. Retrying attempt {attempt + 1}/{retries} after {delay} seconds...")
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}, retrying...")
            time.sleep(delay)

    print(f"Max retries reached for transaction {transaction_sig}.")
    return None


def calculate_specific_sol_balance_change(account_key, pre_balances, post_balances, account_keys):
    account_index = next((index for index, key in enumerate(account_keys) if key['pubkey'] == account_key), None)
    if account_index is not None:
        sol_balance_change = (post_balances[account_index] - pre_balances[
            account_index]) / 1e9  # Convert lamports to SOL
        return sol_balance_change
    return 0


def calculate_spl_balance_changes_for_signer(signer_wallet, pre_token_balances, post_token_balances):
    balance_changes = {}
    wrapped_sol_change = 0
    found_wrapped_sol = False

    for post_balance in post_token_balances:
        if post_balance['owner'] == signer_wallet:
            mint = post_balance['mint']
            post_amount = int(post_balance['uiTokenAmount']['amount'])
            decimals = post_balance['uiTokenAmount']['decimals']

            pre_balance = next((balance for balance in pre_token_balances if
                                balance['mint'] == mint and balance['owner'] == signer_wallet), None)
            pre_amount = int(pre_balance['uiTokenAmount']['amount']) if pre_balance else 0

            balance_change = (post_amount - pre_amount) / (10 ** decimals)
            if mint == "So11111111111111111111111111111111111111112":
                wrapped_sol_change = balance_change
                found_wrapped_sol = True
            elif balance_change != 0:
                balance_changes[mint] = balance_change

    return balance_changes, wrapped_sol_change, found_wrapped_sol


def format_block_time(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%dT%H:%M:%S') if unix_time else 'N/A'


def process_transaction(transaction_sig, index):
    output_data = []

    parsed_transaction = get_parsed_transaction_data(transaction_sig)
    if parsed_transaction:
        formatted_block_time = format_block_time(parsed_transaction['blockTime']) if 'blockTime' in parsed_transaction else 'N/A'
        meta = parsed_transaction.get('meta', {})
        account_keys_info = parsed_transaction['transaction']['message']['accountKeys']
        signer_wallet = next((key['pubkey'] for key in account_keys_info if key['signer']), None)

        if signer_wallet:
            sol_balance_change = calculate_specific_sol_balance_change(signer_wallet, meta['preBalances'], meta['postBalances'], account_keys_info)
            spl_balance_changes, wrapped_sol_change, found_wrapped_sol = calculate_spl_balance_changes_for_signer(signer_wallet, meta.get('preTokenBalances', []), meta.get('postTokenBalances', []))

            # Subtract the gas fee (meta['fee']) from the SOL balance change to get the actual amount used for the SPL token purchase
            gas_fee = meta['fee'] / 1e9 if 'fee' in meta else 0
            total_sol_used_for_spl_purchase = abs(wrapped_sol_change if found_wrapped_sol else sol_balance_change) - gas_fee

            if total_sol_used_for_spl_purchase >= 0.1:
                if spl_balance_changes:
                    for mint, change in spl_balance_changes.items():
                        if change != 0:
                            # Calculate the price per SPL token based on the SOL used excluding the gas fee
                            token_price = total_sol_used_for_spl_purchase / abs(change)
                            output_data.append({
                                'Txhash': transaction_sig,
                                'BlockTime': formatted_block_time,
                                'Fee (SOL)': gas_fee,
                                'SPL BalanceChange': change,
                                'TokenAddress': mint,
                                'CalculatedValue': total_sol_used_for_spl_purchase,
                                'Token Price': token_price
                            })
                else:
                    output_data.append({
                        'Txhash': transaction_sig,
                        'BlockTime': formatted_block_time,
                        'Fee (SOL)': gas_fee,
                        'SPL BalanceChange': 0,
                        'TokenAddress': 'N/A',
                        'CalculatedValue': total_sol_used_for_spl_purchase,
                        'Token Price': 0  # Set token price to 0 because the SOL used is less than 0.1
                    })
            else:
                # Here we append a row with a token price of 0 if the total SOL used is less than 0.1
                output_data.append({
                    'Txhash': transaction_sig,
                    'BlockTime': formatted_block_time,
                    'Fee (SOL)': gas_fee,
                    'SPL BalanceChange': 0,
                    'TokenAddress': 'N/A',
                    'CalculatedValue': total_sol_used_for_spl_purchase,
                    'Token Price': 0  # Set token price to 0 because the SOL used is less than 0.1
                })
    else:
        print(f"Transaction {transaction_sig} ({index}): No data found.")

    return {'index': index, 'data': output_data}


def append_to_csv(output_file_path, data_rows):
    # Convert the incoming rows to a DataFrame
    new_data = pd.DataFrame(data_rows)

    # Write the new DataFrame directly to CSV, overwriting existing content
    new_data.to_csv(output_file_path, index=False)

def main_process(input_csv_path, output_csv_path):
    df = pd.read_csv(input_csv_path)
    transaction_sigs = df['Tx Hash'].tolist()
    new_rows = []

    for index, transaction_sig in enumerate(transaction_sigs):
        print(f"Processing transaction {index + 1}/{len(transaction_sigs)}: {transaction_sig}")
        result = process_transaction(transaction_sig, index)
        if result and result['data']:
            new_rows.extend(result['data'])

    if new_rows:
        append_to_csv(output_csv_path, new_rows)
    else:
        print("No new rows to append to the CSV.")

if __name__ == "__main__":
    input_csv_path = r"C:\Users\dan\PycharmProjects\OurProfitCalculator\GetBlockTransactions.csv"
    output_csv_path = r"C:\Users\dan\PycharmProjects\OurProfitCalculator\GetTokenPrice.csv"
    main_process(input_csv_path, output_csv_path)