from app.extensions import db
from datetime import datetime, timezone


# --- 1. Το Πλάνο Συνδρομής ---
class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)  # Όνομα (π.χ. Standard Plan)
    code = db.Column(db.String(50), unique=True, nullable=False)  # Κωδικός (free, standard)

    price_monthly = db.Column(db.Float, default=0.0)  # Τιμή μήνα
    price_yearly = db.Column(db.Float, default=0.0)  # Τιμή έτους

    # -1 = Απεριόριστα, >0 = Όριο
    invoice_limit_per_month = db.Column(db.Integer, default=5)

    is_active = db.Column(db.Boolean, default=True)  # Ενεργό πακέτο;

    def __repr__(self):
        return f'<SubscriptionPlan {self.name}>'


# --- 2. Η Συναλλαγή Πληρωμής ---
class PaymentTransaction(db.Model):
    __tablename__ = 'payment_transactions'

    id = db.Column(db.Integer, primary_key=True)

    # Ξένα Κλειδιά (Foreign Keys)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)

    # Οικονομικά Στοιχεία
    amount = db.Column(db.Float, nullable=False)  # Ποσό
    currency = db.Column(db.String(10), default='EUR')  # Νόμισμα
    cycle = db.Column(db.String(20), default='monthly')  # monthly / yearly

    # Στοιχεία Παρόχου
    provider = db.Column(db.String(50), default='Stripe')  # Stripe, PayPal, Bank
    transaction_id = db.Column(db.String(100), nullable=True)  # ID από την Τράπεζα
    status = db.Column(db.String(20), default='success')  # success, failed

    # Ημερομηνία (Timezone aware)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships (Για να μπορούμε να λέμε transaction.plan ή transaction.user)
    plan = db.relationship('SubscriptionPlan', backref=db.backref('transactions', lazy=True))
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))

    def __repr__(self):
        return f'<Transaction {self.transaction_id} - {self.amount}€>'