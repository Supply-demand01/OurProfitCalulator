import subprocess

python_path = "C:\\Users\\dan\\PycharmProjects\\OurProfitCalculator\\.venv\\Scripts\\python.exe"

def run_script(script_path, args):
    try:
        cmd = [python_path, script_path] + args
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the script {script_path}: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")

# Define the paths of the scripts
script1 = r"C:\Users\dan\PycharmProjects\OurProfitCalculator\GetAllBlockTransactions.py"
script2 = r"C:\Users\dan\PycharmProjects\OurProfitCalculator\GetPrice2.0.py"
script3 = r"C:\Users\dan\PycharmProjects\OurProfitCalculator\GetBothPrices.py"

# Prompt user for transaction hashes
input_hashes = input("Enter transaction hashes separated by line breaks:\n")
transaction_hashes = input_hashes.strip().split('\n')

# Iterate through each transaction hash
for transaction_hash in transaction_hashes:
    print(f"Processing transaction hash: {transaction_hash}")
    run_script(script1, [transaction_hash])  # Run script1 with the transaction hash
    run_script(script2, [])                  # Run script2 without transaction hash
    run_script(script3, [transaction_hash])  # Run script3 with the transaction hash



