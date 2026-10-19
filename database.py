import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="MyNewPassword123!",
        database="fraud_system_v2"
    )

def get_transactions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions")

    rows = cursor.fetchall()

    print("TOTAL RECORDS IN DB:", len(rows))   # ✅ DEBUG LINE

    cursor.close()
    conn.close()

    return rows

def save_alert(tx_id, score, message):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO fraud_alerts (TransactionID, AlertMessage, RiskScore)
        VALUES (%s, %s, %s)
    """, (tx_id, message, score))

    conn.commit()
    cursor.close()
    conn.close()


def create_incident(tx_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO incidents (TransactionID, Status, Notes)
        VALUES (%s, %s, %s)
    """, (tx_id, "OPEN", "Investigate transaction"))

    conn.commit()
    cursor.close()
    conn.close()


def log_action(action):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO audit_logs (Action)
        VALUES (%s)
    """, (action,))

    conn.commit()
    cursor.close()
    conn.close()