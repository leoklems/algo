appartment_asset_id = 123456  # Replace with actual ASA ID
rent_price = 1000000  # Example: 1 Algo
owner_address = "SOME_OWNER_ADDRESS"  # Replace with owner's address

# Call configure method
app.call(client, acct, "configure", appartment_asset=appartment_asset_id, rent_price=rent_price, owner=owner_address)
