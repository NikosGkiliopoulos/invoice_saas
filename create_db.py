from app import create_app, db
from app.models.user import User
from app.models.customer import Customer
from app.models.product import ProductService
from app.models.invoice import Invoice, InvoiceItem
from datetime import datetime, timezone, timedelta

app = create_app()

with app.app_context():
    # Καθαρισμός
    db.drop_all()
    db.create_all()
    print("✅ Η βάση ενημερώθηκε (Updated Invoice Schema).")

    # 1. Δημιουργία User & Customer & Product (τα γνωστά)
    freelancer = User(
        email="architect@saas.gr", password_hash="123",
        company_title="Office Design", afm="999999999",
        subscription_expires=datetime.now(timezone.utc) + timedelta(days=365)
    )
    db.session.add(freelancer)

    db.session.flush()  # Για να πάρουμε το ID του freelancer άμεσα

    client = Customer(user_id=freelancer.id, name="Hotel SA", afm="888888888", country_code="GR")
    db.session.add(client)

    service = ProductService(
        user_id=freelancer.id, title="Μελέτη Χώρου", default_price=1000.00,
        vat_percent=24.0, vat_category=1,
        classification_type="E3_561_001", classification_category="category2_1"
    )
    db.session.add(service)
    db.session.commit()

    # --- 2. ΔΗΜΙΟΥΡΓΙΑ ΤΙΜΟΛΟΓΙΟΥ ΜΕ ΤΟ ΝΕΟ ΣΧΗΜΑ ---

    now = datetime.now(timezone.utc)

    invoice = Invoice(
        user_id=freelancer.id,
        customer_id=client.id,

        series="A",
        number=101,

        # Προσοχή: Χωρίζουμε ημερομηνία και ώρα
        issue_date=now.date(),
        issue_time=now.time(),

        invoice_type="1.1",  # Τιμολόγιο Πώλησης
        payment_method="3",  # Κατάθεση
        status="draft",
        is_paid=False,

        # Αρχικά μηδενικά, θα τα υπολογίσουμε μετά την προσθήκη των items
        net_value=0, vat_value=0, total_value=0
    )
    db.session.add(invoice)
    db.session.commit()

    # Προσθήκη Γραμμής
    qty = 1
    price = service.default_price
    net = price * qty
    vat = net * (service.vat_percent / 100)

    item = InvoiceItem(
        invoice_id=invoice.id,
        product_id=service.id,
        title=service.title,
        quantity=qty,
        unit_price=price,
        vat_percent=service.vat_percent,
        net_value=net,
        vat_amount=vat,
        classification_type=service.classification_type
    )
    db.session.add(item)

    # Ενημέρωση Κεφαλίδας (Header)
    invoice.net_value = net
    invoice.vat_value = vat
    invoice.total_value = net + vat
    invoice.pdf_path = f"/files/invoices/{invoice.series}-{invoice.number}.pdf"

    db.session.commit()

    print(f"📄 Invoice: {invoice.invoice_type} | {invoice.series}#{invoice.number}")
    print(f"📅 Date: {invoice.issue_date} | Time: {invoice.issue_time}")
    print(f"💰 Total: {invoice.total_value}€ | Method: {invoice.payment_method}")
    print(f"📂 PDF Path: {invoice.pdf_path}")