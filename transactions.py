class Transaction:
    def __init__(self, transaction_id, name, amount, tx_type):
        self.transaction_id = transaction_id
        self.name = name
        self.amount = amount
        self.tx_type = tx_type

    def __str__(self):
        return f"{self.transaction_id} | {self.name} | {self.amount} | {self.tx_type}"
