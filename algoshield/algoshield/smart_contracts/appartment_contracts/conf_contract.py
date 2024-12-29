from algopy import Algorand, Contract, State

class AssetManagementContract(Contract):
    def __init__(self):
        super().__init__()
        self.apartment_asset_id = State.uint64()
        self.owner_address = State.bytes()

    @Algorand.external
    def configure(self, apartment_asset: Algorand.Asset, owner: Algorand.Address):
        self.apartment_asset_id.set(apartment_asset.asset_id())
        self.owner_address.set(owner)

# Deploy the contract
if __name__ == "__main__":
    algorand = Algorand()
    asset_management_contract = AssetManagementContract()
    asset_management_contract.deploy(algorand)