from app.extensions import db
from datetime import datetime, timezone


class ProductService(db.Model):
    __tablename__ = 'products_services'

    id = db.Column(db.Integer, primary_key=True)

    # Σύνδεση με User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # --- Βασικά Στοιχεία ---
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Μετονομάστηκε από unit_price σε default_price
    default_price = db.Column(db.Float, nullable=False)

    # --- myDATA Defaults ---
    # Το ποσοστό ΦΠΑ (π.χ. 24.0) - Χρήσιμο για υπολογισμούς
    vat_percent = db.Column(db.Float, default=24.0)

    # Ο Κωδικός Κατηγορίας ΦΠΑ myDATA (π.χ. 1 = 24%, 2 = 13%, 7 = 0%)
    vat_category = db.Column(db.Integer, default=1)

    # Ο Χαρακτηρισμός E3 (π.χ. E3_561_001)
    classification_type = db.Column(db.String(50), default='E3_561_001')

    # Η Κατηγορία myDATA (π.χ. category2_1)
    classification_category = db.Column(db.String(50), default='category2_1')

    # --- Διαχείριση ---
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    user = db.relationship('User', backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f'<Product {self.title} - {self.default_price}€>'