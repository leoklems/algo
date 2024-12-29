from algosdk import transaction
from beaker import sandbox
from contract2 import ApartmentState

# Set up sandbox environment
client = sandbox.get_algod_client()
acct = sandbox.get_accounts().pop()
app = ApartmentState()

def create(client, creator_sk):
    """
    Create the smart contract application and return app_id, app_addr, and txid.
    """
    # Get the suggested parameters
    sp = client.suggested_params()

    # Create and compile the application
    approval, clear, global_schema, local_schema = app.compile_application()

    # Create the application creation transaction
    txn = app.create_txn(creator=creator_sk, sp=sp)

    # Sign and send the transaction
    signed_txn = txn.sign(creator_sk)
    txid = client.send_transaction(signed_txn)

    # Wait for confirmation
    result = wait_for_confirmation(client, txid)

    # Extract the application ID and calculate the application address
    app_id = result["application-index"]
    app_addr = account.address_from_application(app_id)

    print(f"Application created with ID: {app_id}, Address: {app_addr}, TxID: {txid}")
    return app_id, app_addr, txid


# Deploy the application
# app_id, app_addr, txid = app.create(client, acct)
app_id, app_addr, txid = create(client, acct)

print(f"App ID: {app_id}")
print(f"App Address: {app_addr}")
