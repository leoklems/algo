import pyteal as pt
from beaker import Application, GlobalStateValue
from algosdk import transaction, account  

class ApartmentState:
    apartment_asset_id = GlobalStateValue(stack_type=pt.TealType.uint64)
    rent_amount = GlobalStateValue(stack_type=pt.TealType.uint64)
    owner_address = GlobalStateValue(stack_type=pt.TealType.bytes)
    rental_duration = GlobalStateValue(stack_type=pt.TealType.uint64)
    rental_start_time = GlobalStateValue(stack_type=pt.TealType.uint64)

app = Application("ApartmentRentalApp", state=ApartmentState())


def create_application(client, creator_sk):
    """
    Create and deploy the application on the Algorand blockchain.
    This method initializes the application and returns the app_id and app_addr.
    """
    # Get the suggested parameters for the transaction
    sp = client.suggested_params()

    # Build the application to get the compiled programs
    app_spec = app.build()  # This will compile the approval and clear programs
    print("creator_sk : ",creator_sk)

    # Access the compiled approval and clear programs directly
    approval_program = app_spec.approval_program  # Access as an attribute
    clear_program = app_spec.clear_program          # Access as an attribute

    # Ensure the programs are in bytes format
    if isinstance(approval_program, str):
        approval_program = approval_program.encode('utf-8')  # Convert to bytes if necessary
    if isinstance(clear_program, str):
        clear_program = clear_program.encode('utf-8')  # Convert to bytes if necessary

    # Create the application creation transaction
    txn = transaction.ApplicationCreateTxn(
        sender=creator_sk.address,  # Use the correct function
        sp=sp,
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval_program,  # Use the compiled approval program
        clear_program=clear_program,        # Use the compiled clear program
        global_schema=transaction.StateSchema(num_uints=5, num_byte_slices=0),  # Adjust as needed
        local_schema=transaction.StateSchema(num_uints=0, num_byte_slices=0)  # Adjust as needed
    )


    # Sign the transaction
    signed_txn = txn.sign(creator_sk.private_key)

    # Send the transaction
    txid = client.send_transaction(signed_txn)

    # Wait for confirmation
    transaction.wait_for_confirmation(client, txid)

    # Get the application ID from the transaction result
    transaction_response = client.pending_transaction_info(txid)
    app_id = transaction_response["application-index"]
    app_addr = algosdk_account.address_from_application(app_id)

    print(f"Application created with ID: {app_id}, Address: {app_addr}, TxID: {txid}")
    return app_id, app_addr, txid


@app.external
def configure(apartment_asset: pt.abi.Asset, rent_price: pt.abi.Uint64, owner: pt.abi.Address, duration: pt.abi.Uint64) -> pt.Expr:
    return pt.Seq(
        app.state.apartment_asset_id.set(apartment_asset.asset_id()),
        app.state.rent_amount.set(rent_price.get()),
        app.state.owner_address.set(owner.get()),
        app.state.rental_duration.set(duration.get()),
    )

@app.external
def rent(payment_txn: pt.abi.PaymentTransaction, asset_txn: pt.abi.AssetTransferTransaction) -> pt.Expr:
    return pt.Seq(
        pt.Assert(payment_txn.get().amount() == app.state.rent_amount.get()),
        pt.Assert(payment_txn.get().receiver() == app.state.owner_address.get()),
        pt.Assert(asset_txn.get().asset_amount() == pt.Int(1)),
        pt.Assert(asset_txn.get().xfer_asset() == app.state.apartment_asset_id.get()),
        pt.Assert(asset_txn.get().asset_sender() == app.state.owner_address.get()),
        app.state.rental_start_time.set(pt.Global.latest_timestamp()),
    )

@app.external
def return_asset(asset_txn: pt.abi.AssetTransferTransaction) -> pt.Expr:
    return pt.Seq(
        pt.Assert(pt.Global.latest_timestamp() >= (app.state.rental_start_time.get() + app.state.rental_duration.get())),
        pt.Assert(asset_txn.get().asset_amount() == pt.Int(1)),
        pt.Assert(asset_txn.get().xfer_asset() == app.state.apartment_asset_id.get()),
        pt.Assert(asset_txn.get().asset_receiver() == app.state.owner_address.get()),
    )