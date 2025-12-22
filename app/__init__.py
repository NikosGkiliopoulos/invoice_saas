from flask import Flask
from .extensions import db, login_manager

def create_app():
    app = Flask(__name__)

    # Ρυθμίσεις (Config)
    # Χρησιμοποιούμε SQLite για αρχή -> θα φτιάξει ένα αρχείο app.db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'secret-key-gia-dokimes'

    # Σύνδεση της βάσης με το app
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Αν δεν είσαι logged in, σε πάει εδώ
    login_manager.login_message_category = 'info'
    # Εισαγωγή των Models ώστε να τα "δει" η βάση
    with app.app_context():
        from .models import user
        from .models import customer
        from .models import product
        from .models import invoice
        from .models import subscription
        from .models import security
        from .models import audit

        @login_manager.user_loader
        def load_user(user_id):
            return user.User.query.get(int(user_id))

        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/auth')

        from .main import main as main_blueprint
        app.register_blueprint(main_blueprint)

        # Θα χρειαστούμε και ένα main blueprint για την αρχική σελίδα αργότερα
        # from .main import main as main_blueprint
        # app.register_blueprint(main_blueprint)

        db.create_all()

    return app