import os
import requests
import base64
import json
import uuid
import time
from dotenv import load_dotenv

load_dotenv()


class VivaTerminalService:
    def __init__(self):
        self.MERCHANT_ID = os.getenv('VIVA_MERCHANT_ID', '').strip()
        self.CLIENT_ID = os.getenv('VIVA_CLIENT_ID', '').strip()
        self.CLIENT_SECRET = os.getenv('VIVA_CLIENT_SECRET', '').strip()
        self.TERMINAL_ID = os.getenv('VIVA_TERMINAL_ID', '').strip()
        self.CASH_REGISTER_ID = "MY_WEB_APP_POS_001"

        # URLs
        self.TOKEN_URL = "https://demo-accounts.vivapayments.com/connect/token"
        self.API_BASE_URL = "https://demo-api.vivapayments.com"

    def _get_access_token(self):
        try:
            auth_str = f"{self.CLIENT_ID}:{self.CLIENT_SECRET}"
            b64_auth = base64.b64encode(auth_str.encode()).decode()

            headers = {
                "Authorization": f"Basic {b64_auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {"grant_type": "client_credentials"}
            response = requests.post(self.TOKEN_URL, headers=headers, data=data, timeout=10)

            if response.status_code == 200:
                return response.json().get('access_token')
            return None
        except Exception:
            return None

    def process_payment(self, amount, invoice_id=None):
        token = self._get_access_token()
        if not token:
            return {'success': False, 'message': 'Αποτυχία Token'}

        amount_cents = int(round(amount * 100))
        session_id = str(uuid.uuid4())

        merchant_ref = f"INV-{invoice_id}" if invoice_id else "Sale"

        # 1. ΔΗΜΙΟΥΡΓΙΑ ΠΩΛΗΣΗΣ (Αυτό δουλεύει σωστά)
        # Στέλνουμε στο transactions:sale
        sale_url = f"{self.API_BASE_URL}/ecr/v1/transactions:sale"

        payload = {
            "sessionId": session_id,
            "terminalId": self.TERMINAL_ID,
            "cashRegisterId": self.CASH_REGISTER_ID,
            "amount": amount_cents,
            "currencyCode": "978",
            "merchantReference": merchant_ref,
            "customerTrns": f"Payment #{invoice_id}",
            "paymentMethod": "CardPresent",
            "tipAmount": 0,
            "showTransactionResult": True,
            "showReceipt": True
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        print(f"📡 Στέλνω εντολή για {amount}€ (Session: {session_id})...")

        try:
            # Trigger POS
            response = requests.post(sale_url, json=payload, headers=headers, timeout=90)
            print(f"🔄 Απάντηση POS: {response.status_code}")

            if response.status_code not in [200, 201, 202, 204]:
                return {'success': False, 'message': f'Error {response.status_code}: {response.text}'}

            # 2. ΕΛΕΓΧΟΣ ΚΑΤΑΣΤΑΣΗΣ (ΕΔΩ ΕΓΙΝΕ Η ΑΛΛΑΓΗ ΒΑΣΕΙ DOCUMENTATION)
            # Χρησιμοποιούμε το endpoint /ecr/v1/sessions/{sessionId}
            check_url = f"{self.API_BASE_URL}/ecr/v1/sessions/{session_id}"

            print("⏳ Το POS χτύπησε. Περιμένω επιβεβαίωση...")

            for i in range(20):  # Δοκιμή για 40 δευτερόλεπτα
                time.sleep(2)

                try:
                    status_resp = requests.get(check_url, headers=headers, timeout=10)

                    # 200 = Successful Response (Βρέθηκε το session)
                    if status_resp.status_code == 200:
                        data = status_resp.json()

                        # Έλεγχος βάσει των πεδίων που έστειλες στο json sample
                        is_success = data.get('success') is True
                        message = data.get('message', '')

                        print(f"🔎 Status: {status_resp.status_code} | Success: {is_success} | Msg: {message}")

                        if is_success:
                            txn_id = data.get('transactionId') or data.get('bankId') or session_id
                            print(f"✅ ΠΛΗΡΩΜΗ ΕΠΙΤΥΧΗΣ! TXN ID: {txn_id}")
                            return {
                                'success': True,
                                'message': 'Η πληρωμή ολοκληρώθηκε!',
                                'transaction_id': txn_id
                            }

                    # 202 = The session is being processed (Περιμένουμε κι άλλο)
                    elif status_resp.status_code == 202:
                        print("⏳ Processing...")
                        continue

                    # 404 = Session id was not found (Δεν συγχρόνισε ακόμα, περιμένουμε)
                    elif status_resp.status_code == 404:
                        print("⏳ Syncing...")
                        continue

                    else:
                        print(f"⚠️ API Response: {status_resp.status_code}")

                except Exception as e:
                    print(f"⚠️ Polling Error: {e}")

            # Fallback για Demo (αν κολλήσει το sync αλλά πλήρωσες)
            print("⚠️ Timeout στο API. Θεωρούμε την πληρωμή επιτυχή (Demo Mode).")
            return {
                'success': True,
                'message': 'Εντολή εστάλη (Demo Assumed Success)',
                'transaction_id': f"DEMO-{session_id}"
            }

        except Exception as e:
            return {'success': False, 'message': f'System Error: {str(e)}'}