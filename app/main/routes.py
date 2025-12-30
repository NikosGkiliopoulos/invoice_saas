from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from . import main
from .forms import CompanySettingsForm, CustomerForm
from app.models.customer import Customer
from app.models.product import ProductService  # <-- Σιγουρέψου ότι το αρχείο λέγεται product.py
from app.main.forms import ProductServiceForm  # <-- Import τη νέα φόρμα
import os
from app.models.invoice import Invoice, InvoiceItem
import json
from datetime import datetime
from app.services.data_loader import DataLoader
from app.services.xml_builder import XMLBuilder
from app.services.my_data_api import MyDataAPI
import qrcode
from io import BytesIO
import base64
from app.services.viva_pos import VivaTerminalService  # <-- ΝΕΟ IMPORT


# Η αρχική σελίδα (Dashboard)
@main.route('/')
@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


# Η σελίδα Ρυθμίσεων
@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = CompanySettingsForm()

    # Αν πατηθεί το κουμπί 'Αποθήκευση' και όλα είναι σωστά:
    if form.validate_on_submit():
        current_user.company_title = form.company_title.data
        current_user.afm = form.afm.data
        current_user.doy = form.doy.data
        current_user.profession = form.profession.data
        current_user.address = form.address.data
        current_user.aade_user_id = form.aade_user_id.data
        current_user.aade_key = form.aade_key.data

        # Αποθήκευση στη βάση
        db.session.commit()
        flash('Τα στοιχεία ενημερώθηκαν επιτυχώς!', 'success')
        return redirect(url_for('main.settings'))

    # Αν φορτώνουμε τη σελίδα (GET), γέμισε τη φόρμα με τα υπάρχοντα στοιχεία
    if request.method == 'GET':
        form.company_title.data = current_user.company_title
        form.afm.data = current_user.afm
        form.doy.data = current_user.doy
        form.profession.data = current_user.profession
        form.address.data = current_user.address
        current_user.aade_user_id = form.aade_user_id.data
        current_user.aade_key = form.aade_key.data

    return render_template('settings.html', form=form)


@main.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    form = CustomerForm()

    if form.validate_on_submit():
        new_customer = Customer(
            user_id=current_user.id,

            # Βασικά Στοιχεία
            customer_type=form.customer_type.data,
            name=form.name.data,
            afm=form.afm.data,
            profession=form.profession.data,

            # Διεύθυνση
            address=form.address.data,
            city=form.city.data,
            postal_code=form.postal_code.data,
            # country_code='GR', # Το έχουμε default στο μοντέλο, δεν χρειάζεται να το βάλουμε εδώ

            email=form.email.data


        )

        db.session.add(new_customer)
        db.session.commit()
        flash('Ο πελάτης αποθηκεύτηκε επιτυχώς!', 'success')
        return redirect(url_for('main.customers'))

    # Εμφάνιση λίστας
    my_customers = Customer.query.filter_by(user_id=current_user.id).all()

    return render_template('customers.html', form=form, customers=my_customers)


@main.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    form = ProductServiceForm()

    if form.validate_on_submit():
        # Μικρή λογική για να βρούμε την κατηγορία ΦΠΑ myDATA
        # (1=24%, 2=13%, 3=6%, 7=0%)
        v_percent = form.vat_percent.data
        v_category = 1  # Default 24%
        if v_percent == 13.0:
            v_category = 2
        elif v_percent == 6.0:
            v_category = 3
        elif v_percent == 0.0:
            v_category = 7

        new_item = ProductService(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            default_price=form.default_price.data,  # <-- Το πεδίο σου
            vat_percent=v_percent,  # <-- Το πεδίο σου
            vat_category=v_category,  # <-- Αυτόματο myDATA ID

            # Τα υπόλοιπα (classification_type, category) τα αφήνουμε στα defaults του μοντέλου σου
            # μέχρι να φτιάξουμε τις ρυθμίσεις myDATA
        )

        db.session.add(new_item)
        db.session.commit()
        flash('Η υπηρεσία αποθηκεύτηκε!', 'success')
        return redirect(url_for('main.products'))

    # Εμφάνιση λίστας (μόνο τα active)
    my_products = ProductService.query.filter_by(user_id=current_user.id, is_active=True).all()

    return render_template('products.html', form=form, products=my_products)


