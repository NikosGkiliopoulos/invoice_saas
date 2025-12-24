import xml.etree.ElementTree as ET
from collections import defaultdict


class XMLBuilder:
    @staticmethod
    def create_invoice_xml(invoice, company_config):
        """
        Δημιουργεί το XML για ένα τιμολόγιο (myDATA v1.0.9).
        Υπολογίζει αυτόματα τα σύνολα από τις γραμμές για αποφυγή λαθών.
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

        # --- ISSUER ---
        xml_parts.append(f"""
            <issuer>
                <vatNumber>{company_config['afm']}</vatNumber>
                <country>GR</country>
                <branch>{company_config.get('branch', 0)}</branch>
            </issuer>
        """)

        # --- COUNTERPART ---
        # Ελέγχουμε αν υπάρχει ο πελάτης και το ΑΦΜ του
        try:
            customer_afm = invoice.customer.afm
        except AttributeError:
            customer_afm = ""  # Αν δεν υπάρχει customer object

        xml_parts.append('<counterpart>')
        if customer_afm:
            xml_parts.append(f'<vatNumber>{customer_afm}</vatNumber>')
            xml_parts.append('<country>GR</country>')
        else:
            xml_parts.append('<country>GR</country>')
        xml_parts.append('<branch>0</branch>')
        xml_parts.append('</counterpart>')

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
        # Χρησιμοποιούμε το total_value του invoice, ή 0 αν είναι None
        total_pay = invoice.total_value if hasattr(invoice, 'total_value') else 0

        xml_parts.append(f"""
            <paymentMethods>
                <paymentMethodDetails>
                    <type>{getattr(invoice, 'payment_method', '3')}</type> 
                    <amount>{fmt(total_pay)}</amount>
                </paymentMethodDetails>
            </paymentMethods>
        """)

        # --- DETAILS & CALCULATION ---
        # Μεταβλητές για υπολογισμό συνόλων ON-THE-FLY
        calc_total_net = 0.0
        calc_total_vat = 0.0
        classification_totals = defaultdict(float)

        for index, item in enumerate(invoice.items, 1):
            # Λήψη τιμών γραμμής (με προστασία αν είναι None)
            line_net = item.net_value or 0.0
            line_vat = item.vat_amount or 0.0

            # Αθροισμός για το Summary
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
        # Χρησιμοποιούμε τις υπολογισμένες μεταβλητές (calc_...) και όχι τα πεδία του invoice object
        # Αυτό λύνει το πρόβλημα "'Invoice' object has no attribute..."
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