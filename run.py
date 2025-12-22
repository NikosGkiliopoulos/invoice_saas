from app import create_app

# Δημιουργούμε την εφαρμογή χρησιμοποιώντας τη συνάρτηση που φτιάξαμε στο app/__init__.py
app = create_app()

if __name__ == '__main__':
    # Το debug=True μας βοηθάει να βλέπουμε τα λάθη αναλυτικά
    # και να κάνει reload ο server μόλις αλλάζουμε κώδικα.
    app.run(debug=True)