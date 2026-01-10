import xml.etree.ElementTree as ET
from collections import defaultdict
import html  # <--- ΠΡΟΣΘΗΚΗ 1


class XMLBuilder:
    @staticmethod
    def create_invoice_xml(invoice, company_config):
        """
        Δημιουργεί το XML για ένα τιμολόγιο (myDATA v1.0.9).
        """

        # Helper για escape ειδικών χαρακτήρων (&, <, >)
        def escape(val):  # <--- ΠΡΟΣΘΗΚΗ 2
            return html.escape(str(val or ''))

        def fmt(val):
            return "{:.2f}".format(val or 0)

        xmlns = "http://www.aade.gr/myDATA/invoice/v1.0"
        xmlns_icls = "https://www.aade.gr/myDATA/incomeClassificaton/v1.0"

        issue_date_str = invoice.issue_date.strftime('%Y-%m-%d')

        xml_parts = []
        # Προσοχή: Στο InvoicesDoc καλό είναι να δηλώνεις το namespace prefix
        xml_parts.append(f'<InvoicesDoc xmlns="{xmlns}" xmlns:icls="{xmlns_icls}">')
        xml_parts.append('<invoice>')

        # --- ISSUER ---
        xml_parts.append(f"""
            <issuer>
                <vatNumber>{escape(company_config['afm'])}</vatNumber>
                <country>GR</country>
                <branch>{company_config.get('branch', 0)}</branch>
            </issuer>
        """)

        # --- COUNTERPART ---
        customer_afm = getattr(invoice, 'customer_afm', None)
        if not customer_afm and hasattr(invoice, 'customer') and invoice.customer:
            customer_afm = invoice.customer.afm

        # Logic: Αν υπάρχει ΑΦΜ το βάζουμε. Αν όχι (Λιανική) το παραλείπουμε.
        # ΠΡΟΣΟΧΗ: Αν είναι Τιμολόγιο (1.1) και δεν έχει ΑΦΜ, θα χτυπήσει Error αργότερα,
        # αλλά εδώ φτιάχνουμε απλώς το XML.
        if customer_afm:
            # Παίρνουμε τα στοιχεία ή κενά strings
            name = getattr(invoice, 'customer_name', '') or (invoice.customer.name if invoice.customer else '')
            address = getattr(invoice, 'customer_address', '') or ''
            city = getattr(invoice.customer, 'city', '') if invoice.customer else ''
            postal = getattr(invoice.customer, 'postal_code', '') if invoice.customer else ''

            xml_parts.append(f"""
                <counterpart>
                    <vatNumber>{escape(customer_afm)}</vatNumber>
                    <country>GR</country>
                    <branch>0</branch>
                    <name>{escape(name)}</name>
                    <address>
                        <street>{escape(address)}</street>
                        <postalCode>{escape(postal)}</postalCode>
                        <city>{escape(city)}</city>
                    </address>
                </counterpart>
            """)

        # --- HEADER ---
        xml_parts.append(f"""
            <invoiceHeader>
                <series>{escape(invoice.series)}</series>
                <aa>{invoice.number}</aa>
                <issueDate>{issue_date_str}</issueDate>
                <invoiceType>{invoice.invoice_type}</invoiceType> 
                <currency>EUR</currency>
            </invoiceHeader>
        """)

        # --- PAYMENT METHODS ---
        total_pay = invoice.total_value if getattr(invoice, 'total_value', None) else 0
        xml_parts.append(f"""
            <paymentMethods>
                <paymentMethodDetails>
                    <type>{getattr(invoice, 'payment_method', '3')}</type> 
                    <amount>{fmt(total_pay)}</amount>
                </paymentMethodDetails>
            </paymentMethods>
        """)

        # --- DETAILS & CALCULATION ---
        calc_total_net = 0.0
        calc_total_vat = 0.0
        classification_totals = defaultdict(float)

        for index, item in enumerate(invoice.items, 1):
            line_net = item.net_value or 0.0
            line_vat = item.vat_amount or 0.0

            calc_total_net += line_net
            calc_total_vat += line_vat

            class_key = (item.classification_type, item.classification_category)
            classification_totals[class_key] += line_net

            xml_parts.append(f"""
                <invoiceDetails>
                    <lineNumber>{index}</lineNumber>
                    <netValue>{fmt(line_net)}</netValue>
                    <vatCategory>{item.vat_category}</vatCategory> 
                    <vatAmount>{fmt(line_vat)}</vatAmount>
                    <incomeClassification>
                        <icls:classificationType>{item.classification_type}</icls:classificationType>
                        <icls:classificationCategory>{item.classification_category}</icls:classificationCategory>
                        <icls:amount>{fmt(line_net)}</icls:amount>
                    </incomeClassification>
                </invoiceDetails>
            """)

        calc_total_gross = calc_total_net + calc_total_vat

        # --- SUMMARY ---
        xml_parts.append(f"""
            <invoiceSummary>
                <totalNetValue>{fmt(calc_total_net)}</totalNetValue>
                <totalVatAmount>{fmt(calc_total_vat)}</totalVatAmount>
                <totalWithheldAmount>0.00</totalWithheldAmount>
                <totalFeesAmount>0.00</totalFeesAmount>
                <totalStampDutyAmount>0.00</totalStampDutyAmount>
                <totalOtherTaxesAmount>0.00</totalOtherTaxesAmount>
                <totalDeductionsAmount>0.00</totalDeductionsAmount>
                <totalGrossValue>{fmt(calc_total_gross)}</totalGrossValue>
        """)

        for (ctype, ccat), amount in classification_totals.items():
            xml_parts.append(f"""
                <incomeClassification>
                    <icls:classificationType>{ctype}</icls:classificationType>
                    <icls:classificationCategory>{ccat}</icls:classificationCategory>
                    <icls:amount>{fmt(amount)}</icls:amount>
                </incomeClassification>
            """)

        xml_parts.append('</invoiceSummary>')
        xml_parts.append('</invoice>')
        xml_parts.append('</InvoicesDoc>')

        return "".join(xml_parts)