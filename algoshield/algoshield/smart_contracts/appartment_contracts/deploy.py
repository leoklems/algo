from algopy import Algorand
from algopy import Account
from algopy import Transaction
from algosdk import account, mnemonic

# Import your contracts
from asset_management_contract import AssetManagementContract
from rental_transaction_contract import RentalTransactionContract

def owner_private_key(request):
    """Returns the authenticated users private key"""
    try:
        user = request.user
        print(user)
        customer = Customer.objects.get(user=user)
        print(customer)
    except Exception as e:
        print("error", e)
        return None
    return customer.account.private_key

def deploy_contracts():
    # Initialize Algorand client
    algorand = Algorand()

    private_key = owner_private_key(request)
    # Create an account (or load an existing one)
    # Replace with your mnemonic or private key
    mnemonic_ = mnemonic.from_private_key(private_key)
    account = Account.from_mnemonic(mnemonic_)

    # Set the account for the Algorand client
    algorand.set_account(account)

    # Deploy Asset Management Contract
    asset_management_contract = AssetManagementContract()
    asset_management_app_id = asset_management_contract.deploy(algorand)
    print(f"Asset Management Contract deployed with App ID: {asset_management_app_id}")

    # Deploy Rental Transaction Contract
    rental_transaction_contract = RentalTransactionContract()
    rental_transaction_contract.set_asset_management_app_id(asset_management_app_id)  # Set reference to Asset Management App ID
    rental_transaction_app_id = rental_transaction_contract.deploy(algorand)
    print(f"Rental Transaction Contract deployed with App ID: {rental_transaction_app_id}")

if __name__ == "__main__":
    deploy_contracts()