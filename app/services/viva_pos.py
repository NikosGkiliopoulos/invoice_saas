import requests
import base64
import uuid
import time
import os


class VivaTerminalService:
    def __init__(self):
        # --- ΡΥΘΜΙΣΕΙΣ (Μπορείς να τα βάλεις και σε .env file αργότερα) ---
        self.MERCHANT_ID = os.getenv('VIVA_MERCHANT_ID')
        self.CLIENT_ID = os.getenv('VIVA_CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('VIVA_CLIENT_SECRET')
        self.TERMINAL_ID = os.getenv('VIVA_TERMINAL_ID')

        if not all([self.MERCHANT_ID, self.CLIENT_ID, self.CLIENT_SECRET, self.TERMINAL_ID]):
            print("❌ ΠΡΟΣΟΧΗ: Λείπουν ρυθμίσεις Viva από το .env αρχείο!")

        # URLs
        self.TOKEN_URL = "https://demo-accounts.vivapayments.com/connect/token"
        self.BASE_URL = "https://demo-api.vivapayments.com/ecr/v1"

    def _get_token(self):
        """Εσωτερική συνάρτηση για λήψη Token"""
        auth_str = f"{self.CLIENT_ID}:{self.CLIENT_SECRET}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()
        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        try:
            resp = requests.post(self.TOKEN_URL, headers=headers, data={"grant_type": "client_credentials"})
            if resp.status_code == 200:
                return resp.json()['access_token']
            else:
                print(f"❌ Auth Error: {resp.text}")
                return None
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return None

    def charge(self, amount_euros, reference="SaaS Order"):
        """
        Κύρια συνάρτηση χρέωσης.
        :param amount_euros: Το ποσό σε Ευρώ (π.χ. 10.50)
        :param reference: Κωδικός παραγγελίας (π.χ. 'Order #123')
        :return: (True/False, TransactionData/ErrorMsg)
        """

        # 1. Μετατροπή Ευρώ σε Cents (Η Viva θέλει ακέραιο, π.χ. 10.50 -> 1050)
        amount_cents = int(amount_euros * 100)

        print(f"🚀 Έναρξη συναλλαγής για {amount_euros}€ ({amount_cents} cents)...")

        # 2. Λήψη Token
        token = self._get_token()
        if not token:
            return False, "Αδυναμία σύνδεσης με Viva (Token Error)"

        # 3. Αποστολή Εντολής
        session_id = str(uuid.uuid4())
        sale_url = f"{self.BASE_URL}/transactions:sale"

        payload = {
            "sessionId": session_id,
            "terminalId": self.TERMINAL_ID,
            "cashRegisterId": "SAAS_APP",
            "amount": amount_cents,
            "currencyCode": "978",  # EUR
            "merchantReference": reference,
            "customerTrns": f"Payment: {amount_euros} EUR",
            "paymentMethod": "CardPresent",
            "tipAmount": 0,  # Υποχρεωτικό
            "showTransactionResult": True,
            "showReceipt": True
        }

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        try:
            resp = requests.post(sale_url, json=payload, headers=headers)
            if resp.status_code != 200:
                return False, f"Η εντολή απορρίφθηκε: {resp.text}"
        except Exception as e:
            return False, str(e)

        print("✅ Η εντολή στάλθηκε στο POS. Αναμονή πελάτη...")

        # 4. Polling (Αναμονή για αποτέλεσμα) - Timeout 60 δευτερόλεπτα
        check_url = f"{self.BASE_URL}/transactions"

        for i in range(20):  # 20 φορές * 3 δευτερόλεπτα = 60 sec
            time.sleep(3)
            print(f"⏳ Έλεγχος κατάστασης ({i + 1}/20)...", end="\r")

            try:
                # Ζητάμε τα details του συγκεκριμένου Session
                check_resp = requests.get(
                    f"{check_url}?sessionId={session_id}&merchantId={self.MERCHANT_ID}",
                    headers=headers
                )

                if check_resp.status_code == 200:
                    data = check_resp.json()
                    if data and isinstance(data, list) and len(data) > 0:
                        transaction = data[0]
                        print("\n🎉 Η ΠΛΗΡΩΜΗ ΟΛΟΚΛΗΡΩΘΗΚΕ!")
                        return True, transaction
            except:
                pass  # Συνεχίζουμε να προσπαθούμε

        return False, "Timeout: Ο πελάτης δεν πλήρωσε εντός χρόνου."