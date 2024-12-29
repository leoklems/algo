from algosdk import mnemonic
from algosdk import account
from algosdk.v2client import algod
import io
import os
import subprocess
from pathlib import Path
from algosdk.constants import microalgos_to_algos_ratio
from algosdk.v2client import indexer
from algosdk.transaction import PaymentTxn
from algosdk.error import WrongChecksumError
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

# Load environment variables from .env file 
load_dotenv()

def passphrase_from_private_key(private_key):
    """Return passphrase from provided private key."""
    return mnemonic.from_private_key(private_key)

def add_standalone_account():
    """Create standalone account and return two-tuple of its private key and address."""
    private_key, address = account.generate_account()
    return private_key, address


def _sandbox_executable():
    """Return full path to Algorand's sandbox executable.

    The location of sandbox directory is retrieved either from the SANDBOX_DIR
    environment variable or if it's not set then the location of sandbox directory
    is implied to be the sibling of this Django project in the directory tree.
    """
    # sandbox_dir = os.getenv("SANDBOX_DIR")
    # or str(
    #     Path(__file__).resolve().parent.parent.parent / "sandbox"
    # )
    # print("Sandbox executable path:", sandbox_dir + "/sandbox")
    # return sandbox_dir + "/sandbox"
    sandbox_dir = str(
        Path(__file__).resolve().parent.parent.parent.parent / "sandbox"
    )
    print("Sandbox executable path:", sandbox_dir + "/sandbox")
    return sandbox_dir
    # return os.path.join(sandbox_dir, "goal")  # Assuming 'goal' is in the sandbox directory


def _call_sandbox_command(*args):
    """Call and return sandbox command composed from provided arguments."""
    return subprocess.Popen(
        [_sandbox_executable(), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # process = subprocess.Popen(
    #     [sandbox_path] + list(args), 
    #     stdout=subprocess.PIPE, 
    #     stderr=subprocess.PIPE) 
    # stdout, stderr = process.communicate() 
    # return stdout.decode(), stderr.decode()
# import subprocess

# def _call_sandbox_command(*args):
#     command = [] + list(args)
#     print("Executing command:", command)  # Debugging output
#     return subprocess.Popen(
#         command,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True
#     ).communicate()

def cli_passphrase_for_account(address):
    """Return passphrase for provided address."""
    process = _call_sandbox_command("goal", "account", "export", "-a", address)
    passphrase = ""
    for line in io.TextIOWrapper(process.stdout):
        parts = line.split('"')
        if len(parts) > 1:
            passphrase = parts[1]
    return passphrase


def _algod_client():
    """Instantiate and return Algod client object."""
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    return algod.AlgodClient(algod_token, algod_address)


def account_balance(address):
    """Return funds balance of the account having provided address."""
    account_info = _algod_client().account_info(address)
    return account_info.get("amount")

INITIAL_FUNDS = 1000000000  # in microAlgos


def _indexer_client():
    """Instantiate and return Indexer client object."""
    indexer_address = "http://localhost:8980"
    indexer_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    return indexer.IndexerClient(indexer_token, indexer_address)

def validate_mnemonic(mnemonic_phrase):
    words = mnemonic_phrase.split()
    if len(words) != 25:
        raise ValueError("Invalid mnemonic length. Mnemonic must consist of 25 words.")


def initial_funds_sender():
    """Get the address of initially created account having enough funds."""
    return next(
        (
            account.get("address")
            for account in _indexer_client().accounts().get("accounts", [])
            if account.get("created-at-round") == 0
            and account.get("amount") > INITIAL_FUNDS + microalgos_to_algos_ratio / 10
        ),
        None,
    )

def _wait_for_confirmation(client, transaction_id, timeout):
    """
    Wait until the transaction is confirmed or rejected, or until 'timeout'
    number of rounds have passed.
    Args:
        transaction_id (str): the transaction to wait for
        timeout (int): maximum number of rounds to wait
    Returns:
        dict: pending transaction information, or throws an error if the transaction
            is not confirmed or rejected in the next timeout rounds
    """
    start_round = client.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(transaction_id)
        except Exception:
            return
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:
            raise Exception("pool error: {}".format(pending_txn["pool-error"]))
        client.status_after_block(current_round)
        current_round += 1
    raise Exception(
        "pending tx not found in timeout rounds, timeout value = : {}".format(timeout)
    )


def add_transaction(sender, receiver, passphrase, amount, note):
    """Create and sign transaction from provided arguments."""

    client = _algod_client()
    params = client.suggested_params()
    unsigned_txn = PaymentTxn(sender, params, receiver, amount, None, note.encode())
    try:
        signed_txn = unsigned_txn.sign(mnemonic.to_private_key(passphrase))
    except WrongChecksumError:
        return "passphrase", "Checksum failed to validate"
    except ValueError:
        return "passphrase", "Unknown word in passphrase"

    try:
        transaction_id = client.send_transaction(signed_txn)
        _wait_for_confirmation(client, transaction_id, 4)
    except Exception as err:
        return None, err  # None implies non-field error
    return "", ""



def send_algos(sender, receiver, passphrase, amount, note):
    """Create and sign transaction from provided argument to send algos."""

    client = _algod_client()
    params = client.suggested_params()
    try:
        print(amount)
        unsigned_txn = PaymentTxn(
            sender=sender, 
            sp=params, 
            receiver = receiver, 
            amt = amount, 
            note = note.encode()
        )
        print("unsigned done")
    except Exception as e:
        print("error", e)
        return None, err  # None implies non-field error
    
    try:
        print("started signing")
        signed_txn = unsigned_txn.sign(
            mnemonic.to_private_key(passphrase))
        print("finished signing")
    except Exception as e:
        print("error", e)
        return None, e  # None implies non-field error

    try:
        print("started waiting")
        transaction_id = client.send_transaction(signed_txn)
        # wait for confirmation
        # txn_result = transaction.wait_for_confirmation(algod_client, txid, 4)
        _wait_for_confirmation(client, transaction_id, 4)
        print("finished waiting")
    except Exception as e:
        print("error", e)
        return None, e  # None implies non-field error
    return f"{amount} sent to {receiver}"