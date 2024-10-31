from algosdk.constants import address_len, hash_len
from .helpers import account_balance
from django.db import models

from .helpers import passphrase_from_private_key


class Account(models.Model):
    """Base model class for Algorand accounts."""

    address = models.CharField(max_length=address_len)
    private_key = models.CharField(max_length=address_len + hash_len)
    # private_key = models.CharField(max_length=address_len)
    created = models.DateTimeField(auto_now_add=True)

    def balance(self):
        """Return this instance's balance in microAlgos."""
        return 0

    @property
    def passphrase(self):
        """Return account's mnemonic."""
        return passphrase_from_private_key(self.private_key)


