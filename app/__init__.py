from flask import Flask
from .extensions import db, login_manager
# ΣΗΜΑΝΤΙΚΟ: Κάνουμε import το αρχείο ρυθμίσεων
from config import Config


def create_app():
    app = Flask(__name__)

    # Ρυθμίσεις (Config)
    # Τώρα το Flask διαβάζει τα πάντα (DB, Secret Key, myDATA keys) από το config.py
    app.config.from_object(Config)

    # Σύνδεση της βάσης με το app
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Εισαγωγή των Models και Blueprints
    with app.app_context():
        # Models
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

        # Blueprints
        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/auth')

        from .main import main as main_blueprint
        app.register_blueprint(main_blueprint)

        # Δημιουργία πινάκων (αν δεν υπάρχουν)
        db.create_all()

    return app