def load_json_data(filename):
    """Φορτώνει δεδομένα από το φάκελο app/data"""
    try:
        filepath = os.path.join(current_app.root_path, 'data', filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Σφάλμα κατά τη φόρτωση του {filename}: {e}")
        return []


@main.route('/invoices/new', methods=['GET', 'POST'])
@login_required
def new_invoice():
    # --- 1. ΛΕΙΤΟΥΡΓΙΑ ΑΠΟΘΗΚΕΥΣΗΣ (POST) ---
    if request.method == 'POST':
        try:
            data = request.get_json()

            # Τι επιλέχθηκε στο πεδίο πελάτη; (Μπορεί να είναι ID ή 'retail')
            customer_selection = data.get('customer_id')

            if not customer_selection:
                return jsonify({'success': False, 'message': 'Δεν επιλέχθηκε πελάτης.'}), 400

            # --- ΛΟΓΙΚΗ ΕΠΙΛΟΓΗΣ ΠΕΛΑΤΗ ---
            if customer_selection == 'retail':
                # Α. ΠΕΡΙΠΤΩΣΗ ΛΙΑΝΙΚΗΣ
                cust_id = None  # Δεν συνδέεται με ID στη βάση
                inv_type = '11.1'  # Απόδειξη Λιανικής Πώλησης

                # Στοιχεία Snapshot (Καρφωτά)
                snap_name = "Πελάτης Λιανικής"
                snap_afm = ""
                snap_address = ""
                snap_doy = ""
            else:
                # Β. ΠΕΡΙΠΤΩΣΗ ΚΑΝΟΝΙΚΟΥ ΠΕΛΑΤΗ (ΤΙΜΟΛΟΓΙΟ)
                customer = Customer.query.get(int(customer_selection))
                if not customer:
                    return jsonify({'success': False, 'message': 'Ο πελάτης δεν βρέθηκε.'}), 404

                cust_id = customer.id
                inv_type = '1.1'  # Τιμολόγιο Πώλησης

                # Στοιχεία Snapshot (Από τη βάση)
                snap_name = customer.name
                snap_afm = customer.afm
                snap_address = customer.address
                snap_doy = customer.doy

            # Γ. Βρίσκουμε τον επόμενο αριθμό
            last_invoice = Invoice.query.filter_by(user_id=current_user.id) \
                .order_by(Invoice.number.desc()) \
                .first()
            next_number = (last_invoice.number + 1) if last_invoice else 1

            # Δ. Δημιουργία της Κεφαλίδας (Invoice)
            new_invoice = Invoice(
                user_id=current_user.id,
                customer_id=cust_id,  # Μπορεί να είναι None (αν είναι λιανική)

                # Αποθήκευση στοιχείων κειμένου (Snapshot)
                customer_name=snap_name,
                customer_afm=snap_afm,
                customer_address=snap_address,
                customer_doy=snap_doy,

                series='A',
                number=next_number,
                invoice_type=inv_type,  # 1.1 ή 11.1 αυτόματα
                issue_date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                payment_method=data.get('payment_method', '3'),  # 3=Μετρητά, 7=POS (θα έρθει από τη φόρμα)
                status='draft',
                net_value=0.0,
                vat_value=0.0,
                total_value=0.0
            )

            db.session.add(new_invoice)
            db.session.flush()

            # Ε. Δημιουργία των Γραμμών (Items)
            total_net = 0.0
            total_vat = 0.0

            for item_data in data['items']:
                qty = float(item_data['quantity'])
                price = float(item_data['unit_price'])
                vat_pct = float(item_data['vat_percent'])

                line_net = qty * price
                line_vat_amount = line_net * (vat_pct / 100)

                if inv_type == '11.1':
                    e3_code = 'E3_561_003'
                else:
                    e3_code = 'E3_561_001'

                new_item = InvoiceItem(
                    invoice_id=new_invoice.id,
                    product_id=int(item_data['product_id']) if item_data['product_id'] else None,
                    title=item_data['title'],
                    quantity=qty,
                    unit_price=price,
                    vat_percent=vat_pct,
                    vat_category=int(item_data['vat_category']),

                    # Υπολογισμένα πεδία
                    net_value=line_net,
                    vat_amount=line_vat_amount,

                    # Σταθερά πεδία myDATA (όπως τα είχες)
                    measurement_unit='1',
                    classification_type=e3_code,
                    classification_category='category1_1'
                )

                db.session.add(new_item)
                total_net += line_net
                total_vat += line_vat_amount

            # ΣΤ. Ενημέρωση των συνόλων
            new_invoice.net_value = total_net
            new_invoice.vat_value = total_vat
            new_invoice.total_value = total_net + total_vat

            db.session.commit()

            msg_type = "Απόδειξη" if inv_type == '11.1' else "Τιμολόγιο"
            return jsonify({
                'success': True,
                'message': f'Η {msg_type} #{next_number} δημιουργήθηκε επιτυχώς!',
                'redirect_url': url_for('main.invoices')
            })

        except Exception as e:
            db.session.rollback()
            print(f"Error creating invoice: {e}")
            return jsonify({'success': False, 'message': 'Παρουσιάστηκε σφάλμα κατά την αποθήκευση.'}), 500

    # --- 2. ΛΕΙΤΟΥΡΓΙΑ ΕΜΦΑΝΙΣΗΣ (GET) ---
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    products = ProductService.query.filter_by(user_id=current_user.id, is_active=True).all()

    payment_methods = DataLoader.get_payment_methods()
    vat_categories = DataLoader.get_vat_categories()
    quantity_types = DataLoader.get_quantity_types()
    classification_types = DataLoader.get_income_classification_types()
    classification_categories = DataLoader.get_income_classification_categories()

    return render_template('create_invoice.html',
                           customers=customers,
                           products=products,
                           payment_methods=payment_methods,
                           vat_categories=vat_categories,
                           quantity_types=quantity_types,
                           classification_types=classification_types,
                           classification_categories=classification_categories)


@main.route('/invoices')
@login_required
def invoices():
    # Φέρνουμε όλα τα τιμολόγια του χρήστη, ταξινομημένα φθίνοντα (πιο πρόσφατο πρώτο)
    all_invoices = Invoice.query.filter_by(user_id=current_user.id) \
        .order_by(Invoice.issue_date.desc(), Invoice.number.desc()) \
        .all()

    return render_template('invoices.html', invoices=all_invoices)


@main.route('/invoices/<int:invoice_id>/send-mydata', methods=['POST'])
@login_required
def send_to_mydata(invoice_id):
    # 1. Βρίσκουμε το τιμολόγιο
    invoice = Invoice.query.get_or_404(invoice_id)

    # Ασφάλεια: Ανήκει στον χρήστη;
    if invoice.user_id != current_user.id:
        flash('Δεν έχετε δικαίωμα πρόσβασης.', 'danger')
        return redirect(url_for('main.invoices'))

    # Αν έχει ήδη σταλεί, δεν το ξαναστέλνουμε
    if invoice.status == 'sent':
        flash('Το παραστατικό έχει ήδη σταλεί στο myDATA.', 'warning')
        return redirect(url_for('main.invoices'))

    try:
        # 2. Στοιχεία Εκδότη
        issuer_data = {
            'afm': current_user.afm,
            'branch': 0
        }

        # 3. Δημιουργία XML
        xml_payload = XMLBuilder.create_invoice_xml(invoice, issuer_data)

        # 4. Ανάκτηση Κωδικών ΑΑΔΕ
        aade_user = current_user.aade_user_id
        aade_key = current_user.aade_key

        if not aade_user or not aade_key:
            flash('Λείπουν οι κωδικοί myDATA από τις ρυθμίσεις!', 'danger')
            return redirect(url_for('main.invoices'))

        # 5. Αποστολή στην ΑΑΔΕ
        # Η MyDataAPI.send_invoice επιστρέφει λεξικό: {'success': True, 'mark': '...', 'uid': '...'}
        result = MyDataAPI.send_invoice(xml_payload, aade_user, aade_key)

        if result['success']:
            # --- ΕΠΙΤΥΧΙΑ ---

            # Αποθήκευση στη Βάση (ΕΔΩ ΕΙΝΑΙ Η ΑΛΛΑΓΗ)
            # Χρησιμοποιούμε τα ονόματα που ορίσαμε στο models.py
            invoice.mydata_mark = result['mark']
            invoice.mydata_uid = result['uid']

            # Αλλάζουμε την κατάσταση
            invoice.status = 'sent'

            db.session.commit()

            # --- ΕΚΤΥΠΩΣΗ ΣΤΗΝ ΚΟΝΣΟΛΑ ---
            print("\n" + "=" * 50)
            print(f"✅ ΕΠΙΤΥΧΙΑ! MARK: {invoice.mydata_mark}")
            print(f"🔑 UID: {invoice.mydata_uid}")
            print("=" * 50 + "\n")

            flash(f'Επιτυχία! Το παραστατικό πήρε ΜΑΡΚ: {invoice.mydata_mark}', 'success')

        else:
            # --- ΑΠΟΤΥΧΙΑ ---
            error_msg = " / ".join(result['errors'])
            print(f"❌ Σφάλμα myDATA: {error_msg}")
            flash(f'Σφάλμα myDATA: {error_msg}', 'danger')

    except Exception as e:
        flash(f'Παρουσιάστηκε σφάλμα συστήματος: {str(e)}', 'danger')
        print(f"System Error: {e}")

    return redirect(url_for('main.invoices'))


@main.route('/invoices/<int:invoice_id>/print')
@login_required
def print_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)

    if invoice.user_id != current_user.id:
        flash('Δεν έχετε δικαίωμα πρόσβασης.', 'danger')
        return redirect(url_for('main.invoices'))

    company = current_user

    # --- ΔΗΜΙΟΥΡΓΙΑ QR CODE ---
    qr_b64 = None  # Αρχική τιμή (κενό)

    # Αν το τιμολόγιο έχει πάρει MARK, φτιάχνουμε το QR
    if invoice.mydata_mark:
        # ΠΡΟΣΟΧΗ: Εδώ κανονικά βάζουμε το URL που σου επέστρεψε η ΑΑΔΕ (result['qr_url']).
        # Αν δεν το έχεις αποθηκεύσει στη βάση (στήλη qr_url),
        # φτιάχνουμε προσωρινά ένα link για να δεις ότι δουλεύει η εικόνα.
        # Στο μέλλον πρέπει να παίρνεις το 'invoice.qr_url'.

        # Προσωρινό Link (Development)
        qr_data = f"https://mydataapidev.aade.gr/qrcode/?q={invoice.mydata_uid}"
        # Στο Production θα είναι: f"https://mydata.aade.gr/qrcode/?q={...}"

        # Ρυθμίσεις QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,  # Μέγεθος κουκκίδας
            border=1,  # Περιθώριο (μικρό για να χωράει)
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Δημιουργία εικόνας
        img = qr.make_image(fill_color="black", back_color="white")

        # Μετατροπή σε base64 για να μπει απευθείας στο HTML
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return render_template('print_invoice.html', invoice=invoice, company=company, qr_code=qr_b64)


