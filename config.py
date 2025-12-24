import os


class Config:
    # Βασικές ρυθμίσεις Flask (αν δεν τις έχεις ήδη αλλού)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ena-polu-mystiko-kleidi-gia-to-session'

    # Ρυθμίσεις Βάσης Δεδομένων
    # Βεβαιώσου ότι αυτό το path ταιριάζει με αυτό που είχες στο __init__.py
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Ρυθμίσεις myDATA (ΑΑΔΕ) ---
    # Για το Development (Δοκιμές)
    MYDATA_URL = 'https://mydataapidev.aade.gr/SendInvoices'
    # Βάλε εδώ τα κλειδιά που πήρες από το mydata-dev.azure-api.net
    # (Αν δεν έχεις κάνει εγγραφή ακόμα, πες μου να σου πω πώς)
