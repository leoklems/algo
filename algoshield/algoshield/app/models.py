from algosdk.constants import address_len, hash_len
from .helpers import account_balance
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth import get_user_model

from .helpers import passphrase_from_private_key
from algosdk import account, mnemonic
from algosdk.v2client import algod

# Define the Algorand node (replace with your own node URL if needed)
algod_token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
algod_address = "http://localhost:4001"


# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

# class User (AbstractBaseUser):
#     email = models.EmailField(unique=True)
#     # first_name = models.CharField(max_length=30, blank=True)
#     # last_name = models.CharField(max_length=30, blank=True)
#     # is_active = models.BooleanField(default=True)
#     # is_staff = models.BooleanField(default=False)

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []  # No required fields other than email

#     def __str__(self):
#         return self.email

class Account(models.Model):
    """Base model class for Algorand accounts."""

    address = models.CharField(max_length=address_len)
    private_key = models.CharField(max_length=address_len + hash_len)
    # private_key = models.CharField(max_length=address_len)
    created = models.DateTimeField(auto_now_add=True)

    def balance(self):
        """Return this instance's balance in microAlgos."""
        try:
            # Specify the address of the account (replace with the address you want to check)
            account_address = self.private_key
            print("private", account_address)

            # Get the public key from the private key
            public_key = account.address_from_private_key(account_address)
            address = public_key
            print("public")

            algod_client = algod.AlgodClient(algod_token, algod_address)
            print("client", algod_client," : address ", address)

            # get the mnemonic
            mnemonic_phrase = mnemonic.from_private_key(self.private_key)
            print("mnemonic :", mnemonic_phrase)

            # Fetch account information
            account_info = algod_client.account_info(address)
            print(account_info, "account info")

            # Extract the balance (in microalgos)
            balance_microalgos = account_info['amount']

            # Convert balance to Algos (1 Algo = 1,000,000 microalgos)
            balance_algos = balance_microalgos / 1_000_000

            print(f"Account balance: {balance_algos} Algos")
            return balance_algos
        except Exception as e:
            print("Error fetching account balance:", str(e))
            return 0

    @property
    def passphrase(self):
        """Return account's mnemonic."""
        return passphrase_from_private_key(self.private_key)
    
    def __str__(self):
        return f"{self.address[:10]}"


class Customer(models.Model):
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE,
                                related_name="customer", null=True)
    account = models.OneToOneField(Account, on_delete=models.CASCADE,
                                related_name="customer_account", null=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER, null=True, blank=True)
    is_owner = models.BooleanField(default=False)  # Indicates house owner
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    display_image = models.ImageField(upload_to='images/customers/', null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name}"


class Building(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/buildings/', null=True, blank=True)
    location = models.CharField(max_length=1000, null=True, blank=True)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"


class Appartment(models.Model):
    KIND = (
        ('Single room', 'Single room'),
        ('Flat', 'Flat'),
        ('Shop', 'Shop')
    )
    building = models.ForeignKey(Building, on_delete=models.CASCADE, 
        related_name='appartment_building', null=True, blank=True)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE, 
        related_name='appartment_owner', null=True)
    renter = models.ForeignKey(Customer, on_delete=models.CASCADE, 
        related_name='appartment_renter', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Rent price
    is_available = models.BooleanField(default=True)  # Availability status
    asset_id = models.BigIntegerField(null=True, blank=True)  # ASA ID on Algorand
    description = models.TextField(null=True, blank=True)
    kind = models.CharField(max_length=20, choices=KIND, null=True, blank=True)
    image = models.ImageField(upload_to='images/appartments/', null=True)
    location = models.CharField(max_length=1000, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.building.name}"
