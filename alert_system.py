def send_alert(transaction, risk_score):
    print(f"🚨 ALERT: {transaction.transaction_id}")
    print(f"Customer: {transaction.name}")
    print(f"Amount: {transaction.amount}")
    print(f"Risk Score: {risk_score}")