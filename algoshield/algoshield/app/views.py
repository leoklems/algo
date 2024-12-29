from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView, View, CreateView
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from algosdk.transaction import ApplicationNoOpTxn, ApplicationCreateTxn, StateSchema
from algosdk import mnemonic, account
from algosdk.v2client import algod
from smart_contracts.simple_contract import approval_program, clear_state_program, compileTeal
from pyteal import Mode
from .models import Account, Appartment, Building, Customer
from django.contrib.auth.models import User
from .forms import CustomerForm, UserForm
import os
from django.contrib.auth import authenticate, login, logout
from algosdk.transaction import PaymentTxn, AssetTransferTxn, assign_group_id
from algosdk import transaction
import json


from .helpers import (
    INITIAL_FUNDS,
    add_transaction,
    cli_passphrase_for_account,
    initial_funds_sender,
    add_standalone_account,
    send_algos,
    validate_mnemonic,
    _algod_client
)

# Load environment variables from .env file 
load_dotenv()

# Define the Algorand node (replace with your own node URL if needed)
algod_token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
algod_address = "http://localhost:4001"

algod_client = algod.AlgodClient(algod_token, algod_address)


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



def sign_in(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)  # Log the user in
            return redirect('create_appartment')  # Replace with your success URL
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'forms/sign_in.html')  # Create a sign_in.html template


def sign_out(request):
    logout(request)  # Log the user out
    return redirect('sign_in')  # Redirect to the sign-in page or any other page

def create_standalone():
    """Create standalone account."""
    private_key, address = add_standalone_account()
    account = Account.objects.create(address=address, private_key=private_key)
    # context = {"account": (address, account.passphrase)}
    return Account.objects.get(address=address, private_key=private_key)

def user_exists(email):
    return User.objects.filter(email=email).exists()

def create_customer(request):
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST, request.FILES)

        if customer_form.is_valid():
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')

            # Check if the user already exists
            if User.objects.filter(email=email).exists():  # Use default User model
                messages.error(request, f'A user with this email {email} already exists.')
                return render(request, 'forms/customer.html', {'customer_form': customer_form})

            # Create the user using Django's default User model
            user = User.objects.create_user(username=username, email=email, password=password)  # Use create_user for hashed password
            try:
                customer = customer_form.save(commit=False)
                customer.user = user  # Link the user
                account = create_standalone()
                customer.account = account  # Link the account
                customer.save()
            except Exception as e:
                messages.error(request, 'Error creating customer: ' + str(e))
                return render(request, 'forms/customer.html', {'customer_form': customer_form})

            return redirect('sign_out')
        else:
            return render(request, 'forms/customer.html', {'customer_form': customer_form})
    else:
        customer_form = CustomerForm()

    return render(request, 'forms/customer.html', {'customer_form': customer_form})

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


# class CreateRoomAssetView(APIView):
#     def post(self, request, room_id):
#         try:
#             # Fetch the room instance
#             room = Room.objects.get(id=room_id)

#             # Prepare metadata
#             metadata = json.dumps({
#                 "room_id": room.id,
#                 "building_name": room.building.name,
#                 "rent_price": float(room.price),
#                 "description": room.description,
#             })

#             # Suggested transaction parameters
#             params = algod_client.suggested_params()

#             # Create the asset transaction
#             txn = transaction.AssetConfigTxn(
#                 sender=account.address_from_private_key(OWNER_PRIVATE_KEY),
#                 sp=params,
#                 total=1,
#                 decimals=0,
#                 default_frozen=False,
#                 unit_name=f"ROOM{room.id}",
#                 asset_name=f"{room.building.name}_Room{room.id}",
#                 metadata_hash=metadata.encode("utf-8")[:32],
#                 manager=account.address_from_private_key(OWNER_PRIVATE_KEY),
#                 reserve=None,
#                 freeze=None,
#                 clawback=None,
#             )

#             # Sign the transaction
#             signed_txn = txn.sign(OWNER_PRIVATE_KEY)

#             # Send the transaction
#             txid = algod_client.send_transaction(signed_txn)

#             # Wait for confirmation
#             confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)

#             # Save ASA ID to the database
#             asset_id = confirmed_txn['asset-index']
#             room.asset_id = asset_id
#             room.save()

#             return Response({"message": "Asset created", "asset_id": asset_id}, status=status.HTTP_201_CREATED)

