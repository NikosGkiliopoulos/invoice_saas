from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.user import User
from app.models.subscription import SubscriptionPlan
from app.auth.forms import LoginForm, RegistrationForm
from . import auth


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))  # Θα το φτιάξουμε μετά

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Έλεγχος κωδικού
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Λάθος email ή κωδικός.', 'danger')

    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Έλεγχος αν υπάρχει ήδη το email
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Το email χρησιμοποιείται ήδη.', 'warning')
            return redirect(url_for('auth.register'))

        # Κρυπτογράφηση κωδικού
        hashed_pw = generate_password_hash(form.password.data)

        # Ανάθεση Default Plan (π.χ. Free ή Standard με ID=1)
        # Σιγουρέψου ότι υπάρχει έστω ένα πλάνο στη βάση, αλλιώς βάλε None
        default_plan = SubscriptionPlan.query.filter_by(code='free').first()
        plan_id = default_plan.id if default_plan else None

        new_user = User(
            email=form.email.data,
            password_hash=hashed_pw,
            plan_id=plan_id
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Ο λογαριασμός δημιουργήθηκε! Τώρα μπορείτε να συνδεθείτε.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))