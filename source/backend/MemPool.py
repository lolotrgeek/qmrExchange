import random
from datetime import datetime

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


class MemPool:
    def __init__(self):
        self.transactions = []
        self.total_transactions = 0

    def add_transaction(self, ticker, fee, amount, sender, recipient, dt):
        self.total_transactions += 1
        if (fee == 0):
            return False
        mempool_transaction = MempoolTransaction(ticker, fee, amount, sender, recipient, dt)
        self.transactions.append(mempool_transaction)

    def process_transactions(self):
        unconfirmed_transactions = self.get_pending_transactions()
        unconfirmed_transactions.sort(key=lambda x: x.fee, reverse=True)
        num_unconfirmed = len(unconfirmed_transactions)
        for index, transaction in enumerate(unconfirmed_transactions):
            # create a probablity distribution for confirmation based on the length of the mempool
            confirmation_odds = .9 - (index / num_unconfirmed)
            if random.random() < confirmation_odds:
                transaction.confirmed = True
                num_unconfirmed -= 1        

    def get_pending_transactions(self):
        return [transaction for transaction in self.transactions if not transaction.confirmed]
    
    def get_confirmed_transactions(self):
        return [transaction for transaction in self.transactions if transaction.confirmed]


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

