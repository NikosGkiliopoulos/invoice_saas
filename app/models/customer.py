from app.extensions import db
from datetime import datetime, timezone


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)

    # Σύνδεση με τον Χρήστη
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # --- Βασικά Στοιχεία ---
    name = db.Column(db.String(200), nullable=False)  # Επωνυμία / Ονοματεπώνυμο
    afm = db.Column(db.String(20), nullable=True)  # ΑΦΜ (κενό αν είναι ιδιώτης χωρίς τιμολόγιο)
    profession = db.Column(db.String(200), nullable=True)  # Δραστηριότητα

    # myDATA: 0 = Έδρα, 1 = Υποκατάστημα
    branch = db.Column(db.Integer, default=0)

    # --- Διεύθυνση ---
    address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country_code = db.Column(db.String(2), default='GR')  # ISO Code

    # --- Κατηγοριοποίηση & Επαφή ---
    customer_type = db.Column(db.String(20), default='B2B')  # Επιλογές: 'B2B', 'B2C'
    email = db.Column(db.String(120), nullable=True)  # Για αποστολή PDF

    # --- Audit ---
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # --- Relationship ---
    user = db.relationship('User', backref=db.backref('customers', lazy=True))

    def __repr__(self):
        return f'<Customer {self.name} - {self.customer_type}>'