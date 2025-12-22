from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Αρχικοποίηση της βάσης δεδομένων
db = SQLAlchemy()
login_manager = LoginManager()