from app.extensions import db
from datetime import datetime, timezone


class MyDataLog(db.Model):
    __tablename__ = 'mydata_logs'

    id = db.Column(db.Integer, primary_key=True)

    # Σύνδεση με το Invoice
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)

    # UUID Ιχνηλασιμότητας
    correlation_id = db.Column(db.String(100), nullable=True)

    # TEST / PROD
    environment = db.Column(db.String(20), default='PROD')

    # Ημ/νία Κλήσης
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Ενέργεια (Send/Cancel)
    action = db.Column(db.String(50), nullable=False)

    # Επιτυχία;
    success = db.Column(db.Boolean, default=False)

    # XML Αιτήματος (Text για μεγάλα κείμενα)
    request_xml = db.Column(db.Text, nullable=True)

    # XML Απάντησης
    response_xml = db.Column(db.Text, nullable=True)

    # Μήνυμα Λάθους (αν υπάρχει)
    error_message = db.Column(db.Text, nullable=True)

    # Relationship: Ώστε να γράφουμε invoice.logs και να βλέπουμε το ιστορικό
    invoice = db.relationship('Invoice', backref=db.backref('mydata_logs', lazy=True))

    def __repr__(self):
        return f'<MyDataLog {self.action} - {self.success}>'