from fraud_engine import analyze

def test_fraud_transaction():
    tx = [
        "1", "2", "3", "4", "5",
        "25000",          # amount
        "6",
        "Cape Town",      # location
        "Flagged"         # status
    ]

    level, score, reasons = analyze(tx)

    assert level == "FRAUD"
    assert score == 120

def test_normal_transaction():
    tx = [
        "1", "2", "3", "4", "5",
        "1000",
        "6",
        "Johannesburg",
        "Normal"
    ]

    level, score, reasons = analyze(tx)

    assert level == "OK"
    assert score == 0