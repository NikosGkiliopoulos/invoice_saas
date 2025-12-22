from app import create_app, db
from app.models.subscription import SubscriptionPlan, PaymentTransaction
from app.models.user import User
from app.models.security import ActivityLog, EmailVerification
from app.models.customer import Customer
from app.models.product import ProductService
from app.models.invoice import Invoice, InvoiceItem
from app.models.audit import MyDataLog
from datetime import datetime, timezone, timedelta

app = create_app()


def run_test():
    with app.app_context():
        # 1. ΚΑΘΑΡΙΣΜΟΣ & ΔΗΜΙΟΥΡΓΙΑ ΒΑΣΗΣ
        print("⏳ Διαγραφή παλιάς βάσης και δημιουργία νέας...")
        db.drop_all()
        db.create_all()
        print("✅ Η βάση δημιουργήθηκε με ΟΛΟΥΣ τους πίνακες.")

        # ==========================================
        # 2. SETUP ΣΥΝΔΡΟΜΩΝ (Subscriptions)
        # ==========================================
        print("\n--- 1. Testing Subscriptions ---")
        free_plan = SubscriptionPlan(
            name="Free Plan", code="free",
            price_monthly=20.0, invoice_limit_per_month=3
        )
        db.session.add(free_plan)
        db.session.commit()  # Save to get ID

        # ==========================================
        # 3. SETUP ΧΡΗΣΤΗ (User & Payment)
        # ==========================================
        print("--- 2. Testing User & Payments ---")
        user = User(
            email="nikosss2005@gmail.com", password_hash="6239239232932362d23dv2ydby8bx723b32x8x",
            plan_id=free_plan.id,
            company_title="Gkiliopoulos AE",
            afm="2837623578"
        )
        db.session.add(user)
        db.session.commit()

        # Πληρωμή
        payment = PaymentTransaction(
            user_id=user.id, plan_id=free_plan.id,
            amount=0.0, provider="Stripe", status="success"
        )
        db.session.add(payment)

        # Καταγραφή Security Log (User Login)
        log = ActivityLog(
            user_id=user.id, action="LOGIN",
            ip_address="192.168.1.1", entity_name="User"
        )
        db.session.add(log)
        db.session.commit()

        # ==========================================
        # 4. BUSINESS DATA (Customer & Product)
        # ==========================================
        print("--- 3. Testing Customers & Products ---")
        customer = Customer(
            user_id=user.id, name="Mpakaliaros pelaths",
            afm="999999999", country_code="GR"
        )
        db.session.add(customer)

        product = ProductService(
            user_id=user.id, title="Real estate chatbot",
            default_price=300.0, vat_percent=24.0
        )
        db.session.add(product)
        db.session.commit()

        # ==========================================
        # 5. INVOICING (Header & Items)
        # ==========================================
        print("--- 4. Testing Invoices (Complex) ---")

        # Header
        inv = Invoice(
            user_id=user.id, customer_id=customer.id,
            series="A", number=12,
            issue_date=datetime.now(timezone.utc).date(),
            issue_time=datetime.now(timezone.utc).time(),
            status="draft"
        )
        db.session.add(inv)
        db.session.commit()  # Save to get Invoice ID

        # Item (Γραμμή)
        item = InvoiceItem(
            invoice_id=inv.id,
            product_id=product.id,
            title="Hosting Services 2025",
            quantity=2.0,
            measurement_unit="τεμ",  # <--- ΝΕΟ ΠΕΔΙΟ
            unit_price=100.0,
            net_value=200.0,
            vat_percent=24.0,
            vat_category=1,  # <--- ΝΕΟ ΠΕΔΙΟ
            vat_amount=48.0,
            classification_category="category2_1"  # <--- ΝΕΟ ΠΕΔΙΟ
        )
        db.session.add(item)

        # Update Header Totals
        inv.net_value = 200.0
        inv.vat_value = 48.0
        inv.total_value = 248.0
        db.session.commit()

        # ==========================================
        # 6. AUDIT (MyData Log)
        # ==========================================
        print("--- 5. Testing MyData Audit Logs ---")
        audit = MyDataLog(
            invoice_id=inv.id,
            action="SendInvoices",
            environment="PROD",
            success=True,
            correlation_id="uuid-1234-5678"
        )
        db.session.add(audit)
        db.session.commit()

        # ==========================================
        # 7. FINAL VERIFICATION (Read Back)
        # ==========================================
        print("\n✅ ΕΛΕΓΧΟΣ ΔΕΔΟΜΕΝΩΝ:")

        fetched_user = User.query.first()
        print(f"👤 User Plan: {fetched_user.plan.name} (Limit: {fetched_user.plan.invoice_limit_per_month})")

        fetched_inv = Invoice.query.first()
        print(f"📄 Invoice: {fetched_inv.series}#{fetched_inv.number} | Total: {fetched_inv.total_value}€")

        # Έλεγχος της γραμμής (Item)
        fetched_item = fetched_inv.items[0]
        print(f"   ↳ Item: {fetched_item.title} | Qty: {fetched_item.quantity} {fetched_item.measurement_unit} {fetched_item.unit_price}")
        print(f"   ↳ myDATA: Category {fetched_item.vat_category} | Class: {fetched_item.classification_category}")

        fetched_log = MyDataLog.query.filter_by(invoice_id=fetched_inv.id).first()
        print(f"📡 Audit Log: Action '{fetched_log.action}' was Success? {fetched_log.success}")
        print(f"pelaths: '{customer.name}', '{customer.afm}'")


if __name__ == '__main__':
    run_test()