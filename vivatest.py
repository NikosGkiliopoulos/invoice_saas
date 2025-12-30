import requests
import base64
import uuid
import datetime

# --- ΣΤΟΙΧΕΙΑ (POS API CREDENTIALS) ---
# ΠΡΟΣΟΧΗ: Θέλουμε τα κλειδιά από την ενότητα "POS APIs Credentials"
CLIENT_ID = "5aouqmbz2uviu36z96qqez2cutvy2zcxf3d1wat91ynq4.apps.vivapayments.com"
CLIENT_SECRET = "S58S853L1Hy8YTRjfWD14BGDnRu19F"  # <--- ΤΟ ΖΗΤΟΥΜΕΝΟ

# TERMINAL ID (Από το Sales > Physical Payments ή το App)
TERMINAL_ID = "16013397"

# ΕΝΑ ΤΥΧΑΙΟ ID ΓΙΑ ΤΗΝ "ΤΑΜΕΙΑΚΗ" ΜΑΣ
CASH_REGISTER_ID = "PYTHON_APP_001"


def run_cloud_terminal_sale():
    print("🚀 Ξεκινάμε διαδικασία Cloud Terminal API (ECR)...")

    # ---------------------------------------------------------
    # ΒΗΜΑ 1: ΛΗΨΗ TOKEN
    # ---------------------------------------------------------
    token_url = "https://demo-accounts.vivapayments.com/connect/token"
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers_auth = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print("🔑 Ζητάω Token...")
    try:
        resp_token = requests.post(token_url, headers=headers_auth, data={"grant_type": "client_credentials"})

        if resp_token.status_code != 200:
            print(f"❌ Authentication Failed ({resp_token.status_code})")
            print(resp_token.text)
            print("👉 Πιθανότατα λάθος Client Secret στα POS Credentials.")
            return

        access_token = resp_token.json()['access_token']
        print("✅ Token ελήφθη!")
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return

    # ---------------------------------------------------------
    # ΒΗΜΑ 2: ΑΠΟΣΤΟΛΗ ΠΛΗΡΩΜΗΣ (SALE)
    # Βάσει Docs: POST /ecr/v1/transactions:sale
    # ---------------------------------------------------------
    sale_url = "https://demo-api.vivapayments.com/ecr/v1/transactions:sale"

    session_id = str(uuid.uuid4())  # Μοναδικό ID για κάθε συναλλαγή

    payload = {
        "sessionId": session_id,
        "terminalId": TERMINAL_ID,
        "cashRegisterId": CASH_REGISTER_ID,
        "amount": 10000,  # 1.00 Ευρώ
        "currencyCode": "978",  # EUR
        "merchantReference": "Python Test 1",
        "customerTrns": "Test Transaction",
        "paymentMethod": "CardPresent",
        "tipAmount": 0,  # <--- ΑΥΤΟ ΕΛΕΙΠΕ! (Βάλε το μηδέν)
        "showTransactionResult": True,
        "showReceipt": True
    }

    headers_api = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    print(f"\n💸 Στέλνω 1.00€ στο τερματικό {TERMINAL_ID}...")

    try:
        resp_sale = requests.post(sale_url, json=payload, headers=headers_api)

        # 200 = OK (Success)
        if resp_sale.status_code == 200:
            print("\n🎉 ΕΠΙΤΥΧΙΑ! Η εντολή έφυγε!")
            print("👉 Κοίτα το κινητό σου, πρέπει να ζητάει κάρτα.")
            print(f"Session ID: {session_id}")

        # 400/404/500 = Errors
        else:
            print(f"\n❌ Σφάλμα ({resp_sale.status_code}):")
            print(resp_sale.text)

            if "Terminal is not connected" in resp_sale.text:
                print("⚠️ Το API λέει ότι το τερματικό είναι offline.")
                print("Άνοιξε την εφαρμογή στο κινητό και βεβαιώσου ότι έχει ίντερνετ.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")


if __name__ == "__main__":
    run_cloud_terminal_sale()