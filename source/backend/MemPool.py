import random
from datetime import datetime
import pandas as pd

class MempoolTransaction:
    def __init__(self, ticker, fee, amount, sender, recipient, dt=None):
        self.ticker = ticker
        self.fee = fee
        self.amount = amount
        self.sender = sender
        self.recipient = recipient
        self.confirmed = False
        self.timestamp = None
        self.dt = dt if dt else datetime.now()

    def to_dict(self):
        return {
            'ticker': self.ticker,
            'fee': self.fee,
            'amount': self.amount,
            'sender': self.sender,
            'recipient': self.recipient,
            'confirmed': self.confirmed,
            'timestamp': self.timestamp,
            'dt': self.dt
        }


class MemPool:
    def __init__(self):
        self.transactions = []

    def get_pending_transactions(self):
        return [transaction for transaction in self.transactions if not transaction.confirmed]
    
    def get_confirmed_transactions(self):
        return [transaction for transaction in self.transactions if transaction.confirmed]
    
    @property
    def transaction_log(self):
        return pd.DataFrame.from_records([t.to_dict() for t in self.transactions]).set_index('dt')

# Example usage
# mempool = MemPool()

# Randomly add transactions to the mempool in a while loop
# while True:
    # transaction = "Transaction " + str(mempool.total_transactions + 1)
    # fee = random.uniform(0.01, 0.1)
    # amount = random.randint(1, 100)
    # mempool.add_transaction(transaction, fee, amount)
    # print(f"Added transaction: {transaction}, Fee: {fee}, Amount: {amount}")
    # time.sleep(random.uniform(0.5, 2.0))  # Random sleep interval between adding transactions

    # # Process transactions
    # mempool.process_transactions()

    # # Retrieve pending transactions
    # pending_transactions = mempool.get_pending_transactions()
    # print("Pending transactions:")
    # for mempool_transaction in pending_transactions:
        # print(f"Transaction: {mempool_transaction.transaction}, Fee: {mempool_transaction.fee}, Amount: {mempool_transaction.amount}, Confirmed: {mempool_transaction.confirmed}, Timestamp: {mempool_transaction.timestamp}")

