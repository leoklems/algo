from pyteal import *  # Import all the functions and classes from PyTeal library

def approval_program():  # Define the main approval program for the smart contract
    room_price_key = Bytes("RoomPrice")  # Key for storing room price
    room_owner_key = Bytes("RoomOwner")  # Key for storing the room owner's address

    # Initialize room price in the global state if it hasn't been set
    on_initialize = Seq([
        App.globalPut(room_price_key, Int(1000000)),  # Set the price for the room to 1 Algo (in microAlgos)
        Return(Int(1))  # Indicate success
    ])

    # Check if the room price is already set
    is_price_set = App.globalGet(room_price_key) != Int(0)

    # Check if the payment is correct
    is_payment_correct = Txn.amount() == App.globalGet(room_price_key)

    assign_room = Seq([  # If the payment is correct, assign the room to the sender
        App.globalPut(room_owner_key, Txn.sender()),  # Store the sender's address in the global state under the key "RoomOwner"
        Approve()  # Approve the transaction
    ])

    # Return conditions for the smart contract
    return Cond(  # Define the conditions for the smart contract
        [Txn.application_id() == Int(0), on_initialize],  # If initializing, set the room price
        [And(is_price_set, is_payment_correct), assign_room],  # If the room price is set and payment is correct, assign the room
        [Int(1), Reject()]  # If the payment is incorrect, reject the transaction
    )

def clear_state_program():  # Define the program to clear the contract's state
    return Approve()  # Approve clearing the state

# Compile the approval program to TEAL bytecode
compiled_approval = compileTeal(approval_program(), mode=Mode.Application, version=2)

# Compile the clear state program to TEAL bytecode
compiled_clear = compileTeal(clear_state_program(), mode=Mode.Application, version=2)