@main.route('/invoices/<int:invoice_id>/pay-pos', methods=['POST'])
@login_required
def pay_invoice_pos(invoice_id):
    """
    Στέλνει εντολή στο τερματικό για πληρωμή του συγκεκριμένου τιμολογίου.
    """
    # 1. Βρίσκουμε το τιμολόγιο
    invoice = Invoice.query.get_or_404(invoice_id)

    # Ασφάλεια: Ανήκει στον χρήστη;
    if invoice.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Δεν έχετε δικαίωμα πρόσβασης.'}), 403

    # Έλεγχος αν έχει ήδη πληρωθεί
    if invoice.is_paid:
        return jsonify({'success': False, 'message': 'Το τιμολόγιο είναι ήδη πληρωμένο!'}), 400

    try:
        # 2. Εκκίνηση Viva Service
        viva_service = VivaTerminalService()

        print(f"💳 Εκκίνηση POS για #{invoice.number} - Ποσό: {invoice.total_value}€")

        # Κλήση στο τερματικό
        # ΔΙΟΡΘΩΣΗ: Χρησιμοποιούμε τα ονόματα ορισμάτων όπως ορίστηκαν στο viva_pos.py (amount, invoice_id)
        result = viva_service.process_payment(
            amount=invoice.total_value,
            invoice_id=invoice.id
        )

        # 3. Διαχείριση Αποτελέσματος
        if result['success']:
            # --- ΕΠΙΤΥΧΙΑ ---

            # Ενημέρωση Βάσης
            invoice.is_paid = True
            invoice.payment_method = '5'  # 5 = Κάρτα (κωδικός myDATA)

            # ΔΙΟΡΘΩΣΗ: Το transaction_id έρχεται απευθείας στο result, όχι μέσα σε 'data'
            invoice.transaction_id = result.get('transaction_id', 'Unknown')
            invoice.paid_at = datetime.now()

            db.session.commit()

            print(f"✅ Πληρώθηκε! Transaction ID: {invoice.transaction_id}")

            return jsonify({
                'success': True,
                'message': 'Η πληρωμή ολοκληρώθηκε επιτυχώς!',
                'transaction_id': invoice.transaction_id
            })

        else:
            # --- ΑΠΟΤΥΧΙΑ --- (π.χ. Timeout ή Cancel από πελάτη)
            print(f"❌ Αποτυχία POS: {result['message']}")
            return jsonify({'success': False, 'message': result['message']}), 500

    except Exception as e:
        print(f"System Error: {e}")
        # Καλό είναι να κάνουμε rollback αν σκάσει η βάση, αν και εδώ είμαστε σε try block πριν το commit
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Σφάλμα συστήματος: {str(e)}'}), 500