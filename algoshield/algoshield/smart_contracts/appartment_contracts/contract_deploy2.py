import algosdk
# from algosdk import algod, mnemonic
# from algosdk import account as algosdk_account
from algosdk import transaction
from beaker import sandbox
from contract2 import ApartmentState
from conf_contract import create_configuration_application

# # Function to initialize the Algorand client
# def initialize_algod_client(algod_address, algod_token):
#     """
#     Initialize the Algorand client.
#     """
#     return algod.AlgodClient(algod_token, algod_address)

# Set up sandbox environment
client = sandbox.get_algod_client()
acct = sandbox.get_accounts().pop()
app = ApartmentState()
# Function to deploy the application
def deploy_application():
    # Algorand network parameters
    # algod_address = "http://localhost:4001"  # Replace with your Algorand node address
    # algod_token = "your_algod_token"          # Replace with your Algorand token

    # # Initialize the Algorand client
    # client = initialize_algod_client(algod_address, algod_token)

    # Creator's mnemonic and private key
    # creator_mnemonic = "your_mnemonic_here"  # Replace with your mnemonic
    # creator_sk = mnemonic.to_private_key(creator_mnemonic)

    # Call the create_application function to deploy the application
    app_id, app_addr, txid = create_configuration_application(client, acct)

    # Print the application details
    print(f"Application deployed successfully!")
    print(f"Application ID: {app_id}")
    print(f"Application Address: {app_addr}")
    print(f"Transaction ID: {txid}")

# Run the deployment
if __name__ == "__main__":
    deploy_application()