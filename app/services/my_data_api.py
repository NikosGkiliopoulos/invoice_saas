import requests
import xml.etree.ElementTree as ET
from flask import current_app


# Αν το Config είναι σε άλλο φάκελο, ίσως χρειαστείς: from config import Config
# Αλλά επειδή περνάμε τα κλειδιά ως ορίσματα, χρειαζόμαστε το Config μόνο για το URL.
# Για σιγουριά, θα βάλουμε το URL καρφωτό εδώ ή θα το πάρουμε δυναμικά.

class MyDataAPI:
    @staticmethod
    def send_invoice(xml_payload, user_id, subscription_key):
        """
        Στέλνει το XML στην ΑΑΔΕ.
        Δέχεται 3 ορίσματα: το XML, το User ID και το Subscription Key.
        """

        # URL για Development (Sandbox)
        # Αν θέλεις να το παίρνει από το config, μπορείς να κάνεις: current_app.config['AADE_URL']
        url = 'https://mydataapidev.aade.gr/SendInvoices'

        headers = {
            "aade-user-id": user_id,
            "ocp-apim-subscription-key": subscription_key,
            "Content-Type": "application/xml"
        }

        try:
            # 1. Αποστολή Request
            response = requests.post(url, data=xml_payload.encode('utf-8'), headers=headers)

            # 2. Ανάλυση (Parsing)
            root = ET.fromstring(response.text)

            # Ελέγχουμε αν υπάρχει statusCode = Success (με wildcard {*} για τα namespaces)
            status_code_node = root.find('.//{*}statusCode')

            if status_code_node is not None and status_code_node.text == 'Success':
                # --- ΕΠΙΤΥΧΙΑ ---
                mark = root.find('.//{*}invoiceMark').text
                uid = root.find('.//{*}invoiceUid').text

                # Δημιουργία QR URL
                generated_qr_url = f"https://mydata.aade.gr/qrcode/?q={uid}"

                return {
                    'success': True,
                    'mark': mark,
                    'uid': uid,
                    'qr_url': generated_qr_url
                }
            else:
                # --- ΑΠΟΤΥΧΙΑ ---
                errors = []
                for error in root.findall('.//{*}error'):
                    msg_node = error.find('.//{*}message')
                    code_node = error.find('.//{*}code')

                    msg = msg_node.text if msg_node is not None else "Unknown Message"
                    code = code_node.text if code_node is not None else "Unknown Code"
                    errors.append(f"{code}: {msg}")

                # Αν δεν βρήκε errors tags αλλά δεν είναι success, επιστρέφουμε το raw text
                if not errors:
                    errors.append(f"HTTP Status: {response.status_code} - {response.text}")

                return {
                    'success': False,
                    'errors': errors,
                    'raw_response': response.text
                }

        except Exception as e:
            return {'success': False, 'errors': [f"System Error: {str(e)}"]}