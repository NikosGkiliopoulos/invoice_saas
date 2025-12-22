from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Κωδικός', validators=[DataRequired()])
    remember_me = BooleanField('Να με θυμάσαι')
    submit = SubmitField('Σύνδεση')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Κωδικός', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Επιβεβαίωση Κωδικού', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Εγγραφή')