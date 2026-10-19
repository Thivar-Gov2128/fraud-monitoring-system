def analyze(tx):
    amount = float(tx[5])
    location = tx[7]
    status = tx[8]

    risk_score = 0
    reasons = []

    if amount > 20000:
        risk_score += 50
        reasons.append("High amount")

    if location not in ["Johannesburg"]:
        risk_score += 30
        reasons.append("Unusual location")

    if status == "Flagged":
        risk_score += 40
        reasons.append("Flagged transaction")

    if risk_score >= 70:
        level = "FRAUD"
    elif risk_score >= 40:
        level = "RISK"
    else:
        level = "OK"

    return level, risk_score, reasons