#         except Room.DoesNotExist:
#             return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
class AppartmentCreateView(View):
    template_name = "forms/appartment.html"

    def get(self, request):
        # Owner's private key (should be securely managed)
        OWNER_PRIVATE_KEY = owner_private_key(request)
        # Fetch buildings for the dropdown (if applicable)
        buildings = Building.objects.all()
        print(OWNER_PRIVATE_KEY, "private key")
        return render(request, self.template_name, {"buildings": buildings})

    def post(self, request):
        # Owner's private key (should be securely managed)
        OWNER_PRIVATE_KEY = owner_private_key(request)
        user = request.user
        
        # Parse input fields
        building_id = request.POST.get("building")
        name = request.POST.get("name")
        kind = request.POST.get("kind")
        price = request.POST.get("price")
        location = request.POST.get("location")
        description = request.POST.get("description")

        try:
            # Validate building
            building = Building.objects.get(id=building_id)
            owner = Customer.objects.get(user=user)

            # Create the room instance
            appartment = Appartment(building=building, name=name, owner=owner,
                kind=int(kind), price=price, location=location, description=description)
            appartment.save()

            # Algorand ASA creation logic
            metadata = json.dumps({
                "appartment_id": appartment.id,
                "building_name": building.name,
                "owner_name": owner.name,
                "kind": kind,
                "rent_price": float(price),
                "location": location,
                "description": description,
            })

            params = algod_client.suggested_params()
            print("sender", account.address_from_private_key(OWNER_PRIVATE_KEY))

            txn = transaction.AssetConfigTxn(
                sender=account.address_from_private_key(OWNER_PRIVATE_KEY),
                sp=params,
                total=1,
                decimals=0,
                default_frozen=False,
                unit_name=f"{appartment.id}",
                asset_name=f"{building.name}_Appartment_{appartment.name}",
                metadata_hash=metadata.encode("utf-8")[:32],
                manager=account.address_from_private_key(OWNER_PRIVATE_KEY),
                reserve=None,
                freeze=None,
                clawback=None,
                strict_empty_address_check=False  # Allow empty addresses
            )

            signed_txn = txn.sign(OWNER_PRIVATE_KEY)
            txid = algod_client.send_transaction(signed_txn)
            confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)

            # Save ASA ID
            appartment.asset_id = confirmed_txn["asset-index"]
            appartment.save()

            return redirect(reverse_lazy("appartments"))  # Replace with your list view URL

        except Building.DoesNotExist:
            return HttpResponse("Invalid building ID", status=400)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=400)

class Appartments(View):
    template_name = "apartments.html"

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            # Get the customer instance for the logged-in user
            try:
                owner = Customer.objects.get(user=user)
                # Filter apartments by the owner
                apartments = Appartment.objects.filter(owner=owner)
            except Customer.DoesNotExist:
                apartments = []  # No apartments if the customer does not exist
        else:
            apartments = []  # No apartments if the user is not authenticated

        return render(request, self.template_name, {"apartments": apartments})


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


def send_funds(request):
    """Add initial funds to provided standalone receiver account."""
    if request.method == 'POST':
        sender = request.POST.get('sender')
        receiver = request.POST.get('receiver')
        passphrase = request.POST.get('passphrase')
        amount = request.POST.get('amount')
        note = request.POST.get('note')

        try:
            validate_mnemonic(passphrase)  # Replace with your mnemonic variable
        except ValueError as e:
            print("Error:", str(e))

        print(f"{sender} -> {receiver} : {amount} algos : {passphrase}")

        # Validate the inputs (you can add more validation as needed)
        if not sender or not receiver or not passphrase or not amount:
            messages.error(request, "All fields are required.")
            return redirect('send-funds')

        try:
            # Convert amount to integer and validate
            amount = float(amount)  # Convert to float first
            if amount < 0:
                raise ValueError("Amount must be non-negative.")
            # amount_microalgos = int(amount * 1_000_000)
            amount_microalgos = int(amount)
            print("trying")
            # Call the send_funds function with the cleaned data
            print(send_algos(sender, receiver, passphrase, amount_microalgos, note))
            return redirect("index")
        except Exception as e:
            print("exception")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('send-funds')
    else:
        return render(request, 'send_funds.html')

def rent_room():
    # Create payment transaction
    payment_txn = PaymentTxn(
        sender="RENTER_ADDRESS",
        receiver=owner_address,
        amt=rent_price,
        sp=client.suggested_params(),
    )

    # Create asset transfer transaction
    asset_txn = AssetTransferTxn(
        sender=owner_address,
        receiver="RENTER_ADDRESS",
        index=room_asset_id,
        amt=1,
        sp=client.suggested_params(),
    )

    # Group and sign transactions
    gid = assign_group_id([payment_txn, asset_txn])
    signed_payment = payment_txn.sign(renter_private_key)
    signed_asset = asset_txn.sign(owner_private_key)

    # Submit transactions
    client.send_transactions([signed_payment, signed_asset])
