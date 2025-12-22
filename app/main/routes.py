from flask import render_template
from flask_login import login_required, current_user
from . import main

@main.route('/')
@main.route('/dashboard')
@login_required # Μόνο συνδεδεμένοι χρήστες
def dashboard():
    return render_template('dashboard.html', user=current_user)