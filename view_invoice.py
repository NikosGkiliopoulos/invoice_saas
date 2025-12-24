import requests
import xml.dom.minidom
from datetime import datetime

# URL για τα Διαβιβασθέντα
URL = 'https://mydataapidev.aade.gr/RequestTransmittedDocs'

USER_ID = 'gkilio'
SUBSCRIPTION_KEY = 'd7e14f5f27447be02e0f9bd5b10cb1f4'

# Σημερινή ημερομηνία (ή η ημερομηνία που έβαλες στο τιμολόγιο)
TODAY = datetime.now().strftime("%d/%m/%Y")  # π.χ. "23/12/2025"


def get_invoices_by_date():
    headers = {
        'aade-user-id': USER_ID,
        'ocp-apim-subscription-key': SUBSCRIPTION_KEY
    }

    # Ζητάμε ΟΛΑ τα σημερινά
    params = {
        'dateFrom': TODAY,
        'dateTo': TODAY
    }

    print(f"📡 Αναζήτηση όλων των παραστατικών για την: {TODAY}...")

    try:
        response = requests.get(URL, headers=headers, params=params)

        if response.status_code == 200:
            # Έλεγχος μεγέθους απάντησης
            if not response.content or len(response.content) < 100:
                print("⚠️ Η λίστα είναι κενή (Το σύστημα δεν έχει ενημερωθεί ακόμα).")
            else:
                print("✅ Βρέθηκαν δεδομένα!")
                xml_str = xml.dom.minidom.parseString(response.text).toprettyxml()
                print("\n--- ΟΛΑ ΤΑ ΣΗΜΕΡΙΝΑ ΤΙΜΟΛΟΓΙΑ ΣΟΥ ---")
                print(xml_str)
                print("-------------------------------------")
        else:
            print(f"❌ Σφάλμα: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Connection Error: {e}")


if __name__ == '__main__':
    get_invoices_by_date()