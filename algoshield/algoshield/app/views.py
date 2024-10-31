from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from algosdk.transaction import ApplicationNoOpTxn, ApplicationCreateTxn, StateSchema
from algosdk import mnemonic, account
from algosdk.v2client import algod
from smart_contracts.simple_contract import approval_program, clear_state_program, compileTeal
from pyteal import Mode
from .models import Account
import os


from .helpers import (
    INITIAL_FUNDS,
    add_transaction,
    cli_passphrase_for_account,
    initial_funds_sender,
    add_standalone_account,
)

# Load environment variables from .env file 
load_dotenv()

def create_standalone(request):
    """Create standalone account."""
    private_key, address = add_standalone_account()
    account = Account.objects.create(address=address, private_key=private_key)
    context = {"account": (address, account.passphrase)}
    return render(request, "create_standalone.html", context)


def index(request):
    """Display all the created standalone accounts."""

    accounts = Account.objects.order_by("-created")
    context = {"accounts": accounts}
    return render(request, "index.html", context)


def initial_funds(request, receiver):
    """Add initial funds to provided standalone receiver account."""
    sender = initial_funds_sender()
    if sender is None:
        message = "Initial funds weren't transferred!"
        messages.add_message(request, messages.ERROR, message)
    else:
        add_transaction(
            sender,
            receiver,
            cli_passphrase_for_account(sender),
            INITIAL_FUNDS,
            "Initial funds",
        )
    return redirect("standalone-account", receiver)

# Deploy Smart contract


algod_token = "youralgodtoken"
algod_address = "http://localhost:4001"
# algod_client = algod.AlgodClient(algod_token, algod_address)

# Algorand sandbox client 
algod_client = algod.AlgodClient("a" * 64, "http://localhost:4001")

private_key, public_key = account.generate_account()
# mnemonic_phrase = os.getenv("MNEMONIC_PHRASE")
# Your mnemonic phrase
mnemonic_phrase = mnemonic.from_private_key(private_key)

print(mnemonic_phrase)
# Convert the mnemonic to a private key
try:
    private_key = mnemonic.to_private_key(mnemonic_phrase)
    print("Private Key:", private_key)
except ValueError as e:
    print("Error:", e)
sender_address = mnemonic.to_master_derivation_key(mnemonic_phrase)

@csrf_exempt
def deploy_contract(request):
    params = algod_client.suggested_params()

    compiled_approval = compileTeal(approval_program(), mode=Mode.Application, version=2)
    compiled_clear = compileTeal(clear_state_program(), mode=Mode.Application, version=2)

    txn = ApplicationCreateTxn(
        sender_address,
        params,
        compiled_approval,
        compiled_clear,
        global_schema=StateSchema(num_uints=0, num_byte_slices=1),
        local_schema=StateSchema(num_uints=0, num_byte_slices=0)
    )

    signed_txn = txn.sign(private_key)
    txid = algod_client.send_transaction(signed_txn)

    # Wait for confirmation
    import time
    def wait_for_confirmation(client, txid):
        while True:
            try:
                txinfo = client.pending_transaction_info(txid)
                if txinfo.get('confirmed-round', 0) > 0:
                    return txinfo
            except Exception:
                continue
            time.sleep(1)

    txinfo = wait_for_confirmation(algod_client, txid)
    app_id = txinfo['application-index']

    # JSON response containing the compiled contract and transaction info
    return JsonResponse({
        'app_id': app_id,
        'transaction_id': txid,
        'compiled_approval': compiled_approval,
        'compiled_clear': compiled_clear,
    })



# Inteact with smart contract by assigning a room

# algod_token = "youralgodtoken"
# algod_address = "http://localhost:4001"
# algod_client = algod.AlgodClient(algod_token, algod_address)

# mnemonic_phrase = "your_mnemonic_here"
# private_key = mnemonic.to_private_key(mnemonic_phrase)
# sender_address = mnemonic.to_master_derivation_key(mnemonic_phrase)

@csrf_exempt
def assign_room(request):
    amount = int(request.POST.get('amount'))
    app_id = int(request.POST.get('app_id'))
    params = algod_client.suggested_params()

    txn = ApplicationNoOpTxn(
        sender_address, 
        params, 
        app_id, 
        [bytes(str(amount), 'utf-8')]
    )
    signed_txn = txn.sign(private_key)
    txid = algod_client.send_transaction(signed_txn)
    return JsonResponse({'transaction_id': txid})
