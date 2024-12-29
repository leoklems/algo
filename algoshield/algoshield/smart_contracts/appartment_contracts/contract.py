from beaker import Application, external, GlobalStateValue
from pyteal import *

class AppatmentRental(Application):
    appatment_asset_id = GlobalStateValue(TealType.uint64)
    rent_amount = GlobalStateValue(TealType.uint64)
    owner_address = GlobalStateValue(TealType.bytes)
    rental_duration = GlobalStateValue(TealType.uint64)
    rental_start_time = GlobalStateValue(TealType.uint64)

    @external
    def configure(
        self,
        appatment_asset: abi.Asset,
        rent_price: abi.Uint64,
        owner: abi.Address,
        duration: abi.Uint64
    ):
        return Seq(
            self.appatment_asset_id.set(appatment_asset.asset_id()),
            self.rent_amount.set(rent_price.get()),
            self.owner_address.set(owner.get()),
            self.rental_duration.set(duration.get())
        )

    @external
    def rent(self, payment_txn: abi.PaymentTransaction, asset_txn: abi.AssetTransferTransaction):
        return Seq(
            Assert(payment_txn.get().amount() == self.rent_amount.get()),
            Assert(payment_txn.get().receiver() == self.owner_address.get()),
            Assert(asset_txn.get().asset_amount() == Int(1)),
            Assert(asset_txn.get().xfer_asset() == self.appatment_asset_id.get()),
            Assert(asset_txn.get().asset_sender() == self.owner_address.get()),
            self.rental_start_time.set(Global.latest_timestamp()),
            Approve()
        )

    @external
    def return_asset(self, asset_txn: abi.AssetTransferTransaction):
        return Seq(
            Assert(Global.latest_timestamp() >= (self.rental_start_time.get() + self.rental_duration.get())),
            Assert(asset_txn.get().asset_amount() == Int(1)),
            Assert(asset_txn.get().xfer_asset() == self.appatment_asset_id.get()),
            Assert(asset_txn.get().asset_sender() == self.owner_address.get()),
            Approve()
        )