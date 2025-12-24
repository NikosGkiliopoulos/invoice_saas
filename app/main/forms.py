from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


# Έλεγχος αν το ΑΦΜ αποτελείται από 9 ψηφία
def validate_afm_length(form, field):
    if len(field.data) != 9 or not field.data.isdigit():
        raise ValidationError('Το ΑΦΜ πρέπει να αποτελείται από 9 ψηφία.')


class CompanySettingsForm(FlaskForm):
    company_title = StringField('Επωνυμία Επιχείρησης', validators=[DataRequired(), Length(min=2, max=200)])
    afm = StringField('Α.Φ.Μ.', validators=[DataRequired(), validate_afm_length])
    doy = StringField('Δ.Ο.Υ.', validators=[DataRequired()])
    profession = StringField('Δραστηριότητα (Επάγγελμα)', validators=[DataRequired()])
    address = StringField('Διεύθυνση Έδρας', validators=[DataRequired()])

    # Προαιρετικά πεδία για myDATA (τα αφήνουμε απλά text προς το παρόν)
    aade_user_id = StringField('myDATA User ID')
    aade_key = StringField('myDATA Subscription Key')

    submit = SubmitField('Αποθήκευση Αλλαγών')


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired, Length


class CustomerForm(FlaskForm):
    # Επιλογή: Εταιρεία ή Ιδιώτης
    customer_type = SelectField('Τύπος Πελάτη',
                                choices=[('B2B', 'Εταιρεία / Ελεύθερος Επαγγελματίας'), ('B2C', 'Ιδιώτης')])

    name = StringField('Επωνυμία / Ονοματεπώνυμο', validators=[DataRequired(), Length(min=2, max=200)])

    # Το ΑΦΜ δεν είναι υποχρεωτικό αν είναι Ιδιώτης (B2C), αλλά εδώ το βάζουμε προαιρετικό στο validation
    afm = StringField('Α.Φ.Μ.', validators=[Length(max=20)])

    profession = StringField('Δραστηριότητα (Επάγγελμα)')

    # Διεύθυνση
    address = StringField('Διεύθυνση (Οδός & Αριθμός)', validators=[DataRequired()])
    city = StringField('Πόλη', validators=[DataRequired()])
    postal_code = StringField('Τ.Κ.', validators=[DataRequired()])

    email = EmailField('Email')

    submit = SubmitField('Αποθήκευση Πελάτη')


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length


class ProductServiceForm(FlaskForm):
    title = StringField('Τίτλος Υπηρεσίας / Προϊόντος', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Περιγραφή (Προαιρετικό)')

    # Προσοχή: Το ονομάζουμε default_price όπως στο μοντέλο σου
    default_price = FloatField('Τιμή Μονάδας (Καθαρή Αξία €)', validators=[DataRequired()])

    # Επιλογή ΦΠΑ (αποθηκεύουμε το ποσοστό στο vat_percent)
    vat_percent = SelectField('Φ.Π.Α. (%)', choices=[
        (24.0, '24% (Κανονικός)'),
        (13.0, '13% (Μειωμένος)'),
        (6.0, '6% (Υπερμειωμένος)'),
        (0.0, '0% (Άνευ ΦΠΑ)')
    ], coerce=float)

    submit = SubmitField('Αποθήκευση')