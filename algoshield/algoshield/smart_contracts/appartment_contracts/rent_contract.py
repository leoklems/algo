from algopy import Algorand, Contract, State

class RentalTransactionContract(Contract):
    def __init__(self):
        super().__init__()
        self.rent_amount = State.uint64()
        self.rental_duration = State.uint64()
        self.rental_start_time = State.uint64()
        self.asset_management_app_id = State.uint64()  # Reference to the Asset Management contract

    @Algorand.external
    def set_asset_management_app_id(self, app_id: Algorand.uint64):
        self.asset_management_app_id.set(app_id)

    @Algorand.external
    def rent(self, payment_txn: Algorand.PaymentTransaction, asset_txn: Algorand.AssetTransferTransaction):
        # Logic to handle rental payment and asset transfer
        asset_management = Algorand.get_application(self.asset_management_app_id.get())
        apartment_asset_id = asset_management.apartment_asset_id.get()
        owner_address = asset_management.owner_address.get()

        # Validate payment and asset transfer
        assert payment_txn.amount == self.rent_amount.get()
        assert payment_txn.receiver == owner_address
        assert asset_txn.asset_id == apartment_asset_id

        # Set rental start time
        self.rental_start_time.set(Algorand.latest_timestamp())

    @Algorand.external
    def return_asset(self, asset_txn: Algorand.AssetTransferTransaction):
        # Logic to handle returning the asset
        assert Algorand.latest_timestamp() >= (self.rental_start_time.get() + self.rental_duration.get())
        assert asset_txn.asset_id == self.asset_management_app_id.get()

# Deploy the contract
if __name__ == "__main__":
    algorand = Algorand()
    rental_transaction_contract = RentalTransactionContract()
    rental_transaction_contract.deploy(algorand)