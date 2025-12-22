from app.extensions import db
from datetime import datetime, timezone


# --- 1. ACTIVITY LOG ---
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)

    # Ποιος έκανε την ενέργεια
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Τύπος (UPDATE/DELETE/LOGIN)
    action = db.Column(db.String(50), nullable=False)

    # Πίνακας (Customer/Invoice)
    entity_name = db.Column(db.String(50), nullable=True)

    # ID της εγγραφής που άλλαξε
    entity_id = db.Column(db.String(50), nullable=True)

    # JSON: Τα δεδομένα ΠΡΙΝ
    old_values = db.Column(db.JSON, nullable=True)

    # JSON: Τα δεδομένα ΜΕΤΑ
    new_values = db.Column(db.JSON, nullable=True)

    # Η IP του χρήστη
    ip_address = db.Column(db.String(50), nullable=True)

    # Πότε συνέβη
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    user = db.relationship('User', backref=db.backref('activity_logs', lazy=True))


# --- 2. EMAIL VERIFICATION ---
class EmailVerification(db.Model):
    __tablename__ = 'email_verifications'

    id = db.Column(db.Integer, primary_key=True)

    # User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # URL Token
    token = db.Column(db.String(255), nullable=False)

    # Λήξη token
    expires_at = db.Column(db.DateTime, nullable=False)

    # Relationship
    user = db.relationship('User', backref=db.backref('email_verifications', lazy=True))


# --- 3. PASSWORD RESET ---
class PasswordReset(db.Model):
    __tablename__ = 'password_resets'

    id = db.Column(db.Integer, primary_key=True)

    # User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Hash του token
    token_hash = db.Column(db.String(255), nullable=False)

    # Λήξη token
    expires_at = db.Column(db.DateTime, nullable=False)

    # Χρησιμοποιήθηκε;
    used = db.Column(db.Boolean, default=False)

    # Relationship
    user = db.relationship('User', backref=db.backref('password_resets', lazy=True))