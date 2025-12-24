from app.extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # --- Βασικά Στοιχεία (PK & Login) ---
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # --- Subscription Status ---
    # ΔΙΟΡΘΩΣΗ: Τώρα πρέπει να είναι ForeignKey για να δουλέψει το relationship
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=True, default=1)

    subscription_expires = db.Column(db.DateTime, nullable=True)
    billing_cycle = db.Column(db.String(20), default='monthly')
    auto_renew = db.Column(db.Boolean, default=False)

    # --- Security & Audit ---
    is_email_verified = db.Column(db.Boolean, default=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(50), nullable=True)

    # Χρήση timezone-aware datetime για σωστή λειτουργία
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # --- Στοιχεία Τιμολόγησης Freelancer (Profile) ---
    afm = db.Column(db.String(20), nullable=True)
    company_title = db.Column(db.String(200), nullable=True)
    profession = db.Column(db.String(200), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    doy = db.Column(db.String(100), nullable=True)

    # --- myDATA Credentials (Encrypted) ---
    aade_user_id = db.Column(db.String(500), nullable=True)
    aade_key = db.Column(db.String(500), nullable=True)

    # --- Relationships ---
    # Τώρα αυτό θα δουλέψει επειδή υπάρχει το ForeignKey στο plan_id
    plan = db.relationship('SubscriptionPlan', backref='users')

    def __repr__(self):
        return f'<User {self.email}>'