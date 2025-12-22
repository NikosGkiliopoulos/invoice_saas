from app.extensions import db
from datetime import datetime, timezone


# --- 1. Η Κεφαλίδα του Τιμολογίου ---
class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)

    # Σύνδεση με User (Εκδότης) και Customer (Λήπτης)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)

    # --- Στοιχεία Παραστατικού ---
    series = db.Column(db.String(10), default='A')  # Σειρά (π.χ. Α)
    number = db.Column(db.Integer, nullable=False)  # Αύξων Αριθμός

    # Ημερομηνία και Ώρα ξεχωριστά όπως το ζήτησες
    issue_date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    issue_time = db.Column(db.Time, default=lambda: datetime.now(timezone.utc).time())

    # Είδος Παραστατικού myDATA (π.χ. "1.1" = Τιμολόγιο Πώλησης, "2.1" = ΑΠΥ)
    invoice_type = db.Column(db.String(20), nullable=False, default="1.1")

    # --- Οικονομικά Στοιχεία ---
    net_value = db.Column(db.Float, default=0.0)  # Καθαρή Αξία
    vat_value = db.Column(db.Float, default=0.0)  # Αξία ΦΠΑ
    total_value = db.Column(db.Float, default=0.0)  # Σύνολο Πληρωτέο

    # --- Πληρωμή & Κατάσταση ---
    # Τρόπος Πληρωμής (3=Μετρητά/Κατάθεση, 5=Κάρτα, κλπ)
    payment_method = db.Column(db.String(50), default="3")
    is_paid = db.Column(db.Boolean, default=False)

    # Status: 'draft' (Πρόχειρο), 'sent' (Εστάλη myDATA), 'cancelled' (Ακυρώθηκε)
    status = db.Column(db.String(20), default='draft')

    # --- myDATA Response ---
    mydata_mark = db.Column(db.String(100), nullable=True)  # ΜΑΡΚ Έκδοσης
    mydata_uid = db.Column(db.String(100), nullable=True)  # UID Αναγνωριστικό
    cancel_mark = db.Column(db.String(100), nullable=True)  # ΜΑΡΚ Ακύρωσης (αν ακυρωθεί)

    # Αποθήκευση αρχείου
    pdf_path = db.Column(db.String(500), nullable=True)  # Π.χ. /static/invoices/INV-A-1.pdf

    # --- Relationships ---
    user = db.relationship('User', backref=db.backref('invoices', lazy=True))
    customer = db.relationship('Customer', backref=db.backref('invoices', lazy=True))

    # items relationship ορίζεται παρακάτω

    def __repr__(self):
        return f'<Invoice {self.series}#{self.number} ({self.invoice_type})>'


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)

    # Κρατάμε το product_id (προαιρετικά) για να ξέρουμε από ποιο προϊόν προήλθε η γραμμή
    product_id = db.Column(db.Integer, db.ForeignKey('products_services.id'), nullable=True)

    # --- Βασικά Στοιχεία Γραμμής ---
    title = db.Column(db.String(200), nullable=False)  # Περιγραφή Είδους
    quantity = db.Column(db.Float, default=1.0)  # Ποσότητα

    # ΝΕΟ ΠΕΔΙΟ: Μονάδα Μέτρησης
    measurement_unit = db.Column(db.String(20), default='τεμ')  # Μονάδα (τεμ/ώρες/kg)

    unit_price = db.Column(db.Float, nullable=False)  # Τιμή Μονάδας
    net_value = db.Column(db.Float, nullable=False)  # Σύνολο Γραμμής

    # --- myDATA Λεπτομέρειες ---
    vat_percent = db.Column(db.Float, default=24.0)  # ΦΠΑ %

    # ΝΕΟ ΠΕΔΙΟ: Κωδικός ΦΠΑ (1-8)
    vat_category = db.Column(db.Integer, default=1)  # Κωδικός ΦΠΑ myDATA

    # Κρατάμε και το ποσό ΦΠΑ για ευκολία υπολογισμών, παρόλο που δεν ήταν στο διάγραμμα,
    # είναι απαραίτητο για το Invoice Header summation.
    vat_amount = db.Column(db.Float, nullable=False)

    classification_type = db.Column(db.String(50), default='E3_561_001')  # Χαρακτηρισμός Εσόδου

    # ΝΕΟ ΠΕΔΙΟ: Κατηγορία Χαρακτηρισμού
    classification_category = db.Column(db.String(50), default='category2_1')

    # Relationship
    invoice = db.relationship('Invoice', backref=db.backref('items', cascade="all, delete-orphan", lazy=True))

    def __repr__(self):
        return f'<Item {self.title}>'