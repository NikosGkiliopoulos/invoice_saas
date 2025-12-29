import xml.etree.ElementTree as ET
from collections import defaultdict


class XMLBuilder:
    @staticmethod
    def create_invoice_xml(invoice, company_config):
        """
        Δημιουργεί το XML για ένα τιμολόγιο (myDATA v1.0.9).
        Διορθώνει το Error 101 αποκρύπτοντας το counterpart στη Λιανική.
        """

        # 1. Namespaces & Formatters
        xmlns = "http://www.aade.gr/myDATA/invoice/v1.0"
        xmlns_icls = "https://www.aade.gr/myDATA/incomeClassificaton/v1.0"

        issue_date_str = invoice.issue_date.strftime('%Y-%m-%d')

        def fmt(val):
            return "{:.2f}".format(val or 0)

        # 2. Ξεκινάμε το XML
        xml_parts = []
        xml_parts.append(f'<InvoicesDoc xmlns="{xmlns}" xmlns:icls="{xmlns_icls}">')
        xml_parts.append('<invoice>')

        # --- ISSUER (Εκδότης) ---
        xml_parts.append(f"""
            <issuer>
                <vatNumber>{company_config['afm']}</vatNumber>
                <country>GR</country>
                <branch>{company_config.get('branch', 0)}</branch>
            </issuer>
        """)

        # --- COUNTERPART (Πελάτης) ---
        # Προσπάθεια εύρεσης ΑΦΜ (κοιτάμε πρώτα το snapshot, μετά τη σχέση)
        customer_afm = getattr(invoice, 'customer_afm', None)

        # Αν το snapshot είναι κενό, δοκιμάζουμε από το relationship (για παλιά records)
        if not customer_afm and hasattr(invoice, 'customer') and invoice.customer:
            customer_afm = invoice.customer.afm

        # ΣΗΜΑΝΤΙΚΗ ΔΙΟΡΘΩΣΗ:
        # Αν υπάρχει ΑΦΜ -> Προσθέτουμε τον Counterpart.
        # Αν ΔΕΝ υπάρχει (Λιανική) -> ΔΕΝ βάζουμε τίποτα.
        if customer_afm:
            xml_parts.append(f"""
                <counterpart>
                    <vatNumber>{customer_afm}</vatNumber>
                    <country>GR</country>
                    <branch>0</branch>
                </counterpart>
            """)
        else:
            # Στη λιανική χωρίς ΑΦΜ, το myDATA απαιτεί να ΜΗΝ υπάρχει καθόλου το counterpart block
            pass

        # --- HEADER ---
        xml_parts.append(f"""
            <invoiceHeader>
                <series>{invoice.series}</series>
                <aa>{invoice.number}</aa>
                <issueDate>{issue_date_str}</issueDate>
                <invoiceType>{invoice.invoice_type}</invoiceType> 
                <currency>EUR</currency>
            </invoiceHeader>
        """)

        # --- PAYMENT METHODS ---
        # Χρησιμοποιούμε το total_value ή 0
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

            # Αθροισμός Χαρακτηρισμών
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

        # Υπολογισμός τελικού συνόλου (Gross)
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

        # Προσθήκη των συγκεντρωτικών χαρακτηρισμών
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